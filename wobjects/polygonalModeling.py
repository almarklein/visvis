# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module polygonalModeling

This module defined the Mesh object that represents a polygonal model.
It also defines lights and algorithmic for managing polygonal models.

"""

import sys
import numpy as np
import OpenGL.GL as gl

from visvis.utils.pypoints import is_Pointset
from visvis.core.misc import PropWithDraw, DrawAfter, basestring
from visvis import Wobject, Colormapable, OrientationForWobjects_mixClass
from visvis.core.light import _testColor, _getColor
from visvis.wobjects.textures import TextureObjectToVisualize
from visvis.core import shaders
from visvis.wobjects.textures import minmax


def checkDimsOfArray(value, *ndims):
    """ checkDimsOfArray(value, *ndims)
    
    Coerce value into a numpy array of size NxM, where M is in ndims.
    If 0 is in ndims, a 1D array is allowed.  Return a numpy array or
    raise a ValueError.
    
    """
    # Check if is Pointset with correct dimensionality
    if is_Pointset(value):
        if value.ndim not in ndims:
            raise ValueError()
        return value.data
    
    # Try to coerce to numpy array; raise ValueError if anything goes wrong
    if value is None:
        raise ValueError('Values for mesh is None.')
    if not isinstance(value, np.ndarray):
        try:
            value = np.array(value, dtype=np.float32)
        except Exception:
            raise ValueError('Could not coerce to numpy array.')
    
    # Allow 1D?
    if value.ndim==1 and 0 in ndims:
        value = value.reshape(value.size,1) # reshape gives view on same data
    
    # value is guaranteed to be a numpy array here; check dimensionality
    if not value.ndim == 2 and value.shape[1] in ndims:
        raise ValueError()
    if value.dtype == np.float32:
        return value
    else:
        return value.astype(np.float32)


class BaseMesh(object):
    """ BaseMesh(vertices, faces=None, normals=None, values=None,
                                                            verticesPerFace=3)
    
    The BaseMesh class represents a mesh in its pure mathematical
    form (without any visualization properties). Essentially, it
    serves as a container for the vertices, normals, faces, and values.
    
    See the Mesh and OrientableMesh classes for representations that
    include visualization properties.
    
    The old signature may also be used, but will be removed in future versions:
    BaseMesh(vertices, normals=None, faces=None,
                                colors=None, texcords=None, verticesPerFace=3)
    
    """
    
    def __init__(self, *args, **kwargs):
        
        # Get arguments
        if self._test_if_argumens_use_new_style(*args, **kwargs):
            arguments = self._new_init(*args, **kwargs)
        else:
            arguments = self._old_init(*args, **kwargs)
            try:
                raise Exception("Mesh signature changed.")
            except Exception:
                type, value, tb = sys.exc_info()
                frame = tb.tb_frame
                del tb
            print('DeprecationWarning: The Mesh and BaseMesh signature ' +
                'have been changed. The old signature will be disabled '
                'in future versions. Where to look:')
            # Get lineno and fname
            for iter in range(5):
                frame = frame.f_back
                if frame is None:
                    break
                fname = frame.f_code.co_filename
                lineno = frame.f_lineno
                if 'polygonalModeling' not in fname:
                    print('line %i in %s' % (lineno, fname))
                    break
        vertices, faces, normals, values, verticesPerFace = arguments
        
        # Obtain data from other mesh?
        if isinstance(vertices, BaseMesh):
            other = vertices
            vertices = other._vertices
            faces = other._faces
            normals = other._normals
            values = other._values
            verticesPerFace = other._verticesPerFace
        
        # Set verticesPerFace first (can be reset by faces)
        verticesPerFace = int(verticesPerFace)
        if verticesPerFace in [3, 4]:
            self._verticesPerFace = verticesPerFace
        else:
            raise ValueError('VerticesPerFace should be 3 or 4.')
        
        # Set all things (checks are performed in set methods)
        self._vertices = None
        self._faces = None
        self._normals = None
        self._values = None
        #
        self.SetVertices(vertices)
        self.SetFaces(faces)
        self.SetNormals(normals)
        self.SetValues(values, True) # And set clim to minmax
    
    
    def _test_if_argumens_use_new_style(self, *args, **kwargs):
        """ Returns True if the new style is used, False otherwise.
        """
        
        def getArgAsArrayIfPossible(nr):
            try:
                ob = args[nr]
            except IndexError:
                return None
            try:
                return checkDimsOfArray(ob, 0,1,2,3,4)
            except Exception:
                return ob
        
        intDtypes = [   np.uint8, np.uint16, np.uint32,
                        np.int8, np.int16, np.int32 ]
        
        # Get values
        vertices = getArgAsArrayIfPossible(0)
        faces_new = getArgAsArrayIfPossible(1)
        normals_new = getArgAsArrayIfPossible(2)
        normals_old, faces_old = faces_new, normals_new
        
        # Things we know for sure
        
        # Only the old style has 6 args
        if len(args) == 6:
            return False
        
        # The faces may have a different shape as vertices, normals cannot
        if faces_new is not None and faces_new.shape != vertices.shape:
            return True
        if faces_old is not None and faces_old.shape != vertices.shape:
            return False
        
        # Faces are usually integers (but not necesarily) normals are never
        if faces_new is not None and faces_new.dtype in intDtypes:
            return True
        if faces_old is not None and faces_old.dtype in intDtypes:
            return False
        
        # New style uses values arg, old style uses color and texcords
        if 'values' in kwargs:
            return True
        if 'colors' in kwargs or 'texcords' in kwargs:
            return False
        
        # Things we know pretty sure
        
        # The faces are very unlikely to have the same shape as the vertices
        if normals_new is not None and normals_new.shape == vertices.shape:
            return True
        if normals_old is not None and normals_old.shape == vertices.shape:
            return False
        
        # Not sure, assume new style, it will probably not matter
        return True
    
    
    def _new_init(self, vertices=None, faces=None, normals=None, values=None,
                                        verticesPerFace=3):
        
        # Return
        return vertices, faces, normals, values, verticesPerFace
    
    
    def _old_init(self, vertices, normals=None, faces=None,
                            colors=None, texcords=None, verticesPerFace=3):
        
        # Set values from colors and texcords
        if colors is not None:
            values = colors
        else:
            values = texcords
        
        # Return args in the new order
        return vertices, faces, normals, values, verticesPerFace
    
    
    @DrawAfter
    def SetVertices(self, vertices):
        """ SetVertices(vertices)
        
        Set the vertex data as a Nx3 numpy array or as a 3D Pointset.
        
        """
        try:
            self._vertices = checkDimsOfArray(vertices, 3)
        except ValueError:
            raise ValueError("Vertices should represent an array of 3D vertices.")
    
    
    @DrawAfter
    def SetNormals(self, normals):
        """ SetNormals(normals)
        
        Set the normal data as a Nx3 numpy array or as a 3D Pointset.
        
        """
        if normals is not None:
            try:
                self._normals = checkDimsOfArray(normals, 3)
            except ValueError:
                raise ValueError("Normals should represent an array of 3D vectors.")
        else:
            self._normals = None # User explicitly wants to disable normals
    
    
    @DrawAfter
    def SetValues(self, values, setClim=False):
        """ SetValues(values, setClim=False)
        
        Set the value data for each vertex. This can be given as:
          * Nx1 array, representing the indices in a colormap
          * Nx2 array, representing the texture coordinates in a texture
          * Nx3 array, representing the RGB values at each vertex
          * Nx4 array, representing the RGBA values at each vertex
        
        Use None as an argument to remove the values data.
        
        """
        # _values is the original supplied array (but as float32 or float64)
        # _values2 is the one used for visualization, corrected by clim
        
        if values is None:
            self._values = None # User explicitly wants to disable values
            self._values2 = None
            return
        
        # Make numpy array
        try:
            values = checkDimsOfArray(values, 0, 1, 2, 3, 4)
        except ValueError:
            raise ValueError("Values should be Nx1, Nx2, Nx3 or Nx4.")
        
        if values.shape[1] == 1:
            # Colormap indices: test data type
            if values.dtype == np.float32:
                pass
            else:
                values = values.astype(np.float32)
        
        elif values.shape[1] == 2:
            # Texture coordinates: test data type
            if values.dtype == np.float32:
                pass
            else:
                values = values.astype(np.float32)
        
        elif values.shape[1] in [3,4]:
            # Color: scale color range between 0 and 1
            if values.dtype in [np.float32, np.float64] and values.max()<1.1:
                pass
            elif values.dtype == np.uint8:
                values = values.astype(np.float32) / 256.0
            else:
                #mi, ma = minmax(values)
                #values = (values.astype(np.float32) - mi) / (ma-mi)
                # The clim makes sure the data is scaled
                values = values.astype(np.float32)
        
        # Store
        self._values = values
        
        # A bit of a hack... reset clim for Mesh class so that values2 is created
        if isinstance(self, Colormapable):
            if setClim:
                self.clim = minmax(values)
            else:
                self.clim = self.clim
    
    
    @DrawAfter
    def SetColors(self, colors):
        """ SetColors(colors)
        
        Deprecated: use SetValues() instead.
        
        Set the color data as a Nx3 numpy array or as a 3D Pointset.
        Use None as an argument to remove the color data.
        
        
        """
        print('DeprecationWarning: The SetColors() and SetTexcords() methods '+
                'are replaced by setValues(). ' +
                'The old methods will be removed in future versions.')
        
        self.SetValues(colors)
    
    
    @DrawAfter
    def SetTexcords(self, texcords):
        """ SetTexcords(texcords)
        
        Deprecated: use SetValues() instead.
        
        Set the texture coordinates as a Nx2 numpy array or as a 2D Pointset.
        Use None as an argument to turn off the texture.
        
        """
        print('DeprecationWarning: The SetColors() and SetTexcords() methods '+
                'are replaced by setValues(). ' +
                'The old methods will be removed in future versions.')
        
        self.SetValues(texcords)
    
    
    @DrawAfter
    def SetFaces(self, faces):
        """ SetFaces(faces)
        
        Set the faces data. This can be either a list, a 1D numpy array,
        a Nx3 numpy array, or a Nx4 numpy array. In the latter two cases
        the type is set to GL_TRIANGLES or GL_QUADS respectively.
        
        The front of the face is defined using the right-hand-rule.
        
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
            self._faces = None # User explicitly wants to disable faces
    
    
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
        Nfaces = int(faces.size / vpf)
        return faces.reshape((Nfaces, vpf))


# Import here, because they may require BaseMesh
import visvis.processing as processing

class Mesh(Wobject, BaseMesh, Colormapable):
    """ Mesh(parent, vertices, faces=None, normals=None, values=None, verticesPerFace=3)
    
    A mesh is a generic object to visualize a 3D object made up of
    polygons. These polygons can be triangles or quads. The mesh
    is affected by lighting and its material properties can be
    changed using properties. The reference color and shading can
    be set individually for the faces and edges (using the faceColor,
    edgeColor, faceShading and edgeShading properties).
    
    A mesh can also be created from another mesh using Mesh(parent, otherMesh),
    where otherMesh should be an instance of BaseMesh.
    
    The old signature may also be used, but will be removed in future versions:
    Mesh(vertices, normals=None, faces=None,
                                colors=None, texcords=None, verticesPerFace=3)
    
    Parameters
    ----------
    vertices : Nx3 numpy array
        The vertex positions in 3D space.
    faces : (optional) numpy array or list of indices
        Defines the faces. If this array is Nx3 or Nx4, verticesPerFace is
        inferred from this array. Faces should be of uint8, uint16 or
        uint32 (if it is not, the data is converted to uint32).
        The front of the face is defined using the right-hand-rule.
    normals :(optional) Nx3 numpy array
        The vertex normals. If not given, they are calcululated
        from the vertices.
    values : (optional) Nx1, Nx2, Nx3 or Nx4 numpy array
        The value data for each vertex. If Nx1, they represent the indices
        in the colormap. If Nx2, they represent the texture coordinates for
        the texturegiven with SetTexture(). If Nx3 or Nx4 they represent
        the ambient and diffuse color for each vertex.
    verticesPerFace : 3 or 4
        Determines whether the faces are triangles or quads. If faces is
        specified and is 2D, the number of vertices per face is determined
        from that array.
    
    Note on texture mapping
    -----------------------
    The texture color is multiplied after the ambient and diffuse
    lighting calculations, but before calculating the specular component.
    
    """
    
    
    def __init__(self, parent, *args, **kwargs):
        Wobject.__init__(self, parent)
        
        # Init flat normals
        self._flatNormals = None
        
        # Create colormap and init texture
        Colormapable.__init__(self)
        self._texture = None
        
        # create glsl shaders for this wobject. For faces, edges and shape
        self._faceShader = shaders.Shader()
        self._edgeShader = shaders.Shader()
        self._shapeShader = shaders.Shader()
        self._InitShaders()
        self.useNativeShading = False
        
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
        self.faceShading = 'smooth'
        self.edgeShading = None
        
        # What faces to cull
        self._cullFaces = None # gl.GL_BACK (for surf(), None makes most sense)
        
        # Save data
        BaseMesh.__init__(self, *args, **kwargs)
        
        # Store value2, which are like 'values' but clim-corrected
        self._values2 = self._values
    
    
    def _InitShaders(self):
        
        # Give all shaders the base components, plain shading
        for shader in [self.faceShader, self.edgeShader, self.shapeShader]:
            
            # Vertex shader
            shader.vertex.Clear()
            shader.vertex.AddPart(shaders.SH_MV_BASE)
            shader.vertex.AddPart(shaders.SH_MV_SHADING_PLAIN)
            shader.vertex.AddPart(shaders.SH_NLIGHTS_1)
            
            # Fragment shader
            shader.fragment.Clear()
            shader.fragment.AddPart(shaders.SH_MF_BASE)
            shader.fragment.AddPart(shaders.SH_MF_SHADING_PLAIN)
            shader.fragment.AddPart(shaders.SH_MF_ALBEIDO_UNIT)
            shader.fragment.AddPart(shaders.SH_NLIGHTS_1)
        
    
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
        return locals()
    
    
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
        return locals()
    
    
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
        return locals()
    
    
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
        return locals()
    
    
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
        return locals()
    
    
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
        return locals()
    
    
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
        return locals()
    
    
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
        return locals()
    
    
    @PropWithDraw
    def useNativeShading():
        """ Get/set whether to use the native OpenGl shading. The default
        is False, which means that GLSL-based shading is used, allowing for
        more advanced shader styles.
        
        Note that regardless of the value of this property, native shading
        is used if the hardward does not support GLSL (OpenGl version<2).
        """
        def fget(self):
            return self._useNativeShading
        def fset(self, value):
            self._useNativeShading = bool(value)
        return locals()
    
    
    @PropWithDraw
    def faceShading():
        """ Get/Set the type of shading to apply for the faces.
          * None - Do not show the faces.
          * 'plain' - Display the faces in the faceColor (without lighting).
          * 'flat' - Lit shading uniform for each face
          * 'gouraud' - Lighting is calculated at vertices and interpolated
            over the face.
          * 'smooth' - Lighting is calculated for each fragment (aka
            phong-shading or phong-interpolation).
          * 'toon' - A cartoonish look (aka cel-shading).
        
        Notes
        -----
        In native mode 'smooth' and 'toon' fall back to 'gouraud'.
        In both native and nonnative mode the blinn-phong reflectance model
        is used.
        """
        def fget(self):
            return self._faceShading
        def fset(self, value):
            # Process value
            if value is None:
                self._faceShading = None
            elif isinstance(value, basestring) and (value.lower() in
                    ['plain', 'flat', 'gouraud', 'smooth', 'toon']):
                self._faceShading = value.lower()
            else:
                tmp = "Shading must be None, 'plain', 'flat', 'gouraud, 'smooth' or 'toon.'"
                raise ValueError(tmp)
            
            # Apply for shader code
            self._SetShading(self._faceShading, self.faceShader)
        return locals()
    
    
    @PropWithDraw
    def edgeShading():
        """ Get/Set the type of shading to apply for the edges.
          * None - Do not show the faces.
          * 'plain' - Display the faces in the faceColor (without lighting).
          * 'flat' - Lit shading uniform for each face
          * 'gouraud' - Lighting is calculated at vertices and interpolated
            over the face.
          * 'smooth' - Lighting is calculated for each fragment (aka
            phong-shading or phong-interpolation).
        
        Notes
        -----
        In native mode 'smooth' falls back to 'gouraud'.
        In both native and nonnative mode the blinn-phong reflectance model
        is used.
        """
        def fget(self):
            return self._edgeShading
        def fset(self, value):
            # Process value
            if value is None:
                self._edgeShading = None
            elif isinstance(value, basestring) and (value.lower() in
                    ['plain', 'flat', 'gouraud', 'smooth']):
                self._edgeShading = value.lower()
            else:
                tmp = "Edge shading must be None, 'plain', 'flat', 'gouraud, 'smooth'."
                raise ValueError(tmp)
            
            # Apply for shader code
            self._SetShading(self._edgeShading, self.edgeShader)
        return locals()
    
    
    def _SetShading(self, shading, shader):
        
        # Select shader part
        M = [(shaders.SH_MV_SHADING_PLAIN,   shaders.SH_MF_SHADING_PLAIN),
                (shaders.SH_MV_SHADING_GOURAUD, shaders.SH_MF_SHADING_GOURAUD),
                (shaders.SH_MV_SHADING_SMOOTH,  shaders.SH_MF_SHADING_SMOOTH),
                (shaders.SH_MV_SHADING_TOON, shaders.SH_MF_SHADING_TOON),
            ]
        #
        if shading == 'plain':
            vShading, fShading = M[0]
        elif shading in ['flat', 'gouraud']:
            vShading, fShading = M[1]
        elif shading == 'smooth':
            vShading, fShading = M[2]
        elif shading == 'toon':
            vShading, fShading = M[3]
        else:
            return
        
        # Change shaders accordingly. Does not cause recompile if new
        # part replaces itself.
        if shader.vertex.HasPart('shading'):
            shader.vertex.ReplacePart(vShading)
        if shader.fragment.HasPart('shading'):
            shader.fragment.ReplacePart(fShading)
    
    @PropWithDraw
    def cullFaces():
        """ Get/Set the culling of faces.
        Values can be 'front', 'back', or None (default). If 'back',
        backfacing faces are not drawn. If 'front', frontfacing faces
        are not drawn. The front of the face is defined using the
        right-hand-rule.
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
            else:
                raise ValueError('Invalid value for cullFaces')
        return locals()
    
    @property
    def faceShader(self):
        """ Get the shader object for the faces. This can
        be used to add code of your own and customize the vertex and
        fragment part of the shader.
        """
        return self._faceShader
    
    @property
    def edgeShader(self):
        """ Get the shader object for the edges. This can
        be used to add code of your own and customize the vertex and
        fragment part of the shader.
        """
        return self._edgeShader
    
    @property
    def shapeShader(self):
        """ Get the shader object for the shape. This can
        be used to add code of your own and customize the vertex and
        fragment part of the shader.
        """
        return self._shapeShader
    
    
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
            elif data.ndim==3 and data.shape[2] in [3, 4]:
                pass # ok: color image
            else:
                raise ValueError('Only 2D images can be mapped to a mesh.')
            # Make texture object and bind
            self._texture = TextureObjectToVisualize(2, data, interpolate=True)
            self._texture.SetData(data)
        else:
            self._texture = None
    
    
    def _GetClim(self):
        return self._clim
    def _SetClim(self, value):
        self._clim = value
        if self._values is not None:
            if value.min==0 and value.max==1:
                self._values2 = self._values
            else:
                if value.range == 0:
                    scale = 1.0
                else:
                    scale = 1.0/(value.range)
                self._values2 = (self._values - value.min) * scale
    
    
    ## Method implementations to function as a proper wobject
    
    def _GetLimits(self):
        """ _GetLimits()
        
        Get the limits in world coordinates between which the object exists.
        
        """
        
        # Get vertices with all coordinates unmasked and finite
        v = self._vertices
        if isinstance(v, np.ma.MaskedArray):
            v = v.filled(np.nan)
        valid = np.isfinite(v[:,0]) * np.isfinite(v[:,1]) * np.isfinite(v[:,2])
        validverts = v[valid,:]
        
        try:
            # Obtain untransformed coords
            x1, y1, z1 = validverts.min(axis=0)
            x2, y2, z2 = validverts.max(axis=0)
            
            # There we are
            return Wobject._GetLimits(self, x1, x2, y1, y2, z1, z2)
        except Exception:
            return None
    
    
    def OnDestroyGl(self):
        # Clean up OpenGl resources.
        self._faceShader.DestroyGl()
        self._edgeShader.DestroyGl()
        self._shapeShader.DestroyGl()
        self._colormap.DestroyGl()
        if self._texture is not None:
            self._texture.DestroyGl()
    
    
    def OnDestroy(self):
        # Clean up any resources.
        self._faceShader.Destroy()
        self._edgeShader.Destroy()
        self._shapeShader.Destroy()
        self._colormap.Destroy()
        if self._texture is not None:
            self._texture.Destroy()
    
    
    def OnDraw(self):
        
        # Draw faces
        if self._faceShading:
            
            if self._faceShading == 'toon':
                # Draw outlines. We do check depth buffer, but do not write
                # to it, so all fragments can be overwritten.
                gl.glDepthMask(False)
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
                gl.glLineWidth(3.5)
                clr = 0.0, 0.0, 0.0
                self._Draw('plain', clr, self.shapeShader)
                gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
                gl.glDepthMask(True)
            if True:
                # Draw faces normally
                self._Draw(self._faceShading, self._faceColor, self.faceShader)
        
        # Draw edges
        if self._edgeShading:
            gl.glDepthFunc(gl.GL_LEQUAL)
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
            #
            self._Draw(self._edgeShading, self._edgeColor, self.edgeShader)
            #
            gl.glDepthFunc(gl.GL_LESS)
            gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    
    
    def OnDrawShape(self, color):
        self._Draw('plain', color, self.shapeShader)
    
    
    def _Draw(self, shading, refColor, shader):
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
        
        # Prepare colormap indices, texture cords or colors (if available)
        # useTexCords = False
        SH_ALBEIDO = shaders.SH_MF_ALBEIDO_UNIT
        if self._values is not None:
            values = values2 = self._values
            if self._values2 is not None:
                values2 = self._values2
            if values.shape[1] == 1:
                # Colormap: use values2
                values = values2
                # useTexCords = True
                gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
                gl.glTexCoordPointer(1, gl.GL_FLOAT, 0, values)
                shader.SetUniform('colormap', self._colormap)
                SH_ALBEIDO = shaders.SH_MF_ALBEIDO_LUT1
            elif values.shape[1] == 2 and self._texture is not None:
                # texcords, use original values
                # useTexCords = True
                gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
                gl.glTexCoordPointerf(values)
                shader.SetUniform('texture', self._texture)
                SH_ALBEIDO = shaders.SH_MF_ALBEIDO_LUT2
            elif values.shape[1] in [3,4]:
                # Color, use values2
                values = values2
                gl.glEnable(gl.GL_COLOR_MATERIAL)
                gl.glColorMaterial(gl.GL_FRONT_AND_BACK,
                                    gl.GL_AMBIENT_AND_DIFFUSE)
                gl.glEnableClientState(gl.GL_COLOR_ARRAY)
                gl.glColorPointerf(values)
                if values.shape[1] == 3:
                    SH_ALBEIDO = shaders.SH_MF_ALBEIDO_RGB
                else:
                    SH_ALBEIDO = shaders.SH_MF_ALBEIDO_RGBA
        
        # Prepare material (ambient and diffuse may be overriden by colors)
        if shading == 'plain':
            gl.glColor(*refColor)
        else:
            # Set glColor: unless ALBEIDO is RGB or RGBA,
            # this is used to dermine the alpha value
            gl.glColor(*refColor)
            # Set material properties
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
            if shading == 'flat':
                gl.glShadeModel(gl.GL_FLAT)
            else:
                gl.glShadeModel(gl.GL_SMOOTH)
        
        
        # Set culling (take data aspect into account!)
        # From visvis v1.6 we use the right hand rule (CCW)
        axes = self.GetAxes()
        tmp = 1
        if axes:
            for i in axes.daspect:
                if i<0:
                    tmp *= -1
        gl.glFrontFace({1:gl.GL_CCW, -1:gl.GL_CW}[tmp])
        if self._cullFaces:
            gl.glEnable(gl.GL_CULL_FACE)
            gl.glCullFace(self._cullFaces)
        
        
        # Check number of lights
        self._EnsureRightNumberOfLights(axes, shader)
        
        # Ensure that the right albeido shader part is selected
        if shader.fragment.HasPart('albeido'):
            shader.fragment.AddOrReplace(SH_ALBEIDO)
        
        
        if shader.isUsable and shader.hasCode and not self.useNativeShading:
            # GLSL shading
            shader.Enable()
        else:
            # Fixed pipeline
            if SH_ALBEIDO is shaders.SH_MF_ALBEIDO_LUT1:
                shader.EnableTextureOnly('colormap')
            elif SH_ALBEIDO is shaders.SH_MF_ALBEIDO_LUT2:
                shader.EnableTextureOnly('texture')
        
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
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_NORMAL_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        #
        shader.Disable()
        #
        gl.glDisable(gl.GL_COLOR_MATERIAL)
        gl.glShadeModel(gl.GL_FLAT)
        #
        gl.glDisable(gl.GL_LIGHTING)
        gl.glDisable(gl.GL_NORMALIZE)
        gl.glDisable(gl.GL_CULL_FACE)
    
    
    def _EnsureRightNumberOfLights(self, axes, shader):
        
        # Check number of lights in axes
        nlights = 1
        for i in range(1, 7): # len(axes.lights)):
            if axes.lights[i].isOn:
                nlights = i+1
        
        # Define shader part to use
        M = [ shaders.SH_NLIGHTS_1, shaders.SH_NLIGHTS_2, shaders.SH_NLIGHTS_3,
              shaders.SH_NLIGHTS_4, shaders.SH_NLIGHTS_5, shaders.SH_NLIGHTS_6,
              shaders.SH_NLIGHTS_7, shaders.SH_NLIGHTS_8, ]
        SH_LIGHTS = M[nlights-1]
        
        # Ensure that the right light shaderpart is selected
        if not shader.vertex.HasPart(SH_LIGHTS):
            shader.vertex.AddOrReplace(SH_LIGHTS)
        if not shader.fragment.HasPart(SH_LIGHTS):
            shader.fragment.AddOrReplace(SH_LIGHTS)


class OrientableMesh(Mesh, OrientationForWobjects_mixClass):
    """ OrientableMesh(vertices, faces=None, normals=None, values=None,
                                                            verticesPerFace=3)
    
    An OrientableMesh is a generic object to visualize a 3D object made
    up of polygons. OrientableMesh differs from the Mesh class in that
    it provides additional properties to easily orient the mesh in 3D
    space: scaling, translation, direction, rotation.
    
    See the Mesh class for more information.
    
    """
    
    def __init__(self, *args, **kwargs):
        Mesh.__init__(self, *args, **kwargs)
        OrientationForWobjects_mixClass.__init__(self)
