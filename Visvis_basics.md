
---


## Introduction ##

Visvis is a pure Python library for visualization of 1D to 4D data in an object oriented way. Essentially, visvis is an object oriented layer of Python on top of OpenGl, thereby combining the power of OpenGl with the usability of Python. A Matlab-like interface in the form of a set of functions allows easy creation of objects (e.g. plot(), imshow(), volshow(), surf()).

Visvis shares quite a bit of functionality with both [Matplotlib](http://matplotlib.sourceforge.net/) and [Mayavi](http://code.enthought.com/projects/mayavi/). The combination of a clear object oriented visualization approach, and the simple (yet effective) event system, make that Visvis is good at making interactive applications.

![http://wiki.visvis.googlecode.com/hg/images/visvis_mpl_mayavi.png](http://wiki.visvis.googlecode.com/hg/images/visvis_mpl_mayavi.png)

### Object oriented design ###

Visvis has a strong object oriented design and employs a parental structure. The root of this structure is the [figure](cls_BaseFigure.md) object. Children of this object can be all sorts of widget objects (or [Wibjects](cls_Wibject.md)), which can again contain other widgets. The parental structure can be changed on the fly using the `parent` property, making it easy to build a tree structure of objects, or transfer wobjects from one figure to another.

An important wibject is the [Axes](cls_Axes.md) class: it represents a scene in "world coordinates", that is looked upon with one of the different camera types, and can be interacted with with the mouse.  Note that this concept of figure objects and axes objects is similar to Matplotlib and Matlab.

Multiple world-objects (or [Wobjects](cls_Wobject.md)) can easily be inserted in the scene by making them a child of the axes object. These world objects can be anything from plots ([lines](cls_Line.md) with markers), to [images](cls_Texture2D.md), 3D rendered [volumes](cls_Texture3D.md), shaded [meshes](cls_Mesh.md), or you can program your own world object class.

All [Wibjects](cls_Wibject.md) and [Wobjects](cls_Wobject.md) have various properties that can be modified to change their behavior and appearance. Together with an auto-completion tool, this makes it easy to control the visualization of your data. All classes, methods and functions have a descriptive docstring (from which the API reference in this wiki is generated).


## Naming conventions ##

```
# The prefered way to import visvis:
import visvis as vv

# If you realy want to "import *" something,
# only import the functions:
from visvis.functions import * 

# For clarity, the wibjects module contains all wibjects,
# and the wobjects module contains all the wobjects.
vv.wibjects
vv.wobjects

# Note that all functions, wibjects and wobjects are also inserted
# in the root visvis namespace.
```

In visvis we adopt the following naming conventions. Camelcase is used for
all names. Names of classes and methods start with a capital letter. All
instances, functions, modules, and object properties start with lowercase.
Some names are truncated to relief the user of too much typing. For
example "x limits" becomes `xlim`, and "line width" becomes `lw`.

Visvis makes use of properties. In general, the use of properties is pretty
fast. When getting or setting information is only available via a method,
this probably means that some calculations are required to produce the result, or that the result is not always available (see `GetFigure()`).


## Interactive shell vs. script ##

Visvis is designed to be used interactively in a shell. This does mean the shell needs to implement the backends GUI toolkit's main loop, or otherwise keep the used backend up-to-date.
  * In [IEP](http://code.google.com/p/iep), use `shell > Edit shell configurations` to set the gui toolkit.
  * In IPython use the -wthread or -q4thread for the wx and qt4 backends respectively.  Note that the fltk backend cannot be used interactively in IPython because IPython does not support that GUI toolkit.



To chose a backend, the function `vv.use()` can be used:
```
import visvis as vv
vv.use('qt4') # use qt4
```
If `vv.use()` is not called, or called without an argument, visvis selects a backend automatically. It will first determine whether any of the backend toolkits are already imported. If this is not the case, Visvis will try loading each backend until it finds one for which the GUI backend is installed. The order in which this happens is: wx, qt4, fltk.


Visvis can also be used inside a script. To do so, use the following code:
```
import visvis as vv
app = vv.use('wx') # or vv.use() to chose a backed automatically

# all your drawing commands go here

app.Run() # enter mainloop
```
The  `Run()` method of the `app` instance will start the underlying widget toolkit's main loop. The `app` object can also be used to enter the main loop when embedding a visvis figure in a GUI application.


## Coordinates ##

There are two coordinate systems in visvis: the screen coordinate
system and the world coordinate system.

For the screen coordinate system the origin is at the upper left corner,
just like in most GUI toolkits (WX, QT), but unlike how the figures and
axes are positioned in Matlab. Wibjects (which are in the screen coordinate frame)
have a property called `position` which provides several ways to change the
location and size of the wibject. See the `Wibject.position` documentation
for more details.

The world coordinate system applies to the scenes inside an axes object. This
system is 3D (unlike the screen, which is 2D). Two dimensional data can be
visualized using the 2D camera which looks straight down the z-axis. The
location of the origin in the world coordinate system depends on how you have rotated
your camera and whether any axis are flipped (using the Axes.daspect property).



## On Figures, Axes, Axis and Cameras ##

A figure is the base of the visualization system (it represents the OpenGL context). A figure is usually presented in a window on its own, but can also be
embedded as a widget in an application.

An axes (which is a wibject) resides inside a figure. One figure can
contain multiple axes. Inside an axes, a scene in world coordinates is rendered. (Each Axes object is contained in an AxesContainer object to enable relative positioning of
the axes. See the [AxesContainer](cls_AxesContainer.md) class for more information.)

An Axis (note the "i") is a wobject responsible for drawing the lines and tickmarks for each dimension.  Additionally, it draws the text of the xlabel, ylabel and zlabel properties of the axes, and for drawing the grid and minorgrid.

A camera is a model that determines how the data in the scene is visualized. The 2D
camera, for example, always looks down from above, and the 3D camera is more
suitable for visualizing 3D data. Using the Axes.cameraType property, the camera can be changed.


## More on cameras ##

You cannot view any data without some sort of camera model. As 3D data does not
let itself be visualized easily, a single model does not suffice. Visvis gives
you multiple ways to view and interact with your data via different camera models.

If the daspectAuto property is set to True, the data aspect ratio is
automatically changed to fit the screen. Zooming is performed on the x and y
dimension independently. If daspectAuto is set to False, the property Axes.daspect is
used to set the aspect ratio for each dimension. The daspect property can also be used
to specify whether an axis should be flipped (for images, for example, the y-axis
is flipped). See the docs of the Axes.daspect property for more information.

The "2d" camera model lets you visualize
plots of all sorts as well as 2 dimensional images. By default you can pan
the axes with you mouse (left mouse button) as well as zoom (right mouse
button).

For 3D data the default camera model is the "3d" camera model. It shows your 3D
data from an angle specified by the azimuth, elevation and roll parameters. Using
the mouse you can rotate the camera around your data. Holding shift translates
your data. Zooming is performed by holding the right mouse button, and by holding
control the camera can be rolled.


---
