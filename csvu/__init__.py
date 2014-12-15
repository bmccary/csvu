


__all__ = [
            'BCSVDialect',
            'BCSVDictReader',
            'BCSVDictWriter',
            'GetRowFunction',
            'SetRowFunction',
            'GrepFilter',
            ]








from csv import Dialect, DictReader, DictWriter, QUOTE_MINIMAL, QUOTE_NONNUMERIC, QUOTE_ALL









class BCSVDialect(Dialect):
    doublequote = False
    escapechar = '\\'
    delimiter = ','
    quotechar = '"'
    skipinitialspace = True
    lineterminator = '\r\n'
    #quoting = QUOTE_MINIMAL
    quoting = QUOTE_ALL







class BCSVDictReader:

    def __init__(self, f, 
                    fieldnames=None, 
                    restkey=None,   
                    restval=None, 
                    dialect=BCSVDialect(), 
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










class BCSVDictWriter(DictWriter):

    def __init__(self, *args, **kwds):
        kwds['dialect'] = BCSVDialect()
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
        f = BCSVDictWriter._maybe_to_int
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


















import re


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
            
                
        
        









        



















# vim:ts=4:sw=4:et:syn=python

