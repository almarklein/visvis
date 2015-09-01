
---

#### <font color='#FFF'>quaternion</font> ####
# <font color='#00B'>class Quaternion(w=1, x=0, y=0, z=0, normalize=True)</font> #

Inherits from [object](cls_object.md).

A quaternion is a mathematically convenient way to describe rotations.





**The Quaternion class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#conjugate.md'>conjugate</a><br /><a href='#copy.md'>copy</a><br /><a href='#exp.md'>exp</a><br /><a href='#get_axis_angle.md'>get_axis_angle</a><br /><a href='#get_matrix.md'>get_matrix</a><br /></td>
<td valign='top'>
<a href='#inverse.md'>inverse</a><br /><a href='#log.md'>log</a><br /><a href='#norm.md'>norm</a><br /><a href='#normalize.md'>normalize</a><br /><a href='#rotate_point.md'>rotate_point</a><br /></td>
<td valign='top'>
</td>
</tr></table>



---


## Methods ##

#### <font color='#FFF'>conjugate</font> ####
### <font color='#066'>Quaternion.conjugate()</font> ###

> Obtain the conjugate of the quaternion. This is simply the same quaternion but with the sign of the imaginary (vector) parts reversed.




#### <font color='#FFF'>copy</font> ####
### <font color='#066'>Quaternion.copy()</font> ###

> Create an exact copy of this quaternion.




#### <font color='#FFF'>exp</font> ####
### <font color='#066'>Quaternion.exp()</font> ###

> Returns the exponent of the quaternion.  (not tested)




#### <font color='#FFF'>get_axis_angle</font> ####
### <font color='#066'>Quaternion.get_axis_angle()</font> ###

> Get the axis-angle representation of the quaternion.  (The angle is in radians)




#### <font color='#FFF'>get_matrix</font> ####
### <font color='#066'>Quaternion.get_matrix()</font> ###

> Create a 4x4 homography matrix that represents the rotation of the quaternion.




#### <font color='#FFF'>inverse</font> ####
### <font color='#066'>Quaternion.inverse()</font> ###

> returns q.conjugate()/q.norm()`*``*`2 So if the quaternion is unit length, it is the same as the conjugate.


#### <font color='#FFF'>log</font> ####
### <font color='#066'>Quaternion.log()</font> ###

> Returns the natural logarithm of the quaternion.  (not tested)




#### <font color='#FFF'>norm</font> ####
### <font color='#066'>Quaternion.norm()</font> ###

> Returns the norm of the quaternion. norm = w`*``*`2 + x`*``*`2 + y`*``*`2 + z`*``*`2




#### <font color='#FFF'>normalize</font> ####
### <font color='#066'>Quaternion.normalize()</font> ###

> Returns a normalized (unit length) version of the quaternion.




#### <font color='#FFF'>rotate_point</font> ####
### <font color='#066'>Quaternion.rotate_point(p)</font> ###

> Rotate a Point instance using this quaternion.





---

