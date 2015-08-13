
from copy import copy
from itertools import chain
import traceback

from csvu import (
        reader_make,
        writer_make,
    )

from csvu.cli import default_arg_parser

def cli_arg_parser():
    
    description = 'CSVU cat is like GNU cat, but for CSV files.'
    parser = default_arg_parser(
                    description=description,
                    file1='output',
                    headless=True,
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
    parser.add_argument(
            '--files', 
            type=str, 
            nargs='+',
            required=True,
            help='''The CSV files to cat.'''
        )
    return parser

def filter_d(rows_g, fieldnames):

    fns0 = fieldnames[0]
    for i, fnsi in enumerate(fieldnames[1:]):
        if fns0 != fnsi:
            raise Exception("Column mismatch: {}: {} != {}".format(i+1, fns0, fnsi))

    fieldnames1 = copy(fns0)

    def g():
        for row in chain(*rows_g):
            yield row

    return {'fieldnames': fieldnames1, 'generator': g()}

def cli():

    parser = cli_arg_parser()

    args = parser.parse_args()

    try:

        fieldnames = []
        readers_g  = []

        for fname in args.files:
            reader_d = reader_make(
                            fname=fname,
                            dialect='sniff',
                            headless=args.headless,
                        )
            fieldnames.append(reader_d['fieldnames'])
            readers_g.append(reader_d['reader'])

        d = filter_d(
                        rows_g=readers_g,
                        fieldnames=fieldnames,
                    )

        g           = d['generator']
        fieldnames1 = d['fieldnames']

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=args.dialect1,
                        headless=args.headless,
                        fieldnames=fieldnames1,
                    )

        writer_f(g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

