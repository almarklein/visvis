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

""" Package visvis

Visvis is a pure Python library for visualization of 1D to 4D data in an
object oriented way. Essentially, visvis is an object oriented layer of
Python on top of OpenGl, thereby combining the power of OpenGl with the
usability of Python. A Matlab-like interface in the form of a set of
functions allows easy creation of objects (e.g. plot(), imshow(), volshow(), 
surf()). 

With visvis a range of different data can be visualized by simply adding
world objects to a scene (or axes). These world objects can be anything
from plots (lines with markers), to images, 3D rendered volumes, 
shaded meshes, or you can program your own world object class. If required, 
these data can also be moved in time.

Visvis can be used in Python scripts, interactive Python sessions (as
with IPython or IEP) and can be embedded in applications.

Requirements:
  * Numpy
  * PyOpengl
  * A backend GUI toolkit (PyQt4, wxPython, fltk)
  * (optionally, to enable reading and writing of images) PIL

usage:
import visvis as vv

All wobjects, wibjects and functions are present in the visvis 
namespace. For clean lists, see vv.wibjects, vv.wobjects, or vv.functions, 
respectively.

For more help, see ...
  * the docstrings
  * the examples in the examples dir
  * the examples at the bottom of the function modules (in the functions dir)
  * the online docs: http://code.google.com/p/visvis/

"""

__version__  = '1.3.1' 

import os, sys, time

from constants import *
from events import Timer
from misc import Range
from misc import (Transform_Translate, Transform_Scale, Transform_Rotate)
import vvmovie

from polygonalModeling import BaseMesh
from pypoints import Point, Pointset, Aarray, Quaternion

import cm
L = locals()
for key in cm.colormaps:
  key2 = 'CM_' + key.upper()
  L[key2] = cm.colormaps[key]
del L, key

from wibjects import *
from wobjects import *

# do this last
import backends

from functions import *

# clean up namespace (dont clear modules, that only leads to weird bugs)
del os, sys, time
