
---

#### <font color='#FFF'>texture3d</font> ####
# <font color='#00B'>class Texture3D(parent, data, renderStyle='mip')</font> #

Inherits from [BaseTexture](cls_BaseTexture.md).

A data type that represents structured data in three dimensions (a volume).

If the drawing hangs, your video drived decided to render in  software mode. This is unfortunately (as far as I know) not possible  to detect programatically. It might help if your data is shaped a  power of 2. The mip renderer is the 'easiest' for most systems to render.

Texture3D objects can be created with the function vv.volshow().





**The Texture3D class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#isoThreshold.md'>isoThreshold</a><br /><a href='#renderStyle.md'>renderStyle</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>isoThreshold</font> ####
### <font color='#070'>Texture3D.isoThreshold</font> ###

> Get/Set the isothreshold value used in the iso renderer.


#### <font color='#FFF'>renderStyle</font> ####
### <font color='#070'>Texture3D.renderStyle</font> ###

> Get/Set the render style to render the volumetric data:
    * MIP: maximum intensity projection. Shows the voxel with the  maxiumum value.
    * ISO: isosurface rendering. Casts ray until value is above  threshold. Ligthing is calculated at that voxel. Use together  with isoThreshold property.
    * RAY: ray casting. All voxels along the ray contribute to final  color, weighted by the alpha value.
    * EDGERAY: ray casting in which alpha is scaled with the gradient  magnitude.
    * LITRAY: ray casting in which all voxels are lit. Most pretty and most demanding for GPU.

> <b><u><font color='#A50'>Notes</font></u></b><br /><br />
> MIP and EDGERAY usually work out of the box. ISO requires playing with the isoThreshold property. RAY and LITRAY require playing with the alpha channel using the ColormapEditor wibject.

> If drawing takes really long, your system renders in software mode. Try rendering data that is shaped with a power of two. This  helps on some cards.

> You can also create your own render style by modyfying the GLSL code. See core/shaders\_src.py and the ShaderCode class for more info.



---

