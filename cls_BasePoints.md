
---

#### <font color='#FFF'>basepoints</font> ####
# <font color='#00B'>class BasePoints</font> #

Inherits from [object](cls_object.md).


Abstract class for the Point and Pointset classes. It defines addition, substraction, multiplication and devision for points and pointsets, and it implements some mathematical methods.





**The BasePoints class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#data.md'>data</a><br /><a href='#ndim.md'>ndim</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The BasePoints class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#angle.md'>angle</a><br /><a href='#angle2.md'>angle2</a><br /><a href='#copy.md'>copy</a><br /><a href='#cross.md'>cross</a><br /><a href='#distance.md'>distance</a><br /></td>
<td valign='top'>
<a href='#dot.md'>dot</a><br /><a href='#norm.md'>norm</a><br /><a href='#normal.md'>normal</a><br /><a href='#normalize.md'>normalize</a><br /><a href='#subtract.md'>subtract</a><br /></td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>data</font> ####
### <font color='#070'>BasePoints.data</font> ###

> Get the internal numpy array.


#### <font color='#FFF'>ndim</font> ####
### <font color='#070'>BasePoints.ndim</font> ###

> Get the number of dimensions.




---


## Methods ##

#### <font color='#FFF'>angle</font> ####
### <font color='#066'>BasePoints.angle(p)</font> ###

> Calculate the angle (in radians) between two vectors.  For 2D uses the arctan2 method so the angle has a sign. For 3D the angle is the smallest angles between the two vectors.

> If no point is given, the angle is calculated relative to the positive x-axis.




#### <font color='#FFF'>angle2</font> ####
### <font color='#066'>BasePoints.angle2(p)</font> ###

> Calculate the angle (in radians) of the vector between  two points.

> <b><u><font color='#A50'>Notes</font></u></b><br /><br />
> Say we have p1=(3,4) and p2=(2,1).

> p1.angle(p2) returns the difference of the angles of the two vectors: 0.142 = 0.927 - 0.785

> p1.angle2(p2) returns the angle of the difference vector (1,3): p1.angle2(p2) == (p1-p2).angle()




#### <font color='#FFF'>copy</font> ####
### <font color='#066'>BasePoints.copy()</font> ###

> Make a copy of the point or pointset.




#### <font color='#FFF'>cross</font> ####
### <font color='#066'>BasePoints.cross(p)</font> ###

> Calculate the cross product of two 3D vectors.

> Given two vectors, returns the vector that is orthogonal to both vectors. The right hand rule is applied; this vector is the middle finger, the argument the index finger, the returned vector points in the direction of the thumb.




#### <font color='#FFF'>distance</font> ####
### <font color='#066'>BasePoints.distance(p)</font> ###

> Calculate the Euclidian distance between two points or pointsets.  Use norm() to calculate the length of a vector.




#### <font color='#FFF'>dot</font> ####
### <font color='#066'>BasePoints.dot(p)</font> ###

> Calculate the dot product of the two points or pointsets.  The dot producet is the standard inner product of the  orthonormal Euclidean space.




#### <font color='#FFF'>norm</font> ####
### <font color='#066'>BasePoints.norm()</font> ###

> Calculate the norm (length) of the vector. This is the same as the distance to point 0,0 or 0,0,0, but implemented a bit faster.




#### <font color='#FFF'>normal</font> ####
### <font color='#066'>BasePoints.normal()</font> ###

> Calculate the normalized normal of a vector. Use (p1-p2).normal() to calculate the normal of the line p1-p2. Only works on 2D points. For 3D points use cross().




#### <font color='#FFF'>normalize</font> ####
### <font color='#066'>BasePoints.normalize()</font> ###

> Return normalized vector (to unit length).




#### <font color='#FFF'>subtract</font> ####
### <font color='#066'>BasePoints.subtract(other)</font> ###

> Subtract Pointset/Point instances.



> <b><u><font color='#A50'>Notes</font></u></b><br /><br />
> This method was introduced because of the minus-bug. To get the same behaviour of when the bug was still there, replace "A-B" with B.subtract(A).





---

