# Visvis - the object oriented approach to visualization

[![Build Status](https://travis-ci.org/almarklein/visvis.svg?branch=master)](https://travis-ci.org/almarklein/visvis)

[Visvis](http://github.com/almarklein/visvis) is a pure Python library
for visualization of 1D to 4D data in an object oriented way.
Essentially, visvis is an object oriented layer of Python on top of
OpenGl, thereby combining the power of OpenGl with the usability of
Python. A Matlab/Matplotlib-like interface in the form of a set of functions allows
easy creation of objects (e.g. `plot()`, `imshow()`, `volshow()`, `surf()`).

## Installation

Visvis is cross-platform and runs on Python 2.x and Python 3.x. It
depends on numpy, pyopengl, and needs a GUI backend (either PyQt4, PyQt4, PySide, Wx, GTK, FLTK).

Installation is best done via conda (``conda install vispy``) or pip (``pip install visvis``).


## How visvis works

With visvis a range of different data can be visualized by simply adding
[world objects](https://github.com/almarklein/visvis/wiki/cls_Wobject) to
a scene (i.e. an
[axes](https://github.com/almarklein/visvis/wiki/cls_Axes)). These world
objects can be
anything from plots
([lines](https://github.com/almarklein/visvis/wiki/example_plotting) with
markers), to
[images](https://github.com/almarklein/visvis/wiki/example_images), 3D
rendered
[volumes](https://github.com/almarklein/visvis/wiki/example_volumes), shaded
[meshes](https://github.com/almarklein/visvis/wiki/example_meshes), or you
can program your own world object class.
If required, these data can also be
[moved](https://github.com/almarklein/visvis/wiki/example_fourDimensions)
in time.


## Example
[![](https://raw.githubusercontent.com/wiki/almarklein/visvis/images/overviewScreen.png)](https://github.com/almarklein/visvis/wiki/example_overview)

Click on the figure to see the [code](https://github.com/almarklein/visvis/wiki/example_overview) and how one can interact with the figure.


## Documentation

The docs are on the [wiki](https://github.com/almarklein/visvis/wiki).
Online documentation is available for all
[classes](https://github.com/almarklein/visvis/wiki/classes) and
[functions](https://github.com/almarklein/visvis/wiki/functions). Any
questions can be asked in the visvis [discussion
group](http://groups.google.com/group/visvis).

At EuroScipy 2012, I gave a talk about Visvis. The long version of the
presentation can be seen [here](https://docs.google.com/presentation/pub?id=17J5IVIoh2zQk49ycYh__CYpi33aWi0oSljI_MnYByeg&start=false&loop=false&delayms=3000).


## License

Visvis makes use of the liberal BSD license. See license.txt for details.
