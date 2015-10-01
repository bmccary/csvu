
from copy import copy

import traceback

from csvu import (
        reader_make,
        writer_make,
    )
from csvu.cli import default_arg_parser

def cli_arg_parser():

    description = 'CSVU put will put constant values in columns.'

    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                )

    parser.add_argument(
            '--put',
            metavar=('column', 'value'),
            type=str,
            nargs=2,
            action='append',
            required=True,
            help='Put *value* to *column*.',
        )

    return parser

def filter_d(row_g, fieldnames, puts):

    fieldnames1 = copy(fieldnames)

    puts_set = set()

    for c, v in puts:
        if c in puts_set:
            raise Exception("Duplicate put: {}".format(c))
        puts_set.add(c)
        if not c in fieldnames1:
            fieldnames1.append(c)

    puts_d = {c: v for c, v in puts}

    def g():
        for row in row_g:
            yield {fn: puts_d.get(fn, row.get(fn)) for fn in fieldnames1}

    return {'fieldnames': fieldnames1, 'generator': g()}

def cli():

    parser = cli_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        file_or_path=args.file0,
                        dialect=args.dialect0,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        d = filter_d(
                        row_g=reader_g,
                        fieldnames=fieldnames,
                        puts=args.put,
                    )

        fieldnames1 = d['fieldnames']
        filter_g    = d['generator']

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        file_or_path=args.file1,
                        dialect=dialect1,
                        fieldnames=fieldnames1,
                    )

        writer_f(filter_g)

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

