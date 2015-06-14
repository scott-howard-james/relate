"""Distutils file for relate"""

from setuptools import setup
from src import __version__

setup(
    name         = 'relate',
    version      = __version__,
    description  = 'Discrete mathematical relation',
    author       = 'Scott Howard James',
    author_email = 'scott.analysis.james@gmail.com',
    url='https://github.com/scott-howard-james/relate.git',
    license      = 'MIT',
    long_description = open('README.rst').read(),
    package_dir  = {'relate' : 'src'},
    packages     = ['relate'],
    classifiers  = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Freeware',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
