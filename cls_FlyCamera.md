
---

#### <font color='#FFF'>flycamera</font> ####
# <font color='#00B'>class FlyCamera()</font> #

Inherits from [BaseCamera](cls_BaseCamera.md).

The fly camera provides a fun way to visualise 3D data using an  interaction style that resembles a flight sim.

Think of the fly camera as a remote controlled vessel with which you fly trough your data, much like in the classic game 'Descent'.

<b><u><font color='#A50'>Interaction</font></u></b><br /><br />
Notice: interacting with this camera might need a bit of practice.

Moving:
  * w,a,s,d keys to move forward, backward, left and right
  * f and c keys move up and down
  * Using SHIFT+RMB, the scale factor can be changed, a lower scale means smaller motions (i.e. more fine-grained control).

Viewing:
  * Use the mouse to control the pitch and yaw.
  * Alternatively, the pitch and yaw can be changed using the keys i,k,j,l.
  * The camera auto-rotates to make the bottom of the vessel point down, manual rolling can be performed using q and e.
  * Using the RMB, one can zoom in, like looking through binoculars.  This will also make you move slightly faster.





**The FlyCamera class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#fov.md'>fov</a><br /><a href='#rotation.md'>rotation</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The FlyCamera class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Reset.md'>Reset</a><br /><a href='#SetView.md'>SetView</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>fov</font> ####
### <font color='#070'>FlyCamera.fov</font> ###

> Get/set the current field of view (i.e. camera aperture).  This value is between 10 and 90.


#### <font color='#FFF'>rotation</font> ####
### <font color='#070'>FlyCamera.rotation</font> ###

> Get/set the current rotation quaternion.




---


## Methods ##

#### <font color='#FFF'>!Reset</font> ####
### <font color='#066'>FlyCamera.Reset()</font> ###

> Reset the view.




#### <font color='#FFF'>SetView</font> ####
### <font color='#066'>FlyCamera.SetView()</font> ###

> Prepare the view for drawing This applies the camera model.





---

