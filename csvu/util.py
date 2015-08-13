
from itertools import izip
from numbers import Number

K_NASTRINGs = [ '', 'NA', 'NONE', ]
K_NASTRINGs = [x.strip().upper() for x in K_NASTRINGs]

K_NAs = K_NASTRINGs + [ None, [], ]

def isnum(x):
    return isinstance(x, Number)

def isstr(x):
    return isinstance(x, basestring)

def isna(x, K=K_NAs):
    if x is None:
        return True
    if isstr(x):
        x = x.strip().upper()
    return x in K

def tofloat(x, isna=isna):
    if isna(x):
        return x
    return float(x)

def toint(x, isna=isna):
    if isna(x):
        return x
    return float(x)

def tonnint(x, isna=isna):
    if isna(x):
        return x
    y = toint(x)
    if isnum(y) and y >= 0.0:
        return y
    raise Exception("Cannot convert to non-negative int: {}".format(x))

def tonnfloat(x, isna=isna):
    if isna(x):
        return x
    y = tofloat(x)
    if isnum(y) and y >= 0.0:
        return y
    raise Exception("Cannot convert to non-negative float: {}".format(x))

def tozero(x, isna=isna):
    if isna(x):
        return 0.0
    return x

def tonone(x, isna=isna):
    if isna(x):
        return None
    return x

def sum0(X, isna=isna):
    if isna(X):
        return None
    elif all(isna(x) for x in X):
        return None
    return tofloat(sum(tozero(x, isna=isna) for x in X))

def mean0(X, isna=isna):
    s = sum0(X, isna=isna)
    if isna(s):
        return None
    return s / len(X)

def drop0(X, N, isna=isna):
    Y = sorted((tonone(x, isna=isna) for x in X), reverse=False)
    return Y[N:]

def max0(X, isna=isna):
    if isna(X):
        return None
    return max(tonone(x, isna=isna) for x in X)

def min0(X, isna=isna):
    if isna(X):
        return None
    return min(tonone(x, isna=isna) for x in X)

def equal0(x, y, isna=isna, tol=1e-5):
    #if isna(x) and isna(y):
    #    if isstr(x) and isstr(y):
    #        return x.strip().upper() == y.strip().upper()
    #    return True

    if isnum(x) and isnum(y):
        return abs(x - y) < tol

    if isstr(x) and isstr(y):
        x = x.strip()
        y = y.strip()
        return x == y

    return x == y

def inner0(X, Y, isna=isna):
    if all(isna(x) for x in X) or all(isna(y) for y in Y):
        return None
    return sum(u * v for u, v in izip((tozero(x, isna=isna) for x in X), (tozero(y, isna=isna) for y in Y)))

