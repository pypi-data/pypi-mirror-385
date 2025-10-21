import warnings

import numpy as np
import scipy.interpolate

import aadc
import aadc.ndarray


def interp1d(x, y, kind="linear", axis=-1, copy=None, bounds_error=None, fill_value=np.nan, assume_sorted=None):
    if not (isinstance(x, aadc.ndarray.AADCArray) or isinstance(y, aadc.ndarray.AADCArray)):
        scipy_args = {
            "x": x,
            "y": y,
            "kind": kind,
            "axis": axis,
            "copy": copy,
            "bounds_error": bounds_error,
            "fill_value": fill_value,
        }
        if assume_sorted is not None:
            scipy_args["assume_sorted"] = assume_sorted
        if copy is not None:
            scipy_args["copy"] = copy
        return scipy.interpolate.interp1d(**scipy_args)

    assert kind in ["linear", "cubic"], "Only linear and cubic spline interpolation is supported"

    if axis != -1:
        warnings.warn("Only axis == -1 (default) is supported. Setting to -1.")
        axis = -1

    if (copy is not None) or copy:
        warnings.warn("Copy == True is not supported for the active version. Setting to False.")
        copy = False

    if bounds_error is not None:
        warnings.warn("Bounds error will be ignored for the active version - it will always extrapolate.")

    if not np.isnan(fill_value):
        warnings.warn("fill_value will be ignored for the active version.")

    assert (assume_sorted is None) or assume_sorted, "assume_sorted must be unset or set to True in the active version."

    if kind == "linear":
        return lambda x0: np.interp(x0, x, y)
    elif kind == "cubic":
        return CubicSpline(x, y)


class CubicSpline:
    __slots__ = ["x", "y", "b", "c", "d"]

    def __init__(self, x, y, axis=0, bc_type="not-a-knot", extrapolate=True):
        """
        Compute cubic spline interpolation

        Parameters:
        x : array of x-coordinates
        y : array of y-coordinates
        bc_type : string, optional
            Boundary condition type:
            - "not-a-knot": The third derivatives are equal at the first two and last two points
            - "natural": Second derivatives at endpoints are 0
            - "clamped": First derivatives at endpoints are 0
        """
        supported_bc_types = ["not-a-knot", "natural", "clamped"]
        assert axis == 0, "Currently only x == 0 is supported."
        assert extrapolate, "Currently only extrapolate == True is supported."
        assert bc_type in supported_bc_types, f"Unsupported bc_type. Supported types: {supported_bc_types}"
        assert x.size == y.size, "x and y must have same size"

        n = x.size

        left_not_a_knot = right_not_a_knot = bc_type == "not-a-knot"

        # Special case for 3-point not-a-knot spline. Simply fit a cubic polynomial.
        if n == 3 and left_not_a_knot and right_not_a_knot:
            dx = np.diff(x)
            dy = np.diff(y)
            slope = dy / dx

            system_matrix = aadc.array(np.zeros((3, 3)))
            system_matrix[0, 0] = 1
            system_matrix[0, 1] = 1
            system_matrix[1, 0] = dx[1]
            system_matrix[1, 1] = 2 * (dx[0] + dx[1])
            system_matrix[1, 2] = dx[0]
            system_matrix[2, 1] = 1
            system_matrix[2, 2] = 1

            b = aadc.array([2 * slope[0], 3 * (dx[1] * slope[0] + dx[0] * slope[1]), 2 * slope[1]])
            s = solve_3x3(system_matrix, b)

            self.x = x
            self.y = y
            self.b = s[:-1]  # b in previous version
            self.c = (slope - s[:-1]) / dx  # c in previous version
            self.d = (s[1:] + s[:-1] - 2 * slope) / (dx * dx)  # d in previous version
            return

        # Regular case
        # Calculate differences
        dx = np.diff(x)
        dy = np.diff(y)
        yp = dy / dx

        upper_diagonal = aadc.array(np.zeros(n - 1))
        main_diagonal = aadc.array(np.zeros(n))
        lower_diagonal = aadc.array(np.zeros(n - 1))
        r = aadc.array(np.zeros(n))

        lower_diagonal[:-1] += dx[:-1]
        main_diagonal[1:-1] += 2 * (dx[1:] + dx[:-1])
        upper_diagonal[1:] += dx[1:]
        r[1:-1] += 6 * (yp[1:] - yp[:-1])

        if bc_type == "natural":
            main_diagonal[0] += 1
            main_diagonal[-1] += 1
        elif bc_type == "clamped":
            main_diagonal[0] += 2 * dx[0]
            upper_diagonal[0] += dx[0]
            r[0] += 6 * yp[0]

            main_diagonal[-1] += 2 * dx[-1]
            lower_diagonal[-1] += dx[-1]
            r[-1] += -6 * yp[-1]

        if left_not_a_knot:
            lower_diagonal = lower_diagonal[1:]
            main_diagonal = main_diagonal[1:]
            upper_diagonal = upper_diagonal[1:]
            r = r[1:]

            main_diagonal[0] += dx[0] ** 2 / dx[1] + dx[0]
            upper_diagonal[0] += -(dx[0] ** 2) / dx[1]

        if right_not_a_knot:
            lower_diagonal = lower_diagonal[:-1]
            main_diagonal = main_diagonal[:-1]
            upper_diagonal = upper_diagonal[:-1]
            r = r[:-1]

            lower_diagonal[-1] += -(dx[-1] ** 2) / dx[-2]
            main_diagonal[-1] += dx[-1] ** 2 / dx[-2] + dx[-1]

        # Solve using Thomas algorithm
        full_m = thomas_solve(lower_diagonal, main_diagonal, upper_diagonal, r)

        if left_not_a_knot:
            m0 = aadc.array([1 / dx[1] * ((dx[0] + dx[1]) * full_m[0] - dx[0] * full_m[1])])
            full_m = np.concatenate((m0, full_m))

        if right_not_a_knot:
            mn = aadc.array([1 / dx[-2] * ((dx[-2] + dx[-1]) * full_m[-1] - dx[-1] * full_m[-2])])
            full_m = np.concatenate((full_m, mn))

        # Calculate coefficients
        self.x = x
        self.y = y
        self.b = yp - dx / 6 * (2 * full_m[:-1] + full_m[1:])
        self.c = full_m[:-1] / 2
        self.d = (full_m[1:] - full_m[:-1]) / (6 * dx)

    def __call__(self, x_val):
        i = np.searchsorted(self.x, x_val)
        i_clipped = np.minimum(np.maximum(i - 1, 0), len(self.x) - 2)

        extrapolate_left_sel = i == 0
        extrapolate_right_sel = i == len(self.x)

        interpolated_values = (
            self.y[i_clipped]
            + self.b[i_clipped] * (x_val - self.x[i_clipped])
            + self.c[i_clipped] * (x_val - self.x[i_clipped]) ** 2
            + self.d[i_clipped] * (x_val - self.x[i_clipped]) ** 3
        )

        extrapolate_left_values = (
            self.y[0]
            + self.b[0] * (x_val - self.x[0])
            + self.c[0] * (x_val - self.x[0]) ** 2
            + self.d[0] * (x_val - self.x[0]) ** 3
        )

        extrapolate_right_values = (
            self.y[-2]
            + self.b[-1] * (x_val - self.x[-2])
            + self.c[-1] * (x_val - self.x[-2]) ** 2
            + self.d[-1] * (x_val - self.x[-2]) ** 3
        )

        output = np.where(extrapolate_left_sel, extrapolate_left_values, interpolated_values)
        output = np.where(extrapolate_right_sel, extrapolate_right_values, output)
        return output


def thomas_solve(a, b, c, d):
    """
    Solves a tridiagonal system using the Thomas algorithm.

    Args:
        a: lower diagonal (first element is ignored)
        b: main diagonal
        c: upper diagonal (last element is ignored)
        d: right hand side

    Returns:
        Solution vector x
    """
    n = len(d)
    c_prime = aadc.array(np.zeros(n - 1))
    d_prime = aadc.array(np.zeros(n))
    x = aadc.array(np.zeros(n))

    # Forward sweep
    c_prime[0] = c[0] / b[0]
    d_prime[0] = d[0] / b[0]
    for i in range(1, n - 1):
        denominator = b[i] - a[i - 1] * c_prime[i - 1]
        c_prime[i] = c[i] / denominator
        d_prime[i] = (d[i] - a[i - 1] * d_prime[i - 1]) / denominator
    d_prime[n - 1] = (d[n - 1] - a[n - 2] * d_prime[n - 2]) / (b[n - 1] - a[n - 2] * c_prime[n - 2])

    # Back substitution
    x[n - 1] = d_prime[n - 1]
    for i in range(n - 2, -1, -1):
        x[i] = d_prime[i] - c_prime[i] * x[i + 1]

    return x


def solve_3x3(mat, b):
    """
    Solves a 3x3 system using Cramer's rule

    Args:
        mat: 3x3 coefficient matrix
        b: right hand side vector
    Returns:
        Solution vector x
    """

    def det3x3(m00, m01, m02, m10, m11, m12, m20, m21, m22):
        return m00 * (m11 * m22 - m12 * m21) - m01 * (m10 * m22 - m12 * m20) + m02 * (m10 * m21 - m11 * m20)

    det_val = det3x3(mat[0, 0], mat[0, 1], mat[0, 2], mat[1, 0], mat[1, 1], mat[1, 2], mat[2, 0], mat[2, 1], mat[2, 2])
    x = det3x3(b[0], mat[0, 1], mat[0, 2], b[1], mat[1, 1], mat[1, 2], b[2], mat[2, 1], mat[2, 2]) / det_val
    y = det3x3(mat[0, 0], b[0], mat[0, 2], mat[1, 0], b[1], mat[1, 2], mat[2, 0], b[2], mat[2, 2]) / det_val
    z = det3x3(mat[0, 0], mat[0, 1], b[0], mat[1, 0], mat[1, 1], b[1], mat[2, 0], mat[2, 1], b[2]) / det_val

    return aadc.array([x, y, z])
