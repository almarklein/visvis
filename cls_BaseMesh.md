
---

#### <font color='#FFF'>basemesh</font> ####
# <font color='#00B'>class BaseMesh(vertices, faces=None, normals=None, values=None, verticesPerFace=3)</font> #

Inherits from [object](cls_object.md).

The BaseMesh class represents a mesh in its pure mathematical form (without any visualization properties). Essentially, it serves as a container for the vertices, normals, faces, and values.

See the Mesh and OrientableMesh classes for representations that include visualization properties.

The old signature may also be used, but will be removed in future versions: BaseMesh(vertices, normals=None, faces=None, colors=None, texcords=None, verticesPerFace=3)





**The BaseMesh class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#SetColors.md'>SetColors</a><br /><a href='#SetFaces.md'>SetFaces</a><br /><a href='#SetNormals.md'>SetNormals</a><br /><a href='#SetTexcords.md'>SetTexcords</a><br /><a href='#SetValues.md'>SetValues</a><br /><a href='#SetVertices.md'>SetVertices</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Methods ##

#### <font color='#FFF'>SetColors</font> ####
### <font color='#066'>BaseMesh.SetColors(colors)</font> ###

> Deprecated: use SetValues() instead.

> Set the color data as a Nx3 numpy array or as a 3D Pointset.  Use None as an argument to remove the color data.






#### <font color='#FFF'>SetFaces</font> ####
### <font color='#066'>BaseMesh.SetFaces(faces)</font> ###

> Set the faces data. This can be either a list, a 1D numpy array, a Nx3 numpy array, or a Nx4 numpy array. In the latter two cases the type is set to GL\_TRIANGLES or GL\_QUADS respectively.

> The front of the face is defined using the right-hand-rule.




#### <font color='#FFF'>SetNormals</font> ####
### <font color='#066'>BaseMesh.SetNormals(normals)</font> ###

> Set the normal data as a Nx3 numpy array or as a 3D Pointset.




#### <font color='#FFF'>SetTexcords</font> ####
### <font color='#066'>BaseMesh.SetTexcords(texcords)</font> ###

> Deprecated: use SetValues() instead.

> Set the texture coordinates as a Nx2 numpy array or as a 2D Pointset. Use None as an argument to turn off the texture.




#### <font color='#FFF'>SetValues</font> ####
### <font color='#066'>BaseMesh.SetValues(values, setClim=False)</font> ###

> Set the value data for each vertex. This can be given as:
    * Nx1 array, representing the indices in a colormap
    * Nx2 array, representing the texture coordinates in a texture
    * Nx3 array, representing the RGB values at each vertex
    * Nx4 array, representing the RGBA values at each vertex

> Use None as an argument to remove the values data.




#### <font color='#FFF'>SetVertices</font> ####
### <font color='#066'>BaseMesh.SetVertices(vertices)</font> ###

> Set the vertex data as a Nx3 numpy array or as a 3D Pointset.





---

