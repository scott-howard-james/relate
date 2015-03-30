"""Distutils file for relate"""

from src import __version__

setup(
    name         = 'relate',
    version      = __version__,
    description  = 'Discrete mathematical relation',
    url          = 'http://vmlaker.github.io/mpipe',
    author       = 'Scott Howard James',
    author_email = 'scott.analysis.james@gmail.com',
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
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )
