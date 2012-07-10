# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

description = 'An object oriented approach to visualization of 1D to 4D data.'
long_description = """
Visvis is a pure Python library for visualization of 1D to 4D
data in an object oriented way. Essentially, visvis is an object
oriented layer of Python on top of OpenGl, thereby combining the
power of OpenGl with the usability of Python. A Matlab-like
interface in the form of a set of functions allows easy creation 
of objects (e.g. plot(), imshow(), volshow(), surf()). 

"""

from distutils.core import setup

# Get version
__version__ = None
for line in file('__init__.py').readlines():
    if (line.startswith('__version__')):
        exec(line.strip())


setup(
    name = 'visvis',
    version = __version__,
    author = 'Almar Klein',
    author_email = 'almar.klein at gmail',
    license = '(new) BSD',
    
    url = 'http://code.google.com/p/visvis/',
    download_url = 'http://code.google.com/p/visvis/downloads/list',    
    keywords = "visualization OpenGl medical imaging 3D plotting numpy",
    description = description,
    long_description = long_description,
    
    platforms = 'any',
    provides = ['visvis'],
    requires = ['numpy', 'pyOpenGl'],
    
    packages = ['visvis', 'visvis.functions', 'visvis.backends', 
                'visvis.processing', 'visvis.vvmovie', 'visvis.io',
                'visvis.core', 'visvis.wibjects', 'visvis.wobjects'],
    package_dir = {'visvis': '.'},
    package_data = {'visvis': [ 'examples/*.py', 'visvisResources/*']},
    zip_safe = False, # I want examples to work
    )

# Note that the dir in package_dir must NOT be an empty string! This
# would work for distutils, but not for setuptools...
# I found this on-line doc very helpful for creating a setup script:
# http://docs.python.org/distutils/examples.html
