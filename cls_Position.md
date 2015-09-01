
---

#### <font color='#FFF'>position</font> ####
# <font color='#00B'>class Position(x,y,w,h, wibject_instance)</font> #

Inherits from [object](cls_object.md).

The position class stores and manages the position of wibjects. Each  wibject has one Position instance associated with it, which can be  obtained (and updated) using its position property.

The position is represented using four values: x, y, w, h. The Position object can also be indexed to get or set these four values.

Each element (x,y,w,h) can be either:
  * The integer amount of pixels relative to the wibjects parent's position.
  * The fractional amount (float value between 0.0 and 1.0) of the parent's width or height.

Each value can be negative. For x and y this simply means a negative  offset from the parent's left and top. For the width and height the  difference from the parent's full width/height is taken.

An example: a position (-10, 0.5, 150,-100), with a parent's size of  (500,500) is equal to (-10, 250, 150, 400) in pixels.

Remarks:
  * fractional, integer and negative values may be mixed.
  * x and y are considered fractional on <-1, 1>
  * w and h are considered fractional on `[`-1, 1`]`
  * the value 0 can always be considered to be in pixels

The position class also implements several "long-named" properties that express the position in pixel coordinates. Internally a version in pixel coordinates is buffered, which is kept up to date. These long-named  (read-only) properties are: left, top, right, bottom, width, height,

Further, there are a set of properties which express the position in  absolute coordinates (not relative to the wibject's parent): absLeft, absTop, absRight, absBottom

Finally, there are properties that return a two-element tuple: topLeft, bottomRight, absTopLeft, absBottomRight, size

The method InPixels() returns a (copy) Position object which represents the position in pixels.





**The Position class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#absBottom.md'>absBottom</a><br /><a href='#absBottomRight.md'>absBottomRight</a><br /><a href='#absLeft.md'>absLeft</a><br /><a href='#absRight.md'>absRight</a><br /><a href='#absTop.md'>absTop</a><br /><a href='#absTopLeft.md'>absTopLeft</a><br /><a href='#bottom.md'>bottom</a><br /></td>
<td valign='top'>
<a href='#bottomRight.md'>bottomRight</a><br /><a href='#h.md'>h</a><br /><a href='#height.md'>height</a><br /><a href='#left.md'>left</a><br /><a href='#right.md'>right</a><br /><a href='#size.md'>size</a><br /><a href='#top.md'>top</a><br /></td>
<td valign='top'>
<a href='#topLeft.md'>topLeft</a><br /><a href='#w.md'>w</a><br /><a href='#width.md'>width</a><br /><a href='#x.md'>x</a><br /><a href='#y.md'>y</a><br /></td>
</tr></table>

**The Position class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Copy.md'>Copy</a><br /><a href='#Correct.md'>Correct</a><br /><a href='#InPixels.md'>InPixels</a><br /><a href='#Set.md'>Set</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>absBottom</font> ####
### <font color='#070'>Position.absBottom</font> ###

> Get absTop+height.


#### <font color='#FFF'>absBottomRight</font> ####
### <font color='#070'>Position.absBottomRight</font> ###

> Get a tuple (right, bottom).


#### <font color='#FFF'>absLeft</font> ####
### <font color='#070'>Position.absLeft</font> ###

> Get the x-element of the position, expressed in absolute pixels instead of relative to the parent.


#### <font color='#FFF'>absRight</font> ####
### <font color='#070'>Position.absRight</font> ###

> Get absLeft+width.


#### <font color='#FFF'>absTop</font> ####
### <font color='#070'>Position.absTop</font> ###

> Get the y-element of the position, expressed in absolute pixels instead of relative to the parent.


#### <font color='#FFF'>absTopLeft</font> ####
### <font color='#070'>Position.absTopLeft</font> ###

> Get a tuple (absLeft, absTop).


#### <font color='#FFF'>bottom</font> ####
### <font color='#070'>Position.bottom</font> ###

> Get top+height.


#### <font color='#FFF'>bottomRight</font> ####
### <font color='#070'>Position.bottomRight</font> ###

> Get a tuple (right, bottom).


#### <font color='#FFF'>h</font> ####
### <font color='#070'>Position.h</font> ###

> Get/Set the h-element of the position. This value can be  an integer value or a float expressing the height as a fraction  of the parent's height. The value can also be negative, in which case it's subtracted from the parent's height.


#### <font color='#FFF'>height</font> ####
### <font color='#070'>Position.height</font> ###

> Get the h-element of the position, expressed in pixels.


#### <font color='#FFF'>left</font> ####
### <font color='#070'>Position.left</font> ###

> Get the x-element of the position, expressed in pixels.


#### <font color='#FFF'>right</font> ####
### <font color='#070'>Position.right</font> ###

> Get left+width.


#### <font color='#FFF'>size</font> ####
### <font color='#070'>Position.size</font> ###

> Get a tuple (width, height).


#### <font color='#FFF'>top</font> ####
### <font color='#070'>Position.top</font> ###

> Get the y-element of the position, expressed in pixels.


#### <font color='#FFF'>topLeft</font> ####
### <font color='#070'>Position.topLeft</font> ###

> Get a tuple (left, top).


#### <font color='#FFF'>w</font> ####
### <font color='#070'>Position.w</font> ###

> Get/Set the w-element of the position. This value can be  an integer value or a float expressing the width as a fraction  of the parent's width. The value can also be negative, in which case it's subtracted from the parent's width.


#### <font color='#FFF'>width</font> ####
### <font color='#070'>Position.width</font> ###

> Get the w-element of the position, expressed in pixels.


#### <font color='#FFF'>x</font> ####
### <font color='#070'>Position.x</font> ###

> Get/Set the x-element of the position. This value can be  an integer value or a float expressing the x-position as a fraction  of the parent's width. The value can also be negative.


#### <font color='#FFF'>y</font> ####
### <font color='#070'>Position.y</font> ###

> Get/Set the y-element of the position. This value can be  an integer value or a float expressing the y-position as a fraction  of the parent's height. The value can also be negative.




---


## Methods ##

#### <font color='#FFF'>!Copy</font> ####
### <font color='#066'>Position.Copy()</font> ###

> Make a copy of this position instance.




#### <font color='#FFF'>!Correct</font> ####
### <font color='#066'>Position.Correct(dx=0, dy=0, dw=0, dh=0)</font> ###

> Correct the position by suplying a delta amount of pixels. The correction is only applied if the attribute is in pixels.




#### <font color='#FFF'>InPixels</font> ####
### <font color='#066'>Position.InPixels()</font> ###

> Return a copy, but in pixel coordinates.




#### <font color='#FFF'>!Set</font> ####
### <font color='#066'>Position.Set(<code>*</code>args)</font> ###

> Set(x, y, w, h) or Set(x, y).





---

