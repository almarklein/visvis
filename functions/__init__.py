#   This file is part of VISVIS.
#    
#   VISVIS is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as 
#   published by the Free Software Foundation, either version 3 of 
#   the License, or (at your option) any later version.
# 
#   VISVIS is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
# 
#   You should have received a copy of the GNU Lesser General Public 
#   License along with this program.  If not, see 
#   <http://www.gnu.org/licenses/>.
#
#   Copyright (C) 2010 Almar Klein

""" Package visvis.functions

Each module in this directory contains a function with the same
name as the module it's in. These functions are automatically loaded 
in Visvis, thus making it very easy to expand Visvis' functionality.

There are three things to take into account when making a new function:
- The function to add should be the same name as the module in which 
  it is defined. Other helper functions or classes can be defined, but
  these are not inserted in the Visvis namespace.
- The function's docstring should be very descriptive and starting with
  the function's signature. The docstring is also used to produce the
  on-line documentation.


"""

import os

def _insertFunctions():
    
    # see which files we have
    path = __file__
    path = os.path.dirname( os.path.abspath(path) )
    
    # determine if we're in a zipfile
    i = path.find('.zip')
    if i>0:
        # get list of files from zipfile
        path = path[:i+4]
        import zipfile
        z = zipfile.ZipFile(path)
        files = [os.path.split(i)[1] for i in z.namelist() 
                    if i.startswith('visvis') and i.count('functions')]
    else:
        # get list of files from file system
        files = os.listdir(path)
    
    # extract all functions
    names = []
    for file in files:
        # not this file
        if file.startswith('__'):
            continue
        # only python files
        if file.endswith('.pyc'):
            if file[:-1] in files:
                continue # only try import once
        elif not file.endswith('.py'):
            continue    
        # build names
        fullfile = os.path.join(path, file)
        funname = os.path.splitext(file)[0]
        # import module
        mod = __import__("visvis.functions."+funname, fromlist=[funname])
        if not hasattr(mod,funname):
            print "module %s does not have a function with the same name!" % (
                funname)
        else:
            # insert into THIS namespace
            g = globals()
            g[funname] = mod.__dict__[funname]
            names.append(funname)
    
    return names


# do it and clean up
_functionNames = _insertFunctions()
