import numpy as np
import numpy.typing as npt

import aadc._aadc_core
from aadc._aadc_core import *
import aadc.ndarray
import aadc.numpy_compat.scalar_numpy_compat
import aadc.numpy_compat.statistical_functions
import aadc.numpy_compat.mainpulation_functions
import aadc.numpy_compat.other_functions
from aadc.record_function import record
from aadc.recording_ctx import record_kernel
from typing import Any, Iterator, TYPE_CHECKING


if TYPE_CHECKING:
    def array(input: Any, copy: bool=False) -> aadc.ndarray.AADCArray: ...
    def fromiter(iterator: Iterator[Any], dtype: npt.DTypeLike) -> aadc.ndarray.AADCArray: ...
else:
    def array(input, copy=False):
        """
        Convert the input to an AADCArray object.

        Parameters:
        -----------
        * `input : array-like`
            Input data that can be converted to an AADCArray.
        * `copy : bool, optional`
            If `True`, always copy the input data.
            If `False` (default), copy only if necessary.

        Returns:
        --------
        * `out : aadc.ndarray.AADCArray`
            The input data converted to an AADCArray object.

        Notes:
        ------
        - If input is a numpy array, the buffer is not copied unless copy is set to True.

        Examples:
        ---------
        >>> import aadc
        >>> import numpy as np
        >>> a = aadc.array([1, 2, 3])
        >>> b = aadc.array(np.array([4, 5, 6]))
        >>> c = aadc.array(np.zeros((3, 2)))
        """
        return aadc.ndarray.AADCArray(input, copy)


    def fromiter(iterator, dtype):
        """
        Create a new AADCArray from an iterable object.

        Parameters:
        -----------
        * `iterator : Iterable`
            An object that can be iterated over to produce the array elements.
        * `dtype : data-type`
            The data type of the resulting array.

        Returns:
        --------
        * `out : aadc.ndarray.AADCArray`
            A new AADCArray object created from the input iterator.

        Notes:
        ------
        - This function first creates a NumPy array using `np.fromiter` and then
        converts it to an AADCArray.

        Examples:
        ---------
        >>> import aadc
        >>> it = range(5)
        >>> arr = aadc.fromiter(it, dtype=float)
        >>> print(arr)
        aadc.array([0., 1., 2., 3., 4.])
        """
        return array(np.fromiter(iterator, dtype))

