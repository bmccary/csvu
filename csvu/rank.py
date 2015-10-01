
from copy import copy

import traceback

from csvu import (
        reader_make,
        writer_make,
    )
from csvu.cli import default_arg_parser

def cli_arg_parser():
    
    description = 'CSVU rank computes the rank CSV files.'

    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                    headless=True,
                )

    parser.add_argument(
            '--column',
            default=None,
            help='''The column being ranked, assumed to be sorted.
                    If not supplied then ties will not be accounted.''',
        )

    parser.add_argument(
            '--target',
            default=None,
            required=True,
            help='''The column to insert the rank into''',
        )

    return parser

def filter_d(row_g, fieldnames, column, target):

    fieldnames1 = copy(fieldnames)

    if not target in fieldnames1:
        fieldnames1.append(target)

    def g():
        if column:
            prev = None
            j = -1
            for i, row in enumerate(row_g):
                curr = row[column]
                if curr != prev:
                    j = i
                row[target] = j
                prev = curr
                yield row
        else:
            for i, row in enumerate(row_g):
                row[target] = i
                yield row

    return {'fieldnames': fieldnames1, 'generator': g()}
            
def cli():

    parser = cli_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        file_or_path=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        dialect0    = reader_d['dialect']
        fieldnames0 = reader_d['fieldnames']
        reader_g    = reader_d['reader']

        d = filter_d(
                        row_g=reader_g,
                        fieldnames=fieldnames0,
                        column=args.column,
                        target=args.target,
                    )

        fieldnames1 = d['fieldnames']
        g           = d['generator']

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

