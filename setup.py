#!/usr/bin/env python
from os import walk
from pathlib import Path

from setuptools import setup, find_packages


MAJOR = 0
MINOR = 2
MICRO = 0
VERSION = '.'.join(map(str, (MAJOR, MINOR, MICRO, 'dev')))

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
    'Programming Language :: Python :: 3.8',
    'Topic :: Scientific/Engineering',
    ]

INSTALL_REQUIRES = [
    'click',
    'openpyxl',
    'pandas',
    'pandaSDMX >= 1.0b1',
    'pint',
    'plotnine',
    'pycountry',
    'pyyaml',
    'xarray',
    ]
TESTS_REQUIRE = ['pytest']
EXTRAS_REQUIRE = {
    'doc': ['sphinx', 'sphinx-rtd-theme'],
    'hist': ['jupyter', 'nbformat', 'pprint', 'requests', 'requests-cache'],
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
      url=URL,

      install_requires=INSTALL_REQUIRES,
      tests_require=TESTS_REQUIRE,
      extras_require=EXTRAS_REQUIRE,

      packages=find_packages(),
      # package_data={'item': list_files('item', 'data')},
      include_package_data=True,

      entry_points={
        'console_scripts': [
            'item = item.cli:main',
        ]
      },
      )
