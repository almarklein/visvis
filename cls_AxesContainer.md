
---

#### <font color='#FFF'>axescontainer</font> ####
# <font color='#00B'>class AxesContainer(parent)</font> #

Inherits from [Box](cls_Box.md).

A simple container wibject class to contain one Axes instance. Each Axes in contained in an AxesContainer instance. By default the axes position is expressed in pixel coordinates, while the container's position is expressed in unit coordinates. This  enables advanced positioning of the Axes.

When there is one axes in a figure, the container position will be "0,0,1,1". For subplots however, the containers are positioned to devide the figure in equal parts. The Axes instances themselves are positioned in pixels, such that when resizing, the margins for the tickmarks and labels remains equal.

The only correct way to create (and obtain a reference to)  an AxesContainer instance is to use:
  * axes = vv.Axes(figure)
  * container = axes.parent

This container is automatically destroyed once the axes is removed.  You can attach wibjects to an instance of this class, but note that the container object is destroyed as soon as the axes is gone.





**The AxesContainer class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#GetAxes.md'>GetAxes</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Methods ##

#### <font color='#FFF'>GetAxes</font> ####
### <font color='#066'>AxesContainer.GetAxes()</font> ###

> Get the axes. Creates a new axes object if it has none.





---

