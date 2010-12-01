#   This file is part of VISVIS.
#    
#   VISVIS is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as 
#   published by the Free Software Foundation, either version 3 of 
#   the License, or (at your option) any later version.
# 
#   VISVIS is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
# 
#   You should have received a copy of the GNU Lesser General Public 
#   License along with this program.  If not, see 
#   <http://www.gnu.org/licenses/>.
#
#   Copyright (C) 2010 Almar Klein

""" Module polygonalModeling

This module defined the Mesh object that represents a polygonal model.
It also defines lights and algorithmic for managing polygonal models.

"""

from pypoints import Point, Pointset, is_Point, is_Pointset
from misc import Property, PropWithDraw, DrawAfter, getColor
from base import Wobject, OrientationForWobjects_mixClass
from textures import TextureObjectToVisualize, Colormap

import numpy as np
import OpenGL.GL as gl


def _testColor(value, canBeScalar=True):
    """ _testColor(value)
    Tests a color whether it is a sequence of 3 or 4 values.
    It returns a 4 element tuple or raises an error if the suplied
    data is incorrect.
    """
    
    # Deal with named colors
    if isinstance(value, basestring):
        value = getColor(value)
    
    # Value can be a scalar
    if canBeScalar and isinstance(value, (int, float)):
        if value <= 0:
            value = 0.0
        if value >= 1:
            value = 1.0
        return value
    
    # Otherwise it must be a sequence of 3 or 4 elements
    elif not hasattr(value, '__len__'):
        raise ValueError("Given value can not represent a color.")
    elif len(value) == 4:
        return (value[0], value[1], value[2], value[3])
    elif len(value) == 3:
        return (value[0], value[1], value[2], 1.0)
    else:
        raise ValueError("Given value can not represent a color.")


def _getColor(color, ref):
        """ _getColor(color, reference)
        Get the real color as a 4 element tuple, using the reference
        color if the given color is a scalar.
        """
        if isinstance(color, float):
            return (color*ref[0], color*ref[1], color*ref[2], ref[3])
        else:
            return color


# todo: implement spot light and attenuation
class Light(object):
    """ A Light object represents a light source in the scene. It 
    determines how lit objects (such as Mesh objects) are visualized.
    
    Each axes has 8 light sources, of which only the 0th is turned on
    by default. De 0th light source provides the ambient light in the
    scene (the ambient component is 0 by default for the other light
    sources). Obtain the lights using the axes.light0 and axes.lights
    properties.
    
    The 0th light source is a directional camera light by default; it
    shines in the direction in which you look. The other lights are 
    oriented at the origin by default.
    """
    
    def __init__(self, axes, index):
        
        # Store axes and index of the light (OpenGl can handle up to 8 lights)
        self._axes = axes.GetWeakref()
        self._index = index
        self._on = False
        
        # The three light properties
        self._color = (1, 1, 1, 1)
        self._ambient = 0.0
        self._diffuse = 1.0
        self._specular = 1.0
        
        # The main light has an ambien component by default
        if index == 0:
            self._ambient = 0.2
        
        # Position or direction
        if index == 0:
            self._position = (0,0,1,0)
            self._camLight = True
        else:
            self._position = (0,0,0,1)
            self._camLight = False
    
    
    def Draw(self):
        # Draw axes
        axes = self._axes()
        if axes:
            axes.Draw()
    
    @PropWithDraw
    def color():
        """ Get/Set the reference color of the light. If the ambient,
        diffuse or specular properties specify a scalar, that scalar
        represents the fraction of *this* color. 
        """
        def fget(self):
            return self._color
        def fset(self, value):
            self._color = _testColor(value, True)
    
    
    @PropWithDraw
    def ambient():
        """ Get/Set the ambient color of the light. This is the color
        that is everywhere, coming from all directions, independent of 
        the light position. 
        
        The value can be a 3- or 4-element tuple, a character in 
        "rgbycmkw", or a scalar between 0 and 1 that indicates the 
        fraction of the reference color.
        """
        def fget(self):
            return self._ambient
        def fset(self, value):
            self._ambient = _testColor(value)
    
    
    @PropWithDraw
    def diffuse():
        """ Get/Set the diffuse color of the light. This component is the
        light that comes from one direction, so it's brighter if it comes
        squarely down on a surface than if it barely glances off the 
        surface. It depends on the light position how a material is lit.
        
        """
        def fget(self):
            return self._diffuse
        def fset(self, value):
            self._diffuse = _testColor(value)
    
    
    @PropWithDraw
    def specular():
        """ Get/Set the specular color of the light. This component
        represents the light that comes from the light source and bounces
        off a surface in a particular direction. This is what makes 
        materials appear shiny.
        
        The value can be a 3- or 4-element tuple, a character in 
        "rgbycmkw", or a scalar between 0 and 1 that indicates the 
        fraction of the reference color.
        """
        def fget(self):
            return self._specular
        def fset(self, value):
            self._specular = _testColor(value)
    
    
    @PropWithDraw
    def position():
        """ Get/Set the position of the light. Can be represented as a
        3 or 4 element tuple. If the fourth element is a 1, the light
        has a position, if it is a 0, it represents a direction (i.o.w. the
        light is a directional light, like the sun).
        """
        def fget(self):
            return self._position
        def fset(self, value):
            if len(value) == 3:
                self._position = value[0], value[1], value[2], 1
            elif len(value) == 4:
                self._position = value[0], value[1], value[2], value[3]
            else:
                tmp = "Light position should be a 3 or 4 element sequence."
                raise ValueError(tmp)
    
    
    @PropWithDraw
    def isDirectional():
        """ Get/Set whether the light is a directional light. A directional
        light has no real position (it can be thought of as infinitely far
        away), but shines in a particular direction. The sun is a good
        example of a directional light.
        """
        def fget(self):
            return self._position[3] == 0
        def fset(self, value):
            # Get fourth element
            if value:
                fourth = 0
            else:
                fourth = 1
            # Set position
            tmp = self._position 
            self._position = tmp[0], tmp[1], tmp[2], fourth
    
    
    @PropWithDraw
    def isCamLight():
        """ Get/Set whether the light is a camera light. A camera light
        moves along with the camera, like the lamp on a miner's hat.
        """
        def fget(self):
            return self._camLight
        def fset(self, value):
            self._camLight = bool(value)
    
    
    @DrawAfter
    def On(self, on=True):
        """ On(on=True)
        Turn the light on.
        """
        self._on = bool(on)
    
    
    @DrawAfter
    def Off(self):
        """ Off()
        Turn the light off.
        """
        self._on = False
    
    
    @property
    def isOn(self):
        return self._on
    
    
    def _Apply(self):
        """ _Apply()
        Apply the light position and other properties.
        """
        thisLight = gl.GL_LIGHT0 + self._index
        if self._on:
            # Enable and set position            
            gl.glEnable(thisLight)
            gl.glLightfv(thisLight, gl.GL_POSITION, self._position)
            # Set colors
            amb, dif, spe = gl.GL_AMBIENT, gl.GL_DIFFUSE, gl.GL_SPECULAR
            gl.glLightfv(thisLight, amb, _getColor(self._ambient, self._color))
            gl.glLightfv(thisLight, dif, _getColor(self._diffuse, self._color))
            gl.glLightfv(thisLight, spe, _getColor(self._specular, self._color))
        else:
            gl.glDisable(thisLight)



def check3dArray(value):
    """ Check the shape of vertex/color/texcord data. 
    Always returns a numpy array. 
    """
    if isinstance(value, np.ndarray):
        if not (value.ndim == 2 and value.shape[1] == 3):
            raise ValueError()
        if value.dtype == np.float32:
            return value
        else:
            return value.astype(np.float32)
    elif is_Pointset(value):
        if not value.ndim==3:
            raise ValueError()
        return value.data
    else:
        raise ValueError()


class BaseMesh(object):
    """ BaseMesh(vertices, normals=None, faces=None,
            colors=None, texcords=None, verticesPerFace=3)
        
        The BaseMesh class represents a mesh in its pure mathematical
        form (without any visualization properties). Essentially, it
        serves as a container for the vertices, normals, faces, colors,
        and texcords.
        
        See the Mesh and OrientableMesh classes for representations that
        include visualization properties.
        """
    
    def __init__(self, vertices, normals=None, faces=None,
            colors=None, texcords=None, verticesPerFace=3):
        
        # Set verticesPerFace first (can be reset by faces)
        verticesPerFace = int(verticesPerFace)
        if verticesPerFace in [3, 4]:
            self._verticesPerFace = verticesPerFace
        else:        
            raise ValueError('VerticesPerFace should be 3 or 4.')
        
        # Set all things (checks are performed in set methods)
        self.SetVertices(vertices)
        self.SetNormals(normals)
        self.SetFaces(faces)
        self.SetColors(colors)
        self.SetTexcords(texcords)
    
    
    @DrawAfter
    def SetVertices(self, vertices):
        """ SetVertices(vertices)
        Set the vertex data as a Nx3 numpy array or as a 3D Pointset. 
        """
        try:
            self._vertices = check3dArray(vertices)
        except ValueError:
            raise ValueError("Vertices should represent an array of 3D vertices.")
    
    
    @DrawAfter
    def SetNormals(self, normals):
        """ SetNormals(normals)
        Set the normal data as a Nx3 numpy array or as a 3D Pointset. 
        """
        if normals is not None:
            try:
                self._normals = check3dArray(normals)
            except ValueError:
                raise ValueError("Normals should represent an array of 3D vertices.")
        else:
            self._normals = None
    
    
    @DrawAfter
    def SetColors(self, colors):
        """ SetColors(colors)
        Set the color data as a Nx3 numpy array or as a 3D Pointset. 
        Use None as an argument to remove the color data.
        """
        if colors is not None:
            # Scale
            if colors.dtype in [np.float32, np.float64] and colors.max()<1.1:
                pass
            elif colors.dtype == np.uint8:
                colors = colors.astype(np.float32) / 256.0
            else:
                mi, ma = colors.min(), colors.max()
                colors = (colors.astype(np.float32) - mi) / (ma-mi)
            # Check shape
            try:
                self._colors = check3dArray(colors)
            except ValueError:
                raise ValueError("Colors should represent an array of 3D vertices.")
        else:
            self._colors = None
    
    
    @DrawAfter
    def SetTexcords(self, texcords):
        """ SetTexcords(texcords)
        Set the texture coordinates as a Nx2 numpy array or as a 2D Pointset.
        Use None as an argument to turn off the texture.
        """
        if texcords is not None:
        
            if isinstance(texcords, np.ndarray):
                # Test dimensions
                if texcords.ndim == 2 and texcords.shape[1] == 2:
                    pass # Texture coordinates
                elif texcords.ndim == 1:
                    pass # Colormap entries
                else:
                    raise ValueError("Texture coordinates must be 2D or 1D.")
                # Test data type
                if texcords.dtype == np.float32:
                    self._texcords = texcords
                else:
                    self._texcords = texcords.astype(np.float32)
            
            elif is_Pointset(texcords):
                if not texcords.ndim==2:
                    raise ValueError("Texture coordinates must be 2D or 1D.")
                self._texcords = texcords.data
            else:
                raise ValueError("Texture coordinates must be a numpy array or Pointset.")
        
        else:
            self._texcords = None
    
    
    @DrawAfter
    def SetFaces(self, faces):
        """ SetFaces(faces)
        Set the faces data. This can be either a list, a 1D numpy array,
        a Nx3 numpy array, or a Nx4 numpy array. In the latter two cases
        the type is set to GL_TRIANGLES or GL_QUADS respectively.
        """
        
        # Check and store faces
        if faces is not None:
            if isinstance(faces, list):
                self._faces = np.array(faces, dtype=np.uint32)
            elif isinstance(faces, np.ndarray):
                # Check shape
                if faces.ndim==1:
                    pass # ok
                elif faces.ndim==2 and faces.shape[1] in [3,4]:
                    self._verticesPerFace = faces.shape[1]
                else:
                    tmp = 'Faces should represent a list or, 1D, Nx3 or Nx4'
                    raise ValueError(tmp + ' numpy array.')
                # Check data type
                if faces.dtype in [np.uint8, np.uint16, np.uint32]:
                    self._faces = faces.reshape((faces.size,))
                else:                    
                    self._faces = faces.astype(np.uint32)
                    self._faces.shape = (faces.size,)
            else:
                raise ValueError("Faces should be a list or numpy array.")
            # Check
            if self._faces.min() < 0:
                raise ValueError("Face data should be non-negative integers.")
            if self._vertices is not None:
                if self._faces.max() >= len(self._vertices):
                    raise ValueError("Face data references non-existing vertices.")
        else:
            self._faces = None
    
    
    def _GetFaces(self):
        """ _GetFaces()
        Get 2D array with face indices (even if the mesh has no faces array).
        To be used for mesh processing. On the 0th axis are the different
        faces. Along the 1st axis are the different vertex indices that
        make up that face. 
        """   
        if self._faces is None:
            faces = np.arange(len(self._vertices))
        else:
            faces = self._faces
        # Reshape
        vpf = self._verticesPerFace
        Nfaces = faces.size / vpf
        return faces.reshape((Nfaces, vpf))


# Import here, because they may require BaseMesh
import processing

class Mesh(Wobject, BaseMesh):
    """ Mesh(parent, vertices, normals=None, faces=None, 
        colors=None, texcords=None, verticesPerFace=3)
    
    A mesh is a generic object to visualize a 3D object made up of 
    polygons. These polygons can be triangles or quads. The mesh
    is affected by lighting and its material properties can be 
    changed using properties. The reference color and shading can
    be set individually for the faces and edges (using the faceColor,
    edgeColor, faceShading and edgeShading properties). 
    
    A mesh can also be created from another mesh using Mesh(parent, otherMesh).
    
    *Vertices* is a Nx3 numpy array of vertex positions in 3D space.
    
    *Normals* is a Nx3 numpy array of vertex normals. If not given, 
    it is calcululated from the vertices.
    
    *Faces* (optional) is a numpy array or list of indices to define the faces.
    If this array is Nx3 or Nx4, verticesPerFace is inferred from this array.
    Faces should be of uint8, uint16 or uint32 (if it is not, the data is
    converted to uint32).
    
    Per vertex color can be supplied in three ways:
      * explicitly by giving an Nx3 or Nx4 colors array
      * by supplying 1D texcords which  are looked up in the colormap
      * by supplying a 2D texcords array and setting a 2D texture image
    
    *Colors* is a Nx3 or Nx4 numpy array giving the ambient and diffuse color
    for each vertex. 
    
    *Texcords* is used to map a 2D texture or 1D texture (a colormap) to the
    mesh. The texture color is multiplied after the ambient and diffuse
    lighting calculations, but before calculating the specular component.
    If texcords is a 1D (size N) array it specifies the color index at each
    vertex. If texcords is a Nx2 array it represents the 2D texture 
    coordinates to map an image to the mesh. Use SetTexture() to set 
    the image, and the colormap property to set the colormap.
    
    *VerticesPerFace* can be 3 or 4. It determines whether the faces are
    triangles or quads. If faces is specified and is 2D, the number of
    vertices per face is determined from that array.
    
    """ 
    
    def __init__(self, parent, vertices, normals=None, faces=None, 
            colors=None, texcords=None, verticesPerFace=3):
        Wobject.__init__(self, parent)
        
        # Init flat normals
        self._flatNormals = None
        
        # Create colormap and init texture
        self._colormap = Colormap()
        self._texture = None
        
        # Material properties
        self._ambient = 0.7
        self._diffuse = 0.7
        self._specular = 0.3
        self._shininess = 50
        self._emission = 0.0
        
        # Reference colors
        self._faceColor = (1, 1, 1, 1)
        self._edgeColor = (0,0,0,1)
        
        # Shading
        self._faceShading = 'smooth'
        self._edgeShading = None
        
        # What faces to cull
        self._cullFaces = None # gl.GL_BACK (for surf(), None makes most sense)
        
        # Obtain data from other mesh?
        if isinstance(vertices, BaseMesh):
            other = vertices
            vertices = other._vertices
            normals = other._normals
            faces = other._faces
            colors = other._colors
            texcords = other._texcords
            verticesPerFace = other._verticesPerFace
        
        # Save data
        BaseMesh.__init__(self, vertices, normals, faces,
                            colors, texcords, verticesPerFace)
    
    
    ## Material properties: how the object is lit
    
    @PropWithDraw
    def ambient():
        """ Get/Set the ambient reflection color of the material. Ambient
        light is the light that is everywhere, coming from all directions, 
        independent of the light position. 
        
        The value can be a 3- or 4-element tuple, a character in 
        "rgbycmkw", or a scalar between 0 and 1 that indicates the 
        fraction of the reference color.
        """
        def fget(self):
            return self._ambient
        def fset(self, value):
            self._ambient = _testColor(value)
    
    
    @PropWithDraw
    def diffuse():
        """ Get/Set the diffuse reflection color of the material. Diffuse
        light comes from one direction, so it's brighter if it comes
        squarely down on a surface than if it barely glances off the 
        surface. It depends on the light position how a material is lit.
        
        The value can be a 3- or 4-element tuple, a character in 
        "rgbycmkw", or a scalar between 0 and 1 that indicates the 
        fraction of the reference color.
        """
        def fget(self):
            return self._diffuse
        def fset(self, value):
            self._diffuse = _testColor(value)
    
    
    @PropWithDraw
    def ambientAndDiffuse():
        """ Set the diffuse and ambient component simultaneously. Usually,
        you want to give them the same value. Getting returns the diffuse
        component.
        """
        def fget(self):
            return self._diffuse
        def fset(self, value):
            self._diffuse = self._ambient = _testColor(value)
    
    
    @PropWithDraw
    def specular():
        """ Get/Set the specular reflection color of the material. Specular
        light represents the light that comes from the light source and bounces
        off a surface in a particular direction. It is what makes 
        materials appear shiny.
        
        The value can be a 3- or 4-element tuple, a character in 
        "rgbycmkw", or a scalar between 0 and 1 that indicates the 
        fraction of white (1,1,1).
        """
        def fget(self):
            return self._specular
        def fset(self, value):
            self._specular = _testColor(value)
    
    
    @PropWithDraw
    def shininess():
        """ Get/Set the shininess value of the material as a number between
        0 and 128. The higher the value, the brighter and more focussed the
        specular spot, thus the shinier the material appears to be.
        """
        def fget(self):
            return self._shininess
        def fset(self, value):
            if value < 0: value = 0
            if value > 128: value = 128
            self._shininess = value
    
    
    @PropWithDraw
    def emission():
        """ Get/Set the emission color of the material. It is the 
        "self-lighting" property of the material, and usually only makes
        sense for objects that represent lamps or candles etc.
        
        The value can be a 3- or 4-element tuple, a character in 
        "rgbycmkw", or a scalar between 0 and 1 that indicates the 
        fraction of the reference color.
        """
        def fget(self):
            return self._emission
        def fset(self, value):
            self._emission = _testColor(value)
    
    
    ## Face and edge shading properties, and culling
    
    @PropWithDraw
    def faceColor():
        """ Get/Set the face reference color of the object. If the
        ambient, diffuse or emissive properties specify a scalar, that
        scalar represents the fraction of *this* color for the faces. 
        """
        def fget(self):
            return self._faceColor
        def fset(self, value):
            self._faceColor = _testColor(value, True)
    
    
    @PropWithDraw
    def edgeColor():
        """ Get/Set the edge reference color of the object. If the
        ambient, diffuse or emissive properties specify a scalar, that
        scalar represents the fraction of *this* color for the edges. 
        """
        def fget(self):
            return self._edgeColor
        def fset(self, value):
            self._edgeColor = _testColor(value, True)
    
    
    @PropWithDraw    
    def faceShading():
        """ Get/Set the type of shading to apply for the faces. 
          * None - Do not show the faces
          * 'plain' - Display the faces without lighting
          * 'flat' - Lighted shading uniform for each face
          * 'smooth' - Lighted smooth shading
        """
        def fget(self):
            return self._faceShading
        def fset(self, value):
            if value is None:
                self._faceShading = None
            elif isinstance(value, basestring) and (value.lower() in 
                    ['plain', 'flat', 'smooth']):                
                self._faceShading = value.lower()
            else:
                tmp = "Shading must be None, 'plain', 'flat' or 'smooth'."
                raise ValueError(tmp)
    
    
    @PropWithDraw    
    def edgeShading():
        """ Get/Set the type of shading to apply for the edges. 
          * None - Do not show the edges
          * 'plain' - Display the edges without lighting
          * 'flat' - Lighted shading uniform for each edge
          * 'smooth' - Lighted smooth shading
        """
        def fget(self):
            return self._edgeShading
        def fset(self, value):
            if value is None:
                self._edgeShading = None
            elif isinstance(value, basestring) and (value.lower() in 
                    ['plain', 'flat', 'smooth']):                
                self._edgeShading = value.lower()
            else:
                tmp = "Shading must be None, 'plain', 'flat' or 'smooth'."
                raise ValueError(tmp)
    
    
    @PropWithDraw
    def cullFaces():
        """ Get/Set the culling of faces. 
        Values can be 'front', 'back', or None (default). If 'back', 
        backfacing faces are not drawn. If 'front', frontfacing faces
        are not drawn. 
        """
        def fget(self):
            D = {gl.GL_FRONT:'front', gl.GL_BACK:'back', None:None}
            return D[self._cullFaces]
        def fset(self, value):
            if isinstance(value, basestring):
                try:
                    D = {'front':gl.GL_FRONT, 'back':gl.GL_BACK}
                    self._cullFaces = D[value.lower()]
                except KeyError:
                    raise ValueError('Invalid value for cullFaces')
            elif value is None:
                self._cullFaces = None
    
    
    ## Setters
    
    
    
    
    @DrawAfter
    def SetTexture(self, data):
        """ SetTexture(data)
        Set the texture image to map to the mesh.
        Use None as an argument to remove the texture.
        """
        if data is not None:
            # Check dimensions
            if data.ndim==2:
                pass # ok: gray image
            elif data.ndim==3 and data.shape[2]==3:
                pass # ok: color image
            else:
                raise ValueError('Only 2D images can be mapped to a mesh.')
            # Make texture object and bind
            self._texture = TextureObjectToVisualize(2, data, interpolate=True)
            self._texture.SetData(data)
        else:
            self._texture = None
    
    
    @PropWithDraw
    def colormap():
        """ Get/Set the colormap. The argument must be a tuple/list of 
        iterables with each element having 3 or 4 values. The argument may
        also be a Nx3 or Nx4 numpy array. In all cases the data is resampled
        to create a 256x4 array.
        
        Visvis defines a number of standard colormaps in the global visvis
        namespace: CM_AUTUMN, CM_BONE, CM_COOL, CM_COPPER, CM_GRAY, CM_HOT, 
        CM_HSV, CM_JET, CM_PINK, CM_SPRING, CM_SUMMER, CM_WINTER. 
        A dict of name-colormap pairs is also available as vv.cm.colormaps.
        """
        def fget(self):
            return self._colormap.GetMap()
        def fset(self, value):
            self._colormap.SetMap(value)
    
    
    ## Method implementations to function as a proper wobject
    
    def _GetLimits(self):
        """ _GetLimits()
        Get the limits in world coordinates between which the object exists.
        """
        
        # Get vertices and remove nans
        vertices = self._vertices
        I = np.isnan(vertices[:,2]); vertices[I,0] = np.nan
        I = np.isnan(vertices[:,1]); vertices[I,0] = np.nan
        I = (1-np.isnan(vertices[:,0])).astype(np.bool)
        vertices = vertices[I,:]
        
        try:
            # Obtain untransformed coords         
            x1, x2 = vertices[:,0].min(), vertices[:,0].max()
            y1, y2 = vertices[:,1].min(), vertices[:,1].max()
            z1, z2 = vertices[:,2].min(), vertices[:,2].max()
            
            # There we are
            return Wobject._GetLimits(self, x1, x2, y1, y2, z1, z2)
        except Exception:
            return None
    
    
    def OnDestroyGl(self):
        # Clean up OpenGl resources.
        self._colormap.DestroyGl()
        if self._texture is not None:
            self._texture.DestroyGl()
    
    
    def OnDestroy(self):
        # Clean up any resources.
        self._colormap.Destroy()
        if self._texture is not None:
            self._texture.Destroy()
    
    
    def OnDraw(self):
        
        # Draw faces
        if self._faceShading:
            self._Draw(self._faceShading, self._faceColor)
        
        # Draw edges
        if self._edgeShading:
            gl.glDepthFunc(gl.GL_LEQUAL)
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            #
            self._Draw(self._edgeShading, self._edgeColor)
            #
            gl.glDepthFunc(gl.GL_LESS)
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    
    
    def OnDrawShape(self, color):        
        self._Draw('plain', color)
    
    
    def _Draw(self, shading, refColor):
        """ The actual drawing. Used for drawing faces, lines, and shape.
        """
        
        # Need vertices
        if self._vertices is None:
            return
        
        # Prepare normals
        if shading != 'plain':            
            # Need normals
            if self._normals is None:
                processing.calculateNormals(self)
            # Do we need flat normals?
            if shading == 'flat':
                if self._flatNormals is None:
                    processing.calculateFlatNormals(self)
                normals = self._flatNormals 
            else:
                normals = self._normals
            #
            gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
            gl.glNormalPointerf(normals)
        
        # Prepare vertices (in the code above the vertex array can be updated)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(self._vertices)
        
        # Prepare colors (if available)
        if self._colors is not None:
            gl.glEnable(gl.GL_COLOR_MATERIAL)
            gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
            gl.glEnableClientState(gl.GL_COLOR_ARRAY)
            gl.glColorPointerf(self._colors)
        
        
        # Prepate texture coordinates (if available)
        if self._texcords is not None:
            if (self._texcords.ndim == 2) and (self._texture is not None):
                gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
                gl.glTexCoordPointerf(self._texcords)
                self._texture.Enable(0)
            elif self._texcords.ndim == 1:
                gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
                gl.glTexCoordPointer(1, gl.GL_FLOAT, 0, self._texcords)
                self._colormap.Enable(0)
        
        
        # Prepare material (ambient and diffuse may be overriden by colors)
        if shading == 'plain':
            gl.glColor(refColor)
        else:
            what = gl.GL_FRONT_AND_BACK
            gc = _getColor
            gl.glMaterial(what, gl.GL_AMBIENT, gc(self._ambient, refColor))
            gl.glMaterial(what, gl.GL_DIFFUSE, gc(self._diffuse, refColor))
            gl.glMaterial(what, gl.GL_SPECULAR, gc(self._specular, (1,1,1,1)))
            gl.glMaterial(what, gl.GL_SHININESS, self._shininess)
            gl.glMaterial(what, gl.GL_EMISSION, gc(self._emission, refColor))
        
        
        # Prepare lights
        if shading != 'plain':
            gl.glEnable(gl.GL_LIGHTING)
            gl.glEnable(gl.GL_NORMALIZE)  # GL_NORMALIZE or GL_RESCALE_NORMAL
            if shading == 'smooth':
                gl.glShadeModel(gl.GL_SMOOTH)
            else:
                gl.glShadeModel(gl.GL_FLAT)
        
        
        # Set culling (take data aspect into account!)
        axes = self.GetAxes()
        tmp = 1
        if axes:
            for i in axes.daspect:
                if i<0:
                    tmp *= -1
        gl.glFrontFace({1:gl.GL_CW, -1:gl.GL_CCW}[tmp])
        if self._cullFaces:
            gl.glEnable(gl.GL_CULL_FACE)
            gl.glCullFace(self._cullFaces)
        
        
        # Draw
        type = {3:gl.GL_TRIANGLES, 4:gl.GL_QUADS}[self._verticesPerFace]
        if self._faces is None:
            gl.glDrawArrays(type, 0, self._vertices.shape[0])
        else:
            # Get data type
            if self._faces.dtype == np.uint8:
                face_dtype = gl.GL_UNSIGNED_BYTE
            elif self._faces.dtype == np.uint16:
                face_dtype = gl.GL_UNSIGNED_SHORT
            else:
                face_dtype = gl.GL_UNSIGNED_INT
            # Go
            N = self._faces.size
            gl.glDrawElements(type, N, face_dtype, self._faces)
        
        # Clean up
        gl.glFlush()
        if self._texcords is not None:
            self._colormap.Disable()
            if self._texture:
                self._texture.Disable()
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_NORMAL_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        #
        gl.glDisable(gl.GL_COLOR_MATERIAL)
        gl.glShadeModel(gl.GL_FLAT)
        #
        gl.glDisable(gl.GL_LIGHTING)
        gl.glDisable(gl.GL_NORMALIZE)
        gl.glDisable(gl.GL_CULL_FACE)


class OrientableMesh(Mesh, OrientationForWobjects_mixClass):
    """ OrientableMesh(parent, vertices, normals=None, faces=None, 
        colors=None, texcords=None, verticesPerFace=3)
    
    An OrientableMesh is a generic object to visualize a 3D object made
    up of polygons. OrientableMesh differs from the Mesh class in that 
    it provides additional properties to easily orient the mesh in 3D
    space: scaling, translation, direction, rotation.
    
    See the Mesh class for more information.
    """
    
    def __init__(self, *args, **kwargs):
        Mesh.__init__(self, *args, **kwargs)
        OrientationForWobjects_mixClass.__init__(self)

    