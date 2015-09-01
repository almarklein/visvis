
---

#### <font color='#FFF'>axes</font> ####
# <font color='#00B'>class Axes(parent, axisClass=None)</font> #

Inherits from [Wibject](cls_Wibject.md).

An Axes instance represents the scene with a local coordinate system  in which wobjects can be drawn. It has various properties to influence  the appearance of the scene, such as aspect ratio and lighting.

To set the appearance of the axis (the thing that indicates x, y and z),  use the properties of the Axis instance. For example: Axes.axis.showGrid = True

The cameraType determines how the data is visualized and how the user  can interact with the data.

The daspect property represents the aspect ratio of the data as a three element tuple. The sign of the elements indicate dimensions  being flipped. (The function imshow() for example flips the  y-dimension). If daspectAuto is False, all dimensions are always equally zoomed (The function imshow() sets this to False).

An Axes can be created with the function vv.subplot() or vv.gca().





**The Axes class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#axis.md'>axis</a><br /><a href='#axisType.md'>axisType</a><br /><a href='#bgcolors.md'>bgcolors</a><br /><a href='#camera.md'>camera</a><br /><a href='#cameraType.md'>cameraType</a><br /><a href='#daspect.md'>daspect</a><br /></td>
<td valign='top'>
<a href='#daspectAuto.md'>daspectAuto</a><br /><a href='#daspectNormalized.md'>daspectNormalized</a><br /><a href='#legend.md'>legend</a><br /><a href='#legendWibject.md'>legendWibject</a><br /><a href='#light0.md'>light0</a><br /><a href='#lights.md'>lights</a><br /></td>
<td valign='top'>
<a href='#motionBlur.md'>motionBlur</a><br /><a href='#mousepos.md'>mousepos</a><br /><a href='#useBuffer.md'>useBuffer</a><br /><a href='#wobjects.md'>wobjects</a><br /></td>
</tr></table>

**The Axes class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Clear.md'>Clear</a><br /><a href='#Draw.md'>Draw</a><br /><a href='#GetLimits.md'>GetLimits</a><br /><a href='#GetView.md'>GetView</a><br /><a href='#MakeCurrent.md'>MakeCurrent</a><br /><a href='#SetLimits.md'>SetLimits</a><br /><a href='#SetView.md'>SetView</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>axis</font> ####
### <font color='#070'>Axes.axis</font> ###

> Get the axis object associated with this axes.  A new instance is created if it does not yet exist. This object can be used to change the appearance of the axis (tickmarks, labels, grid, etc.).

> See also the [Axis class](cls_BaseAxis.md).




#### <font color='#FFF'>axisType</font> ####
### <font color='#070'>Axes.axisType</font> ###

> Get/Set the axis type to use.

> Currently supported are:
    * 'cartesian' - a normal axis (default)
    * 'polar' - a polar axis.


#### <font color='#FFF'>bgcolors</font> ####
### <font color='#070'>Axes.bgcolors</font> ###

> Get/Set the colors for the axes background gradient. If used, this value overrides the normal bgcolor property. Notes:
    * Set to None to disable the gradient
    * Setting two colors defines a gradient from top to bottom.
    * Setting four colors sets the colors at the four corners.
    * The value must be an iterable (2 or 4 elements) in which each element can be converted to a color.


#### <font color='#FFF'>camera</font> ####
### <font color='#070'>Axes.camera</font> ###

> Get/Set the current camera.

> Setting can be done using:
    * The index of the camera; 1,2,3 for fly, 2d and 3d respectively.
    * A value as in the 'cameraType' property.
    * A new camera instance. This will replace any existing camera  of the same type. To have multiple 3D cameras at the same axes, one needs to subclass cameras.ThreeDCamera.

> <b><u><font color='#A50'>Shared cameras</font></u></b><br /><br />
> One can set the camera to the camera of another Axes, so that they share the same camera. A camera that is shared uses daspectAuto  property of the first axes it was attached to.

> <b><u><font color='#A50'>Interactively changing a camera</font></u></b><br /><br />
> By default, the camera can be changed using the keyboard using the shortcut ALT+i, where i is the camera number. Similarly the daspectAuto propert can be switched with ALT+d.


#### <font color='#FFF'>cameraType</font> ####
### <font color='#070'>Axes.cameraType</font> ###

> Get/Set the camera type to use.

> Currently supported are:
    * '2d' or 2  - two dimensional camera that looks down the z-dimension.
    * '3d' or 3  - three dimensional camera.
    * 'fly' or 1 - a camera like a flight sim.




#### <font color='#FFF'>daspect</font> ####
### <font color='#070'>Axes.daspect</font> ###

> Get/set the data aspect ratio of the current camera. Setting will also update daspect for the other cameras.

> The daspect is a 3-element tuple (x,y,z). If a 2-element tuple is given, z is assumed 1. Note that only the ratio between the values matters (i.e. (1,1,1) equals (2,2,2)). When a value is negative, the  corresponding dimension is flipped.

> Note that if daspectAuto is True, the camera automatically changes its daspect to nicely scale the data to fit the screen (but the sign is preserved).


#### <font color='#FFF'>daspectAuto</font> ####
### <font color='#070'>Axes.daspectAuto</font> ###

> Get/Set whether to scale the dimensions independently.

> If True, the camera changes the value of its daspect to nicely fit  the data on screen (but the sign is preserved). This can happen  (depending on the type of camera) during resetting, zooming, and  resizing of the axes.

> If set to False, the daspect of all cameras is reverted to  the user-set daspect.


#### <font color='#FFF'>daspectNormalized</font> ####
### <font color='#070'>Axes.daspectNormalized</font> ###

> Get the data aspect ratio, normalized such that the x scaling  is +/- 1.


#### <font color='#FFF'>legend</font> ####
### <font color='#070'>Axes.legend</font> ###

> Get/Set the string labels for the legend. Upon setting, a legend wibject is automatically shown.


#### <font color='#FFF'>legendWibject</font> ####
### <font color='#070'>Axes.legendWibject</font> ###

> Get the legend wibject, so for exampe its position can be changed programatically.


#### <font color='#FFF'>light0</font> ####
### <font color='#070'>Axes.light0</font> ###

> Get the default light source in the scene.


#### <font color='#FFF'>lights</font> ####
### <font color='#070'>Axes.lights</font> ###

> Get a list of all available lights in the scene. Only light0 is enabeled by default.


#### <font color='#FFF'>motionBlur</font> ####
### <font color='#070'>Axes.motionBlur</font> ###

> Get/Set the amount of motion blur when interacting with this axes. The value should be a number between 0 and 1.  Note: this is a rather useless feature :)


#### <font color='#FFF'>mousepos</font> ####
### <font color='#070'>Axes.mousepos</font> ###

> Get position of mouse in screen pixels, relative to this axes.


#### <font color='#FFF'>useBuffer</font> ####
### <font color='#070'>Axes.useBuffer</font> ###

> Get/Set whether to use a buffer; after drawing, a screenshot of the result is obtained and stored. When the axes needs to be redrawn, but has not changed, the buffer can be used to  draw the contents at great speed (default True).


#### <font color='#FFF'>wobjects</font> ####
### <font color='#070'>Axes.wobjects</font> ###

> Get a shallow copy of the list of wobjects in the scene.




---


## Methods ##

#### <font color='#FFF'>!Clear</font> ####
### <font color='#066'>Axes.Clear()</font> ###

> Clear the axes. Removing all wobjects in the scene.




#### <font color='#FFF'>!Draw</font> ####
### <font color='#066'>Axes.Draw(fast=False)</font> ###

> Calls Draw(fast) on its figure, as the total opengl canvas  has to be redrawn. This might change in the future though.




#### <font color='#FFF'>GetLimits</font> ####
### <font color='#066'>Axes.GetLimits()</font> ###

> Get the limits of the 2D axes as currently displayed. This can differ from what was set by SetLimits if the daspectAuto is False.  Returns a tuple of limits for x and y, respectively.

> Note: the limits are queried from the twod camera model, even  if this is not the currently used camera.




#### <font color='#FFF'>GetView</font> ####
### <font color='#066'>Axes.GetView()</font> ###

> Get a dictionary with the camera parameters. The parameters are named so they can be changed in a natural way and fed back using SetView(). Note that the parameters can differ for different camera types.




#### <font color='#FFF'>MakeCurrent</font> ####
### <font color='#066'>Axes.MakeCurrent()</font> ###

> Make this the current axes. Also makes the containing figure the current figure.




#### <font color='#FFF'>SetLimits</font> ####
### <font color='#066'>Axes.SetLimits(rangeX=None, rangeY=None, rangeZ=None, margin=0.02)</font> ###

> Set the limits of the scene. For the 2D camera, these are taken  as hints to set the camera view. For the 3D camear, they determine where the axis is drawn.

> Returns a 3-element tuple of visvis.Range objects.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>rangeX : (min, max), optional</u><br /><font color='#020'> The range for the x dimension.<br /></font><u>rangeY : (min, max), optional</u><br /><font color='#020'> The range for the y dimension.<br /></font><u>rangeZ : (min, max), optional</u><br /><font color='#020'> The range for the z dimension.<br /></font><u>margin : scalar</u><br /><font color='#020'> Represents the fraction of the range to add for the ranges that are automatically obtained (default 2%).</font>

> <b><u><font color='#A50'>Notes</font></u></b><br /><br />
> Each range can be None, a 2 element iterable, or a visvis.Range  object. If a range is None, the range is automatically obtained from the wobjects currently in the scene. To set the range that will fit all wobjects, simply use "SetLimits()"




#### <font color='#FFF'>SetView</font> ####
### <font color='#066'>Axes.SetView(s=None, <code>*</code><code>*</code>kw)</font> ###

> Set the camera view using the given dictionary with camera parameters. Camera parameters can also be passed as keyword/value pairs; these will supersede the values of the same key in s.  If neither s nor any keywords are set, the camera is reset to its initial state.





---

