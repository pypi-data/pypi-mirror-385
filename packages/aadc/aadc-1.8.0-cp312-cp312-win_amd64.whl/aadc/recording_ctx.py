import contextlib
from typing import Iterator

import aadc
from aadc._aadc_core import Functions


@contextlib.contextmanager
def record_kernel() -> Iterator[Functions]:
    """
    A context manager for recording AADC kernel operations.

    This context manager creates an AADC Functions object (kernel) and manages
    its recording state. It starts recording when entered and stops recording
    when exited, ensuring proper cleanup.

    Yields:
    -------
    * `aadc.Functions`
        An AADC kernel object for recording operations.

    Examples:
    ---------
    >>> import numpy as np
    >>> import aadc
    >>> from aadc.evaluate_wrappers import evaluate_kernel
    >>> with record_kernel() as kernel:
    ...     x = aadc.idouble(1.0)
    ...     y = aadc.idouble(2.0)
    ...     z = aadc.idouble(3.0)
    ...     xin = x.mark_as_input()
    ...     f = np.exp(x / y + z) + x
    ...     fout = f.mark_as_output()
    >>> inputs = {xin: 1.0}
    >>> request = {fout: [xin]}
    >>> result = evaluate_kernel(kernel, request, inputs, 1)

    Notes:
    ------
    - The context ensures that recording is properly started and stopped, even under exceptions.
    """
    kernel = aadc.Functions()
    kernel.start_recording()

    try:
        yield kernel
    finally:
        kernel.stop_recording()
