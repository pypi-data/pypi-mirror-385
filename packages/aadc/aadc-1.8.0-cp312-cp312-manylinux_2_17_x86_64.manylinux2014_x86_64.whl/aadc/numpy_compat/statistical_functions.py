import numpy as np

import aadc
import aadc.ndarray
import aadc.numpy_compat.function_bindings as fbindings
import aadc.numpy_compat.ufuncs as ufuncs
import aadc.utils as utils

# >>>>>>> IN ARRAY API

cumulative_sum = fbindings.bind_single_argument_function_with_unpack(
    np.cumsum, "cumsum"
)  # ARRAY API NAME: cumulative_sum
mean = fbindings.bind_single_argument_function_with_unpack(np.mean, "mean")
prod = fbindings.bind_single_argument_function_with_unpack(np.prod, "prod")
std = fbindings.bind_single_argument_function_with_unpack(np.std, "std")
sum = fbindings.bind_single_argument_function_with_unpack(np.sum, "sum")
var = fbindings.bind_single_argument_function_with_unpack(np.var, "var")


@fbindings.aadc_array_function_bind("max", "amax")
def max(a, axis=None, out=None, keepdims=np._NoValue, initial=np._NoValue, where=np._NoValue):
    return _wrapreduction(
        utils.unpack(a),
        ufuncs.ARRAY_UFUNCS["maximum"],
        axis,
        None,
        out,
        keepdims=keepdims,
        initial=initial,
        where=where,
    )


@fbindings.aadc_array_function_bind("min", "amin")
def min(a, axis=None, out=None, keepdims=np._NoValue, initial=np._NoValue, where=np._NoValue):
    return _wrapreduction(
        utils.unpack(a),
        ufuncs.ARRAY_UFUNCS["minimum"],
        axis,
        None,
        out,
        keepdims=keepdims,
        initial=initial,
        where=where,
    )


# <<<<<<< IN ARRAY API


# >>>>>>> NOT IN ARRAY API

diff = fbindings.bind_single_argument_function_with_unpack(np.diff, "diff")


# This function is copied from numpy and adapted to our needs
@fbindings.aadc_array_function_bind("average")
def average(a, axis=None, weights=None, returned=False, *, keepdims=np._NoValue):
    if keepdims is np._NoValue:
        # Don't pass on the keepdims argument if one wasn't given.
        keepdims_kw = {}
    else:
        keepdims_kw = {"keepdims": keepdims}

    if weights is None:
        avg = a.mean(axis, **keepdims_kw)
        scl = a.size / (avg.size if isinstance(avg, aadc.ndarray.AADCArray) else 1)
    else:
        # Sanity checks
        if a.shape != weights.shape:
            if axis is None:
                raise TypeError("Axis must be specified when shapes of a and weights " "differ.")
            if weights.ndim != 1:
                raise TypeError("1D weights expected when shapes of a and weights differ.")
            if weights.shape[0] != a.shape[axis]:
                raise ValueError("Length of weights not compatible with specified axis.")

            # setup weights to broadcast along axis
            weights = np.broadcast_to(weights, (a.ndim - 1) * (1,) + weights.shape)
            weights = weights.swapaxes(-1, axis)

        scl = weights.sum(axis=axis, **keepdims_kw)
        zero_scale_present = np.any(scl == 0.0)

        if zero_scale_present.val() if isinstance(zero_scale_present, aadc.ibool) else zero_scale_present:
            raise ZeroDivisionError("Weights sum to zero, can't be normalized")

        avg = np.multiply(a, weights).sum(axis, **keepdims_kw) / scl

    if returned:
        if isinstance(avg, (np.ndarray, aadc.ndarray.AADCArray)):
            avgshape = avg.shape
        else:
            avgshape = tuple()

        if isinstance(scl, (np.ndarray, aadc.ndarray.AADCArray)):
            sclshape = scl.shape
        else:
            sclshape = tuple()

        if sclshape != avgshape:
            scl = np.broadcast_to(scl, avg.shape).copy()
        return avg, scl
    else:
        return avg


# This function is copied from numpy and adapted to our needs
@fbindings.aadc_array_function_bind("cov")
def cov(m, y=None, rowvar=True, bias=False, ddof=None, fweights=None, aweights=None, *, dtype=None):
    # Check inputs
    if ddof is not None and ddof != int(ddof):
        raise ValueError("ddof must be integer")

    # Handles complex arrays too
    if m.ndim > 2:
        raise ValueError("m has more than 2 dimensions")

    if y is not None:
        if y.ndim > 2:
            raise ValueError("y has more than 2 dimensions")

    if dtype is None:
        if y is None:
            dtype = np.result_type(m, np.float64)
        else:
            dtype = np.result_type(m, y, np.float64)

    x = np.atleast_2d(m)
    if not rowvar and x.shape[0] != 1:
        x = x.T
    if x.shape[0] == 0:
        return aadc.ndarray.AADCArray([]).reshape(0, 0)
    if y is not None:
        y = np.atleast_2d(y)
        if not rowvar and y.shape[0] != 1:
            y = y.T
        x = np.concatenate((x, y), axis=0)

    if ddof is None:
        if bias == 0:
            ddof = 1
        else:
            ddof = 0

    # Get the product of frequencies and weights
    w = None
    if fweights is not None:
        fweights = np.asarray(fweights, dtype=float)
        if not np.all(fweights == np.around(fweights)):
            raise TypeError("fweights must be integer")
        if fweights.ndim > 1:
            raise RuntimeError("cannot handle multidimensional fweights")
        if fweights.shape[0] != x.shape[1]:
            raise RuntimeError("incompatible numbers of samples and fweights")
        if any(fweights < 0):
            raise ValueError("fweights cannot be negative")
        w = fweights
    if aweights is not None:
        aweights = np.asarray(aweights, dtype=float)
        if aweights.ndim > 1:
            raise RuntimeError("cannot handle multidimensional aweights")
        if aweights.shape[0] != x.shape[1]:
            raise RuntimeError("incompatible numbers of samples and aweights")
        if any(aweights < 0):
            raise ValueError("aweights cannot be negative")
        if w is None:
            w = aweights
        else:
            w *= aweights

    avg, w_sum = average(x, axis=1, weights=w, returned=True)
    w_sum = w_sum[0]

    # Determine the normalization
    if w is None:
        fact = x.shape[1] - ddof
    elif ddof == 0:
        fact = w_sum
    elif aweights is None:
        fact = w_sum - ddof
    else:
        fact = w_sum - ddof * sum(w * aweights) / w_sum

    fact = np.maximum(fact, 0.0)

    x -= avg[:, None]
    if w is None:
        x_t = x.T
    else:
        x_t = (x * w).T
    c = np.dot(x, x_t.conj())
    c *= np.true_divide(1, fact)
    return c.squeeze()


# <<<<<<< NOT IN ARRAY API


def _wrapreduction(obj, ufunc, axis, dtype, out, **kwargs):
    """
    Copy of a similar function from numpy to delegate stuff to ufuncs
    """
    passkwargs = {k: v for k, v in kwargs.items() if v is not np._NoValue}
    return ufunc.reduce(obj, axis, dtype, out, **passkwargs)
