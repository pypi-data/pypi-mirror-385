from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple, Union

import numpy as np
import numpy.typing as npt

from aadc._aadc_core import Argument, Functions, Result, ThreadPool, _evaluate_matrix_inputs, evaluate


@dataclass
class EvaluateAnswer:
    """
    Represents the result of evaluating a recorded kernel with given inputs.
    It contains the computed values and their derivatives obtained from evaluating
    a recorded kernel using the `evaluate_kernel` function.

    Below we will assume the kernel is a vector field `f: (x, y, z) |-> (f1, f2, f3)`.
    Abstract variable names `x, y, z` are represented by `aadc.Argument` objects, and
    points `f1, f2, f3` in the image are represented by `aadc.Result` objects.

    Attributes:
    -----------
    * `values : dict[Result, npt.NDArray[np.double]]`
        A dictionary mapping Result objects to numpy arrays containing the values computed for each pass.
        If kernel was evaluted as follows: `(out11, out12, out13) = f(x1, y1, z1)`, `(out21, out22, out23) = f(x2, y1, z2)`,
        then this dictionary will be of the form: `{f1: [out11, out21], f2: [out12, out22], f3: [out13, out23]}`
    * `derivs : dict[Result, dict[Argument, npt.NDArray[np.double]]]`
        A nested dictionary containing the computed derivatives. The outer dictionary maps
        Result objects to inner dictionaries, which in turn map `Argument` objects to numpy
        arrays containing the derivative values.
        If kernel was evaluted as follows: `(out11, out12, out13) = f(x1, y1, z1)`, `(out21, out22, out23) = (x2, y1, z2)`,
        and the request was `{f1: [x, y], f2: [z]}`, then the output dictionary will be:
        `{f1: {x: [df1/dx1, df1/dx2], y: [df1/dy1, df1/dy1]}, f2: {z: [df2/dz1, df2/dz2]}}`

    Example:
    --------
    >>> import aadc
    >>> from aadc.recording_ctx import record_kernel
    >>> with record_kernel() as kernel:
    ...     x = aadc.idouble(1.0)
    ...     y = aadc.idouble(2.0)
    ...     z = aadc.idouble(3.0)
    ...     xin = x.mark_as_input()
    ...     f = aadc.math.exp(x / y + z) + x
    ...     fout = f.mark_as_output()
    >>> output = evaluate_kernel(
    ...     kernel,
    ...     request={fout: [xin]},
    ...     inputs={xin: 1.0},
    ...     num_threads=1
    ... )
    >>> bool(np.isclose(output.values[fout].item(), 34.11545196))
    True
    >>> bool(np.isclose(output.derivs[fout][xin].item(), 17.55772598))
    True
    """

    values: Dict[Result, npt.NDArray[np.double]]
    derivs: Dict[Result, Dict[Argument, npt.NDArray[np.double]]]

    __slots__ = ("values", "derivs")


def evaluate_kernel(
    kernel: Functions,
    request: Dict[Result, Sequence[Argument]],
    inputs: Dict[Argument, Union[npt.NDArray[np.double], float]],
    num_threads: int,
) -> EvaluateAnswer:
    """
    Evaluates a recorded kernel with given inputs and calculates derivatives.

    This function takes a recorded kernel, a request specifying which outputs and
    inputs to consider, the input values, and the number of threads to use for
    computation. It returns both the computed values and their derivatives.

    Below we will assume the kernel is a vector field `f: (x, y, z) |-> (f1, f2, f3)`.
    Abstract variable names `x, y, z` are represented by `aadc.Argument` objects, and
    points `f1, f2, f3` in the image are represented by `aadc.Result` objects.

    Parameters
    ----------
    * `kernel : Functions`
        The recorded kernel containing the computational graph.
    * `request : dict[Result, Sequence[Argument]]`
        A dictionary specifying derviatives to compute.
        If the request is `{f1: [x, y], f2: [z]}`, then `df1/dx`, `df1/dy`, `df2/dz` will be computed.
    * `inputs : dict[Argument, npt.NDArray[np.double] | float]`
        Specifies the input values for the kernel. For each scalar argument you can assign
        a float or a numpy array. For arguments where arrays were given, all arrays need to be
        the same length. If the following inputs are given: `{x: [x1, x2], y: y1, z: [z1, z2]}`,
        then the vector field will be evaulated for 2 inputs: `(x1, y1, z1)` and `(x2, y1, z2)`.
    * `num_threads : int`
        The number of threads to use for parallel computation.

    Returns
    -------
    * `EvaluateAnswer` -
        An object containing the computed values and their derivatives.

    Example
    -------
    >>> import aadc
    >>> from aadc.recording_ctx import record_kernel
    >>> with record_kernel() as kernel:
    ...     x = aadc.idouble(1.0)
    ...     y = aadc.idouble(2.0)
    ...     z = aadc.idouble(3.0)
    ...     xin = x.mark_as_input()
    ...     f = aadc.math.exp(x / y + z) + x
    ...     fout = f.mark_as_output()
    >>> output = evaluate_kernel(
    ...     kernel,
    ...     request={fout: [xin]},
    ...     inputs={xin: 1.0},
    ...     num_threads=1
    ... )
    >>> bool(np.isclose(output.values[fout].item(), 34.11545196))
    True
    >>> bool(np.isclose(output.derivs[fout][xin].item(), 17.55772598))
    True
    """
    values, derivs = evaluate(kernel, request, inputs, ThreadPool(num_threads))
    return EvaluateAnswer(values, derivs)


def evaluate_matrix_inputs(
    kernel: Functions,
    requests: Sequence[Tuple[Result, List[npt.NDArray[np.object_]]]],
    inputs: Sequence[Tuple[npt.NDArray[np.object_], npt.NDArray[np.float64]]],
    num_threads: int,
) -> Tuple[npt.NDArray[np.double], dict[Result, list[npt.NDArray[np.double]]]]:
    results, grads_internal = _evaluate_matrix_inputs(kernel, requests, inputs, num_threads)
    grads_processed = defaultdict(list)

    for i, (result, arg_matrices) in enumerate(requests):
        total_index = 0
        for arg_matrix in arg_matrices:
            current_grads = grads_internal[i][2][:, total_index : total_index + arg_matrix.size]
            grads_processed[result].append(current_grads.reshape((-1, *arg_matrix.shape)))
            total_index += arg_matrix.size

    return results, grads_processed
