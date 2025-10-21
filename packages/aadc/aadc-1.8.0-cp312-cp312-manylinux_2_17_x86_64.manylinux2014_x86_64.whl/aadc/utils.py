from typing import Any

import numpy as np

import aadc.ndarray


def unpack(data: Any, arrays_only: bool = False) -> Any:
    if type(data) in (aadc.ndarray.ACTIVE_TYPES if not arrays_only else (aadc.ndarray.AADCArray,)):
        return data._buffer
    elif not isinstance(data, (tuple, list, dict)):
        return data
    elif isinstance(data, tuple):
        return tuple(unpack(item, arrays_only) for item in data)
    elif isinstance(data, list):
        return [unpack(item, arrays_only) for item in data]
    else:  # Must be dict
        return {key: unpack(value, arrays_only) for key, value in data.items()}


def one_or_more_items_active(data: Any) -> bool:
    if type(data) in aadc.ndarray.ACTIVE_TYPES:
        return data.is_active()
    elif isinstance(data, (list, tuple)):
        return any(one_or_more_items_active(item) for item in data)
    elif isinstance(data, np.ndarray) and (data.dtype == "O"):
        if data.ndim == 0:
            return one_or_more_items_active(data.item())
        else:
            return any(one_or_more_items_active(item) for item in data.flat)
    elif isinstance(data, dict):
        return any(one_or_more_items_active(value) for value in data.values())
    else:
        return False
