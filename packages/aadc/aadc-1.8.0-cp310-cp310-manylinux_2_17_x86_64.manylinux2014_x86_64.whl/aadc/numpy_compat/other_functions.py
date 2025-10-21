import numpy as np

import aadc.ndarray
import aadc.numpy_compat.function_bindings as fbindings
import aadc.overrides_free
import aadc.utils as utils
from aadc import iand, ibool, iif, ior


# NOT IN ARRAY API
@fbindings.aadc_array_function_bind("isclose")
def iisclose(x, y, rtol=1e-05, atol=1e-08):
    dist = np.abs(x - y)
    absy = np.abs(y)
    return dist <= (atol + rtol * absy)


# NOT IN ARRAY API
@fbindings.aadc_array_function_bind("allclose")
def iallclose(x, y, rtol=1e-05, atol=1e-08):
    return iall(iisclose(x, y, rtol, atol))


@fbindings.aadc_array_function_bind("where")
def iwhere(condition, iftrue, iffalse):
    if not utils.one_or_more_items_active(condition):
        condition, iftrue, iffalse = utils.unpack((condition, iftrue, iffalse))
        return np.where(condition, iftrue, iffalse)

    if not any(isinstance(x, (aadc.ndarray.AADCArray, np.ndarray)) for x in (condition, iftrue, iffalse)):
        return iif(condition, iftrue, iffalse)

    condition, iftrue, iffalse = utils.unpack((condition, iftrue, iffalse))

    if isinstance(condition, np.ndarray) and isinstance(condition.item(0), ibool):
        return np.vectorize(iif)(condition, iftrue, iffalse)
    elif isinstance(condition, ibool):
        return np.vectorize(iif)(condition, iftrue, iffalse)
    else:
        return np.vectorize(lambda sel, x, y: x if sel else y)(condition, iftrue, iffalse)


iand_ufunc = np.frompyfunc(iand, 2, 1, identity=True)


@fbindings.aadc_array_function_bind("all")
def iall(a, axis=None, out=None, keepdims=False, where=True):
    return iand_ufunc.reduce(utils.unpack(a), axis=axis, out=out, keepdims=keepdims, where=where, initial=True)


ior_ufunc = np.frompyfunc(ior, 2, 1, identity=False)


@fbindings.aadc_array_function_bind("any")
def iany(a, axis=None, out=None, keepdims=False, where=True):
    return ior_ufunc.reduce(utils.unpack(a), axis=axis, out=out, keepdims=keepdims, where=where, initial=False)


# NOT IN ARRAY API
@fbindings.aadc_array_function_bind("interp")
def interpolate_1d(x0, x, y, left=None, right=None, period=None):
    if period is not None:
        raise ValueError("Period argument not supported for active args")

    if not isinstance(x, aadc.ndarray.AADCArray):
        x = aadc.array(x)

    indices = np.searchsorted(x, x0)

    extrapolate_left_sel = indices == 0
    extrapolate_right_sel = indices == len(x)

    indices_left = np.maximum(indices - 1, 0)
    indices_right = np.minimum(indices, len(x) - 1)

    x_left = x[indices_left]
    x_right = x[indices_right]
    y_left = y[indices_left]
    y_right = y[indices_right]

    slope = (y_right - y_left) / (x_right - x_left)
    interpolated_values = y_left + slope * (x0 - x_left)

    output = np.where(extrapolate_left_sel, y[0] if left is None else left, interpolated_values)
    output = np.where(extrapolate_right_sel, y[-1] if right is None else right, output)

    return output


@fbindings.aadc_array_function_bind("clip")
def clip(a, a_min, a_max, out=None, **kwargs):
    return np.minimum(a_max, np.maximum(a, a_min, **kwargs), out=out, **kwargs)


@fbindings.aadc_array_function_bind("ptp")
def ptp(a, axis=None, out=None, keepdims=np._NoValue):
    maxa = a.max(axis=axis, keepdims=keepdims)
    mina = a.min(axis=axis, keepdims=keepdims)
    return np.subtract(maxa, mina, out=out)


@fbindings.aadc_array_function_bind("searchsorted")
def searchsorted(a, v, side="left", sorter=None):
    if side != "left":
        raise ValueError("Side other than 'left' is unsupported.")

    if sorter is not None:
        raise ValueError("Sorter argument is unsupported.")

    if isinstance(v, (np.ndarray, aadc.ndarray.AADCArray)):
        return aadc.array(aadc.lower_bound(a, v))
    else:
        return aadc.lower_bound(a, v)



@fbindings.aadc_array_function_bind("cholesky")
def cholesky(a, /, *, upper=False):
    if a.ndim == 2:
        return _cholesky_single_matrix(a, upper=upper)
    else:
        return np.vectorize(lambda x: _cholesky_single_matrix(x, upper=upper), signature="(n,n)->(n,n)")(a.get_buffer())


def _cholesky_single_matrix(a, /, *, upper=False):
    if a.shape[0] != a.shape[1]:
        raise ValueError("Input array must be a square matrix.")

    sqrt_a = aadc.array(np.zeros_like(a))
    n = a.shape[0]

    for i in range(n):
        for j in range(i + 1):
            s = sum(sqrt_a[i, k] * sqrt_a[j, k] for k in range(j))

            if i == j:
                sqrt_a[i, j] = np.sqrt(a[i, i] - s)
            else:
                sqrt_a[i, j] = 1.0 / sqrt_a[j, j] * (a[i, j] - s)

    if upper:
        return sqrt_a.T
    else:
        return sqrt_a
