import functools

import numpy as np

import aadc.ndarray as array
import aadc.numpy_compat.function_bindings as fbindings
import aadc.numpy_compat.ufuncs as ufuncs
import aadc.overrides_free
import aadc.utils
from aadc import ibool, idouble, iint


def replace_self_with_passive(self, data):
    if data is self:
        return data.val()
    elif isinstance(data, list):
        return [replace_self_with_passive(self, item) for item in data]
    elif isinstance(data, tuple):
        return tuple(replace_self_with_passive(self, item) for item in data)
    elif isinstance(data, dict):
        return {key: replace_self_with_passive(self, value) for key, value in data.items()}
    else:
        return data


def array_ufunc(self, ufunc, method, *inputs, out=None, **kwargs):
    # logging.debug("__array_ufunc__ called with:")
    # logging.debug(f"ufunc: {ufunc}")
    # logging.debug(f"method: {method}")
    # logging.debug(f"inputs: {inputs}")
    # logging.debug(f"out: {out}")

    if not self.is_active():
        method_to_call = getattr(ufunc, method)
        return method_to_call(*replace_self_with_passive(self, inputs), out=out, **kwargs)
    elif len(inputs) == 1:
        if ufunc.__name__ in ufuncs.UNARY_AADC_FUNCS:
            return ufuncs.UNARY_AADC_FUNCS[ufunc.__name__](inputs[0])
        else:
            return NotImplemented
    elif any(
        isinstance(input, np.ndarray) for input in inputs
    ):  # Numpy array operands - convert to AADC Array and re-call ufunc
        transformed_inputs = tuple(
            array.AADCArray(input) if isinstance(input, np.ndarray) else input for input in inputs
        )
        transformed_outputs = (
            tuple(array.AADCArray(output) if isinstance(output, np.ndarray) else output for output in out)
            if out is not None
            else None
        )
        method_to_call = getattr(ufunc, method)
        return method_to_call(*transformed_inputs, out=transformed_outputs, **kwargs)
    elif any(
        isinstance(input, array.AADCArray) for input in inputs
    ):  # All numpy arrays converted to AADC Arrays - delegate to their implementation
        return NotImplemented
    else:  # Must be scalar only operands
        if ufunc.__name__ in ufuncs.ARRAY_UFUNCS:
            ufunc = ufuncs.ARRAY_UFUNCS[ufunc.__name__]

        transformed_outputs = (
            tuple(array.AADCArray(output) if isinstance(output, np.ndarray) else output for output in out)
            if out is not None
            else None
        )
        method_to_call = getattr(ufunc, method)
        return method_to_call(*aadc.utils.unpack(inputs), out=transformed_outputs, **kwargs)


def array_function(self, func, types, args, kwargs):
    if not self.is_active():
        # Called on inactive idouble, replace idouble with its value
        args = replace_self_with_passive(self, args)
    return fbindings.array_function_dispatch(func, types, args, kwargs)


idouble.__array_ufunc__ = array_ufunc
idouble.__array_function__ = array_function
iint.__array_ufunc__ = array_ufunc
iint.__array_function__ = array_function
ibool.__array_ufunc__ = array_ufunc
ibool.__array_function__ = array_function
# TODO could also pre-init empty wrapper per object and then do wrapper_a[()] = x; return wrapper_a. Not thread-safe.
idouble._buffer = property(lambda self: aadc.overrides_free.np_array(self))
ibool._buffer = property(lambda self: aadc.overrides_free.np_array(self))
iint._buffer = property(lambda self: aadc.overrides_free.np_array(self))


def binary_op_delegate_to_array_rop(func):
    @functools.wraps(func)
    def new_func(self, other):
        if isinstance(other, (np.ndarray, aadc.ndarray.AADCArray)):
            return NotImplemented  # Delegate to __rmul__ of other.
        else:
            return func(self, other)

    return new_func


idouble.__mul__ = binary_op_delegate_to_array_rop(idouble.__mul__)
idouble.__add__ = binary_op_delegate_to_array_rop(idouble.__add__)
idouble.__sub__ = binary_op_delegate_to_array_rop(idouble.__sub__)
idouble.__truediv__ = binary_op_delegate_to_array_rop(idouble.__truediv__)
idouble.__pow__ = binary_op_delegate_to_array_rop(idouble.__pow__)

iint.__mul__ = binary_op_delegate_to_array_rop(iint.__mul__)
iint.__add__ = binary_op_delegate_to_array_rop(iint.__add__)
iint.__sub__ = binary_op_delegate_to_array_rop(iint.__sub__)
