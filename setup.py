
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
                'openpyxl', # To open XLSX
            ],
        scripts=[
                    'bin/csvu-grep',
                    'bin/csvu-get',
                    'bin/csvu-tr',
                    'bin/csvu-sniff',
                    'bin/csvu-sort',
                    'bin/csvu-xlsx-to-csv',
                ],
        zip_safe=False
    )
