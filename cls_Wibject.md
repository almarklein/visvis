
---

#### <font color='#FFF'>wibject</font> ####
# <font color='#00B'>class Wibject(parent)</font> #

Inherits from [BaseObject](cls_BaseObject.md).

A Wibject (widget object) is a 2D object drawn in  screen coordinates. A Figure is a widget and so are an Axes and a  PushButton. Wibjects have a position property to set their location and size. They also have a background color and multiple event properties.

This class may also be used as a container object for other wibjects.  An instance of this class has no visual appearance. The Box class  implements drawing a rectangle with an edge.





**The Wibject class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#bgcolor.md'>bgcolor</a><br /><a href='#eventPosition.md'>eventPosition</a><br /><a href='#position.md'>position</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>bgcolor</font> ####
### <font color='#070'>Wibject.bgcolor</font> ###

> Get/Set the background color of the wibject.


#### <font color='#FFF'>eventPosition</font> ####
### <font color='#070'>Wibject.eventPosition</font> ###

> Fired when the position (or size) of this wibject changes.


#### <font color='#FFF'>position</font> ####
### <font color='#070'>Wibject.position</font> ###

> Get/Set the position of this wibject. Setting can be done by supplying either a 2-element tuple or list to only change the location, or a 4-element tuple or list to change location and size.

> See the docs of the vv.base.Position class for more information.



---

