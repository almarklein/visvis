
---

#### <font color='#FFF'>threedcamera</font> ####
# <font color='#00B'>class ThreeDCamera()</font> #

Inherits from [BaseCamera](cls_BaseCamera.md).

The ThreeDCamera camera is a camera to visualise 3D data.

In contrast to the 2D camera, this camera can be rotated around the data to look at it from different angles. By default the  field of view of this camera is set to 0, corresponding to an  orthografic projection. If the field of view is larger than 0, projective projection is applied.



<b><u><font color='#A50'>Interaction</font></u></b><br />
  * Hold down the LMB and then move the mouse to change the azimuth  and elivation (i.e. rotate around the scene).
  * Hold down the RMB and then move the mouse to zoom.
  * Hold down SHIFT + LMB and then move to pan.
  * Hold down SHIFT + RMB and then move to change the vield of view.
  * Hold down CONTROL + LMB and then move to rotate the whole scene  around the axis of the camera.





**The ThreeDCamera class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#azimuth.md'>azimuth</a><br /><a href='#elevation.md'>elevation</a><br /><a href='#fov.md'>fov</a><br /><a href='#roll.md'>roll</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The ThreeDCamera class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#OnResize.md'>OnResize</a><br /><a href='#Reset.md'>Reset</a><br /><a href='#SetView.md'>SetView</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>azimuth</font> ####
### <font color='#070'>ThreeDCamera.azimuth</font> ###

> Get/set the current azimuth angle (rotation around z-axis). This angle is between -180 and 180 degrees.


#### <font color='#FFF'>elevation</font> ####
### <font color='#070'>ThreeDCamera.elevation</font> ###

> Get/set the current elevation angle (rotation with respect to  the x-y plane). This angle is between -90 and 90 degrees.


#### <font color='#FFF'>fov</font> ####
### <font color='#070'>ThreeDCamera.fov</font> ###

> Get/set the current field of view (i.e. camera aperture).  This value is between 0 (orthographic projection) and 180.


#### <font color='#FFF'>roll</font> ####
### <font color='#070'>ThreeDCamera.roll</font> ###

> Get/set the current roll angle (rotation around the camera's  viewing axis). This angle is between -90 and 90 degrees.




---


## Methods ##

#### <font color='#FFF'>OnResize</font> ####
### <font color='#066'>ThreeDCamera.OnResize(event)</font> ###

> Callback that adjusts the daspect (if axes.daspectAuto is True) when the window dimensions change.




#### <font color='#FFF'>!Reset</font> ####
### <font color='#066'>ThreeDCamera.Reset()</font> ###

> Reset the view.




#### <font color='#FFF'>SetView</font> ####
### <font color='#066'>ThreeDCamera.SetView()</font> ###

> Prepare the view for drawing This applies the camera model.





---

