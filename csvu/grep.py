
import re
import traceback

from csvu import (
        default_arg_parser, 
        reader_make,
        writer_make,
    )

def cli_arg_parser():
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
            default=False, 
            action='store_true', 
            help='Include only non-matches.'
        )
    parser.add_argument(
            'column', 
            type=str,
            help='The column to grep upon.'
        )
    parser.add_argument(
            'regex',
            type=str,
            help='The regular expression (see the python re module).'
        )
    return parser

def filter_g(row_g, col, regex, negate):

    if type(regex) is str:
        regex = re.compile(regex)

    for row in row_g:
        m = regex.search(row[col]) is None
        if not m ^ negate:
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

        if not args.column in fieldnames:
            m = 'Requested column {c} not found, available options are: {fieldnames}'.format(c=args.column, fieldnames=fieldnames)
            parser.error(m)

        g = filter_g(
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

        writer_f(g)

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

