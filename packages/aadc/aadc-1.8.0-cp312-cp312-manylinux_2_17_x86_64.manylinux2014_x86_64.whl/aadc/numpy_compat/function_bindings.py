from functools import wraps
from typing import Callable

import numpy as np

import aadc.ndarray as array
import aadc.utils as utils

AADC_ARRAY_FUNCTION_BINDINGS = {}


def aadc_array_function_bind(*override_function_names: str) -> Callable:
    def decorator(func):
        for name in override_function_names:
            AADC_ARRAY_FUNCTION_BINDINGS[name] = {"func": func}
        return func

    return decorator


def bind_single_argument_function_with_unpack(
    function: Callable, override_function_name: str, wrap_output: bool = False
) -> Callable:
    if wrap_output:

        @aadc_array_function_bind(override_function_name)
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            res = function(*utils.unpack(args), **kwargs)
            if isinstance(res, np.ndarray):
                return array.AADCArray(res)
            else:
                return res
    else:

        @aadc_array_function_bind(override_function_name)
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            return function(*utils.unpack(args), **kwargs)

    return wrapped_function


def check_and_wrap_result(result):
    if isinstance(result, list):
        return [check_and_wrap_result(item) for item in result]
    elif isinstance(result, tuple):
        return tuple(check_and_wrap_result(item) for item in result)
    elif isinstance(result, dict):
        return {key: check_and_wrap_result(value) for key, value in result.items()}
    elif isinstance(result, np.ndarray):
        return array.AADCArray(result)
    elif result is NotImplemented:
        raise ValueError("__array_function__ returned NotImplemented")
    else:
        return result


def array_function_dispatch(func, types, args, kwargs):
    if utils.one_or_more_items_active(args):
        if func.__name__ in AADC_ARRAY_FUNCTION_BINDINGS:
            results = AADC_ARRAY_FUNCTION_BINDINGS[func.__name__]["func"](*args, **kwargs)
        else:
            try:
                results = func(*utils.unpack(args), **utils.unpack(kwargs))
            except Exception as e:
                raise ValueError(f"Numpy function np.{func.__name__} seems to be unsupported for active types.") from e
    else:
        results = func(*utils.unpack(args), **utils.unpack(kwargs))

    return check_and_wrap_result(results)
