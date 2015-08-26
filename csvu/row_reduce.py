
from copy import copy
from functools import partial
import importlib
import os
import sys
import traceback

from csvu import (
        reader_make,
        writer_make,
    )
from csvu.cli import (
        default_arg_parser,
        positive_int,
    )
from csvu.util import equal0

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

def filter_g(row_g, fieldnames, reductions, coercions=None, formats=None, N=10, debug=False):

    equal0_ = equal0 

    if coercions:
        equal0_ = getattr(coercions, 'equal0', equal0)
        if not callable(equal0_):
            raise Exception('Found a non-callable object named :equal0: in :coercions:')

    def gimme_None(x):
        return None

    for row in row_g:

        if coercions:
            implicit_f = getattr(coercions, 'implicit_f', None)
            if implicit_f is None:
                implicit_f = gimme_None
            elif callable(implicit_f):
                pass
            else:
                raise Exception('Found a non-callable object named :implicit_f: in :coercions:')
            for fn in fieldnames:
                explicit = getattr(coercions, fn, None)
                implicit = implicit_f(fn)
                if explicit is None or callable(explicit):
                    pass
                else:
                    raise Exception('Found a non-callable object named :{}: in :coercions:'.format(fn))
                if implicit is None or callable(implicit):
                    pass
                else:
                    raise Exception('Found a non-callable object named :{}: in :coercions.implicit_f:'.format(fn))
                f = explicit or implicit
                if not callable(f):
                    continue
                try:
                    row[fn] = f(row[fn])
                except Exception as exc:
                    m = "row[{}] = {} could not be coerced: {}".format(fn, row[fn], exc)
                    raise Exception(m)

        implicit_f = getattr(reductions, 'implicit', None)
        if implicit_f is None:
            implicit_f = gimme_None
        elif callable(implicit_f):
            pass
        else:
            raise Exception('Found a non-callable object named :implicit_f: in :reductions:')
        for fn in fieldnames:
            explicit = getattr(reductions, fn, None)
            implicit = implicit_f(fn)
            if explicit is None or callable(explicit):
                pass
            else:
                raise Exception('Found a non-callable object named :{}: in :reductions:'.format(fn))
            if implicit is None or callable(implicit):
                pass
            else:
                raise Exception('Found a non-callable object named :{}: in :reductions.implicit_f:'.format(fn))
            f = explicit or implicit
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
            implicit_f = getattr(formats, 'implicit_f', None)
            if implicit_f is None:
                implicit_f = gimme_None
            elif callable(implicit_f):
                pass
            else:
                raise Exception('Found a non-callable object named :implicit_f: in :formats:')
            for fn in fieldnames:
                explicit = getattr(formats, fn, None)
                implicit = implicit_f(fn)
                if explicit is None or callable(explicit):
                    pass
                else:
                    raise Exception('Found a non-callable object named :{}: in :formats:'.format(fn))
                if implicit is None or callable(implicit):
                    pass
                else:
                    raise Exception('Found a non-callable object named :{}: in :formats.implicit_f:'.format(fn))
                f = explicit or implicit
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
        except ImportError:
            coercions = None

        try:
            formats = importlib.import_module(args.formats)
        except ImportError:
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
                        debug=args.debug,
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

