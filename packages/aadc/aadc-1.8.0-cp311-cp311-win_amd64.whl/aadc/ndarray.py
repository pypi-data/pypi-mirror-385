from typing import Any, Callable, Optional, Tuple, Union

# Try to import TypeAlias from typing (Python 3.10+)
# Fall back to typing_extensions (older Python versions)
try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

from numpy import ndarray, ufunc

import aadc._aadc_core

__docformat__ = "numpy"

import numpy as np
import numpy.typing as npt

import aadc
import aadc.numpy_compat.function_bindings as fbindings
import aadc.numpy_compat.other_functions as other_functions
import aadc.numpy_compat.ufuncs as ufuncs
import aadc.overrides_free
import aadc.utils as utils
from aadc import ibool, idouble, iint
from aadc.utils import unpack

AADCScalarTypes: TypeAlias = Union[aadc._aadc_core.idouble, aadc._aadc_core.iint, aadc._aadc_core.ibool]


METHOD_NAME_TO_NP_FUNC: dict[str, Callable] = {
    "all": np.all,
    "any": np.any,
    "argmax": np.argmax,
    "argmin": np.argmin,
    "clip": np.clip,
    "conj": np.conj,
    "conjugate": np.conjugate,
    "max": np.max,
    "mean": np.mean,
    "min": np.min,
    "prod": np.prod,
    "ptp": np.ptp,
    "round": np.round,
    "std": np.std,
    "sum": np.sum,
    "trace": np.trace,
    "var": np.var,
    "argsort": np.argsort,
    "choose": np.choose,
    "compress": np.compress,
    "copy": np.copy,
    "cumprod": np.cumprod,
    "cumsum": np.cumsum,
    "diagonal": np.diagonal,
    "nonzero": np.nonzero,
    "partition": np.partition,
    "put": np.put,
    "ravel": np.ravel,
    "repeat": np.repeat,
    "reshape": np.reshape,
    "resize": np.resize,
    "searchsorted": np.searchsorted,
    "sort": np.sort,
    "squeeze": np.squeeze,
    "swapaxes": np.swapaxes,
    "take": np.take,
    "transpose": np.transpose,
}

METHOD_FORWARD_TO_BUFFER_RETURN_AADC_ARRAY = {"astype", "flatten", "view"}
METHOD_FORWARD_TO_BUFFER_RETURN_DIRECTLY = {"tolist", "item", "tostring"}
VOID_METHOD_FORWARD_TO_BUFFER = {"setflags"}


def tup_of_arrays_as_obj(data: Tuple[ndarray, ...]) -> Tuple[ndarray, ...]:
    return tuple(item.astype("O") for item in data) if data is not None else data


class AADCArray(np.lib.mixins.NDArrayOperatorsMixin):
    """
    A NumPy-compatible array class with additional automatic differentiation capabilities.

    AADCArray can be used as a drop-in replacement for numpy.ndarray in most scenarios,
    providing seamless integration with existing NumPy-based code. It supports standard
    array operations, indexing, and NumPy universal functions (ufuncs).
    It also exposes an interface nearly identical to the standard NumPy array class.

    In addition to standard array functionality, AADCArray offers methods to manage recording:

    - mark_as_input(): Marks array elements as inputs for gradient computation.
    - mark_as_input_no_diff(): Marks array elements as inputs without gradient computation.
    - mark_as_output(): Marks array elements as outputs for the recording.
    - is_active(): Checks if the array is in active (recording) mode.
    - to_inactive(): Converts an active array to an inactive one.


    Examples:
    ---------
    >>> import aadc
    >>> from aadc.recording_ctx import record_kernel
    >>> with record_kernel() as kernel:
    ...     a = aadc.array([1., 2., 3.])
    ...     a_in = a.mark_as_input()
    ...     b = a * 2
    ...     b_out = b.mark_as_output()


    See also:
    ---------
    * `numpy.ndarray` : The standard NumPy array class.
    * `aadc.recording_ctx.record_kernel` : The recording context manager.
    """

    __slots__ = "_buffer"

    def __init__(self, input_buffer: Any, copy: bool = False) -> None:
        if not isinstance(input_buffer, np.ndarray):
            if not copy:
                input_buffer = aadc.overrides_free.np_asarray(utils.unpack(input_buffer, arrays_only=True))
            else:
                input_buffer = np.array(input_buffer)
        elif copy:
            input_buffer = np.array(input_buffer)

        self._buffer = input_buffer

    # >>>>>>>>>>>>>> ARRAY API START

    @property
    def ndim(self) -> int:
        return self._buffer.ndim

    @property
    def shape(self) -> Tuple[int, ...]:
        return self._buffer.shape

    @property
    def size(self) -> int:
        return self._buffer.size

    @property
    def T(self) -> "AADCArray":  # noqa: N802
        return AADCArray(self._buffer.T)

    @property
    def dtype(self) -> npt.DTypeLike:
        return np.float64  # TODO: shall we return something else for iints / ibools?

    # ARRAY API END <<<<<<<<<<<<<<<<

    # >>>>>>>>>>>>>> NUMPY ARRAY METHODS START

    def __array__(self, dtype: npt.DTypeLike = None, copy: Optional[bool] = None) -> ndarray:
        if self.is_active():
            if aadc.is_recording():
                raise ValueError("Cannot convert an active AADCArray to a numpy array")
            else:
                return self._convert_numpy_to_inactive(self._buffer, dtype)

        return self._buffer.copy() if copy else self._buffer

    def __iter__(self) -> Any:
        return iter(self._buffer)

    def __getattr__(self, name: str) -> Any:
        if name in METHOD_NAME_TO_NP_FUNC:

            def func(*args: Any, **kwargs: Any) -> Any:
                return METHOD_NAME_TO_NP_FUNC[name](self, *args, **kwargs)

            return func
        elif name in METHOD_FORWARD_TO_BUFFER_RETURN_AADC_ARRAY:

            def func(*args: Any, **kwargs: Any) -> Any:
                buffer_func = getattr(self._buffer, name)
                buffer_op_output = buffer_func(*args, **kwargs)
                return AADCArray(buffer_op_output)

            return func
        elif name in METHOD_FORWARD_TO_BUFFER_RETURN_DIRECTLY:

            def func(*args: Any, **kwargs: Any) -> Any:
                buffer_func = getattr(self._buffer, name)
                return buffer_func(*args, **kwargs)

            return func
        elif name in VOID_METHOD_FORWARD_TO_BUFFER:

            def func(*args: Any, **kwargs: Any) -> Any:
                buffer_func = getattr(self._buffer, name)
                buffer_func(*args, **kwargs)

            return func
        else:
            object.__getattribute__(self, name)

    def fill(self, item: aadc._aadc_core.idouble) -> None:
        if utils.one_or_more_items_active(item) and not self.is_active():
            self._buffer = self._buffer.astype("O")
        self._buffer.fill(item)

    def itemset(self, *items: Any) -> None:
        if utils.one_or_more_items_active(items) and not self.is_active():
            self._buffer = self._buffer.astype("O")
        self._buffer.itemset(*items)

    # NUMPY ARRAY METHODS END <<<<<<<<<<<<<<<<

    def get_buffer(self) -> ndarray:
        """
        Returns the underlying AADCArray buffer in a form of a numpy array.
        This is useful when you want to work with underlying buffer directly,
        e.g. to feed it to np.vectorize function.
        Usual "np.asarray" won't work on an active array to protect the user from
        uninteded casting - this method should be used instead.

        Returns:
        --------
        * `out : np.ndarray`
            A numpy array representing underlying AADCArray buffer
        """
        return self._buffer

    def is_active(self) -> bool:
        return self._buffer.dtype == "O"

    def to_inactive(self) -> None:
        """
        Converts an active array to an inactive array.
        This will speed up any computation that uses this array as no recording will be performed.
        This method will raise a ValueError if recording is active.

        Returns:
        --------
        * `out : AADCArray`
            An AADCArray with an inactive buffer.

        Notes:
        ------
        - Underlying AADCArray buffer is copied whenever this method is called.

        See also:
        ---------
        * `AADCArray.mark_as_input` : Marks the elements of the array as recording inputs that do require gradients.
        * `AADCArray.mark_as_input_no_diff` : Marks the elements of the array as recording inputs that do not require gradients.
        * `AADCArray.mark_as_output` : Marks the elements of the array as outputs of the recording.
        """
        self._buffer = self._convert_numpy_to_inactive(self._buffer)

    def astype(self, dtype: npt.DTypeLike, copy: None = None) -> "AADCArray":
        return self  # TODO this should be migrated when array wrapper is introduced

    def __getitem__(self, key: Any) -> Union[AADCScalarTypes, "AADCArray", np.generic]:
        if utils.one_or_more_items_active(key):
            if self.ndim != 1:
                raise ValueError("Active indexing is currently only supported for 1-dimensional arrays")

            if isinstance(key, AADCArray):
                return aadc.fromiter((aadc.get(self, key_el) for key_el in key), "O")
            elif isinstance(key, iint):
                return aadc.get(self, key)
            else:
                raise ValueError(f"Unsupported type for active indexing. Expected: iint, AADCArray. Got: {type(key)}")

        else:
            return self._coerce_bufferop_output(self._buffer[key])

    def __setitem__(self, key: Any, newvalue: Union[AADCScalarTypes, "AADCArray", np.generic, np.ndarray]) -> None:
        if utils.one_or_more_items_active(newvalue) and not self.is_active():
            self._buffer = self._buffer.astype("O")

        if isinstance(newvalue, AADCArray):
            newvalue = newvalue._buffer

        if utils.one_or_more_items_active(key):
            self._buffer = other_functions.iwhere(key, newvalue, self._buffer)
            return

        self._buffer[key] = newvalue

    def __len__(self) -> int:
        return len(self._buffer)

    def __repr__(self) -> str:
        return "aadc." + self._buffer.__repr__()

    def _coerce_bufferop_output(self, output: Any) -> Union[AADCScalarTypes, "AADCArray", np.generic]:
        if output is NotImplemented:
            raise ValueError("Buffer operation returned NotImplemented")

        if isinstance(output, np.ndarray):
            return AADCArray(output)
        else:
            return output

    def __array_ufunc__(
        self, ufunc: ufunc, method: str, *inputs: tuple[Any, ...], out: Optional[Any] = None, **kwargs: dict[str, Any]
    ) -> Union[AADCScalarTypes, "AADCArray", np.generic]:
        # logging.debug("__array_ufunc__ called with:")
        # logging.debug(f"ufunc: {ufunc}")
        # logging.debug(f"method: {method}")
        # logging.debug(f"inputs: {inputs}")
        # logging.debug(f"out: {out}")

        if out is None:
            if len(inputs) == 2:  # Most common case
                active = utils.one_or_more_items_active(inputs[0]) or utils.one_or_more_items_active(inputs[1])
            elif len(inputs) == 1:  # 2nd most common
                active = utils.one_or_more_items_active(inputs[0])
            else:  # Generic implementation
                active = utils.one_or_more_items_active(inputs)
        else:
            active = utils.one_or_more_items_active(inputs + out)

        if active:
            if ufunc.__name__ in ufuncs.ARRAY_UFUNCS:
                ufunc = ufuncs.ARRAY_UFUNCS[ufunc.__name__]
            else:
                return NotImplemented

            method_to_call = getattr(ufunc, method)

            if out is not None:
                out = tup_of_arrays_as_obj(utils.unpack(out))
        else:
            # Dispatch from NumPy
            method_to_call = getattr(ufunc, method)

            if out is not None:
                out = utils.unpack(out)

        if len(inputs) == 2:  # Most common case
            i0 = unpack(inputs[0])
            i1 = unpack(inputs[1])
            results = method_to_call(i0, i1, out=out, **kwargs)
        elif len(inputs) == 1:  # 2nd most common
            i0 = unpack(inputs[0])
            results = method_to_call(i0, out=out, **kwargs)
        elif len(inputs) == 3:  # 3rd most common
            i0 = unpack(inputs[0])
            i1 = unpack(inputs[1])
            i2 = unpack(inputs[2])
            results = method_to_call(i0, i1, i2, out=out, **kwargs)
        else:
            results = method_to_call(*utils.unpack(inputs), out=out, **kwargs)

        return self._coerce_bufferop_output(results)

    def __array_function__(
        self, func: Callable, types: Any, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> "AADCArray":
        return fbindings.array_function_dispatch(func, types, args, kwargs)

    def mark_as_input(self) -> ndarray:
        """
        Mark the array as input to the recording, with respect to which gradients should be computed.
        Returns a numpy array of aadc.Argument objects, of the same shape as itself.

        Returns:
        --------
        * `out : numpy.ndarray`
            An ndarray of `aadc.Argument` object, of the same shape as the AADCArray.

        Notes:
        ------
        - Underlying AADCArray buffer is copied whenever this method is called.

        See also:
        ---------
        * `aadc.Argument` : Object representing a single scalar input to the recording.
        * `AADCArray.mark_as_input_no_diff` : Marks the elements of the array as recording inputs that do not require gradients.
        * `AADCArray.mark_as_output` : Marks the elements of the array as outputs of the recording.
        """
        if self.size == 0:
            return np.array([], dtype=object)

        self._buffer = self._convert_numpy_to_active(self._buffer)
        return np.vectorize(lambda x: x.mark_as_input())(self._buffer)

    def mark_as_input_no_diff(self) -> ndarray:
        """
        Mark the array as input to the recording, which does not require gradients to be calcuated.
        Returns a numpy array of aadc.Argument objects, of the same shape as itself.

        Returns:
        --------
        * `out : numpy.ndarray`
            An ndarray of `aadc.Argument` object, of the same shape as the AADCArray.

        Notes:
        ------
        - Underlying AADCArray buffer is copied whenever this method is called.

        See also:
        ---------
        * `aadc.Argument` : Object representing a single scalar input to the recording.
        * `AADCArray.mark_as_input` : Marks the elements of the array as recording inputs that do require gradients.
        * `AADCArray.mark_as_output` : Marks the elements of the array as outputs of the recording.
        """
        self._buffer = self._convert_numpy_to_active(self._buffer)
        return np.vectorize(lambda x: x.mark_as_input_no_diff())(self._buffer)

    def mark_as_output(self) -> ndarray:
        """
        Mark the array as output of the recording.
        Returns a numpy array of aadc.Result objects, of the same shape as itself.

        Returns:
        --------
        * `out : numpy.ndarray`
            An ndarray of aadc.Argument object, of the same shape as the AADCArray.

        See also:
        ---------
        * `aadc.Result` : Object representing a single scalar output of the recording.
        * `AADCArray.mark_as_input_no_diff` : Marks the elements of the array as recording inputs that do not require gradients.
        * `AADCArray.mark_as_input` : Marks the elements of the array as recording inputs that do require gradients.
        """
        return np.vectorize(lambda x: x.mark_as_output())(self._buffer)

    @classmethod
    def _convert_numpy_to_active(cls, array: ndarray) -> ndarray:
        if array.dtype in (np.double, np.float32):
            return np.vectorize(idouble)(array)
        elif array.dtype == np.int_:
            return np.vectorize(iint)(array)
        elif array.dtype == np.bool_:
            return np.vectorize(ibool)(array)

        return array

    @classmethod
    def _convert_numpy_to_inactive(cls, array: ndarray, dtype: Optional[npt.DTypeLike] = None) -> ndarray:
        sample_el = array.item(0)

        if dtype is None:
            if isinstance(sample_el, idouble):
                return aadc.overrides_free.np_asarray(array, dtype=np.double)
            elif isinstance(sample_el, iint):
                return aadc.overrides_free.np_asarray(array, dtype=np.int_)
            else:  # isinstance(sample_el, ibool):
                return aadc.overrides_free.np_asarray(array, dtype=np.bool_)
        else:
            return aadc.overrides_free.np_asarray(array, dtype=dtype)


ACTIVE_TYPES = (AADCArray, idouble, iint, ibool)
