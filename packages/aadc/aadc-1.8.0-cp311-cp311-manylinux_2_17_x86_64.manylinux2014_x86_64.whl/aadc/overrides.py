"""
This module provides overrides and utility functions for integrating AADC with existing code.
It should be used whenever it is not possible or not desired to modify existing code that
uses buried array instantiation routines or instance checks. They help active types pass through
the existing code without raising exceptions or taking unintended branches.

This module relies on monkeypatching so it should be imported as early as possible for it to work
(e.g. before any `from numpy import ...` statements). Importing this module will also hinder performance
since it uses a thread and coroutine-safe mechanism for patching.

The module includes:
1. `aadc_overrides`: context manager that activates the AADC versions of the patched routines for the duration of the context.
2. Overrides for builtin: `int`, `float`, `isinstance` (should get imported at the top of a given module).
"""

import builtins
import contextlib
import contextvars
import functools
from typing import Any, Callable, Iterator, Optional, Type, Union, overload

import numpy as np
import scipy

import aadc
import aadc.ndarray
import aadc.numpy_compat.ufuncs
import aadc.overrides_free
import aadc.utils
from aadc._aadc_core import idouble, iint

OVERRIDE_ACTIVE = {}


def _wrap_in_aadc_array(name: str, impl: Callable) -> Callable:
    if name in OVERRIDE_ACTIVE:
        raise ValueError(f"Override already defined for name {name}")

    OVERRIDE_ACTIVE[name] = contextvars.ContextVar(name, default=False)

    @functools.wraps(impl)
    def wrapper(*args: Any, **kwargs: Any) -> Union[np.ndarray, aadc.ndarray.AADCArray]:
        array = impl(*args, **kwargs)
        if OVERRIDE_ACTIVE[name].get():
            return aadc.ndarray.AADCArray(array)
        else:
            return array

    return wrapper


def _full_like_override() -> Callable:
    name = "np.full_like"
    if name in OVERRIDE_ACTIVE:
        raise ValueError(f"Override already defined for name {name}")

    OVERRIDE_ACTIVE[name] = contextvars.ContextVar(name, default=False)
    old_impl = np.full_like

    @functools.wraps(old_impl)
    def wrapper(
        a: Any, fill_value: Any, dtype: Any = None, order: Any = "K", subok: Any = True, shape: Any = None
    ) -> Any:
        if OVERRIDE_ACTIVE[name].get():
            if aadc.utils.one_or_more_items_active(fill_value):
                return aadc.ndarray.AADCArray(old_impl(a, fill_value, "O", order, subok, shape))
            else:
                return aadc.ndarray.AADCArray(old_impl(a, fill_value, dtype, order, subok, shape))
        else:
            return old_impl(a, fill_value, dtype, order, subok, shape)

    return wrapper


def _scipy_stats_norm_cdf_override() -> Callable:
    name = "scipy.stats.norm.cdf"
    if name in OVERRIDE_ACTIVE:
        raise ValueError(f"Override already defined for name {name}")

    OVERRIDE_ACTIVE[name] = contextvars.ContextVar(name, default=False)
    old_impl = scipy.stats.norm.cdf

    @functools.wraps(old_impl)
    def wrapper(x: Any, *args: Any, **kwargs: Any) -> Any:
        if OVERRIDE_ACTIVE[name].get():
            return scipy.special.ndtr(x)
        else:
            return old_impl(x, *args, **kwargs)

    return wrapper


@contextlib.contextmanager
def aadc_overrides(wanted_overrides: Optional[list[str]] = None) -> Iterator[None]:
    """
    A context manager for temporarily activating AADC overrides. The overrides
    are thread and coroutine-local.

    This context manager allows you to selectively enable AADC overrides
    within a specific code block. When the context is entered, the specified
    overrides are activated and all calls to the overriden functions will be
    redirected to the AADC implementations.

    Supported overrides:
    - `np.ones`
    - `np.zeros`
    - `np.array`
    - `np.empty`
    - `np.asarray`
    - `np.full_like`
    - `scipy.interpolate._interpolate.array`

    Parameters:
    -----------
    * `wanted_overrides : Optional[list[str]]`
        A list of names of the overrides to be activated. If None, all
        available overrides will be activated. The names must come from the
        list of supported overrides.

    Yields:
    -------
    None

    Examples:
    ---------
    >>> with aadc_overrides(['np.array', 'np.zeros']):
    ...     # Code here will use the np.array and np.zeros implementation from AADC.
    ...     pass
    >>> # Overrides are automatically deactivated here

    >>> with aadc_overrides():
    ...     # All available AADC overrides are activated.
    ...     pass

    Notes:
    ------
    - Each override is activated using `ContextVar` system for thread-safety.
    - If an exception occurs within the context, all activated overrides
      will still be properly deactivated.
    """
    tokens = {}

    for name, var in OVERRIDE_ACTIVE.items():
        if (wanted_overrides is not None) and (name not in wanted_overrides):
            continue
        tokens[name] = var.set(True)

    try:
        yield
    finally:
        for name, token in tokens.items():
            OVERRIDE_ACTIVE[name].reset(token)


class float(builtins.float):  # noqa: N801
    """
    A custom `float` class that extends the built-in `float`.

    Entire purpose is to be able to execute `float(aadc.idouble(var))`.
    This allows for seamless integration of `aadc.idouble` objects in
    contexts where `float` is expected.

    This class should be imported at the top of a given module where `float()`
    is called on variables that are supposed to be `aadc.idouble`.

    Examples:
    ---------
    >>> from aadc.overrides import float
    >>> from aadc.recording_ctx import record_kernel
    >>> from aadc import idouble
    >>> with record_kernel():
    ...     var = idouble(1.0)
    ...     var_in = var.mark_as_input()
    ...     float(var) # This would raise an exception without float() override.
    idouble([AAD[rv] [adj] :6,1.00e+00])
    """

    @overload
    def __new__(cls: Type[float], x: idouble) -> idouble: ...  # type: ignore

    @overload
    def __new__(cls: Type[float], x: float) -> float: ...

    def __new__(cls: Type[float], x: Union[idouble, float]) -> Union[idouble, float]:  # type: ignore
        if isinstance(x, aadc.idouble):
            return x
        else:
            return super().__new__(cls, x)


class int(builtins.int):  # noqa: N801
    """
    A custom `int` class that extends the built-in `int`.

    Entire purpose is to be able to execute `int(aadc.idouble(var))`.
    This allows for seamless integration of `aadc.idouble` objects in
    contexts where `int` is expected.

    This class should be imported at the top of a given module where `int()`
    is called on variables that are supposed to be `aadc.idouble`.

    Examples:
    ---------
    >>> from aadc.overrides import int
    >>> from aadc.recording_ctx import record_kernel
    >>> from aadc import iint, idouble
    >>> with record_kernel():
    ...     x0 = idouble(1.5)
    ...     x0_in = x0.mark_as_input()
    ...     x = np.array([1.1, 2.5, 3.0, 3.9])
    ...     idx = np.searchsorted(x, x0)  # idx is iint
    ...     int(idx) # This would raise an exception without int() override.
    iint([AAD[rv] :8,1])
    """

    @overload
    def __new__(cls: Type[int], x: iint) -> iint: ...  # type: ignore

    @overload
    def __new__(cls: Type[int], x: int) -> int: ...

    def __new__(cls: Type[int], x: Union[int, iint]) -> Union[int, iint]:  # type: ignore
        if isinstance(x, aadc.iint):
            return x
        else:
            return super().__new__(cls, x)


def isinstance(obj: Any, typ: Any) -> bool:
    """
    A custom implementation of the built-in `isinstance` function.

    This function extends the behavior of the built-in `isinstance` to handle
    AADC types (`aadc.idouble` and `aadc.iint`) in addition to standard Python types.
    It allows for seamless type checking of AADC objects in contexts where
    `isinstance` is used with `float` or `int` types.

    Parameters:
    -----------
    * `obj : object`
        The object to check.
    * `typ : type or tuple of types`
        The type or tuple of types to check against.

    Returns:
    --------
    * `bool`
        `True` if the object is an instance of the specified type(s), `False` otherwise.

    Examples:
    ---------
    >>> from aadc.overrides import isinstance
    >>> from aadc.recording_ctx import record_kernel
    >>> from aadc import idouble, iint
    >>> x = idouble(1.0)
    >>> isinstance(x, float)
    True
    >>> y = iint(1)
    >>> isinstance(y, int)
    True
    """
    if builtins.isinstance(obj, aadc.idouble) and ((typ == builtins.float) or (typ == float)):
        return True
    elif builtins.isinstance(obj, builtins.float) and ((typ == builtins.float) or (typ == float)):
        return True
    elif builtins.isinstance(obj, aadc.iint) and ((typ == builtins.int) or (typ == int)):
        return True
    elif builtins.isinstance(obj, builtins.int) and ((typ == builtins.int) or (typ == int)):
        return True
    else:
        return builtins.isinstance(obj, typ)


# This module needs to be imported before any "from numpy import ..." occur
# Fortunately these statements are rare in case of numpy.
# NOTE: More thread-safe overrides can be created by user using syntax below
np.ones = _wrap_in_aadc_array("np.ones", np.ones)
np.zeros = _wrap_in_aadc_array("np.zeros", np.zeros)
np.array = _wrap_in_aadc_array("np.array", np.array)
np.empty = _wrap_in_aadc_array("np.empty", np.empty)
np.asarray = _wrap_in_aadc_array("np.asarray", np.asarray)
np.full_like = _full_like_override()

scipy.interpolate._interpolate.array = _wrap_in_aadc_array(
    "scipy.interpolate._interpolate.array", scipy.interpolate._interpolate.array
)
scipy.stats.norm.cdf = _scipy_stats_norm_cdf_override()
