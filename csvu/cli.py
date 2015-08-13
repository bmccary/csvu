
import argparse

def positive_int(x):
    try:
        y = int(x)
        if y < 1:
            raise None
        return y
    except:
        m = "Not a positive integer: '{}'".format(x)
        raise argparse.ArgumentTypeError(m)

def nonnegative_int(x):
    try:
        y = int(x)
        if y < 0:
            raise None
        return y
    except:
        m = "Not a nonnegative integer: '{}'".format(x)
        raise argparse.ArgumentTypeError(m)

def default_arg_debug(parser):

    parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='''Use this flag when debugging these scripts.''',
        )

def default_arg_headless(parser):

    parser.add_argument(
            '--headless',
            default=False,
            action='store_true',
            help='''Use this flag if there is no header.''',
        )

def default_arg_dialect0(parser):

    parser.add_argument(
            '--dialect0', 
            default='sniff', 
            choices=['sniff', 'excel', 'excel-tab',],
            help='''The CSV dialect of file0.
                    Option *sniff* detects the dialect, 
                    *excel* dialect uses commas, 
                    *excel-tab* uses tabs.
                    Note that *sniff* will load the
                    entire file into memory, so for large
                    files it may be better to explicitly
                    specify the dialect.
                    '''
        )

def default_arg_dialect1_as_input(parser):

    parser.add_argument(
            '--dialect1', 
            default='sniff', 
            choices=['sniff', 'excel', 'excel-tab',],
            help='''The CSV dialect of file1.
                    Option *sniff* detects the dialect, 
                    *excel* dialect uses commas, 
                    *excel-tab* uses tabs.
                    Note that *sniff* will load the
                    entire file into memory, so for large
                    files it may be better to explicitly
                    specify the dialect.
                    '''
        )

def default_arg_dialect1_as_output(parser):

    parser.add_argument(
            '--dialect1', 
            default='dialect0', 
            choices=['dialect0', 'excel', 'excel-tab', 'pretty',],
            help='''The CSV dialect of the output.
                    Option *dialect0* uses the same dialect as file0,
                    *excel* dialect uses commas, 
                    *excel-tab* uses tabs,
                    *pretty* prints a human-readable table.
                    '''
        )

def default_arg_dialect2(parser):

    parser.add_argument(
            '--dialect2', 
            default='dialect0', 
            choices=['dialect0', 'excel', 'excel-tab', 'pretty',],
            help='''The CSV dialect of the output.
                    Option *dialect0* uses the same dialect as file0,
                    *excel* dialect uses commas, 
                    *excel-tab* uses tabs,
                    *pretty* prints a human-readable table.
                    '''
        )

def default_arg_file0(parser):

    parser.add_argument(
            '--file0', 
            type=str, 
            default='-',
            help='Input CSV file, defaults to STDIN.'
        )

def default_arg_file1_as_input(parser):

    parser.add_argument(
            '--file1', 
            type=str,
            required=True,
            help='Input CSV file.'
        )

def default_arg_file1_as_output(parser):

    parser.add_argument(
            '--file1', 
            type=str, 
            default='-',
            help='Output CSV file, defaults to STDOUT.'
        )

def default_arg_file2(parser):

    parser.add_argument(
            '--file2', 
            type=str, 
            default='-',
            help='Output CSV file, defaults to STDOUT.'
        )

def default_arg_parser(
        description,
        headless=None,
        dialect0=None,
        dialect1=None,
        dialect2=None,
        file0=None,
        file1=None,
        file2=None,
    ):

    parser = argparse.ArgumentParser(
                    description=description,
                    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                )

    if headless:
        default_arg_headless(parser)

    if dialect0:
        default_arg_dialect0(parser)

    if dialect1 is not None:
        if dialect1 == 'input':
            default_arg_dialect1_as_input(parser)
        elif dialect1 == 'output':
            default_arg_dialect1_as_output(parser)
        else:
            raise Exception("Bad dialect1: {}".format(dialect1))

    if dialect2:
        default_arg_dialect2(parser)

    if file0:
        default_arg_file0(parser)

    if file1 is not None:
        if file1 == 'input':
            default_arg_file1_as_input(parser)
        elif file1 == 'output':
            default_arg_file1_as_output(parser)
        else:
            raise Exception("Bad file1: {}".format(dialect1))

    if file2:
        default_arg_file2(parser)

    default_arg_debug(parser)

    return parser

