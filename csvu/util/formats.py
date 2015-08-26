
from functools import partial

from . import isnum, isint, isna

def lexical_int(x, width=2):
    if isint(x):
        return str(int(x)).zfill(width)
    return x
lexical_int2 = partial(lexical_int, width=2)
lexical_int3 = partial(lexical_int, width=3)

def lexical_float(x, width=3):
    width = int(width)
    if isnum(x):
        return ('{{:.{}f}}'.format(width).format(x)).zfill(2*width + 1)
    return x

lexical_float2 = partial(lexical_float, width=2)
lexical_float3 = partial(lexical_float, width=3)

def nodecimal(x):
    if isint(x):
        return int(x)
    return x

