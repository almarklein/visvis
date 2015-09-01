
---

#### <font color='#FFF'>mesh</font> ####
# <font color='#00B'>class Mesh(parent, vertices, faces=None, normals=None, values=None, verticesPerFace=3)</font> #

Inherits from [Wobject](cls_Wobject.md), [BaseMesh](cls_BaseMesh.md), [Colormapable](cls_Colormapable.md).

A mesh is a generic object to visualize a 3D object made up of  polygons. These polygons can be triangles or quads. The mesh is affected by lighting and its material properties can be  changed using properties. The reference color and shading can be set individually for the faces and edges (using the faceColor, edgeColor, faceShading and edgeShading properties).

A mesh can also be created from another mesh using Mesh(parent, otherMesh), where otherMesh should be an instance of BaseMesh.

The old signature may also be used, but will be removed in future versions: Mesh(vertices, normals=None, faces=None, colors=None, texcords=None, verticesPerFace=3)

<b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>vertices : Nx3 numpy array </u><br /><font color='#020'> The vertex positions in 3D space.<br /></font><u>faces : (optional) numpy array or list of indices</u><br /><font color='#020'> Defines the faces. If this array is Nx3 or Nx4, verticesPerFace is inferred from this array. Faces should be of uint8, uint16 or uint32 (if it is not, the data is converted to uint32). The front of the face is defined using the right-hand-rule. normals :(optional) Nx3 numpy array The vertex normals. If not given, they are calcululated from the vertices.<br /></font><u>values : (optional) Nx1, Nx2, Nx3 or Nx4 numpy array</u><br /><font color='#020'> The value data for each vertex. If Nx1, they represent the indices in the colormap. If Nx2, they represent the texture coordinates for the texturegiven with SetTexture(). If Nx3 or Nx4 they represent the ambient and diffuse color for each vertex. <br /></font><u>verticesPerFace : 3 or 4</u><br /><font color='#020'> Determines whether the faces are triangles or quads. If faces is specified and is 2D, the number of vertices per face is determined from that array.</font>

<b><u><font color='#A50'>Note on texture mapping</font></u></b><br /><br />
The texture color is multiplied after the ambient and diffuse lighting calculations, but before calculating the specular component.





**The Mesh class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#ambient.md'>ambient</a><br /><a href='#ambientAndDiffuse.md'>ambientAndDiffuse</a><br /><a href='#cullFaces.md'>cullFaces</a><br /><a href='#diffuse.md'>diffuse</a><br /><a href='#edgeColor.md'>edgeColor</a><br /></td>
<td valign='top'>
<a href='#edgeShader.md'>edgeShader</a><br /><a href='#edgeShading.md'>edgeShading</a><br /><a href='#emission.md'>emission</a><br /><a href='#faceColor.md'>faceColor</a><br /><a href='#faceShader.md'>faceShader</a><br /></td>
<td valign='top'>
<a href='#faceShading.md'>faceShading</a><br /><a href='#shapeShader.md'>shapeShader</a><br /><a href='#shininess.md'>shininess</a><br /><a href='#specular.md'>specular</a><br /><a href='#useNativeShading.md'>useNativeShading</a><br /></td>
</tr></table>

**The Mesh class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#SetTexture.md'>SetTexture</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>ambient</font> ####
### <font color='#070'>Mesh.ambient</font> ###

> Get/Set the ambient reflection color of the material. Ambient light is the light that is everywhere, coming from all directions,  independent of the light position.

> The value can be a 3- or 4-element tuple, a character in  "rgbycmkw", or a scalar between 0 and 1 that indicates the  fraction of the reference color.


#### <font color='#FFF'>ambientAndDiffuse</font> ####
### <font color='#070'>Mesh.ambientAndDiffuse</font> ###

> Set the diffuse and ambient component simultaneously. Usually, you want to give them the same value. Getting returns the diffuse component.


#### <font color='#FFF'>cullFaces</font> ####
### <font color='#070'>Mesh.cullFaces</font> ###

> Get/Set the culling of faces. Values can be 'front', 'back', or None (default). If 'back',  backfacing faces are not drawn. If 'front', frontfacing faces are not drawn. The front of the face is defined using the  right-hand-rule.


#### <font color='#FFF'>diffuse</font> ####
### <font color='#070'>Mesh.diffuse</font> ###

> Get/Set the diffuse reflection color of the material. Diffuse light comes from one direction, so it's brighter if it comes squarely down on a surface than if it barely glances off the  surface. It depends on the light position how a material is lit.

> The value can be a 3- or 4-element tuple, a character in  "rgbycmkw", or a scalar between 0 and 1 that indicates the  fraction of the reference color.


#### <font color='#FFF'>edgeColor</font> ####
### <font color='#070'>Mesh.edgeColor</font> ###

> Get/Set the edge reference color of the object. If the ambient, diffuse or emissive properties specify a scalar, that scalar represents the fraction of **this** color for the edges.


#### <font color='#FFF'>edgeShader</font> ####
### <font color='#070'>Mesh.edgeShader</font> ###

> Get the shader object for the edges. This can  be used to add code of your own and customize the vertex and fragment part of the shader.


#### <font color='#FFF'>edgeShading</font> ####
### <font color='#070'>Mesh.edgeShading</font> ###

> Get/Set the type of shading to apply for the edges.
    * None - Do not show the faces.
    * 'plain' - Display the faces in the faceColor (without lighting).
    * 'flat' - Lit shading uniform for each face
    * 'gouraud' - Lighting is calculated at vertices and interpolated  over the face.
    * 'smooth' - Lighting is calculated for each fragment (aka  phong-shading or phong-interpolation).

> <b><u><font color='#A50'>Notes</font></u></b><br /><br />
> In native mode 'smooth' falls back to 'gouraud'. In both native and nonnative mode the blinn-phong reflectance model  is used.


#### <font color='#FFF'>emission</font> ####
### <font color='#070'>Mesh.emission</font> ###

> Get/Set the emission color of the material. It is the  "self-lighting" property of the material, and usually only makes sense for objects that represent lamps or candles etc.

> The value can be a 3- or 4-element tuple, a character in  "rgbycmkw", or a scalar between 0 and 1 that indicates the  fraction of the reference color.


#### <font color='#FFF'>faceColor</font> ####
### <font color='#070'>Mesh.faceColor</font> ###

> Get/Set the face reference color of the object. If the ambient, diffuse or emissive properties specify a scalar, that scalar represents the fraction of **this** color for the faces.


#### <font color='#FFF'>faceShader</font> ####
### <font color='#070'>Mesh.faceShader</font> ###

> Get the shader object for the faces. This can  be used to add code of your own and customize the vertex and fragment part of the shader.


#### <font color='#FFF'>faceShading</font> ####
### <font color='#070'>Mesh.faceShading</font> ###

> Get/Set the type of shading to apply for the faces.
    * None - Do not show the faces.
    * 'plain' - Display the faces in the faceColor (without lighting).
    * 'flat' - Lit shading uniform for each face
    * 'gouraud' - Lighting is calculated at vertices and interpolated  over the face.
    * 'smooth' - Lighting is calculated for each fragment (aka  phong-shading or phong-interpolation).
    * 'toon' - A cartoonish look (aka cel-shading).

> <b><u><font color='#A50'>Notes</font></u></b><br /><br />
> In native mode 'smooth' and 'toon' fall back to 'gouraud'. In both native and nonnative mode the blinn-phong reflectance model  is used.


#### <font color='#FFF'>shapeShader</font> ####
### <font color='#070'>Mesh.shapeShader</font> ###

> Get the shader object for the shape. This can  be used to add code of your own and customize the vertex and fragment part of the shader.


#### <font color='#FFF'>shininess</font> ####
### <font color='#070'>Mesh.shininess</font> ###

> Get/Set the shininess value of the material as a number between 0 and 128. The higher the value, the brighter and more focussed the specular spot, thus the shinier the material appears to be.


#### <font color='#FFF'>specular</font> ####
### <font color='#070'>Mesh.specular</font> ###

> Get/Set the specular reflection color of the material. Specular light represents the light that comes from the light source and bounces off a surface in a particular direction. It is what makes  materials appear shiny.

> The value can be a 3- or 4-element tuple, a character in  "rgbycmkw", or a scalar between 0 and 1 that indicates the  fraction of white (1,1,1).


#### <font color='#FFF'>useNativeShading</font> ####
### <font color='#070'>Mesh.useNativeShading</font> ###

> Get/set whether to use the native OpenGl shading. The default is False, which means that GLSL-based shading is used, allowing for more advanced shader styles.

> Note that regardless of the value of this property, native shading is used if the hardward does not support GLSL (OpenGl version<2).




---


## Methods ##

#### <font color='#FFF'>SetTexture</font> ####
### <font color='#066'>Mesh.SetTexture(data)</font> ###

> Set the texture image to map to the mesh. Use None as an argument to remove the texture.





---

