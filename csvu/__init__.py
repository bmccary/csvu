


__all__ = [
            'GetRowFunction',
            'TrRowFunction',
            'GrepFilter',
            'xlsx_row_g',
            ]




import openpyxl
import re
import string




def xlsx_row_g(f, sheet = 0):
    wb = openpyxl.load_workbook(f, use_iterators=True)
    N  = len(wb.worksheets)   
    if not (0 <= sheet < N):
        raise Exception("Sheet must be in range [{}, {}), but sheet = {}.".format(0, N, sheet))
    ws = wb.worksheets[sheet]
    for row in ws.rows:
        yield [c.value for c in row]




class GetRowFunction:

    def __init__(self, cols):
        self.cols = cols

    def __call__(self, row):
        return {k : row[k] for k in self.cols}




class SetRowFunction:

    def __init__(self, dest, const):
        self.dest  = dest
        self.const = const

    def __call__(self, row):
        row[self.dest] = self.const
        return row




class BlankRowFunction:

    def __init__(self, columns):
        self.columns = columns

    def __call__(self, row):
        for c in self.columns:
            row[c] = None
        return row




class GrepFilter:

    def __init__(self, col, regex, include=True):
        self.col   = col
        self.regex = regex
        if type(regex) is str:
            self.regex = re.compile(regex)
        else:
            self.regex = regex
        self.include = include
    
    def __call__(self, row):
        m = self.regex.search(row[self.col])
        if m:
            return self.include
        else:
            return not self.include
            



class TrRowFunction:

    def __init__(self, set1, set2, cols=None):
        
        self.cols  = cols
        self.set1  = set1
        self.set2  = set2
        self.table = string.maketrans(set1, set2)

    def __call__(self, row):
       
        def maybe_tr(k, v):
            tr = False
            if self.cols:
                tr = k in self.cols
            else:
                tr = True
            if tr:
                return string.translate(v, self.table)
            return v

        return {k: maybe_tr(k, v) for k, v in row.iteritems()}

