
from copy import copy
from functools import partial
import importlib
import os
import sys
import traceback

from csvu import (
        equal0,
        isna,
        default_arg_parser,
        positive_int,
        reader_make,
        writer_make,
    )

def cli_arg_parser():

    description = 'CSVU row-reduce repeatedly applies a module of row functions.'

    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                )

    parser.add_argument(
            '--reductions', 
            type=str,
            default='reductions',
            help='''The file from which to get reductions.'''
        )

    parser.add_argument(
            '--coercions', 
            type=str,
            default='coercions',
            help='''The file from which to get coercions.'''
        )

    parser.add_argument(
            '--formats', 
            type=str,
            default='formats',
            help='''The file from which to get formats.'''
        )

    parser.add_argument(
            '--N',
            default=10,
            type=positive_int,
            help='''The number of iterations to attempt per row.'''
        )

    return parser

def filter_g(row_g, fieldnames, reductions, coercions=None, formats=None, N=10):

    equal0_ = equal0 

    if coercions:
        isna_   = getattr(coercions, 'isna', isna)
        equal0_ = getattr(coercions, 'equal0', equal0)
        equal0_ = partial(equal0_, isna=isna_)

    for row in row_g:

        if coercions:
            for fn in fieldnames:
                f = getattr(coercions, fn, None)
                if not callable(f):
                    continue
                try:
                    row[fn] = f(row[fn])
                except Exception as exc:
                    m = "row[{}] = {} could not be coerced: {}".format(fn, row[fn], exc)
                    raise Exception(m)

        for fn in fieldnames:
            f = getattr(reductions, fn, None)
            if not callable(f):
                continue
            try:
                for i in xrange(N):
                    v0 = row[fn]
                    v1 = f(row)
                    row[fn] = v1
                    if equal0_(v0, v1):
                        break
            except Exception as exc:
                m = "row[{}] = {} could not be reduced: {}".format(fn, row[fn], exc)
                raise Exception(m)

        if formats:
            for fn in fieldnames:
                f = getattr(formats, fn, None)
                if not callable(f):
                    continue
                try:
                    row[fn] = f(row[fn])
                except Exception as exc:
                    m = "row[{}] = {} could not be formatted: {}".format(fn, row[fn], exc)
                    raise Exception(m)

        yield row
            
def cli():

    parser = cli_arg_parser()

    args = parser.parse_args()

    try:

        #
        # CSV reader.
        #

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        #
        # Modules.
        #

        sys.path.append(os.getcwd())

        try:
            coercions = importlib.import_module(args.coercions)
        except:
            coercions = None

        try:
            formats = importlib.import_module(args.formats)
        except:
            formats = None

        reductions = importlib.import_module(args.reductions)
            

        #
        # Filter.
        #

        g = filter_g(
                        row_g=reader_g,
                        fieldnames=fieldnames,
                        coercions=coercions,
                        reductions=reductions,
                        formats=formats,
                    )

        #
        # CSV writer.
        #

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        fieldnames=fieldnames,
                    )

        writer_f(g)
                        
    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

