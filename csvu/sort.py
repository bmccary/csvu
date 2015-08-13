
from copy import copy
from operator import itemgetter
import traceback

from csvu import (
        default_arg_parser, 
        reader_make,
        writer_make,
        K_NASTRINGs,
    )

def cli_arg_parser():

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

def filter_g(row_g, cols, asc=True, numeric=False, nastrings=K_NASTRINGs):
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

def cli():

    parser = cli_arg_parser()

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

        g = filter_g(
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

        writer_f(g)

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)





