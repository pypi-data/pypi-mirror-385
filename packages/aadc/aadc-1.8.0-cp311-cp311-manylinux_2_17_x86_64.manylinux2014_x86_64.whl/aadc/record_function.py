from typing import Any, Callable, Dict, List, Sequence, Type, Union

import numpy as np
import numpy.typing as npt

import aadc
from aadc.overrides_free import np_asarray


def record(
    func: Callable[..., Any],
    x0: Union[float, npt.ArrayLike],
    params: Sequence[Union[float, aadc.idouble, npt.ArrayLike]] = (),
    kwparams: Dict[str, Any] = {},
    bump_size: float = 1e-10,
) -> Type:
    kernel = aadc.Functions()

    # start_rec_time = time.time()

    kernel.start_recording()
    x = aadc.array(x0)
    x_args = x.mark_as_input_no_diff()

    params_active: List[aadc.idouble | aadc.ndarray.AADCArray] = [
        p if isinstance(p, aadc.idouble) else aadc.idouble(p) if isinstance(p, float) else aadc.array(p) for p in params
    ]
    param_args = (
        np.concatenate([np.atleast_1d(np_asarray(p.mark_as_input_no_diff())) for p in params_active])
        if params_active
        else []
    )
    param_vec = np.empty(len(param_args), dtype=np.float64)

    f = func(x, *params_active, **kwparams)
    f_res = f.mark_as_output()
    kernel.stop_recording()

    recorded_function = aadc.VectorFunctionWithJacobian(kernel, x_args, param_args, f_res, bump_size=bump_size)

    # print(f"Recording took {time.time() - start_rec_time} seconds")

    class CurreidRecordedFunction:
        func = recorded_function.func
        jac = recorded_function.jac

        @classmethod
        def set_params(cls, *params: Sequence[Union[float, aadc.idouble, npt.ArrayLike]]) -> Type:
            i = 0
            for p in params:
                if isinstance(p, (float, aadc.idouble)):
                    param_vec[i] = p
                    i += 1
                else:
                    param_vec[i : i + len(p)] = p
                    i += len(p)

            recorded_function.set_params(param_vec)
            return cls

    return CurreidRecordedFunction
