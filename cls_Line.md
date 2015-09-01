
---

#### <font color='#FFF'>line</font> ####
# <font color='#00B'>class Line(parent, points)</font> #

Inherits from [Wobject](cls_Wobject.md).

The line class represents a set of points (locations) in world coordinates. This class can draw lines between the points, markers at the point coordinates, or both.

Line objects can be created with the function vv.plot().

<b><u><font color='#A50'>Performance tips</font></u></b><br /><br />
The s, o (and .) styles can be drawn using standard OpenGL points if alpha is 1 or if no markeredge is drawn.

Otherwise point sprites are used, which can be slower on some cards (like ATI, Nvidia performs quite ok with with sprites).

Some video cards simply do not support sprites (seen on ATI).





**The Line class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#alpha.md'>alpha</a><br /><a href='#lc.md'>lc</a><br /><a href='#ls.md'>ls</a><br /><a href='#lw.md'>lw</a><br /><a href='#mc.md'>mc</a><br /></td>
<td valign='top'>
<a href='#mec.md'>mec</a><br /><a href='#mew.md'>mew</a><br /><a href='#ms.md'>ms</a><br /><a href='#mw.md'>mw</a><br /><a href='#points.md'>points</a><br /></td>
<td valign='top'>
</td>
</tr></table>

**The Line class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#SetPoints.md'>SetPoints</a><br /><a href='#SetXdata.md'>SetXdata</a><br /><a href='#SetYdata.md'>SetYdata</a><br /><a href='#SetZdata.md'>SetZdata</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>alpha</font> ####
### <font color='#070'>Line.alpha</font> ###

> Get/Set the alpha (transparancy) of the line and markers. When this is < 1, the line cannot be anti-aliased, and it is drawn on top of any other wobjects.


#### <font color='#FFF'>lc</font> ####
### <font color='#070'>Line.lc</font> ###

> Get/Set the lineColor: the color of the line, as a 3-element tuple or as a single character string (shown in uppercase): Red, Green, Blue, Yellow, Cyan, Magenta, blacK, White.


#### <font color='#FFF'>ls</font> ####
### <font color='#070'>Line.ls</font> ###

> Get/Set the lineStyle: the style of the line.
> `*` Solid line: '-'
> `*` Dotted line: ':'
> `*` Dashed line: '--'
> `*` Dash-dot line: '-.' or '.-'
> `*` A line that is drawn between each pair of points: '+'
> `*` No line: '' or None.


#### <font color='#FFF'>lw</font> ####
### <font color='#070'>Line.lw</font> ###

> Get/Set the lineWidth: the width of the line in pixels. If zero, the line is not drawn.


#### <font color='#FFF'>mc</font> ####
### <font color='#070'>Line.mc</font> ###

> Get/Set the markerColor: The color of the face of the marker If None, '', or False, the marker face is not drawn (but the edge is).


#### <font color='#FFF'>mec</font> ####
### <font color='#070'>Line.mec</font> ###

> Get/Set the markerEdgeColor: the color of the edge of the marker.


#### <font color='#FFF'>mew</font> ####
### <font color='#070'>Line.mew</font> ###

> Get/Set the markerEdgeWidth: the width of the edge of the marker. If zero, no edge is drawn.


#### <font color='#FFF'>ms</font> ####
### <font color='#070'>Line.ms</font> ###

> Get/Set the markerStyle: the style of the marker.
> `*` Plus: '+'
> `*` Cross: 'x'
> `*` Square: 's'
> `*` Diamond: 'd'
> `*` Triangle (pointing up, down, left, right): '^', 'v', '<', '>'
> `*` Pentagram star: 'p' or '`*`'
> `*` Hexgram: 'h'
> `*` Point/cirle: 'o' or '.'
> `*` No marker: '' or None


#### <font color='#FFF'>mw</font> ####
### <font color='#070'>Line.mw</font> ###

> Get/Set the markerWidth: the width (bounding box) of the marker in (screen) pixels. If zero, no marker is drawn.


#### <font color='#FFF'>points</font> ####
### <font color='#070'>Line.points</font> ###

> Get a reference to the internal Pointset used to draw the line object. Note that this pointset is always 3D. One can modify this pointset in place, but note that a call to Draw() may be required to update the screen. (New in version 1.7.)




---


## Methods ##

#### <font color='#FFF'>SetPoints</font> ####
### <font color='#066'>Line.SetPoints(points)</font> ###

> Set x,y (and optionally z) data. The given argument can be anything that can be converted to a pointset. (From version 1.7 this method also works with 2D pointsets.)

> The data is copied, so changes to original data will not affect  the visualized points. If you do want this, use the points property.




#### <font color='#FFF'>SetXdata</font> ####
### <font color='#066'>Line.SetXdata(data)</font> ###

> Set the x coordinates of the points of the line.




#### <font color='#FFF'>SetYdata</font> ####
### <font color='#066'>Line.SetYdata(data)</font> ###

> Set the y coordinates of the points of the line.




#### <font color='#FFF'>SetZdata</font> ####
### <font color='#066'>Line.SetZdata(data)</font> ###

> Set the z coordinates of the points of the line.





---

