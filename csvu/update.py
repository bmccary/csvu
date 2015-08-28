
from copy import copy
from operator import itemgetter
import traceback

from csvu import (
        reader_make,
        writer_make,
    )
from csvu.cli import default_arg_parser

EXTRA_ROW_ACTIONS = ['die', 'ignore',]
EXTRA_ROW_ACTION_DEFAULT = 'ignore'

EXTRA_COL_ACTIONS = ['die', 'ignore', 'insert']
EXTRA_COL_ACTION_DEFAULT = 'insert'

def cli_arg_parser():
    
    description = 'CSVU Update updates FILE0 with records from FILE1.'

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
            required=True,
            help='''The key column name.''',
        )

    parser.add_argument(
            '--extra-row-action',
            choices=EXTRA_ROW_ACTIONS,
            default=EXTRA_ROW_ACTION_DEFAULT,
            help='''The action to take if extra rows are found in FILE1.''',
        )

    parser.add_argument(
            '--extra-col-action',
            choices=EXTRA_COL_ACTIONS,
            default=EXTRA_COL_ACTION_DEFAULT,
            help='''The action to take if extra cols are found in FILE1.''',
        )

    return parser

def filter_d(row0_g, row1_g, fieldnames0, fieldnames1, keyname, 
                    extra_row_action=EXTRA_ROW_ACTION_DEFAULT,
                    extra_col_action=EXTRA_COL_ACTION_DEFAULT,
                ):

    fieldnames2 = copy(fieldnames0)

    fn0 = set(fieldnames0)
    fn1 = set(fieldnames1)

    fnd10 = fn1 - fn0

    if fnd10:
        if extra_col_action == 'die':
            extras = [c for c in fieldnames1 if c in fnd10]
            raise Exception('Unexpected columns in FILE1: {}'.format(extras))
        elif extra_col_action == 'ignore':
            pass
        elif extra_col_action == 'insert':
            fieldnames2.extend(fn for fn in fieldnames1 if fn in fnd10)
        else:
            raise Exception('Unknown extra_col_action: {}'.format(extra_col_action))

    def g():

        s0 = sorted(row0_g, key=itemgetter(keyname))
        s1 = sorted(row1_g, key=itemgetter(keyname))

        g0 = iter(s0)
        g1 = iter(s1)

        row0 = next(g0)
        row1 = next(g1)

        def k(x):
            return x[keyname]

        while True:
            # Find the next row to update.
            while k(row0) < k(row1):
                row0 = next(g0)
            while k(row0) > k(row1):
                if extra_row_action == 'die':
                    raise Exception('Unexpected row in FILE1: {}'.format(row1))
                elif extra_row_action == 'ignore':
                    pass
                row1 = next(g1)
            if k(row0) == k(row1):
                row0.update({k: v for k, v in row1.iteritems() if k in fieldnames2})
            yield row0
            row0 = next(g0)

    return {'fieldnames': fieldnames2, 'generator': g()}
            
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
                        extra_row_action=args.extra_row_action,
                        extra_col_action=args.extra_col_action,
                    )

        g           = d['generator']
        fieldnames2 = d['fieldnames']

        dialect2 = args.dialect2

        if dialect2 == 'dialect0':
            dialect2 = dialect0
        elif dialect2 == 'dialect1':
            dialect2 = dialect1

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

