#!/usr/bin/env python

from __future__ import with_statement

# http://docs.python.org/distutils/
# http://packages.python.org/distribute/
try:
    from setuptools import setup
except:
    from distutils.core import setup

import os.path

version_py = os.path.join(os.path.dirname(__file__), 'lantz_drivers', 'version.py')
with open(version_py, 'r') as f:
    d = dict()
    exec(f.read(), d)
    version = d['__version__']

setup(
    name = 'lantz_drivers',
    description = 'Instrumentation framework',
    version = version,
    long_description = '''Lantz is an automation and instrumentation toolkit
with a clean, well-designed and consistent interface. It provides a core of
commonly used functionalities for building applications that communicate with
scientific instruments allowing rapid application prototyping, development and
testing. Lantz benefits from Python's extensive library flexibility as a glue
language to wrap existing drivers and DLLs.''',
    author = 'Lantz Developers',
    author_email = 'labpy@googlegroups.com',
    url = 'http://github.com/LabPy/lantz_drivers',
    download_url = 'http://github.com/LabPy/lantz_drivers/tarball/master',
    keywords = 'instrument control frameork measurement science',
    license = 'BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Networking',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
        ],
    packages = ['lantz_drivers'],
    requires = ['lantz_core'],
)

