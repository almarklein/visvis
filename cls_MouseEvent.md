
---

#### <font color='#FFF'>mouseevent</font> ####
# <font color='#00B'>class MouseEvent(owner)</font> #

Inherits from [BaseEvent](cls_BaseEvent.md).

A MouseEvent is an event for things that happen  with the mouse.





**The MouseEvent class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#absx.md'>absx</a><br /><a href='#absy.md'>absy</a><br /><a href='#button.md'>button</a><br /><a href='#x.md'>x</a><br /><a href='#x2d.md'>x2d</a><br /><a href='#y.md'>y</a><br /><a href='#y2d.md'>y2d</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The MouseEvent class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Set.md'>Set</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>absx</font> ####
### <font color='#070'>MouseEvent.absx</font> ###

> The absolute x position in screen coordinates when the event happened.


#### <font color='#FFF'>absy</font> ####
### <font color='#070'>MouseEvent.absy</font> ###

> The absolute y position in screen coordinates when the event happened.


#### <font color='#FFF'>button</font> ####
### <font color='#070'>MouseEvent.button</font> ###

> The The mouse button that was pressed, 0=none, 1=left, 2=right.


#### <font color='#FFF'>x</font> ####
### <font color='#070'>MouseEvent.x</font> ###

> The x position in screen coordinates relative to the owning object when the event happened. (For Wobjects, relative to the Axes.)


#### <font color='#FFF'>x2d</font> ####
### <font color='#070'>MouseEvent.x2d</font> ###

> The x position in 2D world coordinates when the event happened.  This is only valid when the used camera is 2D.


#### <font color='#FFF'>y</font> ####
### <font color='#070'>MouseEvent.y</font> ###

> The y position in screen coordinates relative to the owning object when the event happened. (For Wobjects, relative to the Axes.)


#### <font color='#FFF'>y2d</font> ####
### <font color='#070'>MouseEvent.y2d</font> ###

> The y position in 2D world coordinates when the event happened.  This is only valid when the used camera is 2D.




---


## Methods ##

#### <font color='#FFF'>!Set</font> ####
### <font color='#066'>MouseEvent.Set(absx, absy, but, modifiers=())</font> ###

> Set the event properties before firing it.





---

