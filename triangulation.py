""" Module Polygon
Polygonial data.
"""

import os
os.chdir('/home/almar/py/visvis')

from points import Point, Pointset
from misc import Property
from base import Wobject
from textures import TextureObjectToVisualize

import numpy as np
import OpenGL.GL as gl


def _testColor(value):
    if not hasattr(value, '__len__'):
        raise ValueError("A color should be a 3 or 4 element sequence.")
    elif len(value) == 4:
        return (value[0], value[1], value[2], value[3])
    elif len(value) == 3:
        return (value[0], value[1], value[2], 1.0)
    else:
        raise ValueError("A color should be a 3 or 4 element sequence.")


# todo: implement spot light and attenuation
class Light(object):
    def __init__(self, index):
        
        # Store index of the light (OpenGl can handle up to 8 lights)
        self._index = index
        self._on = False
        
        # The three light properties
        self._ambient = (0.2, 0.2, 0.2 ,1)
        self._diffuse = (1,1,1, 1)
        self._specular = (1,1,1, 1)
        
        # Position or direction
        self._position = (0,0,1,0)
        self._camLight = True
    
    
    @Property
    def ambient():
        """ Get/Set the ambient color of the light. This is the color
        that is everywhere, coming from all directions, independent of 
        the light position. 
        """
        def fget(self):
            return self._ambient
        def fset(self, value):
            self._ambient = _testColor(value)
    
    
    @Property
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
    
    
    @Property
    def specular():
        """ Get/Set the specular color of the light. This component
        represents the light that comes from the light source and bounces
        off a surface in a particular direction. This is what makes 
        materials appear shiny.
        """
        def fget(self):
            return self._specular
        def fset(self, value):
            self._specular = _testColor(value)
    
    
    @Property
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
    
    
    @Property
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
    
    
    @Property
    def isCamLight():
        """ Get/Set whether the light is a camera light. A camera light
        moves along with the camera, like the lamp on a miner's hat.
        """
        def fget(self):
            return self._camLight
        def fset(self, value):
            self._camLight = bool(value)
    
    
    def On(self, on=True):
        """ On(on=True)
        Turn the light on.
        """
        self._on = bool(on)
    
    
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
            gl.glLightfv(thisLight, gl.GL_AMBIENT, self._ambient)
            gl.glLightfv(thisLight, gl.GL_DIFFUSE, self._diffuse)
            gl.glLightfv(thisLight, gl.GL_SPECULAR, self._specular)    
        else:
            gl.glDisable(thisLight)
    


def getSphere(ndiv=3, radius=1.0):
    # Example taken from the Red book, end of chaper 2.
    
    # Define constants
    X = 0.525731112119133606 
    Z = 0.850650808352039932
    
    # Creta vdata
    vdata = Pointset(3)
    app = vdata.Append
    app(-X, 0.0, Z); app(X, 0.0, Z); app(-X, 0.0, -Z); app(X, 0.0, -Z)
    app(0.0, Z, X); app(0.0, Z, -X); app(0.0, -Z, X); app(0.0, -Z, -X)
    app(Z, X, 0.0); app(-Z, X, 0.0); app(Z, -X, 0.0); app(-Z, -X, 0.0)
    
    # Create indices
    tindices = [
        [0,4,1], [0,9,4], [9,5,4], [4,5,8], [4,8,1],    
        [8,10,1], [8,3,10], [5,3,8], [5,2,3], [2,7,3],    
        [7,10,3], [7,6,10], [7,11,6], [11,0,6], [0,1,6], 
        [6,1,10], [9,0,11], [9,11,2], [9,2,5], [7,2,11] ]
    tindices = np.array(tindices, dtype=np.uint32)
    
    # Init vertex array
    vertices = Pointset(3)
    
    # Define function to recursively create vertices and normals
    def drawtri(a, b, c, div):
        if (div<=0):
            vertices.Append(a)
            vertices.Append(b)
            vertices.Append(c)
        else:
            ab = Point(0,0,0)
            ac = Point(0,0,0)
            bc = Point(0,0,0)
            for i in range(3):
                ab[i]=(a[i]+b[i])/2.0;
                ac[i]=(a[i]+c[i])/2.0;
                bc[i]=(b[i]+c[i])/2.0;
            ab = ab.Normalize(); ac = ac.Normalize(); bc = bc.Normalize()
            drawtri(a, ab, ac, div-1)
            drawtri(b, bc, ab, div-1)
            drawtri(c, ac, bc, div-1)
            drawtri(ab, bc, ac, div-1)
    
    # Create vertices
    for i in range(20):
        drawtri(    vdata[tindices[i][0]], 
                    vdata[tindices[i][1]], 
                    vdata[tindices[i][2]], 
                    ndiv )
    
    # Create normals and scale vertices
    normals = vertices.Copy()
    vertices *= radius
    
    # Done
    return vertices, normals


def getCube(a):
    
    # Create vertices of a cube
    pp = Pointset(3)
    # Bottom
    pp.Append(-0.5,-0.5,-0.5)
    pp.Append(+0.5,-0.5,-0.5)
    pp.Append(+0.5,+0.5,-0.5)
    pp.Append(-0.5,+0.5,-0.5)
    # Top
    pp.Append(-0.5,-0.5,+0.5)
    pp.Append(-0.5,+0.5,+0.5)
    pp.Append(+0.5,+0.5,+0.5)
    pp.Append(+0.5,-0.5,+0.5)
    
    vertices = Pointset(3)
    normals = Pointset(3)
    
    # Create vertices
    for i in [0,1,2,3]: # Top
        vertices.Append(pp[i]); normals.Append(0,0,-1)
    for i in [4,5,6,7]: # Bottom
        vertices.Append(pp[i]); normals.Append(0,0,+1)
    for i in [3,2,6,5]: # Front
        vertices.Append(pp[i]); normals.Append(0,+1,0)
    for i in [0,4,7,1]: # Back
        vertices.Append(pp[i]); normals.Append(0,-1,0)
    for i in [0,3,5,4]: # Left
        vertices.Append(pp[i]); normals.Append(-1,0,0)
    for i in [1,7,6,2]: # Right
        vertices.Append(pp[i]); normals.Append(+1,0,0)
    
    # Create colors
    colors = vertices.Copy()
    colors[:10,0] = 0; colors[:10,1] = 0; colors[:10,2] = 1
    colors[10:,0] = 0; colors[10:,1] = 1; colors[10:,2] = 0
    
#     # Create quads (taken from Texture3D._CreateQuads)
#     indices = [0,1,2,3, 4,5,6,7, 3,2,6,5, 0,4,7,1, 0,3,5,4,]# 1,7,6,2]
#     indices = np.array(indices,dtype=np.uint8)
    
#     # Create normals
#     # Note that this is true for the discrete case
#     nn = Pointset(3)
#     for p in pp:
#         nn.Append(1*p.Normalize())
    
#     return pp, nn, indices
    p = Patch(a,vertices, normals, None, gl.GL_QUADS)
    p._colors = colors
    return p


class Patch(Wobject):
    """ Patch(vertices, normals=None, indices=None, type=gl.GL_TRIANGLES)
    A patch is a generic object to visualize a 3D object made up of faces.
    """ 
    
    def __init__(self, parent, vertices, normals=None, indices=None, type=None):
        Wobject.__init__(self, parent)
        
        # Set vertices and information for each vertex
        self._vertices = vertices
        self._normals = normals
        self._colors = None
        self._texcords = None
        
        # Set indices
        self._indices = indices
        
        # We can apply a texture ...
        self._texture = None
        
        # Type
        self._type = gl.GL_TRIANGLES
        if type:
            self._type = type
        
        # Material properties
        self._ambient = (0.7, 0.7, 0.7, 1.0)
        self._diffuse = (0.7, 0.7, 0.7, 1.0)
        self._specular = (0.3, 0.3, 0.3, 1.0)        
        self._shininess = 50
        self._emission = (0.0, 0.0, 0.0, 1.0)
        
#         self._vertices, self._normals = getSphere(3)
#         self._vertices, self._normals, self._indices, self._type = getCube()
    
    
    @Property
    def ambient():
        """ Get/Set the ambient reflection color of the material. Ambient
        light is the light that is everywhere, coming from all directions, 
        independent of the light position. 
        """
        def fget(self):
            return self._ambient
        def fset(self, value):
            self._ambient = _testColor(value)
    
    
    @Property
    def diffuse():
        """ Get/Set the diffuse reflection color of the material. Diffuse
        light comes from one direction, so it's brighter if it comes
        squarely down on a surface than if it barely glances off the 
        surface. It depends on the light position how a material is lit.
        """
        def fget(self):
            return self._diffuse
        def fset(self, value):
            self._diffuse = _testColor(value)
    
    
    @Property
    def ambientAndDiffuse():
        """ Set the diffuse and ambient component simultaneously. Getting
        returns the diffuse component.
        """
        def fget(self):
            return self._diffuse
        def fset(self, value):
            self._diffuse = self._ambient = _testColor(value)
    
    
    @Property
    def specular():
        """ Get/Set the specular reflection color of the material. Specular
        light represents the light that comes from the light source and bounces
        off a surface in a particular direction. It is what makes 
        materials appear shiny.
        """
        def fget(self):
            return self._specular
        def fset(self, value):
            self._specular = _testColor(value)
    
    
    @Property
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
    
    
    @Property
    def emission():
        """ Get/Set the emission color of the material. It is the 
        "self-lighting" property of the material, and usually only makes
        sense for objects that represent lamps or candles etc.
        """
        def fget(self):
            return self._emission
        def fset(self, value):
            self._emission = _testColor(value)
    
    
    def SetTexture(self, data):
        self._texture = TextureObjectToVisualize(2, data)
        self._texture.SetData(data)
    
    def OnDraw(self):
        
        # We need vertices
        if self._vertices is None:
            return
        
        # We need normals
        if self._normals is None:
            self.CalculateNormals()
        
        # Prepare for drawing
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(self._vertices.data)
        #
        gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
        gl.glNormalPointerf(self._normals.data)
        #
        if not None in [self._texcords, self._texture]:
            gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
            gl.glTexCoordPointerf(self._texcords.data)
            # enable texture
            self._texture.Enable(0)
        #
        elif self._colors is not None:
            gl.glEnable(gl.GL_COLOR_MATERIAL)
            gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
            gl.glEnableClientState(gl.GL_COLOR_ARRAY)
            gl.glColorPointerf(self._colors.data)
        #
        gl.glFrontFace(gl.GL_CW)
        
        # Prepare material
        gl.glMaterial(gl.GL_FRONT, gl.GL_AMBIENT, self._ambient)
        gl.glMaterial(gl.GL_FRONT, gl.GL_DIFFUSE, self._diffuse)
        gl.glMaterial(gl.GL_FRONT, gl.GL_SPECULAR, self._specular)
        gl.glMaterial(gl.GL_FRONT, gl.GL_SHININESS, self._shininess)
        gl.glMaterial(gl.GL_FRONT, gl.GL_EMISSION, self._emission)
#         gl.glMaterial(gl.GL_BACK, gl.GL_AMBIENT, (0,1,0,1))
        
        # Prepare lights
        gl.glEnable(gl.GL_LIGHTING)
        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glEnable(gl.GL_NORMALIZE)  # gl.GL_RESCALE_NORMAL
#         gl.glEnable(gl.GL_CULL_FACE)
#         gl.glCullFace(gl.GL_FRONT)
        
        # Draw
        if self._indices is None:
            gl.glDrawArrays(self._type, 0, len(self._vertices))
        elif self._indices.dtype == np.uint8:
            gl.glDrawElements(self._type, len(self._indices), 
                gl.GL_UNSIGNED_BYTE, self._indices)
        elif self._indices.dtype == np.uint32:
            gl.glDrawElements(self._type, len(self._indices), 
                gl.GL_UNSIGNED_INT, self._indices)
        
        # Clean up
        gl.glFlush()
        if self._texture:
            self._texture.Disable()
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_NORMAL_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
#         gl.glDisable(gl.GL_COLOR_MATERIAL)
        gl.glDisable(gl.GL_LIGHTING)


if __name__ == '__main__':
    import visvis as vv
    a = vv.cla()
    a.daspectAuto = False
    a.cameraType = '3d'
    a.SetLimits((-2,2),(-2,2),(-2,2))
    #p = vv.polygon.getCube(a)
    p = vv.solidSphere(2,50,50)
    im = vv.imread('lena.png')
    p.SetTexture(im)
    p.Draw()
    