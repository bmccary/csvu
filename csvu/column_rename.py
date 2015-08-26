
import traceback

from csvu import (
        reader_make,
        writer_make,
    )

from csvu.cli import default_arg_parser

def cli_arg_parser():

    description = 'CSVU column rename will rename columns.'

    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    dialect1='output',
                )

    parser.add_argument(
            '--rename',
            metavar=('from', 'to'),
            type=str,
            nargs=2,
            action='append',
            required=True,
            help='Rename *from* to *to*.',
        )

    return parser

def filter_d(row_g, fieldnames, renames):

    for from_, to in renames:
        if from_ not in fieldnames:
            raise Exception('*from* not found: {}'.format(from_))
        if from_ == to:
            raise Exception('*from* == *to*, abort: {} == {}'.format(from_, to))

    renames_d = {k: v for k, v in renames}
    fieldnames1 = [renames_d.get(k, k) for k in fieldnames]
    fieldnames1_set = set()
    for fn in fieldnames1:
        if fn in fieldnames1_set:
            raise Exception('Rename would result in a duplicate column: {}'.format(fn))
        fieldnames1_set.add(fn)

    def g():
        for row in row_g:
            yield {renames_d.get(k, k): v for k, v in row.iteritems()}

    return {'fieldnames': fieldnames1, 'generator': g()}

def cli():

    parser = cli_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        d = filter_d(
                        row_g=reader_g,
                        fieldnames=fieldnames,
                        renames=args.rename,
                    )

        fieldnames1 = d['fieldnames']
        filter_g    = d['generator']

        dialect1 = args.dialect1

        if dialect1 == 'dialect0':
            dialect1 = dialect0

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        fieldnames=fieldnames1,
                    )

        writer_f(filter_g)

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)

