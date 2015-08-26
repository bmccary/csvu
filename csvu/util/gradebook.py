
from itertools import izip

LETTER         = [ 'F',          'D',                 'C',                 'B',                 'A', ]
LETTER_CUTS    = [             60.00,               70.00,               80.00,               90.00, ]

LETTER_PM      = [ 'F',  'D-',   'D',  'D+',  'C-',   'C',  'C+',  'B-',   'B',  'B+',  'A-',   'A',  'A+', ]
LETTER_CUTS_PM = [      60.00, 63.33, 66.66, 70.00, 73.33, 76.66, 80.00, 83.33, 86.66, 90.00, 93.33, 96.66, ]

def toletter(grade, cuts=LETTER_CUTS_PM):

    if type(cuts) != list:
        raise Exception("Bad cuts: " + str(cuts))

    L = None

    if len(cuts) == len(LETTER) - 1:
        L = LETTER
    elif len(cuts) == len(LETTER_PM) - 1:
        L = LETTER_PM
    else:
        raise Exception("Bad cuts: " + str(cuts))

    for c, l in izip(cuts, L):
        if grade < c:
            return l

    return L[-1]

_gpa_d = {
    "A+": 4.000,
    "A" : 4.000,
    "A-": 3.670,
    "B+": 3.330,
    "B" : 3.000,
    "B-": 2.670,
    "C+": 2.330,
    "C" : 2.000,
    "C-": 1.670,
    "D+": 1.330,
    "D" : 1.000,
    "D-": 0.670,
    "F" : 0.000,
    "NF": 0.000,
            }

def togpa(grade):
    v = _gpa_d.get(grade)
    if v is None:
        raise Exception("Unknown grade: {}".format(grade))
    return v

