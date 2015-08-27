
from setuptools import setup

setup(
        name='csvu',
        version='0.9',
        description='CSV Utilities for the Command Line',
        url='http://github.com/bmccary/csvu',
        author='Brady McCary',
        author_email='brady.mccary@gmail.com',
        license='MIT',
        packages=['csvu'],
        install_requires=[
                'openpyxl',
                'PrettyTable',
                'pyxdameraulevenshtein',
            ],
        scripts=[
                    'bin/csvu-cat',
                    'bin/csvu-column-rename',
                    'bin/csvu-cut',
                    'bin/csvu-dialect',
                    'bin/csvu-diff',
                    'bin/csvu-grep',
                    'bin/csvu-head',
                    'bin/csvu-levenshtein',
                    'bin/csvu-pretty',
                    'bin/csvu-put',
                    'bin/csvu-rank',
                    'bin/csvu-row-reduce',
                    'bin/csvu-sniff',
                    'bin/csvu-sort',
                    'bin/csvu-tail',
                    'bin/csvu-tr',
                    'bin/csvu-transpose',
                    'bin/csvu-update',
                    'bin/csvu-xlsx-to-csv',
                ],
        zip_safe=False
    )
