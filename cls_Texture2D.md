
---

#### <font color='#FFF'>texture2d</font> ####
# <font color='#00B'>class Texture2D(parent, data)</font> #

Inherits from [BaseTexture](cls_BaseTexture.md).

A data type that represents structured data in two dimensions (an image). Supports grayscale, RGB,  and RGBA images.

Texture2D objects can be created with the function vv.imshow().





**The Texture2D class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#aa.md'>aa</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>aa</font> ####
### <font color='#070'>Texture2D.aa</font> ###

> Get/Set anti aliasing quality.
    * 0 or False for no anti aliasing
    * 1 for anti aliasing using 3-element kernel.
    * 2 for anti aliasing using 5-element kernel.
    * 3 for anti aliasing using 7-element kernel.

> Higher numbers result in better quality anti-aliasing, but may be slower on older hardware.

> Note that in previous versions of visvis, this property influenced the **amount** of aliasing. We now use a better kernel (Lanczos instead  of Gaussian), such that the amount can be fixed without negatively affecting the visualization.



---

