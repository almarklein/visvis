
---

#### <font color='#FFF'>basemapableeditor</font> ####
# <font color='#00B'>class BaseMapableEditor(parent)</font> #

Inherits from [DraggableBox](cls_DraggableBox.md).

Base class for widgets that are used to edit the mapable properties of objects: colormap and clim.





**The BaseMapableEditor class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#GetMapables.md'>GetMapables</a><br /><a href='#SetMapables.md'>SetMapables</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Methods ##

#### <font color='#FFF'>GetMapables</font> ####
### <font color='#066'>BaseMapableEditor.GetMapables()</font> ###

> Get a list of mappable objects that was given earlier using SetMapables. If an axes or figure was given, all eligable  objects are queried from their children.




#### <font color='#FFF'>SetMapables</font> ####
### <font color='#066'>BaseMapableEditor.SetMapables(mapable1, mapable2, mapable3, etc.)</font> ###

> Set the mapables to take into account. A mapable is any wibject or wobject that inherits from Colormapable (and can be recognized by having a colormap and clim property).

> The argument may also be a list or tuple of objects, or an Axes  or Figure instance, in which case all mapable children are used. If args is not given, the parent is used.





---

