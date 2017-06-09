"""
Repoman
-------
Repoman is a collection of utilities for managing
individual software packages for the Fermi Gamma-Ray
Space telescope.

Links
`````
* `GitHub <http://github.com/fermi-lat/repoman/>`_
* `development version
  <https://github.com/fermi-lat/repoman/zipball/master#egg=repoman-dev>`_
"""

import re
import ast
from setuptools import setup, find_packages

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('repoman/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='fermi-repoman',
    version=version,
    packages=find_packages(),
    url='http://github.com/fermi-lat/repoman',
    license='Modified BSD',
    author='Brian Van Klaveren',
    author_email='bvan@slac.stanford.edu',
    description='A collection of utilities for managing '
                'individual software packages for the Fermi Gamma-Ray Space '
                'telescope',
    long_description=__doc__,
    entry_points={
        'console_scripts': ['repoman = repoman.cli:cli'],
    },
    install_requires=[
        'gitpython',
        'click'
    ],
    classifiers=[
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5'
    ],
    zip_safe=True
)
