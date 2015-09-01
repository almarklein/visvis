
---

#### <font color='#FFF'>aarray</font> ####
# <font color='#00B'>class Aarray(shape_or_array, sampling=None, origin=None, fill=None, dtype='float32', <code>*</code><code>*</code>kwargs)</font> #

Inherits from [ndarray](cls_ndarray.md).

Anisotropic array; inherits from numpy.ndarray and adds a sampling  and origin property which gives the sample distance and offset for each dimension.

<b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>shape_or_array : shape-tuple or numpy.ndarray</u><br /><font color='#020'> Specifies the shape of the produced array. If an array instance is given, the returned Aarray is a view of the same data (i.e. no data is copied).<br /></font><u>sampling : tuple of ndim elements</u><br /><font color='#020'> Specifies the sample distance (i.e. spacing between elements) for each dimension. Default is all ones.<br /></font><u>origin : tuple of ndim elements</u><br /><font color='#020'> Specifies the world coordinate at the first element for each dimension. Default is all zeros.<br /></font><u>fill : scalar (optional)</u><br /><font color='#020'> If given, and the first argument is not an existing array, fills the array with this given value.<br /></font><u>dtype : any valid numpy data type</u><br /><font color='#020'> The type of the data</font>

All extra arguments are fed to the constructor of numpy.ndarray.

<b><u><font color='#A50'>Implemented properties and methods</font></u></b><br />
  * sampling - The distance between samples as a tuple
  * origin - The origin of the data as a tuple
  * get\_start() - Get the origin of the data as a Point instance
  * get\_end() - Get the end of the data as a Point instance
  * get\_size() - Get the size of the data as a Point instance
  * sample() - Sample the value at the given point
  * point\_to\_index() - Given a poin, returns the index in the array
  * index\_to\_point() - Given an index, returns the world coordinate

<b><u><font color='#A50'>Slicing</font></u></b><br /><br />
This class is aware of slicing. This means that when obtaining a part of the data (for exampled 'data`[`10:20,::2`]`'), the origin and sampling of the resulting array are set appropriately.

When applying mathematical opertaions to the data, or applying  functions that do not change the shape of the data, the sampling and origin are copied to the new array. If a function does change the shape of the data, the sampling are set to all zeros and ones for the origin and sampling, respectively.

<b><u><font color='#A50'>World coordinates vs tuples</font></u></b><br /><br />
World coordinates are expressed as Point instances (except for the  "origin" property). Indices as well as the "sampling" and "origin"  attributes are expressed as tuples in z,y,x order.





**The Aarray class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#origin.md'>origin</a><br /><a href='#sampling.md'>sampling</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The Aarray class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#get_end.md'>get_end</a><br /><a href='#get_size.md'>get_size</a><br /><a href='#get_start.md'>get_start</a><br /><a href='#index_to_point.md'>index_to_point</a><br /><a href='#point_to_index.md'>point_to_index</a><br /><a href='#sample.md'>sample</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>origin</font> ####
### <font color='#070'>Aarray.origin</font> ###

> A tuple with the origin for each dimension.

#### <font color='#FFF'>sampling</font> ####
### <font color='#070'>Aarray.sampling</font> ###

> A tuple with the sample distance for each dimension.



---


## Methods ##

#### <font color='#FFF'>get_end</font> ####
### <font color='#066'>Aarray.get_end()</font> ###

> Get the end of the array expressed in world coordinates.




#### <font color='#FFF'>get_size</font> ####
### <font color='#066'>Aarray.get_size()</font> ###

> Get the size (as a vector) of the array expressed in world coordinates.




#### <font color='#FFF'>get_start</font> ####
### <font color='#066'>Aarray.get_start()</font> ###

> Get the origin of the array expressed in world coordinates.  Differs from the property 'origin' in that this method returns a point rather than indices z,y,x.




#### <font color='#FFF'>index_to_point</font> ####
### <font color='#066'>Aarray.index_to_point(<code>*</code>index)</font> ###

> Given a multidimensional index, get the corresponding point in world coordinates.




#### <font color='#FFF'>point_to_index</font> ####
### <font color='#066'>Aarray.point_to_index(point, non_on_index_error=False)</font> ###

> Given a point returns the sample index (z,y,x,..) closest to the given point. Returns a tuple with as many elements  as there are dimensions.

> If the point is outside the array an IndexError is raised by default, and None is returned when non\_on\_index\_error == True.




#### <font color='#FFF'>sample</font> ####
### <font color='#066'>Aarray.sample(point, default=None)</font> ###

> Take a sample of the array, given the given point in world-coordinates, i.e. transformed using sampling. By default raises an IndexError if the point is not inside the array, and returns the value of "default" if it is given.





---

