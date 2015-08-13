
import importlib
from itertools import izip
import os
import sys
import traceback

from csvu import (
        reader_make,
        writer_make,
    )
from csvu.cli import default_arg_parser
from csvu.util import (
        equal0,
        isna,
        K_NASTRINGs,
    )

def cli_arg_parser():
    
    description = 'CSVU diff computes the diff between two CSV files.'

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
            help='''The key column name, if any.''',
        )
    parser.add_argument(
            '--compact',
            default=False,
            action='store_true',
            help='''Omit empty rows/cols.''',
        )
    parser.add_argument(
            '--coercions', 
            type=str,
            default='coercions',
            help='''The file from which to get coercions.'''
        )
    parser.add_argument(
            '--nastrings', 
            nargs='*',
            default=K_NASTRINGs,
            help='Values which get converted to *None* prior to diffing.'
        )
    return parser

def filter_d(row0_g, row1_g, fieldnames0, fieldnames1, keyname=None, compact=False, coercions=None, nastrings=K_NASTRINGs):

    fieldnames0_set = set(fieldnames0)
    fieldnames1_set = set(fieldnames1)

    if not fieldnames0_set.issubset(fieldnames1_set):
        raise Exception("SET0 is not a subset of SET1, abort!")

    if keyname:
        if not keyname in fieldnames0_set:
            raise Exception("keyname '{}' is not in SET0.".format(keyname))
        if not keyname in fieldnames1_set:
            raise Exception("keyname '{}' is not in SET1.".format(keyname))

    equal0_ = equal0 
    isna_   = isna

    if coercions:
        equal0_ = getattr(coercions, 'equal0', equal0)
        isna_   = getattr(coercions, 'isna', isna)

    def diff_g1():
        for row0, row1 in izip(row0_g, row1_g):
            if keyname:
                v0 = row0[keyname]
                v1 = row1[keyname]
                if v0 != v1:
                    raise Exception("Difference in key column, cannot diff: {} != {}".format(v0, v1))
            for fn in fieldnames1:
                if fn == keyname:
                    continue
                v0 = row0.get(fn)
                v1 = row1.get(fn)
                if False:
                    f = getattr(coercions, fn, None)
                    if callable(f):
                        try:
                            v0 = f(v0)
                        except Exception as exc:
                            raise Exception("file0 row[{fn}] = {} is invalid/uncoercable: {}".format(fn, v0, exc))
                        try:
                            v1 = f(v1)
                        except Exception as exc:
                            raise Exception("file1 row[{fn}] = {} is invalid/uncoercable: {}".format(fn, v1, exc))
                    if equal0_(v0, v1):
                        row1[fn] = None
                else:
                    if v0 == v1:
                        row1[fn] = None
            yield row1

    def diff_d1():
        rows = [row for row in diff_g1() if any(row[fn] for fn in fieldnames1 if fn != keyname)]
        keeps = []
        for fn in fieldnames1:
            if fn == keyname:
                keeps.append(fn)
            elif any(row[fn] for row in rows):
                keeps.append(fn)

        def diff_g2():
            for row in rows:
                yield {fn: row[fn] for fn in keeps}

        return {'fieldnames': keeps, 'generator': diff_g2()}

    if compact:
        return diff_d1()

    return {'fieldnames': fieldnames1, 'generator': diff_g1()}

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

        sys.path.append(os.getcwd())

        coercions = importlib.import_module(args.coercions)

        d = filter_d(
                            row0_g=reader0_g,
                            row1_g=reader1_g,
                            fieldnames0=fieldnames0,
                            fieldnames1=fieldnames1,
                            keyname=args.keyname,
                            compact=args.compact,
                            coercions=coercions,
                            nastrings=args.nastrings,
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

