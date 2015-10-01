
from cStringIO import StringIO
from csv import excel, reader, DictReader, DictWriter, Sniffer
import sys
from itertools import izip
from prettytable import PrettyTable

DELIMITERS = ',\t|'

def reader_make(file_or_path='-', dialect='sniff', headless=False):
    """
    Make a reader for CSV files.

    :param file_or_name: 
        The file to read from. Default is '-', which denotes STDIN.
        Can be path to a file or a file-like object.

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

    if file_or_name == '-':
        f = sys.stdin
    elif isinstance(file_or_name, basestring):
        f = open(file_or_name, 'r')
    else:
        f = file_or_name

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

def writer_make(fieldnames, file_or_path='-', dialect='excel', headless=False):

    #
    # File
    #

    if file_or_name == '-':
        f = sys.stdout
    elif isinstance(file_or_name, basestring):
        f = open(file_or_name, 'w')
    else:
        f = file_or_name

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

