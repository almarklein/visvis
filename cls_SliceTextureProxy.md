
---

#### <font color='#FFF'>slicetextureproxy</font> ####
# <font color='#00B'>class SliceTextureProxy(<code>*</code>sliceTextures)</font> #

Inherits from [Wobject](cls_Wobject.md), [Colormapable](cls_Colormapable.md).

A proxi class for multiple SliceTexture instances. By making them children of an instance of this class, their properties can be  changed simultaneously.

This makes it possible to call volshow() and stay agnostic of how the volume is vizualized (using a 3D render, or with 3 slice  textures); all public texture-specific methods and properties are transferred to all children automatically.





**The SliceTextureProxy class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#axis.md'>axis</a><br /><a href='#edgeColor.md'>edgeColor</a><br /><a href='#edgeColor2.md'>edgeColor2</a><br /><a href='#index.md'>index</a><br /><a href='#interpolate.md'>interpolate</a><br /><a href='#isoThreshold.md'>isoThreshold</a><br /><a href='#renderStyle.md'>renderStyle</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>axis</font> ####
### <font color='#070'>SliceTextureProxy.axis</font> ###

> The axis of the slice in the volume to display.


#### <font color='#FFF'>edgeColor</font> ####
### <font color='#070'>SliceTextureProxy.edgeColor</font> ###

> The color of the edge of the slice (can be None).


#### <font color='#FFF'>edgeColor2</font> ####
### <font color='#070'>SliceTextureProxy.edgeColor2</font> ###

> The color of the edge of the slice when interacting.


#### <font color='#FFF'>index</font> ####
### <font color='#070'>SliceTextureProxy.index</font> ###

> The index of the slice in the volume to display.


#### <font color='#FFF'>interpolate</font> ####
### <font color='#070'>SliceTextureProxy.interpolate</font> ###

> Get/Set whether to interpolate the image when zooming in  (using linear interpolation).


#### <font color='#FFF'>isoThreshold</font> ####
### <font color='#070'>SliceTextureProxy.isoThreshold</font> ###

> Not available for SliceTextures. This  property is implemented to be able to produce a warning when it is used.


#### <font color='#FFF'>renderStyle</font> ####
### <font color='#070'>SliceTextureProxy.renderStyle</font> ###

> Not available for SliceTextures. This  property is implemented to be able to produce a warning when it is used.



---

