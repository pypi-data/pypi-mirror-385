import numpy as np

import aadc.ndarray as array
import aadc.numpy_compat.function_bindings as fbindings
import aadc.utils as utils

# >>>>>>> IN ARRAY API


@fbindings.aadc_array_function_bind("broadcast_arrays")
def broadcast_arrays(*args, subok=False):
    return [array.AADCArray(arr) for arr in np.broadcast_arrays(*utils.unpack(args), subok=subok)]


broadcast_to = fbindings.bind_single_argument_function_with_unpack(np.broadcast_to, "broadcast_to", wrap_output=True)
concat = fbindings.bind_single_argument_function_with_unpack(np.concatenate, "concatenate", wrap_output=True)
expand_dims = fbindings.bind_single_argument_function_with_unpack(np.expand_dims, "expand_dims", wrap_output=True)
flip = fbindings.bind_single_argument_function_with_unpack(np.flip, "flip", wrap_output=True)
moveaxis = fbindings.bind_single_argument_function_with_unpack(np.moveaxis, "moveaxis", wrap_output=True)
repeat = fbindings.bind_single_argument_function_with_unpack(np.repeat, "repeat", wrap_output=True)
reshape = fbindings.bind_single_argument_function_with_unpack(np.reshape, "reshape", wrap_output=True)
roll = fbindings.bind_single_argument_function_with_unpack(np.roll, "roll", wrap_output=True)
squeeze = fbindings.bind_single_argument_function_with_unpack(np.squeeze, "squeeze", wrap_output=True)
stack = fbindings.bind_single_argument_function_with_unpack(np.stack, "stack", wrap_output=True)
tile = fbindings.bind_single_argument_function_with_unpack(np.tile, "tile", wrap_output=True)

# TODO remaining Array API elements:
# permute_dims
# unstack

# <<<<<<< IN ARRAY API


# >>>>>>> NOT IN ARRAY API

hstack = fbindings.bind_single_argument_function_with_unpack(np.hstack, "hstack", wrap_output=True)
vstack = fbindings.bind_single_argument_function_with_unpack(np.vstack, "vstack", wrap_output=True)
copyto = fbindings.bind_single_argument_function_with_unpack(np.copyto, "copyto", wrap_output=True)

# <<<<<<< IN ARRAY API
