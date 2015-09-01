
---

#### <font color='#FFF'>orientationforwobjects_mixclass</font> ####
# <font color='#00B'>class OrientationForWobjects_mixClass()</font> #

Inherits from [object](cls_object.md).

This class can be mixed with a wobject class to enable easy  orientation of the objects in space. It makes use of the  tranformation list that each wobject has.

The functionality provided by this class is not made part of the Wobject class because it does not make sense for all kind of wobjects (for example lines and images). The OrientableMesh is a class that inherits from this class.





**The OrientationForWobjects\_mixClass class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#direction.md'>direction</a><br /><a href='#rotation.md'>rotation</a><br /><a href='#scaling.md'>scaling</a><br /><a href='#translation.md'>translation</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>direction</font> ####
### <font color='#070'>OrientationForWobjects_mixClass.direction</font> ###

> Get/Set the direction (i.e. orientation) of the object. Can  be set using a 3-element tuple or a 3D point. The getter always  returns a Point.


#### <font color='#FFF'>rotation</font> ####
### <font color='#070'>OrientationForWobjects_mixClass.rotation</font> ###

> Get/Set the rotation of the object (in degrees, around its  direction vector).


#### <font color='#FFF'>scaling</font> ####
### <font color='#070'>OrientationForWobjects_mixClass.scaling</font> ###

> Get/Set the scaling of the object. Can be set using a 3-element tuple, a 3D point, or a scalar. The getter always returns a Point.


#### <font color='#FFF'>translation</font> ####
### <font color='#070'>OrientationForWobjects_mixClass.translation</font> ###

> Get/Set the transaltion of the object. Can be set using a 3-element tuple or a 3D point. The getter always returns a Point.



---

