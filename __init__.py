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
#   Copyright (C) 2009 Almar Klein

""" Package visvis

Visvis is a Python visualization library that uses OpenGl to display
1D to 4D data; it can be used from simple plotting tasks to rendering 
3D volumetric data that moves in time. 

Visvis can be used in Python scripts, interactive Python sessions (as
with IPython or IEP) and can be embedded in applications.

Visvis employs an object oriented structure; each object being 
visualized (e.g. a line or a texture) has various properties that 
can be modified to change its behaviour or appearance. A Matlab-like 
interface in the form of a set of functions allows easy creation of 
these objects (e.g. plot(), imshow(), volshow()). 

Requirements:
  * Numpy
  * PyOpengl
  * A backend GUI toolkit (PyQt4 or wxPython)
  * (optionally, to enable reading and writing of images) PIL

usage:
import visvis as vv

Visvis is an object oriented visualization toolkit. There are two
types of objects that can be visualized: wibjects and wobjects. The
first are 2D objects that reside in a figure, axes or each-other.
In fact the Figure and Axes class are wibjects. Wobjects are objects
that reside in the 3D world inside an axes object. 

All wobjects, wibjects and functions are present in the visvis 
namespace. For clean lists, see vv.wibjects, vv.wobjects, or vv.functions, 
respectively.

For more help, see the docs, the examples in the examples dir, or 
the examples at the bottom of the function modules (in the functions
dir).

$Author$
$Date$
$Rev$

"""

import os, sys, time

from constants import *
from events import Timer, processEvents, callLater
from misc import Range
from misc import (Transform_Translate, Transform_Scale, Transform_Rotate)
from misc import getOpenGlInfo

import cm

from wibjects import *
from wobjects import *

# do this last
from backends import use, App

from functions import *

# clean up namespace (dont clear modules, that only leads to weird bugs)
del os, sys, time
