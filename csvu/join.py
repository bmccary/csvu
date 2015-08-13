
from copy import copy
from operator import itemgetter
import traceback

from csvu import (
        default_arg_parser, 
        reader_make,
        writer_make,
    )

def cli_arg_parser():
    
    description = 'CSVU join computes the join of two CSV files.'

    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='input',
                    file2='output',
                    dialect0='input',
                    dialect1='input',
                    dialect2='output',
                    headless=True,
                )

    parser.add_argument(
            '--keyname',
            default=None,
            required=True,
            help='''The key column name, if any.''',
        )

    parser.add_argument(
            '--kind',
            default='INNER',
            choices=['INNER', 'OUTER'],
            help='''The kind of join to perform.''',
        )

    return parser

def filter_d(row0_g, row1_g, fieldnames0, fieldnames1, keyname, kind='INNER'):

    fn0 = set(fieldnames0)
    fn1 = set(fieldnames1)

    fnd10 = fn1 - fn0
    fnd01 = fn0 - fn1

    fieldnames = copy(fieldnames0)
    fieldnames.extend(fn for fn in fieldnames1 if fn in fnd10)

    def g():

        s0 = sorted(row0_g, key=itemgetter(keyname))
        s1 = sorted(row1_g, key=itemgetter(keyname))

        g0 = iter(s0)
        g1 = iter(s1)

        row0 = next(g0)
        row1 = next(g1)

        def k(x):
            return x[keyname]

        blank0 = {k: '' for k in fnd01}
        blank1 = {k: '' for k in fnd10}

        while True:
            while k(row0) < k(row1):
                if kind == 'OUTER':
                    row0.update(blank1)
                    yield row0
                row0 = next(g0)
            while k(row0) > k(row1):
                if kind == 'OUTER':
                    row1.update(blank0)
                    yield row1
                row1 = next(g1)
            row0.update(row1)
            yield row0
            row0 = next(g0)
            row1 = next(g1)

    return {'fieldnames': fieldnames, 'generator': g()}
            
def cli():

    parser = cli_arg_parser()

    args = parser.parse_args()

    try:

        reader0_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        reader1_d = reader_make(
                        fname=args.file1,
                        dialect=args.dialect1,
                        headless=args.headless,
                    )

        dialect0    = reader0_d['dialect']
        fieldnames0 = reader0_d['fieldnames']
        reader0_g   = reader0_d['reader']

        dialect1    = reader1_d['dialect']
        fieldnames1 = reader1_d['fieldnames']
        reader1_g   = reader1_d['reader']

        if not args.keyname in fieldnames0:
            raise Exception("Column '{}' is not in FILE0.".format(args.keyname))
        if not args.keyname in fieldnames1:
            raise Exception("Column '{}' is not in FILE1.".format(args.keyname))

        d = filter_d(
                        row0_g=reader0_g,
                        row1_g=reader1_g,
                        fieldnames0=fieldnames0,
                        fieldnames1=fieldnames1,
                        keyname=args.keyname,
                        kind=args.kind,
                    )

        g           = d['generator']
        fieldnames2 = d['fieldnames']

        dialect2 = args.dialect2

        if dialect2 == 'dialect0':
            dialect2 = dialect0

        writer_f = writer_make(
                        fname=args.file2,
                        dialect=dialect2,
                        headless=args.headless,
                        fieldnames=fieldnames2,
                    )

        writer_f(g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

