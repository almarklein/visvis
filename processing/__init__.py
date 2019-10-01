# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Package visvis.processing

Each module in this directory contains a function with the same
name as the module it's in. These functions are automatically loaded
in Visvis, thus making it easy to expand Visvis' functionality.

In the future, I may make it possible to supply a cython implementation
of a function (along side a pure Python one implementation), so that
after running a compile script, the function will run much faster.
As for now, I'm ok with processing whole arrays at once using numpy.
(I'm not sure, for example, whether calculateNormals can be made faster
in Cython.)

There are three things to take into account when making a new function:
- The function to add should be the same name as the module in which
  it is defined. Other helper functions or classes can be defined, but
  these are not inserted in the Visvis namespace.
- The function's docstring should be very descriptive and starting with
  the function's signature. The docstring is also used to produce the
  on-line documentation.

"""

import os
import sys
import zipfile

from visvis.core.misc import splitPathInZip


def _insertFunctions():

    # see which files we have
    if hasattr(sys, '_MEIPASS'):  # PyInstaller
        zipfilename, path = sys.executable, ""
    else:
        path = __file__
        path = os.path.dirname( os.path.abspath(path) )
        zipfilename, path = splitPathInZip(path)

    if zipfilename:
        # get list of files from zipfile
        z = zipfile.ZipFile(zipfilename)
        files = [os.path.split(i)[1] for i in z.namelist()
                    if i.startswith('visvis') and i.count('processing')]
    else:
        # get list of files from file system
        files = os.listdir(path)

    # extract all functions
    names = []
    for file in files:
        # not this file
        if file.startswith('_'):
            continue
        # only python files
        if file.endswith('.pyc'):
            if file[:-1] in files:
                continue # only try import once
        elif not file.endswith('.py'):
            continue
        # build name
        funname = os.path.splitext(file)[0]
        # import module
        mod = __import__("visvis.processing."+funname, fromlist=[funname])
        if not hasattr(mod,funname):
            print("module %s does not have a function with the same name!" % funname)
        else:
            # insert into THIS namespace
            g = globals()
            g[funname] = mod.__dict__[funname]
            names.append(funname)

    return names


# do it and clean up
_functionNames = _insertFunctions()
