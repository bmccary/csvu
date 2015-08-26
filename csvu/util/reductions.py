
from functools import partial
from itertools import izip

def sum_XX_YY(XX, YY, N, s_m_n_f='{}_{:02d}', denom=1.0):
    s_m   = '{}_{:02d}'.format(XX, YY)
    s_m_o = '{}_override'.format(s_m)
    s_m_p = '{}_penalty'.format(s_m)
    s_m_n = [s_m_n_f.format(s_m, n + 1) for n in xrange(N)]

    def f(row, ALL=[], denom=denom):

        o = row.get(s_m_o)
        if not isna(o):
            return o

        v = sum0([row.get(k) for k in s_m_n])
        if isna(v):
            if s_m in ALL:
                v = K_MISSED
            return v

        p = row.get(s_m_p)
        if isnum(p):
            v = max(v - p, 0)

        return v/denom

    return s_m, f

def X_all(row, ALL): 
    return [row[k] for k in ALL if not isexempt(row[k])]

def X_grade(row, ALL, DROPS, DENOM):
    m = mean0(drop0(X_all(row, ALL), DROPS))
    if not isnum(m):
        return 'None'
    return m/DENOM*100.0

def X_misses_g(row, ALL): 
    return (k for k in ALL if ismissed(row[k]))

def X_misses(row, ALL):
    def bb9_sucks(x):
        return str(int(x[-2:]))
    return ','.join(bb9_sucks(x) for x in X_misses_g(row, ALL))

def X_misses_count(row, ALL): 
    return sum(1 for x in X_misses_g(row, ALL))

def X_misses_percent(row, ALL, DROPS):
    N = len(X_all(row, ALL))
    if N <= DROPS:
        return None
    M = max(X_misses_count(row, ALL) - DROPS, 0)
    return float(M)/N*100.0

LETTER         = [ 'F',          'D',                 'C',                 'B',                 'A', ]
LETTER_CUTS    = [             60.00,               70.00,               80.00,               90.00, ]
LETTER_PM      = [ 'F',  'D-',   'D',  'D+',  'C-',   'C',  'C+',  'B-',   'B',  'B+',  'A-',   'A',  'A+', ]
LETTER_CUTS_PM = [      60.00, 63.33, 66.66, 70.00, 73.33, 76.66, 80.00, 83.33, 86.66, 90.00, 93.33, 96.66, ]

def letterize(grade, cuts=LETTER_CUTS_PM):

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

def gpaize(grade):
    v = _gpa_d.get(grade)
    if v is None:
        raise Exception("Unknown grade: {}".format(grade))
    return v

def donothing(row):
    return None

