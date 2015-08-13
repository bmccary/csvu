
from csv import Sniffer
import sys
import traceback
from prettytable import PrettyTable

from csvu import DELIMITERS
from csvu.cli import (
        default_arg_parser,
        positive_int,
    )

def cli_arg_parser():

    description = 'CSVU sniff will determine the dialect of a CSV file.'
    parser = default_arg_parser(
                    description=description,
                    file0='input',
                )

    parser.add_argument(
            '--N', 
            type=positive_int, 
            default=1024,
            help='The number of characters to use in the sniff.'
        )

    return parser

def cli():

    parser = cli_arg_parser()

    args = parser.parse_args()

    try:

        f = sys.stdin

        if args.file0 != '-':
            f = open(args.file0, 'r')

        sample = f.read(args.N)

        dialect = Sniffer().sniff(sample, delimiters=DELIMITERS)

        v = vars(dialect)

        x = PrettyTable(header=False)
        for k, v in vars(dialect).iteritems():
            if not k.startswith('_'):
                x.add_row([k, repr(v)])

        print x

    except Exception as exc:

        m = traceback.format_exc()
        parser.error(m)



