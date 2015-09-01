
---

#### <font color='#FFF'>twodcamera</font> ####
# <font color='#00B'>class TwoDCamera()</font> #

Inherits from [BaseCamera](cls_BaseCamera.md).

The default camera for viewing 2D data.

This camera uses orthografic projection and looks down the z-axis from inifinitly far away.

<b><u><font color='#A50'>Interaction</font></u></b><br />
  * Hold down the LMB and then move the mouse to pan.
  * Hold down the RMB and then move the mouse to zoom.





**The TwoDCamera class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#OnResize.md'>OnResize</a><br /><a href='#Reset.md'>Reset</a><br /><a href='#SetView.md'>SetView</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Methods ##

#### <font color='#FFF'>OnResize</font> ####
### <font color='#066'>TwoDCamera.OnResize(event)</font> ###

> Callback that adjusts the daspect (if axes.daspectAuto is True) when the window dimensions change.




#### <font color='#FFF'>!Reset</font> ####
### <font color='#066'>TwoDCamera.Reset()</font> ###

> Reset the view.




#### <font color='#FFF'>SetView</font> ####
### <font color='#066'>TwoDCamera.SetView()</font> ###

> Prepare the view for drawing This applies the camera model.





---

