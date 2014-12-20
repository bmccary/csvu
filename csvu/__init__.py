


__all__ = [
            'CSVUDialect',
            'CSVUDictReader',
            'CSVUDictWriter',
            'GetRowFunction',
            'SetRowFunction',
            'GrepFilter',
            ]








from csv import Dialect, DictReader, DictWriter, QUOTE_MINIMAL, QUOTE_NONNUMERIC, QUOTE_ALL

import re

import string






class CSVUDialect(Dialect):
    doublequote = False
    escapechar = '\\'
    delimiter = ','
    quotechar = '"'
    skipinitialspace = True
    lineterminator = '\r\n'
    #quoting = QUOTE_MINIMAL
    quoting = QUOTE_ALL







class CSVUDictReader:

    def __init__(self, f, 
                    fieldnames=None, 
                    restkey=None,   
                    restval=None, 
                    dialect=CSVUDialect(), 
                    filter=None,
                    *args, 
                    **kwds):

        self._reader = DictReader(
                                    f, 
                                    fieldnames=fieldnames,
                                    restkey=restkey, 
                                    restval=restval,    
                                    dialect=dialect,
                                    *args,
                                    **kwds
                                )
        self._filter = filter

    @property
    def fieldnames(self):
        return self._reader.fieldnames

    def __iter__(self):
        return self

    def next(self):
        f = self._filter
        r = self._reader
        if f:
            while True:
                d = r.next()
                if f(d):
                    return d
        else:
            return r.next()










class CSVUDictWriter(DictWriter):

    def __init__(self, *args, **kwds):
        kwds['dialect'] = CSVUDialect()
        DictWriter.__init__(self, *args, **kwds)

    @classmethod
    def _maybe_to_int(cls, v):

        t = type(v)
        
        if t is int:
            return v

        if t is float and v.is_integer():
            return int(v)

        return v

    def _dict_to_list(self, rowdict):
        f = CSVUDictWriter._maybe_to_int
        return [f(rowdict[k]) for k in self.fieldnames]
             








class GetRowFunction:

    def __init__(self, columns):
        self._meta = columns

    @property
    def meta(self):
        return self._meta

    def __call__(self, row):
        return {k : row[k] for k in self.meta}










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

    def __init__(self, set1, set2, cols=None, where=None):
        
        self.cols = cols
        self.set1 = set1
        self.set2 = set2
        
        if where is None:
            self.where = None
        else:
            self.where = (where[0], re.compile(where[1]))

        self.table = string.maketrans(set1, set2)

    def __call__(self, row):
       
        m = True
 
        if self.where:
            m = self.where[1].search(row[self.where[0]])

        if not m:
            return row

        def maybe_tr(k, v):
            tr = False
            if self.cols:
                if k in self.cols:
                    tr = True
            else:
                tr = True
            if tr:
                return string.translate(v, self.table)
            return v

        return {k: maybe_tr(k, v) for k, v in row.iteritems()}
           
