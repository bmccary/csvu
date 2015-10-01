
from copy import copy
from operator import itemgetter
from pyxdameraulevenshtein import damerau_levenshtein_distance
import traceback

from csvu import (
        reader_make,
        writer_make,
    )
from csvu.cli import default_arg_parser

def cli_arg_parser():
    
    description = 'CSVU Levenshtein computes the edit distance from a given string to the strings in a column'

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
            required=True,
            help='''The column being scored''',
        )

    parser.add_argument(
            '--target',
            default=None,
            required=True,
            help='''The column to insert the score into''',
        )

    parser.add_argument(
            '--sort',
            choices=['ascending', 'descending', 'none'],
            default='ascending',
            help='''How to sort the rows by score''',
        )

    parser.add_argument(
            'string',
            default=None,
            help='''The string to score''',
        )
    
    return parser

def filter_d(row_g, fieldnames, column, target, sort, string, debug=False):

    fieldnames1 = copy(fieldnames)

    if not target in fieldnames1:
        fieldnames1.append(target)

    def score_g():
        for row in row_g:
            row[target] = damerau_levenshtein_distance(row[column], string)
            yield row

    def sort_asc_g():
        return sorted(score_g(), key=itemgetter(target))

    def sort_dec_g():
        return sorted(score_g(), key=itemgetter(target), reverse=True)

    d = {
            'ascending' : sort_asc_g,
            'descending': sort_dec_g,
            'none'      : score_g,
        }

    g = d[sort]

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
                        sort=args.sort,
                        string=args.string,
                        debug=args.debug,
                    )

        g           = d['generator']
        fieldnames1 = d['fieldnames']

        if args.debug:
            pprint(fieldnames0)
            pprint(fieldnames1)

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

