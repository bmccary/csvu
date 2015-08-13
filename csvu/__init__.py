
from cStringIO import StringIO
from csv import excel, reader, DictReader, DictWriter, Sniffer
import sys
from itertools import izip
from prettytable import PrettyTable

DELIMITERS = ',\t|'

def reader_make(fname='-', dialect='sniff', headless=False):
    """
    Make a reader for CSV files.

    :param fname: 
        The file to read from. Default is '-', which denotes STDIN.

    :param dialect: 
        The CSV dialect. Default is 'sniff', which (usually) automatically
        detects the dialect. However, 'sniff' will load the entire CSV
        file into memory, which may be unsuitable. Options are 'sniff', 
        'excel', 'excel-tab', or any Dialect object from the python
        csv module.

    :param headless:
        Whether or not CSV is headless. Default is False. When CSV has
        a header, column names are the values in the first row. When
        CSV is headless, column names are integers 0, 1, 2, et cetera.

    """

    #
    # File
    #

    f = sys.stdin

    if fname != '-':
        f = open(fname, 'r')

    #
    # Dialect
    #

    if dialect == 'sniff':
        # read the entire file into memory.
        f = StringIO(f.read())
        sample = f.read()
        f.reset()
        try:
            dialect = Sniffer().sniff(sample, delimiters=DELIMITERS)
        except:
            dialect = excel

    #
    # Reader
    #

    if headless:
        r = reader(f, dialect=dialect)
        row0 = r.next()
        fieldnames = [str(i) for i, x in enumerate(row0)]
        def gen():
            yield {fn: x for fn, x in izip(fieldnames, row0)}
            for row in r:
                yield {fn: x for fn, x in izip(fieldnames, row)}
        return {'dialect': dialect, 'fieldnames': fieldnames, 'reader': gen()}
    else:
        r = DictReader(f, dialect=dialect)
        fieldnames = r.fieldnames
        def gen():
            for row in r:
                yield row
        return {'dialect': dialect, 'fieldnames': fieldnames, 'reader': gen()}

def writer_make(fieldnames, fname='-', dialect='excel', headless=False):

    #
    # File
    #

    f = sys.stdout

    if fname != '-':
        f = open(fname, 'w')

    #
    # Writer
    #

    if dialect == 'pretty':
        def wf(gen):

            w = None

            if headless:
                w = PrettyTable(header=False)
            else:
                w = PrettyTable(fieldnames)

            for row in gen:
                w.add_row([row[fn] for fn in fieldnames])

            w.align = 'l'

            f.write(w.get_string()) 
            f.write('\n')

        return wf
    else:
        def wf(gen):
            w = DictWriter(f, dialect=dialect, fieldnames=fieldnames)
            if not headless:
                w.writeheader()
            w.writerows(row for row in gen)

        return wf

