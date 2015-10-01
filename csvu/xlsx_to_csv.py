
from cStringIO import StringIO
from itertools import izip_longest
import openpyxl
import sys
import traceback

from csvu import writer_make
from csvu.cli import (
        default_arg_parser, 
        nonnegative_int,
    )

def cli_arg_parser():

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

def filter_d(f, sheet=0):
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

    return {'fieldnames': K, 'generator': g()}

def cli():

    parser = cli_arg_parser()

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

        d = filter_d(
                        f,
                        sheet=args.sheet,
                    )

        fieldnames = d['fieldnames']
        g          = d['generator']

        writer_f = writer_make(
                        file_or_path=args.file1,
                        dialect=args.dialect1,
                        headless=True,
                        fieldnames=fieldnames,
                    )

        writer_f(g)

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

