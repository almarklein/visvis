
---

#### <font color='#FFF'>pointset</font> ####
# <font color='#00B'>class Pointset(ndim)</font> #

Inherits from [BasePoints](cls_BasePoints.md).

Represents a set of points or vectors (of any dimension).

Can also be initialized using: Pointset(<ndim times npoints numpy array>)

A pointset provides an efficient way to store points. Internally the points are stored in a numpy array that is resized by a factor of two when more space is required. This makes adding and removing points (from the end) very efficient. Also mathematical  operations can be applied on all the points in the set efficiently.

<b><u><font color='#A50'>Notes on slicing and indexing</font></u></b><br />
  * pp`[`7`]`: When indexing, the corresponding Point instance is get/set.
  * pp`[`7:20`]`: When slicing, a new poinset (subset) is get/set.
  * pp`[`4:9,3`]` When using two indices or slices, the indices are applied to  the internal data. (In this example returning the z-value for points 4 till 8.)

<b><u><font color='#A50'>Math</font></u></b><br /><br />
The same mathematical operations that can be applied to a Point  instance can also be applied to a Pointset instance. The operation is applied to all points in the set. For example pp.distance(3,4) returns an array with the distances of all points in pp to (3,4).

<b><u><font color='#A50'>Example</font></u></b><br />
```
a  = <...>          # an existing 100x2 array
pp1 = Pointset(2)   # pointset with two dimensions
pp2 = Pointset(a)   # dito    
pp1.append(3,4)     # add a point
pp1.append(p)       # add an existing point p
pp1.extend(pp1)     # extend pp1 to itself
pp2`[`:4`]` = pp1       # replace first four points of pp2
pp`[`1`]`               # returns the point (3,4) (as a Point instance)
pp`[`1,0`]`             # returns the value 3.0
pp`[`:,1`]`             # get all y values
pp.contains(3,4)    # will return True

```


**The Pointset class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#data.md'>data</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The Pointset class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#append.md'>append</a><br /><a href='#clear.md'>clear</a><br /><a href='#contains.md'>contains</a><br /><a href='#copy.md'>copy</a><br /><a href='#extend.md'>extend</a><br /></td>
<td valign='top'>
<a href='#insert.md'>insert</a><br /><a href='#pop.md'>pop</a><br /><a href='#remove.md'>remove</a><br /><a href='#remove_all.md'>remove_all</a><br /></td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>data</font> ####
### <font color='#070'>Pointset.data</font> ###

> Get a view of the data. Note that internally the points  are stored in a numpy array that is in general longer than the amount of points (at most 4 times as long). This is to  make adding/removing points much faster by prevening reallocating  memory. The internal array is resized with a factor two when  necesary. This property returns a (sub)view of that array and is  always 2D.




---


## Methods ##

#### <font color='#FFF'>append</font> ####
### <font color='#066'>Pointset.append(<code>*</code>p)</font> ###

> Append a point to this pointset.  If p is not an instance of the Point class,  the constructor  of Point is called to create one from the given argument. This  enables pp.append(x,y,z)




#### <font color='#FFF'>clear</font> ####
### <font color='#066'>Pointset.clear()</font> ###

> Remove all points in the pointset.




#### <font color='#FFF'>contains</font> ####
### <font color='#066'>Pointset.contains(<code>*</code>p)</font> ###

> Check whether a point is already in this set.




#### <font color='#FFF'>copy</font> ####
### <font color='#066'>Pointset.copy()</font> ###

> Return a copy of this pointset.




#### <font color='#FFF'>extend</font> ####
### <font color='#066'>Pointset.extend(pp)</font> ###

> Extend this pointset with another pointset, thus combining the two.          If pp is not an instance of the Pointset class, the constructor  of Pointset is called to create one from the given argument.




#### <font color='#FFF'>insert</font> ####
### <font color='#066'>Pointset.insert(index, <code>*</code>p)</font> ###

> Insert a point at the given index.




#### <font color='#FFF'>pop</font> ####
### <font color='#066'>Pointset.pop(index=-1)</font> ###

> Removes and returns a point from the pointset. Removes the last by default (which is more efficient than popping from anywhere else).




#### <font color='#FFF'>remove</font> ####
### <font color='#066'>Pointset.remove(<code>*</code>p)</font> ###

> Remove first occurance of the given point from the list.  Produces an error if such a point is not present. See also remove\_all()




#### <font color='#FFF'>remove_all</font> ####
### <font color='#066'>Pointset.remove_all(<code>*</code>p)</font> ###

> Remove all occurances of the given point. If there is no occurance, no action is taken.





---

