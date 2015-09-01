
---

#### <font color='#FFF'>basetexture</font> ####
# <font color='#00B'>class BaseTexture(parent, data)</font> #

Inherits from [Wobject](cls_Wobject.md), [Colormapable](cls_Colormapable.md).

Base texture class for visvis 2D and 3D textures.





**The BaseTexture class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#interpolate.md'>interpolate</a><br /><a href='#shader.md'>shader</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The BaseTexture class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Refresh.md'>Refresh</a><br /><a href='#SetClim.md'>SetClim</a><br /><a href='#SetData.md'>SetData</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>interpolate</font> ####
### <font color='#070'>BaseTexture.interpolate</font> ###

> Get/Set whether to interpolate the image when zooming in  (using linear interpolation).


#### <font color='#FFF'>shader</font> ####
### <font color='#070'>BaseTexture.shader</font> ###

> Get the shader object for the texture. This can  be used to add code of your own and customize the vertex and fragment part of the shader.




---


## Methods ##

#### <font color='#FFF'>!Refresh</font> ####
### <font color='#066'>BaseTexture.Refresh()</font> ###

> Refresh the data. If the numpy array was changed, calling this  function will re-upload the data to OpenGl, making the change visible. This can be done efficiently.




#### <font color='#FFF'>SetClim</font> ####
### <font color='#066'>BaseTexture.SetClim(min, max)</font> ###

> Set the contrast limits. Different than the property clim, this re-uploads the texture using different transfer functions. You should use this if your data has a higher contrast resolution than 8 bits. Takes a bit more time than clim though (which basically takes no time at all).




#### <font color='#FFF'>SetData</font> ####
### <font color='#066'>BaseTexture.SetData(data)</font> ###

> (Re)Set the data to display. If the data has the same shape as the data currently displayed, it can be updated very efficiently.

> If the data is an anisotripic array (vv.Aarray) the sampling and origin are (re-)applied.





---

