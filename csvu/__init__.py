


__all__ = [
            'GetFunction',
            'TrFunction',
            'GrepFilter',
            'xlsx_row_g',
            ]




import openpyxl
import re
import string
from itertools import izip




def xlsx_row_g(f, sheet = 0):
    wb = openpyxl.load_workbook(f, use_iterators=True)
    N  = len(wb.worksheets)   
    if not (0 <= sheet < N):
        raise Exception("Sheet must be in range [{}, {}), but sheet = {}.".format(0, N, sheet))
    ws = wb.worksheets[sheet]
    for row in ws.rows:
        yield [c.value for c in row]






class TransposeFunction:
    
    def __init__(self, mat, safe=False):

        m = len(mat)
        if m > 0:
            n = len(mat[0])
        else:
            n = 0

        if not safe:
            for row in mat:
                if len(row) != n:
                    raise ValueError("Argument :mat: non-rectangular.")

        self.mat = mat

    def __iter__(self):
        tr = izip(*self.mat)
        for row in tr:
            yield row


##
## Function
## 
##     dict0 -> dict1
##

class Function:
    pass


class GetFunction(Function):

    def __init__(self, keys, strict=False):
        self.keys   = keys
        self.strict = strict

    def __call__(self, dyct):
        if self.strict:
            return {k : dyct[k] for k in self.keys}
        else:
            return {k : dyct.get(k) for k in self.keys}


class SetFunction:

    def __init__(self, key, val):
        self.key = key
        self.val = val

    def __call__(self, dyct):
        dyct[self.key] = self.val
        return dyct


class TrFunction:

    def __init__(self, set0, set1, keys=None):
        self.keys  = keys
        self.set0  = set0
        self.set1  = set1
        self.table = string.maketrans(set0, set1)

    def __call__(self, dyct):
       
        def maybe_tr(k, v):
            tr = False
            if self.keys:
                tr = k in self.keys
            else:
                tr = True
            if tr:
                return string.translate(v, self.table)
            return v

        return {k: maybe_tr(k, v) for k, v in dyct.iteritems()}



##
## Filter
## 
##     dict -> True | False
##

class Filter:
    pass


NASTRINGS = [
                'None',
                'NA',
                '',
            ]


def blank_p(x, nastrings=NASTRINGS):
    if x is None:
        return True
    if isinstance(x, basestring):
        x = x.strip()
        if x in nastrings:
            return True
    return False
    

class BlankFilter(Filter):

    def __init__(self, blank_p=blank_p):
        self.blank_p = blank_p

    def __call__(self, dyct):
        p = self.blank_p
        return all(not p(x) for x in dyct)


class GrepFilter(Filter):

    def __init__(self, key, regex, include=True):
        self.key   = key 
        self.regex = regex
        if type(regex) is str:
            self.regex = re.compile(regex)
        else:
            self.regex = regex
        self.include = include
    
    def __call__(self, dyct):
        m = self.regex.search(dyct[self.key])
        if m:
            return self.include
        else:
            return not self.include
            

