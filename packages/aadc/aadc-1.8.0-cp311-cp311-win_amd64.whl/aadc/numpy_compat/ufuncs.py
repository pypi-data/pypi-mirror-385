import numpy as np

import aadc
from aadc import math

UNARY_AADC_FUNCS = {
    #############################
    # Unary aritmetic functions
    #############################
    "negative": aadc.idouble.__neg__,
    "positive": aadc.idouble.__pos__,
    "absolute": aadc.idouble.__abs__,
    "exp": math.exp,
    "exp2": math.exp2,
    "expm1": math.expm1,
    "log": math.log,
    "log2": math.log2,
    "log10": math.log10,
    "log1p": math.log1p,
    "sqrt": math.sqrt,
    "trunc": math.trunc,
    "floor": math.floor,
    "ceil": math.ceil,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "arcsin": math.asin,
    "arccos": math.acos,
    "arctan": math.atan,
    "arctan2": aadc.idouble.atan2,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "arcsinh": math.asinh,
    "arccosh": math.acosh,
    "arctanh": math.atanh,
    "erf": math.erf,
    "erfc": math.erfc,
    "ndtr": math.cdf_normal,
    "cbrt": math.cbrt,
    "sign": math.sign,
    "conj": aadc.idouble.conjugate,
    "conjugate": aadc.idouble.conjugate,
    "square": lambda x: aadc.idouble.pow(x, 2),
    # TODO:
    # expm1 = ufunc(np.expm1)
    # reciprocal = ufunc(np.reciprocal)
    # hypot = ufunc(np.hypot)
    # deg2rad = ufunc(np.deg2rad)
    # rad2deg = ufunc(np.rad2deg)
    #############################
    # Unary utility functions
    #############################
    "isfinite": aadc.idouble.isfinite,
    "isinf": aadc.idouble.isinf,
    "isnan": aadc.idouble.isnan,
    # TODO:
    # signbit = ufunc(np.signbit)
    # copysign = ufunc(np.copysign)
    # nextafter = ufunc(np.nextafter)
    # spacing = ufunc(np.spacing)
    # ldexp = ufunc(np.ldexp)
    # fmod = ufunc(np.fmod)
    # degrees = ufunc(np.degrees)
    # radians = ufunc(np.radians)
    # rint = ufunc(np.rint)
    # clip = wrap_elemwise(np.clip)
    # isreal = wrap_elemwise(np.isreal)
    # iscomplex = wrap_elemwise(np.iscomplex)
    # real = wrap_elemwise(np.real)
    # imag = wrap_elemwise(np.imag)
    # fix = wrap_elemwise(np.fix)
    # i0 = wrap_elemwise(np.i0)
    # sinc = wrap_elemwise(np.sinc)
    # nan_to_num = wrap_elemwise(np.nan_to_num)
}

ARRAY_UFUNCS = {
    **{ufunc_name: np.frompyfunc(aadc_func, 1, 1) for ufunc_name, aadc_func in UNARY_AADC_FUNCS.items()},
    #############################
    # Binary arithmetic functions
    #############################
    "add": np.frompyfunc(math.add, 2, 1),
    "subtract": np.frompyfunc(math.subtract, 2, 1),
    "multiply": np.frompyfunc(aadc.idouble.__mul__, 2, 1),
    "divide": np.frompyfunc(aadc.idouble.__truediv__, 2, 1),
    "true_divide": np.frompyfunc(aadc.idouble.__truediv__, 2, 1),
    "power": np.frompyfunc(math.pow, 2, 1),
    "float_power": np.frompyfunc(math.pow, 2, 1),
    "matmul": np.matmul,
    # TODO:
    # logaddexp = ufunc(np.logaddexp)
    # logaddexp2 = ufunc(np.logaddexp2)
    # floor_divide = ufunc(np.floor_divide)
    # remainder = ufunc(np.remainder)
    #############################
    # Binary comparison functions
    #############################
    "equal": np.frompyfunc(math.equal_to, 2, 1),
    "not_equal": np.frompyfunc(math.not_equal, 2, 1),
    "less": np.frompyfunc(math.less, 2, 1),
    "less_equal": np.frompyfunc(math.leq, 2, 1),
    "greater": np.frompyfunc(math.greater, 2, 1),
    "greater_equal": np.frompyfunc(math.geq, 2, 1),
    "maximum": np.frompyfunc(math.max, 2, 1),
    "minimum": np.frompyfunc(math.min, 2, 1),
    # TODO:
    # fmax = ufunc(np.fmax)
    # fmin = ufunc(np.fmin)
    # isneginf = partial(equal, -np.inf)
    # isposinf = partial(equal, np.inf)
    #############################
    # Other binary functions
    #############################
    "copysign": np.frompyfunc(math.copysign, 2, 1),
    # TODO:
    # mod = ufunc(np.mod)
    #############################
    # Binary logical functions
    #############################
    # TODO:
    # logical_and = ufunc(np.logical_and)
    # logical_or = ufunc(np.logical_or)
    # logical_xor = ufunc(np.logical_xor)
    # logical_not = ufunc(np.logical_not)
    #############################
    # Binary bitwise functions
    #############################
    "bitwise_and": np.frompyfunc(aadc.ibool.__and__, 2, 1),
    "bitwise_or": np.frompyfunc(aadc.ibool.__or__, 2, 1),
    "invert": np.frompyfunc(aadc.ibool.__invert__, 1, 1),
    # TODO:
    # bitwise_xor = ufunc(np.bitwise_xor)
    # bitwise_not = ufunc(np.bitwise_not)
    # left_shift = ufunc(np.left_shift)
    # right_shift = ufunc(np.right_shift)
}
