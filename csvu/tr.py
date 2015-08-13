
import string
import traceback

from csvu import (
        default_arg_parser, 
        reader_make,
        writer_make,
    )

def cli_arg_parser():
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

def filter_g(row_g, set0, set1, cols=None):

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

        if args.columns:
            for c in args.columns:
                if not c in fieldnames:
                    m = 'Requested column {c} not found, available options are: {fieldnames}'.format(c=c, fieldnames=fieldnames)
                    parser.error(m)

        g = filter_g(
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

        writer_f(g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

