
---

#### <font color='#FFF'>basetext</font> ####
# <font color='#00B'>class BaseText(text='', fontName=None, fontSize=9, color='k')</font> #

Inherits from [object](cls_object.md).

Base object for the Text wobject and Label wibject. fontname may be 'mono', 'sans', 'serif' or None, in which case the vv.settings.defaultFontName is used.



**The BaseText class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#fontName.md'>fontName</a><br /><a href='#fontSize.md'>fontSize</a><br /><a href='#halign.md'>halign</a><br /><a href='#text.md'>text</a><br /></td>
<td valign='top'>
<a href='#textAngle.md'>textAngle</a><br /><a href='#textColor.md'>textColor</a><br /><a href='#textSpacing.md'>textSpacing</a><br /><a href='#valign.md'>valign</a><br /></td>
<td valign='top'>
</td>
</tr></table>

**The BaseText class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#GetVertexLimits.md'>GetVertexLimits</a><br /><a href='#Invalidate.md'>Invalidate</a><br /><a href='#UpdatePosition.md'>UpdatePosition</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>fontName</font> ####
### <font color='#070'>BaseText.fontName</font> ###

> Get/Set the font type by its name.


#### <font color='#FFF'>fontSize</font> ####
### <font color='#070'>BaseText.fontSize</font> ###

> Get/Set the size of the text.


#### <font color='#FFF'>halign</font> ####
### <font color='#070'>BaseText.halign</font> ###

> Get/Set the horizontal alignment. Specify as:
> `*` 'left', 'center', 'right'
> `*` -1, 0, 1


#### <font color='#FFF'>text</font> ####
### <font color='#070'>BaseText.text</font> ###

> Get/Set the text to display.


#### <font color='#FFF'>textAngle</font> ####
### <font color='#070'>BaseText.textAngle</font> ###

> Get/Set the angle of the text in degrees.


#### <font color='#FFF'>textColor</font> ####
### <font color='#070'>BaseText.textColor</font> ###

> Get/Set the color of the text.


#### <font color='#FFF'>textSpacing</font> ####
### <font color='#070'>BaseText.textSpacing</font> ###

> Get/Set the spacing between characters.


#### <font color='#FFF'>valign</font> ####
### <font color='#070'>BaseText.valign</font> ###

> Get/Set the vertical alignment. Specify as:
> `*` 'up', 'center', 'down'
> `*` 'top', 'center', 'bottom'
> `*` -1, 0, 1




---


## Methods ##

#### <font color='#FFF'>GetVertexLimits</font> ####
### <font color='#066'>BaseText.GetVertexLimits()</font> ###

> Get the limits of the vertex data. Returns (xmin, xmax), (ymin, ymax)


#### <font color='#FFF'>!Invalidate</font> ####
### <font color='#066'>BaseText.Invalidate()</font> ###

> Invalidate this object, such that the text is recompiled the next time it is drawn.


#### <font color='#FFF'>UpdatePosition</font> ####
### <font color='#066'>BaseText.UpdatePosition()</font> ###

> Updates the position now, Compiles the text if necessary.



---

