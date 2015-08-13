
from copy import copy

import traceback

from csvu import (
        default_arg_parser, 
        positive_int,
        reader_make,
        writer_make,
    )

def cli_arg_parser():

    description = 'CSVU Tail is like GNU Tail, but for CSV files.'

    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                    headless=True,
                )

    parser.add_argument(
            'count', 
            type=positive_int, 
            help='''Return the last :count: rows.'''
        )

    return parser

def filter_g(row_g, count, debug=False):
    L = list(row_g)
    for row in L[-count:]:
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

        g = filter_g(
                        row_g=reader_g,
                        count=args.count,
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



