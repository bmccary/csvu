



import argparse
from cStringIO import StringIO
from csv import excel, excel_tab, reader, DictReader, DictWriter, Sniffer
import openpyxl
import re
import string
import sys
import os
from itertools import izip, izip_longest
from operator import itemgetter
from prettytable import PrettyTable
import importlib
from pprint import pformat
from numbers import Number
import traceback
from copy import copy


K_NASTRINGs = [ '', 'NA', 'NONE', ]
K_NASTRINGs = [x.strip().upper() for x in K_NASTRINGs]

K_NAs = K_NASTRINGs + [ None, [], ]





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

    parser = argparse.ArgumentParser(description=description)

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
        dialect = Sniffer().sniff(sample)

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













def xlsx_to_csv_arg_parser():

    description='CSVU xlsx-to-csv converts a sheet of an XLSX file to CSV.'

    parser = default_arg_parser(
                    description=description,
                    file1='output',
                )

    parser.add_argument(
            '--file0', 
            type=str, 
            default='-',
            help='The XLSX file, defaults to STDIN.'
        )

    def nonnegative_int(x):
        try:
            y = int(x)
            if y < 0:
                raise None
            return y
        except:
            m = "Not a nonnegative integer: '{}'".format(x)
            raise argparse.ArgumentTypeError(m)

    parser.add_argument(
            '--sheet',
            default=0,
            type=nonnegative_int,
            help='The sheet of the XLSX file to convert to CSV.'
        )

    parser.add_argument(
            '--dialect1', 
            default='excel', 
            choices=['excel', 'excel-tab', 'pretty',],
            help='''The CSV dialect of the output.
                    Option *excel* dialect uses commas, 
                    *excel-tab* uses tabs,
                    *pretty* prints a human-readable table.
                    '''
        )

    return parser

def xlsx_to_csv_d(f, sheet=0):
    wb = openpyxl.load_workbook(f, use_iterators=True)
    N  = len(wb.worksheets)   
    if not (0 <= sheet < N):
        raise Exception("Sheet must be in range [0, {}), but sheet = {}.".format(N, sheet))
    ws = wb.worksheets[sheet]
    M = max(len(row) for row in ws.rows)
    K = [str(i) for i in range(M)]

    def g():
        for row in ws.rows:
            yield {k: (c.value or '') for k, c in izip_longest(K, row, fillvalue='')}

    return {'fieldnames': K, 'xlsx_to_csv_g': g()}

def xlsx_to_csv_program():

    parser = xlsx_to_csv_arg_parser()

    args = parser.parse_args()

    try:

        f = None

        if args.file0 == '-':
            # OpenPYXL needs random access to the XLSX
            # file, so dump STDIN into a StringIO.
            f = StringIO(sys.stdin.read())
            f.reset()
        else:
            f = open(args.file, 'rb')

        filter_d = xlsx_to_csv_d(
                            f,
                            sheet=args.sheet,
                        )

        fieldnames = filter_d['fieldnames']
        filter_g   = filter_d['xlsx_to_csv_g']

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=args.dialect1,
                        headless=True,
                        fieldnames=fieldnames,
                    )

        writer_f(filter_g)
                        

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)


















def sort_arg_parser():

    description = 'CSVU Sort is like GNU Sort, but for CSV files.'

    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                    headless=True,
                )

    parser.add_argument(
            '--columns', 
            type=str, 
            required=True,
            nargs='+',
            help='''The columns to sort upon, in lexical order.
                    If --headless then --columns are integers starting
                    with 0 otherwise --columns are named columns.
                    '''
        )

    parser.add_argument(
            '--numeric', 
            action='store_true', 
            help='Attempt to convert each field to *float* prior to sort.'
        )

    parser.add_argument(
            '--nastrings', 
            nargs='*',
            default=K_NASTRINGs,
            help='Values which get converted to *None* prior to sorting.'
        )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
            '--ascending', 
            action='store_true',
            help='Sort rows in ascending order.'
        )
    group.add_argument(
            '--descending', 
            action='store_true',
            help='Sort rows in descending order.'
        )

    return parser

def sort_g(row_g, cols, asc=True, numeric=False, nastrings=K_NASTRINGs):
    """
    :param row_g: Rows to sort. :row_g: must be a generator of dictionaries.
    :param cols: Columns for keys. :cols: must be a generator of strings.
    :param asc: Ascending or descending. :asc: must be bool.
    :param numeric: Interpret keys as numeric. :asc: must be bool.
    :param nastrings: Values to compare as equivalent to None in python term order.
    """

    def mkkey():

        def caster(y):
            y = y.strip().upper()
            if y in nastrings:
                return None
            if numeric:
                try:
                    z = float(y)
                    return z
                except:
                    pass
            return y

        ig = itemgetter(*cols)

        def key_len_1(x):
            y = ig(x)
            return caster(y)

        def key_len_N(x):
            y = ig(x)
            return tuple(caster(i) for i in y)

        if len(cols) == 1:
            return key_len_1
        else:
            return key_len_N

    key = mkkey()

    for row in sorted(row_g, key=key, reverse=(not asc)):
        yield row

def sort_program():

    parser = sort_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        for c in args.columns:
            if not c in fieldnames:
                m = 'Requested column {c} not found, available options are: {fieldnames}'.format(c=c, fieldnames=fieldnames)
                parser.error(m)

        filter_g = sort_g(
                            row_g=reader_g,
                            cols=args.columns,
                            asc=args.ascending,
                            numeric=args.numeric,
                            nastrings=args.nastrings,
                        )

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        headless=args.headless,
                        fieldnames=fieldnames,
                    )

        writer_f(filter_g)
                        

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)























def sniff_arg_parser():

    description = 'CSVU sniff will determine the dialect of a CSV file.'
    parser = default_arg_parser(
                    description=description,
                    file0='input',
                )

    return parser

def sniff_program():

    parser = sniff_arg_parser()

    args = parser.parse_args()

    try:

        f = sys.stdin

        if args.file0 != '-':
            f = open(args.file, 'r')

        sample = f.read(2**16)

        dialect = Sniffer().sniff(sample)

        v = vars(dialect)

        x = PrettyTable(header=False)
        for k, v in vars(dialect).iteritems():
            if not k.startswith('_'):
                x.add_row([k, repr(v)])

        print x

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)










def dialect_arg_parser():
    description = 'CSVU dialect converts one CSV dialect to another.'
    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                    headless=True,
                )
    return parser

def dialect_g(row_g):

    return row_g
    
def dialect_program():

    parser = dialect_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        filter_g = dialect_g(
                            row_g=reader_g,
                        )

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        headless=args.headless,
                        fieldnames=fieldnames,
                    )

        writer_f(filter_g)
                        

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)
        

def pretty_arg_parser():
    description = 'CSVU pretty pretty-prints a CSV file.'
    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    headless=True,
                )
    return parser

def pretty_g(row_g):

    return row_g
    
def pretty_program():

    parser = pretty_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        filter_g = dialect_g(
                            row_g=reader_g,
                        )

        dialect1 = 'pretty'

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        headless=args.headless,
                        fieldnames=fieldnames,
                    )

        writer_f(filter_g)
                        

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)
        














def tr_arg_parser():
    description = 'CSVU tr is like GNU tr, but for CSV files.'
    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                    headless=True,
                )
    parser.add_argument(
            '--columns', 
            required=False, 
            type=str, 
            nargs='+',
            help='Space-separated list of columns to *tr*.'
        )
    parser.add_argument(
            'set0', 
            type=str,
            help='The character set to translate *from*.'
        )
    parser.add_argument(
            'set1', 
            type=str,
            help='The character set to translate *to*.'
        )
    return parser

def tr_g(row_g, set0, set1, cols=None):

    table = string.maketrans(set0, set1)

    def maybe_tr(k, v):
        tr = False
        if cols is None:
            tr = True
        else:
            tr = k in cols 
        if tr:
            return string.translate(v, table)
        return v

    for row in row_g:
        yield {k: maybe_tr(k, v) for k, v in row.iteritems()}
    
def tr_program():

    parser = tr_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        if args.columns:
            for c in args.columns:
                if not c in fieldnames:
                    m = 'Requested column {c} not found, available options are: {fieldnames}'.format(c=c, fieldnames=fieldnames)
                    parser.error(m)

        filter_g = tr_g(
                            row_g=reader_g,
                            set0=args.set0,
                            set1=args.set1,
                            cols=args.columns,
                        )

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        headless=args.headless,
                        fieldnames=fieldnames,
                    )

        writer_f(filter_g)
                        

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)















def grep_arg_parser():
    description = 'CSVU grep is like GNU grep, but for CSV files.'
    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                    headless=True,
                )
    parser.add_argument(
            '--negate',
            '-v', 
            default=True, 
            action='store_const', 
            const=False,
            help='Include only non-matches.'
        )
    parser.add_argument(
            '--column', 
            type=str,
            required=True,
            help='The column to grep upon.'
        )
    parser.add_argument(
            '--regex', 
            type=str,
            required=True,
            help='The regular expression (see the python re module).'
        )
    return parser

def grep_g(row_g, col, regex, negate):

    if type(regex) is str:
        regex = re.compile(regex)

    for row in row_g:
        m = regex.search(row[col]) is None
        if m ^ negate:
            yield row

def grep_program():

    parser = grep_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        if not args.column in fieldnames:
            m = 'Requested column {c} not found, available options are: {fieldnames}'.format(c=args.column, fieldnames=fieldnames)
            parser.error(m)

        filter_g = grep_g(
                            row_g=reader_g,
                            col=args.column,
                            regex=args.regex,
                            negate=args.negate,
                        )

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        headless=args.headless,
                        fieldnames=fieldnames,
                    )

        writer_f(filter_g)
                        

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)








def transpose_arg_parser():
    
    description = 'CSVU transpose will transpose a CSV file.'
    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                )
    return parser

def transpose_d(row_g, fieldnames):

    rows = [[row[fn] for fn in fieldnames] for row in row_g]

    m = len(rows)
    if m > 0:
        n = len(rows[0])
    else:
        n = 0

    for row in rows:
        if n != len(row):
            raise ValueError("Not rectangular.")

    keys = [str(i) for i in range(m)]

    def g():
        for row in izip(*rows):
            yield {i: c for i, c in izip(keys, row)}

    return {'fieldnames': keys, 'transpose_g': g()}

def transpose_program():

    parser = transpose_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=True,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        filter_d = transpose_d(
                            row_g=reader_g,
                            fieldnames=fieldnames,
                        )

        filter_g   = filter_d['transpose_g']
        fieldnames = filter_d['fieldnames']

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        headless=True,
                        fieldnames=fieldnames,
                    )

        writer_f(filter_g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)







def cut_arg_parser():
    
    description = 'CSVU cut is like GNU cut, but for CSV files.'
    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                    headless=True,
                )

    parser.add_argument(
            '--columns', 
            type=str, 
            required=True,
            nargs='+',
            help='''The columns to cut.
                    If --headless then --columns are integers starting
                    with 0 otherwise --columns are named columns.
                    '''
        )

    parser.add_argument(
            '--negate',
            default=False, 
            action='store_true', 
            help='''Include only columns not listed.'''
        )

    return parser

def cut_g(row_g, cols, fieldnames, negate=False):

    for row in row_g:
        yield {c: row[c] for c in fieldnames if (c in cols) ^ negate}

def cut_program():

    parser = cut_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        filter_g = cut_g(
                            row_g=reader_g,
                            fieldnames=fieldnames,
                            cols=args.columns,
                            negate=args.negate,
                        )

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        fieldnames = [c for c in fieldnames if (c in args.columns) ^ args.negate]

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        headless=args.headless,
                        fieldnames=fieldnames,
                    )

        writer_f(filter_g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)










def diff_arg_parser():
    
    description = 'CSVU diff computes the diff between two CSV files.'

    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='input',
                    file2='output',
                    dialect0='input',
                    dialect1='input',
                    dialect2='output',
                    headless=True,
                )

    parser.add_argument(
            '--keyname',
            default=None,
            help='''The key column name, if any.''',
        )

    parser.add_argument(
            '--compact',
            default=False,
            action='store_true',
            help='''Omit empty rows/cols.''',
        )

    parser.add_argument(
            '--nastrings', 
            nargs='*',
            default=K_NASTRINGs,
            help='Values which get converted to *None* prior to diffing.'
        )

    return parser

def diff_d(row0_g, row1_g, fieldnames, keyname=None, compact=False, nastrings=K_NASTRINGs):

    def diff_g1():
        for row0, row1 in izip(row0_g, row1_g):
            if keyname:
                k0 = row0[keyname]
                k1 = row1[keyname]
                if k0 != k1:
                    raise Exception("Difference in key column, cannot diff: {} != {}".format(k0, k1))
            d = False
            for fn in fieldnames:
                v0 = row0[fn]
                v1 = row1[fn]
                if equal0(v0, v1):
                    if fn != keyname:
                        row1[fn] = None
                else:
                    d = True
            if (not compact) or d:
                yield row1

    def diff_d():
        rows = [row for row in diff_g1()]
        keeps = []
        for fn in fieldnames:
            if fn == keyname:
                keeps.append(fn)
            elif not all(isna(row[fn], K=nastrings) for row in rows):
                keeps.append(fn)

        def diff_g2():
            for row in rows:
                yield {fn: row[fn] for fn in keeps}

        return {'fieldnames': keeps, 'diff_g': diff_g2()}

    if compact:
        return diff_d()

    return {'fieldnames': fieldnames, 'diff_g': diff_g1()}

    

def diff_program():

    parser = diff_arg_parser()

    args = parser.parse_args()

    try:

        reader0_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        reader1_d = reader_make(
                        fname=args.file1,
                        dialect=args.dialect1,
                        headless=args.headless,
                    )

        dialect0    = reader0_d['dialect']
        fieldnames0 = reader0_d['fieldnames']
        reader0_g   = reader0_d['reader']

        dialect1    = reader1_d['dialect']
        fieldnames1 = reader1_d['fieldnames']
        reader1_g   = reader1_d['reader']

        if fieldnames0 != fieldnames1:
            raise Exception("'{}' and '{}' have different columns.".format(args.file0, args.file1))

        if args.keyname:
            if not args.keyname in fieldnames0:
                raise Exception("Column '{}' is not in FILE0.".format(args.keyname))
            if not args.keyname in fieldnames1:
                raise Exception("Column '{}' is not in FILE1.".format(args.keyname))

        filter_d = diff_d(
                            row0_g=reader0_g,
                            row1_g=reader1_g,
                            fieldnames=fieldnames0,
                            keyname=args.keyname,
                            compact=args.compact,
                            nastrings=args.nastrings,
                        )

        fieldnames2 = filter_d['fieldnames']
        filter_g    = filter_d['diff_g']

        dialect2 = args.dialect2

        if dialect2 == 'dialect0':
            dialect2 = dialect0

        writer_f = writer_make(
                        fname=args.file2,
                        dialect=dialect2,
                        headless=args.headless,
                        fieldnames=fieldnames2,
                    )

        writer_f(filter_g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)















def join_arg_parser():
    
    description = 'CSVU join computes the join of two CSV files.'

    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='input',
                    file2='output',
                    dialect0='input',
                    dialect1='input',
                    dialect2='output',
                    headless=True,
                )

    parser.add_argument(
            '--keyname',
            default=None,
            required=True,
            help='''The key column name, if any.''',
        )

    return parser

def join_d(row0_g, row1_g, fieldnames0, fieldnames1, keyname):

    fn0 = set(fieldnames0)
    fn1 = set(fieldnames1)
    fnd = fn1 - fn0

    fieldnames = copy(fieldnames0)
    fieldnames.extend(fn for fn in fieldnames1 if fn in fnd)

    def g():

        s0 = sorted(row0_g, key=itemgetter(keyname))
        s1 = sorted(row1_g, key=itemgetter(keyname))

        g0 = iter(s0)
        g1 = iter(s1)

        row0 = next(g0)
        row1 = next(g1)

        def k(x):
            return x[keyname]

        while True:
            while k(row0) < k(row1):
                row0 = next(g0)
            while k(row0) > k(row1):
                row1 = next(g1)
            row0.update(row1)
            yield row0
            row0 = next(g0)
            row1 = next(g1)

    return {'fieldnames': fieldnames, 'join_g': g()}
            
def join_program():

    parser = join_arg_parser()

    args = parser.parse_args()

    try:

        reader0_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        reader1_d = reader_make(
                        fname=args.file1,
                        dialect=args.dialect1,
                        headless=args.headless,
                    )

        dialect0    = reader0_d['dialect']
        fieldnames0 = reader0_d['fieldnames']
        reader0_g   = reader0_d['reader']

        dialect1    = reader1_d['dialect']
        fieldnames1 = reader1_d['fieldnames']
        reader1_g   = reader1_d['reader']

        if not args.keyname in fieldnames0:
            raise Exception("Column '{}' is not in FILE0.".format(args.keyname))
        if not args.keyname in fieldnames1:
            raise Exception("Column '{}' is not in FILE1.".format(args.keyname))

        filter_d = join_d(
                            row0_g=reader0_g,
                            row1_g=reader1_g,
                            fieldnames0=fieldnames0,
                            fieldnames1=fieldnames1,
                            keyname=args.keyname,
                        )

        fieldnames2 = filter_d['fieldnames']
        filter_g    = filter_d['join_g']

        dialect2 = args.dialect2

        if dialect2 == 'dialect0':
            dialect2 = dialect0

        writer_f = writer_make(
                        fname=args.file2,
                        dialect=dialect2,
                        headless=args.headless,
                        fieldnames=fieldnames2,
                    )

        writer_f(filter_g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

















def isnum(x):
    return isinstance(x, Number)

def isstr(x):
    return isinstance(x, basestring)

def isna(x, K=K_NAs):
    if isstr(x):
        x = x.strip().upper()
    return x in K

def tona_or(f):
    def g(x, isna=isna):
        if isna(x):
            return None
        return f(x)
    return g

def tonn_or(f):
    def g(x, isna=isna):
        x = f(x)
        if isna(x):
            return x
        if not isnum(x):
            raise Exception("Not a number: {}".format(x))
        if x < 0:
            raise Exception("Negative argument: {}".format(x))
        return x
    return g

tofloat = tona_or(float)
toint   = tona_or(int)

tonnfloat = tonn_or(tofloat)
tonnint   = tonn_or(toint)

def tozero(x, isna=isna):
    if isna(x):
        return 0.0
    return x

def tonone(x, isna=isna):
    if isna(x):
        None
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

def equal0(x, y, isna=isna):
    if isna(x) and isna(y):
        return True

    if isnum(x) and isnum(y):
        return abs(x - y) < 1e-5

    if isstr(x) and isstr(y):
        x = x.strip()
        y = y.strip()
        return x == y

    return x == y

def inner0(X, Y, isna=isna):
    if all(isna(x) for x in X) or all(isna(y) for y in Y):
        return None
    return sum(x * y for x, y in izip(
                                        (tozero(x) for x in X), 
                                        (tozero(y) for y in Y),
                                ))

def row_reduce_arg_parser():

    description = 'CSVU row-reduce repeatedly applies a module of row functions.'

    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                )

    parser.add_argument(
            '--reductions', 
            type=str,
            default='reductions',
            help='''The file from which to get reductions.'''
        )

    parser.add_argument(
            '--coercions', 
            type=str,
            default='coercions',
            help='''The file from which to get coercions.'''
        )

    parser.add_argument(
            '--formats', 
            type=str,
            default='formats',
            help='''The file from which to get formats.'''
        )

    def positive_int(x):
        try:
            y = int(x)
            if y < 1:
                raise None
            return y
        except:
            m = "Not a nonnegative integer: '{}'".format(x)
            raise argparse.ArgumentTypeError(m)

    parser.add_argument(
            '--N',
            default=10,
            type=positive_int,
            help='''The number of iterations to attempt per row.'''
        )

   

    return parser

def row_reduce_g(row_g, fieldnames, reductions, coercions=None, formats=None, N=10):

    for row in row_g:

        if coercions:
            for fn in fieldnames:
                f = getattr(coercions, fn, None)
                if not callable(f):
                    continue
                try:
                    row[fn] = f(row[fn])
                except Exception as exc:
                    m = "The following row has an invalid/uncoercable '{}':\n\n\t{}\n\nFor the following reason: \n\n\t{}\n".format(fn, pformat(row), exc)
                    raise Exception(m)

        for fn in fieldnames:
            f = getattr(reductions, fn, None)
            if not callable(f):
                continue
            for i in xrange(N):
                v0 = row[fn]
                v1 = f(row)
                if equal0(v0, v1):
                    break
                row[fn] = v1

        if formats:
            for fn in fieldnames:
                f = getattr(formats, fn, None)
                if not callable(f):
                    continue
                try:
                    row[fn] = f(row[fn])
                except Exception as exc:
                    m = "The following row could not be formatted '{}':\n\n\t{}\n\nFor the following reason: \n\n\t{}\n".format(fn, pformat(row), exc)
                    raise Exception(m)

        yield row
            
def row_reduce_program():

    parser = row_reduce_arg_parser()

    args = parser.parse_args()

    try:

        #
        # CSV reader.
        #

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        #
        # Modules.
        #

        sys.path.append(os.getcwd())

        coercions  = importlib.import_module(args.coercions)
        reductions = importlib.import_module(args.reductions)
        formats    = importlib.import_module(args.formats)

        #
        # Filter.
        #

        filter_g = row_reduce_g(
                            row_g=reader_g,
                            fieldnames=fieldnames,
                            coercions=coercions,
                            reductions=reductions,
                            formats=formats,
                        )


        #
        # CSV writer.
        #

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        headless=args.headless,
                        fieldnames=fieldnames,
                    )

        writer_f(filter_g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)




