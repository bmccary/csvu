
import argparse
from cStringIO import StringIO
from csv import excel, reader, DictReader, DictWriter, Sniffer
import sys
from itertools import izip
from prettytable import PrettyTable
from numbers import Number

K_NASTRINGs = [ '', 'NA', 'NONE', ]
K_NASTRINGs = [x.strip().upper() for x in K_NASTRINGs]

K_NAs = K_NASTRINGs + [ None, [], ]

DELIMITERS = ',\t|'

def positive_int(x):
    try:
        y = int(x)
        if y < 1:
            raise None
        return y
    except:
        m = "Not a positive integer: '{}'".format(x)
        raise argparse.ArgumentTypeError(m)

def nonnegative_int(x):
    try:
        y = int(x)
        if y < 0:
            raise None
        return y
    except:
        m = "Not a nonnegative integer: '{}'".format(x)
        raise argparse.ArgumentTypeError(m)

def default_arg_debug(parser):

    parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='''Use this flag when debugging these scripts.''',
        )

def default_arg_headless(parser):

    parser.add_argument(
            '--headless',
            default=False,
            action='store_true',
            help='''Use this flag if there is no header.''',
        )

def default_arg_dialect0(parser):

    parser.add_argument(
            '--dialect0', 
            default='sniff', 
            choices=['sniff', 'excel', 'excel-tab',],
            help='''The CSV dialect of file0.
                    Option *sniff* detects the dialect, 
                    *excel* dialect uses commas, 
                    *excel-tab* uses tabs.
                    Note that *sniff* will load the
                    entire file into memory, so for large
                    files it may be better to explicitly
                    specify the dialect.
                    '''
        )

def default_arg_dialect1_as_input(parser):

    parser.add_argument(
            '--dialect1', 
            default='sniff', 
            choices=['sniff', 'excel', 'excel-tab',],
            help='''The CSV dialect of file1.
                    Option *sniff* detects the dialect, 
                    *excel* dialect uses commas, 
                    *excel-tab* uses tabs.
                    Note that *sniff* will load the
                    entire file into memory, so for large
                    files it may be better to explicitly
                    specify the dialect.
                    '''
        )

def default_arg_dialect1_as_output(parser):

    parser.add_argument(
            '--dialect1', 
            default='dialect0', 
            choices=['dialect0', 'excel', 'excel-tab', 'pretty',],
            help='''The CSV dialect of the output.
                    Option *dialect0* uses the same dialect as file0,
                    *excel* dialect uses commas, 
                    *excel-tab* uses tabs,
                    *pretty* prints a human-readable table.
                    '''
        )

def default_arg_dialect2(parser):

    parser.add_argument(
            '--dialect2', 
            default='dialect0', 
            choices=['dialect0', 'excel', 'excel-tab', 'pretty',],
            help='''The CSV dialect of the output.
                    Option *dialect0* uses the same dialect as file0,
                    *excel* dialect uses commas, 
                    *excel-tab* uses tabs,
                    *pretty* prints a human-readable table.
                    '''
        )

def default_arg_file0(parser):

    parser.add_argument(
            '--file0', 
            type=str, 
            default='-',
            help='Input CSV file, defaults to STDIN.'
        )

def default_arg_file1_as_input(parser):

    parser.add_argument(
            '--file1', 
            type=str,
            required=True,
            help='Input CSV file.'
        )

def default_arg_file1_as_output(parser):

    parser.add_argument(
            '--file1', 
            type=str, 
            default='-',
            help='Output CSV file, defaults to STDOUT.'
        )

def default_arg_file2(parser):

    parser.add_argument(
            '--file2', 
            type=str, 
            default='-',
            help='Output CSV file, defaults to STDOUT.'
        )

def default_arg_parser(
        description,
        headless=None,
        dialect0=None,
        dialect1=None,
        dialect2=None,
        file0=None,
        file1=None,
        file2=None,
    ):

    parser = argparse.ArgumentParser(
                    description=description,
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                )

    if headless:
        default_arg_headless(parser)

    if dialect0:
        default_arg_dialect0(parser)

    if dialect1 is not None:
        if dialect1 == 'input':
            default_arg_dialect1_as_input(parser)
        elif dialect1 == 'output':
            default_arg_dialect1_as_output(parser)
        else:
            raise Exception("Bad dialect1: {}".format(dialect1))

    if dialect2:
        default_arg_dialect2(parser)

    if file0:
        default_arg_file0(parser)

    if file1 is not None:
        if file1 == 'input':
            default_arg_file1_as_input(parser)
        elif file1 == 'output':
            default_arg_file1_as_output(parser)
        else:
            raise Exception("Bad file1: {}".format(dialect1))

    if file2:
        default_arg_file2(parser)

    default_arg_debug(parser)

    return parser

def reader_make(fname='-', dialect='sniff', headless=False):
    """
    Make a reader for CSV files.

    :param fname: 
        The file to read from. Default is '-', which denotes STDIN.

    :param dialect: 
        The CSV dialect. Default is 'sniff', which (usually) automatically
        detects the dialect. However, 'sniff' will load the entire CSV
        file into memory, which may be unsuitable. Options are 'sniff', 
        'excel', 'excel-tab', or any Dialect object from the python
        csv module.

    :param headless:
        Whether or not CSV is headless. Default is False. When CSV has
        a header, column names are the values in the first row. When
        CSV is headless, column names are integers 0, 1, 2, et cetera.

    """

    #
    # File
    #

    f = sys.stdin

    if fname != '-':
        f = open(fname, 'r')

    #
    # Dialect
    #

    if dialect == 'sniff':
        # read the entire file into memory.
        f = StringIO(f.read())
        sample = f.read()
        f.reset()
        try:
            dialect = Sniffer().sniff(sample, delimiters=DELIMITERS)
        except:
            dialect = excel

    #
    # Reader
    #

    if headless:
        r = reader(f, dialect=dialect)
        row0 = r.next()
        fieldnames = [str(i) for i, x in enumerate(row0)]
        def gen():
            yield {fn: x for fn, x in izip(fieldnames, row0)}
            for row in r:
                yield {fn: x for fn, x in izip(fieldnames, row)}
        return {'dialect': dialect, 'fieldnames': fieldnames, 'reader': gen()}
    else:
        r = DictReader(f, dialect=dialect)
        fieldnames = r.fieldnames
        def gen():
            for row in r:
                yield row
        return {'dialect': dialect, 'fieldnames': fieldnames, 'reader': gen()}

def writer_make(fieldnames, fname='-', dialect='excel', headless=False):

    #
    # File
    #

    f = sys.stdout

    if fname != '-':
        f = open(fname, 'w')

    #
    # Writer
    #

    if dialect == 'pretty':
        def wf(gen):

            w = None

            if headless:
                w = PrettyTable(header=False)
            else:
                w = PrettyTable(fieldnames)

            for row in gen:
                w.add_row([row[fn] for fn in fieldnames])

            w.align = 'l'

            f.write(w.get_string()) 
            f.write('\n')

        return wf
    else:
        def wf(gen):
            w = DictWriter(f, dialect=dialect, fieldnames=fieldnames)
            if not headless:
                w.writeheader()
            w.writerows(row for row in gen)

        return wf

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

