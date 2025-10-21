from typing import Callable, Tuple, Union

import numpy as np
from numpy import ndarray

import aadc


class VectorizedFunction:
    __slots__ = ("_func", "_kernel", "_num_threads", "_in_args", "_out_args")

    def __init__(self, func: Callable, num_threads: int) -> None:
        self._func = func
        self._num_threads = num_threads
        self._kernel: Union[None, aadc.Functions] = None

    def __call__(self, arg: ndarray) -> Tuple[ndarray, ndarray]:
        if self._kernel is None:
            self._kernel = aadc.Functions()
            self._kernel.start_recording()

            rec_input = aadc.array(arg[0])
            self._in_args = rec_input.mark_as_input()
            rec_output = self._func(rec_input)
            self._out_args = np.atleast_1d(rec_output.mark_as_output())

            self._kernel.stop_recording()

        inputs = {self._in_args.item(i): arg[..., i] for i in range(self._in_args.size)}
        request = {self._out_args.item(i): self._in_args for i in range(self._out_args.size)}
        workers = aadc.ThreadPool(self._num_threads)
        res = aadc.evaluate(self._kernel, request, inputs, workers)

        # This seems costly perhaps we can return contiguous buffers?
        output = np.stack(tuple(res[0][out_arg] for out_arg in self._out_args))
        grads = np.stack(
            tuple(np.stack(tuple(res[1][out_arg][in_arg] for out_arg in self._out_args)) for in_arg in self._in_args)
        )

        return np.squeeze(output), np.squeeze(grads)
