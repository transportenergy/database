#!/usr/bin/env python
from os import walk
from pathlib import Path

from setuptools import setup, find_packages


MAJOR = 0
MINOR = 1
MICRO = 0
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

DISTNAME = 'item'
AUTHOR = 'International Transport Energy Modeling group'
AUTHOR_EMAIL = 'mail@transportenergy.org'
URL = 'https://github.com/transportenergy/database'
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Operating System :: OS Independent',
    'Intended Audience :: Science/Research',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Scientific/Engineering',
    ]

INSTALL_REQUIRES = [
    'click >= 0.6',
    'pandas >= 0.20',
    'pint >= 0.8',
    'plotnine >= 0.1',
    'pycountry >= 17.5',
    'pyyaml >= 3.12',
    'xarray >= 0.9',
    ]
TESTS_REQUIRE = ['pytest >= 2.7']
EXTRAS_REQUIRE = {
    'doc': ['sphinx', 'sphinx-rtd-theme', 'numpydoc'],
    'hist': ['requests', 'requests-cache'],
    'tests': ['pytest'],
    'eppa': ['gdx >= 3'],
    }

DESCRIPTION = "Transportation energy projections database"
LONG_DESCRIPTION = """
*iTEM* provides an interface to two databases maintained by the
`International Transport Energy Modeling group`_:

1. A database of projections from international models of transportation and
   its energy demand, and
2. A database of primary and derived transport statistics.

.. _International Transport Energy Modeling group: https://transportenergy.org

"""


def list_files(*parts):
    """Walk the path specified by *parts* for package data files."""
    paths = []
    for dirpath, _, filenames in walk(Path(*parts), followlinks=True):
        paths.extend(Path(dirpath) / filename for filename in filenames)
    return paths


setup(name=DISTNAME,
      version=VERSION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      classifiers=CLASSIFIERS,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      install_requires=INSTALL_REQUIRES,
      tests_require=TESTS_REQUIRE,
      extras_require=EXTRAS_REQUIRE,
      url=URL,
      packages=find_packages(),
      package_data={'item': list_files('item', 'data')},
      )
