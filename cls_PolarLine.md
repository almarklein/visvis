
---

#### <font color='#FFF'>polarline</font> ####
# <font color='#00B'>class PolarLine(parent, angle(radians), mag)</font> #

Inherits from [Line](cls_Line.md).

The Polarline class represents a set of points (locations) in world coordinates. This class can draw lines between the points,  markers at the point coordinates, or both.

There are several linestyles that can be used:
  * -  a solid line<br /><u>  <code>*</code> :   a dotted line</u><br /><font color='#020'></font>
  * --  a dashed line
  * -.  a dashdot line
  * .-  dito
  * +   draws a line between each pair of points (handy for visualizing for example vectore fields) If None, '' or False is given no line is drawn.

There are several marker styles that can be used:
  * `+`  a plus
  * `x`  a cross
  * `s`  a square
  * `d`  a diamond
  * `^v<>` an up-, down-, left- or rightpointing triangle
  * ```*``` or `p`  a (pentagram star)
  * `h`  a hexagram
  * `o` or `.`  a point/circle If None, '', or False is given, no marker is drawn.

<b><u><font color='#A50'>Performance tip</font></u></b><br /><br />
The s, o (and .) styles can be drawn using standard OpenGL points if alpha is 1 or if no markeredge is drawn. Otherwise point sprites are used, which can be slower on some cards (like ATI, Nvidia performs quite ok with with sprites)






---

