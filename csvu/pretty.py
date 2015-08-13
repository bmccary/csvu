
import traceback

from csvu import (
        default_arg_parser, 
        reader_make,
        writer_make,
    )

def cli_arg_parser():
    description = 'CSVU pretty pretty-prints a CSV file.'
    parser = default_arg_parser(
                    description=description,
                    file0='input',
                    file1='output',
                    dialect0='input',
                    headless=True,
                )
    return parser

def cli():

    parser = cli_arg_parser()

    args = parser.parse_args()

    try:

        reader_d = reader_make(
                        fname=args.file0,
                        dialect=args.dialect0,
                        headless=args.headless,
                    )

        dialect0   = reader_d['dialect']
        fieldnames = reader_d['fieldnames']
        reader_g   = reader_d['reader']

        dialect1 = 'pretty'

        writer_f = writer_make(
                        fname=args.file1,
                        dialect=dialect1,
                        headless=args.headless,
                        fieldnames=fieldnames,
                    )

        writer_f(reader_g)

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)
        
