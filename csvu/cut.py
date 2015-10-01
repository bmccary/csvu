
import traceback

from csvu import (
        reader_make,
        writer_make,
    )

from csvu.cli import default_arg_parser

def cli_arg_parser():
    
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
            nargs='+',
            help='''The columns to cut.
                    If *headless* then *columns* are integers starting
                    with 0 otherwise *columns* are named columns.
                    '''
        )
    parser.add_argument(
            '--rename',
            metavar=('from', 'to'),
            type=str,
            nargs=2,
            action='append',
            help='Rename *from* to *to*.',
        )
    parser.add_argument(
            '--negate',
            default=False, 
            action='store_true', 
            help='''Include only columns not listed.'''
        )
    return parser

def filter_d(row_g, fieldnames, columns, renames, negate=False):

    if renames:
        if negate:
            raise Exception("negate and rename is not defined.")
        if columns:
            renames.extend((c, c) for c in columns)
    elif columns:
        if negate:
            renames = [(c, c) for c in fieldnames if not (c in columns)]
        else:
            renames = [(c, c) for c in columns]
    else:
        raise Exception("Need renames or columns.")

    for c, r in renames:
        if not c in fieldnames:
            raise Exception("Column not found: {}".format(c))

    fieldnames1 = [r for c, r in renames]

    def g():
        for row in row_g:
            yield {r: row[c] for c, r in renames if r in fieldnames1}

    return {'fieldnames': fieldnames1, 'generator': g()}

def cli():

    parser = cli_arg_parser()

    args = parser.parse_args()

    if args.columns is None and args.rename is None:
        parser.error("need argument --columns or argument --rename or both")

    if args.rename and args.negate:
        parser.error("negate and rename is not defined")

    try:

        reader_d = reader_make(
                        file_or_path=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        d = filter_d(
                        row_g=reader_g,
                        fieldnames=fieldnames,
                        columns=args.columns,
                        renames=args.rename,
                        negate=args.negate,
                    )

        g           = d['generator']
        fieldnames1 = d['fieldnames']

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        file_or_path=args.file1,
                        dialect=dialect1,
                        headless=args.headless,
                        fieldnames=fieldnames1,
                    )

        writer_f(g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

