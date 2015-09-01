
---

#### <font color='#FFF'>point</font> ####
# <font color='#00B'>class Point(x,y,<code>[</code>z,<code>[</code>...])</font> #

Inherits from [BasePoints](cls_BasePoints.md).

Represents a point or vector (of any dimension).

This class implements many usefull operators such as addition and multiplication, and provides common mathematical operations that can be applied to points and pointsets.

<b><u><font color='#A50'>Example</font></u></b><br />
```
p1 = Point(3.2,4)   # a 2D point
p2 = p1.copy()      # make a copy
p1`[`0`]` = 9           # set the first element
p1.x                # convenience property (.y and .z also available)
p1.xi               # idem, but rounded to nearest integer
p1.distance(p2)     # calculate distance
p1 + p2             # calculate the addition of the two vectors
p2 = p1`*`2           # scale vector
p2 = p1 `*` p2        # even for each dimension seperately
p2 = p2.normalize() # make unit length

```


**The Point class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#data.md'>data</a><br /><a href='#x.md'>x</a><br /><a href='#xi.md'>xi</a><br /><a href='#y.md'>y</a><br /><a href='#yi.md'>yi</a><br /><a href='#z.md'>z</a><br /><a href='#zi.md'>zi</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The Point class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#copy.md'>copy</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>data</font> ####
### <font color='#070'>Point.data</font> ###

> Get the point as the (2D) numpy array it is stored in.


#### <font color='#FFF'>x</font> ####
### <font color='#070'>Point.x</font> ###

> Get/set p`[`0`]`.

#### <font color='#FFF'>xi</font> ####
### <font color='#070'>Point.xi</font> ###

> Get p`[`0`]` rounded to the nearest integer, for indexing.

#### <font color='#FFF'>y</font> ####
### <font color='#070'>Point.y</font> ###

> Get/set p`[`1`]`.

#### <font color='#FFF'>yi</font> ####
### <font color='#070'>Point.yi</font> ###

> Get p`[`1`]` rounded to the nearest integer, for indexing.

#### <font color='#FFF'>z</font> ####
### <font color='#070'>Point.z</font> ###

> Get/set p`[`2`]`.

#### <font color='#FFF'>zi</font> ####
### <font color='#070'>Point.zi</font> ###

> Get p`[`2`]` rounded to the nearest integer, for indexing.



---


## Methods ##

#### <font color='#FFF'>copy</font> ####
### <font color='#066'>Point.copy()</font> ###

> Get a copy of this point.





---

