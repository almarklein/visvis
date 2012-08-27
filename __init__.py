# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" 
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
  * A backend GUI toolkit (PySide, PyQt4, wxPython, GTK, fltk)
  * (optionally, to enable reading and writing of images) imageio or PIL

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

Visvis is maintained by `Science Applied <http://www.science-applied.nl>`_.

"""

__version__  = '1.6.dev' 

# Loose sub-modules and sub-packages
from visvis.utils.pypoints import Point, Pointset, Aarray, Quaternion
from visvis.utils import ssdf
from visvis import vvmovie

# The core
from visvis.core import *

# The wibjects and wobjects
from visvis.wibjects import *
from visvis.wobjects import *

# Expose some more classes
from visvis.wobjects.polygonalModeling import BaseMesh
from visvis.processing.statistics import StatData

# Do this last
from visvis import backends
from visvis.functions import *
