# -*- coding: utf-8 -*-
# Copyright (C) 2015, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Steps to do a new release:

Preparations:
  * Test on Windows, Linux, Mac
  * Test on a machine with OpenGl v1.1 (e.g. winXP virtual machine)
  * Make release notes
  * Update API documentation and other docs that need updating.

Test installation:
  * clear the build and dist dir (if they exist)
  * python setup.py register -r http://testpypi.python.org/pypi
  * python setup.py sdist upload -r http://testpypi.python.org/pypi
  * pip install -i http://testpypi.python.org/pypi

Define the version:
  * update __version__ in __init__.py
  * Tag the tip changeset as version x.x

Generate and upload package (preferably on Windows)
  * python setup.py register
  * python setup.py sdist upload

Announcing:
  * It can be worth waiting a day for eager users to report critical bugs
  * Announce in scipy-user, visvis mailing list, G+
  
"""

import os
from distutils.core import setup

name = 'visvis'
description = 'An object oriented approach to visualization of 1D to 4D data.'

# Get version and docstring
__version__ = None
__doc__ = ''
docStatus = 0 # Not started, in progress, done
initFile = os.path.join(os.path.dirname(__file__), '__init__.py')
for line in open(initFile).readlines():
    if (line.startswith('__version__')):
        exec(line.strip())
    elif line.startswith('"""'):
        if docStatus == 0:
            docStatus = 1
            line = line.lstrip('"')
        elif docStatus == 1:
            docStatus = 2
    if docStatus == 1:
        __doc__ += line


setup(
    name = name,
    version = __version__,
    author = 'Almar Klein',
    author_email = 'almar.klein@gmail.com',
    license = '(new) BSD',
    
    url = 'https://github.com/almarklein/visvis',
    keywords = "visualization OpenGl medical imaging 3D plotting numpy",
    description = description,
    long_description = __doc__,
    
    platforms = 'any',
    provides = ['visvis'],
    #install_requires = ['numpy', 'pyOpenGl', 'imageio'], # have imageio be auto-installed by pip?
    install_requires = ['numpy', 'pyOpenGl'],
    
    packages = ['visvis',
                'visvis.functions',
                'visvis.backends',
                'visvis.processing',
                'visvis.vvmovie',
                'visvis.vvio',
                'visvis.core',
                'visvis.wibjects',
                'visvis.wobjects',
                'visvis.text', 'visvis.text.freetype',
                'visvis.utils', 'visvis.utils.ssdf', 'visvis.utils.iso',
               ],
    package_dir = {'visvis': '.'},
    package_data = {'visvis': [ 'examples/*.py', 'visvisResources/*', 'utils/iso/*.pyx']},
    zip_safe = False,
    
    classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'Intended Audience :: Developers',
          'Topic :: Scientific/Engineering :: Visualization',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          ],
    )

# Note that the dir in package_dir must NOT be an empty string! This
# would work for distutils, but not for setuptools...
# I found this on-line doc very helpful for creating a setup script:
# http://docs.python.org/distutils/examples.html
