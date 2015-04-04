
from setuptools import setup

setup(
        name='csvu',
        version='0.1',
        description='CSV Utilities for the Command Line',
        url='http://github.com/bmccary/csvu',
        author='Brady McCary',
        author_email='brady.mccary@gmail.com',
        license='MIT',
        packages=['csvu'],
        install_requires=[
                'openpyxl',    # To open XLSX
                'PrettyTable', # For printing human-readable CSV on console
            ],
        scripts=[
                    'bin/csvu-column-rename',
                    'bin/csvu-cut',
                    'bin/csvu-dialect',
                    'bin/csvu-diff',
                    'bin/csvu-grep',
                    'bin/csvu-join',
                    'bin/csvu-pretty',
                    'bin/csvu-row-reduce',
                    'bin/csvu-sniff',
                    'bin/csvu-sort',
                    'bin/csvu-tr',
                    'bin/csvu-transpose',
                    'bin/csvu-xlsx-to-csv',
                ],
        zip_safe=False
    )
