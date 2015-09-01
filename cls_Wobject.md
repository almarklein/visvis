
---

#### <font color='#FFF'>wobject</font> ####
# <font color='#00B'>class Wobject(parent)</font> #

Inherits from [BaseObject](cls_BaseObject.md).

A Wobject (world object) is a visual element that  is drawn in 3D world coordinates (in the scene). Wobjects can be  children of other wobjects or of an Axes object (which is the wibject that represents the scene).

To each wobject, several transformations can be applied,  which are also applied to its children. This way complex models can  be build. For example, in a robot arm the fingers would be children  of the hand, so that when the hand moves or rotates, the fingers move along automatically. The fingers can then also be moved without affecting  the hand or other fingers.

The transformations are represented by Transform_`*` objects in  the list named "transformations". The transformations are applied in the order as they appear in the list._





**The Wobject class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#transformations.md'>transformations</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The Wobject class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Draw.md'>Draw</a><br /><a href='#GetAxes.md'>GetAxes</a><br /><a href='#TransformPoint.md'>TransformPoint</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>transformations</font> ####
### <font color='#070'>Wobject.transformations</font> ###

> Get the list of transformations of this wobject. These can be Transform\_Translate, Transform\_Scale, or Transform\_Rotate instances.




---


## Methods ##

#### <font color='#FFF'>!Draw</font> ####
### <font color='#066'>Wobject.Draw(fast=False)</font> ###

> Calls Draw on the axes that contains this object.




#### <font color='#FFF'>GetAxes</font> ####
### <font color='#066'>Wobject.GetAxes()</font> ###

> Get the axes in which this wobject resides.

> Note that this is not necesarily an Axes instance (like the line objects in the Legend wibject).




#### <font color='#FFF'>TransformPoint</font> ####
### <font color='#066'>Wobject.TransformPoint(p, baseWobject=None)</font> ###

> Transform a point in the local coordinate system of this wobject to the coordinate system of the given baseWobject (which should be a parent of this wobject), or to the global (Axes) coordinate  system if not given.

> This is done by taking into account the transformations applied to this wobject and its parent wobjects.

> If baseWobject is the current wobject itself, only the tranformations of this wobject are applied.





---

