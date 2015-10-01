
from itertools import izip
import traceback

from csvu import (
        reader_make,
        writer_make,
    )
from csvu.cli import default_arg_parser

def cli_arg_parser():
    
    description = 'CSVU transpose will transpose a CSV file.'
    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                )
    return parser

def filter_d(row_g, fieldnames):

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

    return {'fieldnames': keys, 'generator': g()}

def cli():

    parser = cli_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        file_or_path=args.file0,
                        dialect=args.dialect0,
                        headless=True,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        d = filter_d(
                        row_g=reader_g,
                        fieldnames=fieldnames,
                    )

        g          = d['generator']
        fieldnames = d['fieldnames']

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        file_or_path=args.file1,
                        dialect=dialect1,
                        headless=True,
                        fieldnames=fieldnames,
                    )

        writer_f(g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

