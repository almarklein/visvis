# -*- coding: utf-8 -*-
# Copyright (c) 2011, Almar Klein

description = 'Simple Structured Data Format.'
long_description = """

Simple Structured Data Format
-----------------------------
Ssdf is a simple format for stroring structured data. It supports
seven data types, two of which are container elements:
None, int, float, (Unicode) string, numpy array, list/tuple, dict/Struct.

One spec, two formats
---------------------
Ssdf is actually two formats: the original text format is human readable,
and thus enables inspecting databases and data structures using a simple
text editor. The binary format is more efficient and uses compression on
the whole file (the text format only compresses arrays). It is more suited
for storing really large databases or structures containing large arrays.
Both formats are fully compatible.

Notes
-----
SSDF comes as a single module. While it's a bit big (approaching 2k lines), 
it enables easier deployment inside a package in a way that works for 
Python 2 as well as Python 3.

"""

from distutils.core import setup

# Get version
for line in file('ssdf.py').readlines():
    if (line.startswith('__version__')):
        exec(line.strip())


setup(
    name = 'ssdf',
    version = __version__,
    author = 'Almar Klein',
    author_email = 'almar.klein at gmail',
    license = 'BSD',
    
    url = 'http://code.google.com/p/ssdf/',
    download_url = 'http://code.google.com/p/ssdf/downloads/list',    
    keywords = "simple structured data fileformat",
    description = description,
    long_description = long_description,
    
    platforms = 'any',
    provides = ['ssdf'],
    requires = [],
    
    py_modules = ['ssdf'],
    
    zip_safe = False, # I want examples to work
    )

# Note that the dir in package_dir must NOT be an empty string! This
# would work for distutils, but not for setuptools...
# I found this on-line doc very helpful for creating a setup script:
# http://docs.python.org/distutils/examples.html

