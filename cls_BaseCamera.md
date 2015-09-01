
---

#### <font color='#FFF'>basecamera</font> ####
# <font color='#00B'>class BaseCamera()</font> #

Inherits from [object](cls_object.md).

Abstract camera class. A camera represents both the camera model and the interaction style.





**The BaseCamera class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#axes.md'>axes</a><br /><a href='#axeses.md'>axeses</a><br /><a href='#daspect.md'>daspect</a><br /><a href='#daspectNormalized.md'>daspectNormalized</a><br /><a href='#loc.md'>loc</a><br /><a href='#zoom.md'>zoom</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The BaseCamera class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#GetViewParams.md'>GetViewParams</a><br /><a href='#Reset.md'>Reset</a><br /><a href='#ScreenToWorld.md'>ScreenToWorld</a><br /><a href='#SetLimits.md'>SetLimits</a><br /><a href='#SetView.md'>SetView</a><br /><a href='#SetViewParams.md'>SetViewParams</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>axes</font> ####
### <font color='#070'>BaseCamera.axes</font> ###

> Get the axes that this camera applies to (or the first axes if it applies to multiple axes).


#### <font color='#FFF'>axeses</font> ####
### <font color='#070'>BaseCamera.axeses</font> ###

> Get a tuple with the axeses that this camera applies to.


#### <font color='#FFF'>daspect</font> ####
### <font color='#070'>BaseCamera.daspect</font> ###

> Get/Set the data aspect ratio as a three element tuple.

> The daspect is a 3-element tuple (x,y,z). If a 2-element tuple is given, z is assumed 1. Note that only the ratio between the values matters (i.e. (1,1,1) equals (2,2,2)). When a value is negative, the  corresponding dimension is flipped.

> Note that if axes.daspectAuto is True, the daspect is changed by the  camera to nicely scale the data to fit the screen (but the sign is preserved).


#### <font color='#FFF'>daspectNormalized</font> ####
### <font color='#070'>BaseCamera.daspectNormalized</font> ###

> Get the data aspect ratio, normalized such that the x scaling  is +/- 1.


#### <font color='#FFF'>loc</font> ####
### <font color='#070'>BaseCamera.loc</font> ###

> Get/set the current viewing location.


#### <font color='#FFF'>zoom</font> ####
### <font color='#070'>BaseCamera.zoom</font> ###

> Get/set the current zoom factor.




---


## Methods ##

#### <font color='#FFF'>GetViewParams</font> ####
### <font color='#066'>BaseCamera.GetViewParams()</font> ###

> Get a dictionary with view parameters.




#### <font color='#FFF'>!Reset</font> ####
### <font color='#066'>BaseCamera.Reset()</font> ###

> Reset the view. Overload this in the actual camera models.




#### <font color='#FFF'>ScreenToWorld</font> ####
### <font color='#066'>BaseCamera.ScreenToWorld(x_y=None)</font> ###

> Given a tuple of screen coordinates, calculate the world coordinates.         If not given, the current mouse position is used.

> This basically simulates the actions performed in SetView but then for a single location.




#### <font color='#FFF'>SetLimits</font> ####
### <font color='#066'>BaseCamera.SetLimits(xlim, ylim, zlim=None)</font> ###

> Set the data limits of the camera. Always set this before rendering! This also calls reset to reset the view.




#### <font color='#FFF'>SetView</font> ####
### <font color='#066'>BaseCamera.SetView()</font> ###

> Set the view, thus simulating a camera. Overload this in the actual camera models.




#### <font color='#FFF'>SetViewParams</font> ####
### <font color='#066'>BaseCamera.SetViewParams(s=None, <code>*</code><code>*</code>kw)</font> ###

> Set the view, given a dictionary with view parameters.  View parameters may also be passed as keyword/value pairs; these will supersede the same keys in s.





---

