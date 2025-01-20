# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module sliceTextures

Defines texture wobjects for visualizing slices in 3D volumes.

"""

import OpenGL.GL as gl
import OpenGL.GLU as glu

from visvis.utils.pypoints import Point
from visvis import Wobject, Colormapable
from visvis.core.misc import Property, PropWithDraw, getColor
from visvis.core import shaders
from visvis.wobjects.textures import BaseTexture, TextureObjectToVisualize


class SliceTexture(BaseTexture):
    """ SliceTexture
    
    A slice texture is a 2D texture of a 3D data volume. It enables
    visualizing 3D data without the need for glsl renderering (and can
    therefore be used on older systems.
    
    """
    
    def __init__(self, parent, data, axis=0, index=0):
        BaseTexture.__init__(self, parent, data)
        self._ndim = 3
        
        # Init parameters
        self._axis = axis
        self._index = index
        
        # create texture
        self._texture1 = TextureObjectToVisualize(2, data)
        
        # init shader
        self._InitShader()
        
        # set data  (data to textureToV. only for min/max)
        self.SetData(data)
        
        # init interpolation
        self._texture1._interpolate = True
        
        # For edge
        self._edgeColor = None
        self._edgeColor2 = getColor('g')
        self._edgeWidth = 3.0
        
        # For interaction
        self._interact_over = False
        self._interact_down = False
        self._screenVec = None
        self._refPos = (0,0)
        self._refIndex = 0
        #
        self.eventEnter.Bind(self._OnMouseEnter)
        self.eventLeave.Bind(self._OnMouseLeave)
        self.eventMouseDown.Bind(self._OnMouseDown)
        self.eventMouseUp.Bind(self._OnMouseUp)
        self.eventMotion.Bind(self._OnMouseMotion)
    
    
    def _InitShader(self):
        
        # Add components of shaders
        self.shader.vertex.Clear()
        self.shader.fragment.Clear()
        self.shader.fragment.AddPart(shaders.SH_2F_BASE)
        self.shader.fragment.AddPart(shaders.SH_2F_AASTEPS_0)
        self.shader.fragment.AddPart(shaders.SH_COLOR_SCALAR)
        
        def uniform_shape():
            shape = self._texture1._shape[:2] # as in opengl
            return [float(s) for s in reversed(list(shape))]
        def uniform_extent():
            data = self._texture1._dataRef # as original array
            shape = reversed(data.shape[:2])
            if hasattr(data, 'sampling'):
                sampling = reversed(data.sampling[:2])
            else:
                sampling = [1.0 for s in range(2)]
            
            del data
            return [s1*s2 for s1, s2 in zip(shape, sampling)]
        
        # Set some uniforms
        self.shader.SetStaticUniform('colormap', self._colormap)
        self.shader.SetStaticUniform('shape', uniform_shape)
        self.shader.SetStaticUniform('scaleBias', self._texture1._ScaleBias_get)
        self.shader.SetStaticUniform('extent', uniform_extent)
        self.shader.SetStaticUniform('aakernel', [1.0, 0, 0, 0])
    
    
    def _SetData(self, data):
        """ _SetData(data)
        
        Give reference to the raw data. For internal use. Inheriting
        classes can override this to store data in their own way and
        update the OpenGL textures accordingly.
        
        """
        
        # Store data
        self._dataRef3D = data
        
        # Slice it
        i = self._index
        if self._axis == 0:
            slice = self._dataRef3D[i]
        elif self._axis == 1:
            slice = self._dataRef3D[:,i]
        elif self._axis == 2:
            slice = self._dataRef3D[:,:,i]
        
        # Update texture
        self._texture1.SetData(slice)
    
    
    def _GetData(self):
        """ _GetData()
        
        Get a reference to the raw data. For internal use.
        
        """
        return self._dataRef3D
    
    
    def _GetLimits(self):
        """ Get the limits in world coordinates between which the object exists.
        """
        
        # Obtain untransformed coords
        shape = self._dataRef3D.shape
        x1, x2 = -0.5, shape[2]-0.5
        y1, y2 = -0.5, shape[1]-0.5
        z1, z2 = -0.5, shape[0]-0.5
        
        # There we are
        return Wobject._GetLimits(self, x1, x2, y1, y2, z1, z2)
    
    
    def OnDestroy(self):
        # Clear normaly, and also remove reference to data
        BaseTexture.OnDestroy(self)
        self._dataRef3D = None
    
    
    def OnDrawShape(self, clr):
        # Implementation of the OnDrawShape method.
        gl.glColor(clr[0], clr[1], clr[2], 1.0)
        self._DrawQuads()
    
    
    def OnDraw(self, fast=False):
        # Draw the texture.
        
        # set color to white, otherwise with no shading, there is odd scaling
        gl.glColor3f(1.0,1.0,1.0)
        
        # Enable texture, so that it has a corresponding OpenGl texture.
        # Binding is done by the shader
        self._texture1.Enable(-1)
        self.shader.SetUniform('texture', self._texture1)
        
        # _texture._shape is a good indicator of a valid texture
        if not self._texture1._shape:
            return
        
        if self.shader.isUsable and self.shader.hasCode:
            # fragment shader on -> anti-aliasing
            self.shader.Enable()
        else:
            # Fixed funcrion pipeline
            self.shader.EnableTextureOnly('texture')
        
        # do the drawing!
        self._DrawQuads()
        gl.glFlush()
        
        # clean up
        self.shader.Disable()
        
        
        # Draw outline?
        clr = self._edgeColor
        if self._interact_down or self._interact_over:
            clr = self._edgeColor2
        if clr:
            self._DrawQuads(clr)
        
        # Get screen vector?
        if self._screenVec is None:
            pos1 = [int(s/2) for s in self._dataRef3D.shape]
            pos2 = [s for s in pos1]
            pos2[self._axis] += 1
            #
            screen1 = glu.gluProject(pos1[2], pos1[1], pos1[0])
            screen2 = glu.gluProject(pos2[2], pos2[1], pos2[0])
            #
            self._screenVec = screen2[0]-screen1[0], screen1[1]-screen2[1]
    
    
    def _DrawQuads(self, clr=None):
        """ Draw the quads of the texture.
        This is done in a seperate method to reuse code in
        OnDraw() and OnDrawShape().
        """
        if not self._texture1._shape:
            return
        
        # The -0.5 offset is to center pixels/voxels. This works correctly
        # for anisotropic data.
        x1, x2 = -0.5, self._dataRef3D.shape[2]-0.5
        y2, y1 = -0.5, self._dataRef3D.shape[1]-0.5
        z2, z1 = -0.5, self._dataRef3D.shape[0]-0.5
        
        # Calculate quads
        i = self._index
        if self._axis == 0:
            quads = [   (x1, y2, i),
                        (x2, y2, i),
                        (x2, y1, i),
                        (x1, y1, i),    ]
        elif self._axis == 1:
            quads = [   (x1, i, z2),
                        (x2, i, z2),
                        (x2, i, z1),
                        (x1, i, z1),    ]
        elif self._axis == 2:
            quads = [   (i, y2, z2),
                        (i, y1, z2),
                        (i, y1, z1),
                        (i, y2, z1),    ]
        
        if clr:
            # Draw lines
            gl.glColor(clr[0], clr[1], clr[2], 1.0)
            gl.glLineWidth(self._edgeWidth)
            gl.glBegin(gl.GL_LINE_STRIP)
            for i in [0,1,2,3,0]:
                gl.glVertex3d(*quads[i])
            gl.glEnd()
        else:
            # Draw texture
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f(0,0); gl.glVertex3d(*quads[0])
            gl.glTexCoord2f(1,0); gl.glVertex3d(*quads[1])
            gl.glTexCoord2f(1,1); gl.glVertex3d(*quads[2])
            gl.glTexCoord2f(0,1); gl.glVertex3d(*quads[3])
            gl.glEnd()
    
    
    ## Interaction
    
    def _OnMouseEnter(self, event):
        self._interact_over = True
        self.Draw()
    
    def _OnMouseLeave(self, event):
        self._interact_over = False
        self.Draw()
    
    def _OnMouseDown(self, event):
        
        if event.button == 1:
            
            # Signal that its down
            self._interact_down = True
            
            # Make the screen vector be calculated on the next draw
            self._screenVec = None
            
            # Store position and index for reference
            self._refPos = event.x, event.y
            self._refIndex = self._index
            
            # Redraw
            self.Draw()
            
            # Handle the event
            return True
        
        else:
            event.Ignore()
    
    def _OnMouseUp(self, event):
        self._interact_down = False
        self.Draw()
    
    def _OnMouseMotion(self, event):
        
        # Handle or pass?
        if not (self._interact_down and self._screenVec):
            return
        
        # Get vector relative to reference position
        refPos = Point(self._refPos)
        pos = Point(event.x, event.y)
        vec = pos - refPos
        
        # Length of reference vector, and its normalized version
        screenVec = Point(self._screenVec)
        L = screenVec.norm()
        V = screenVec.normalize()
        
        # Number of indexes to change
        n = vec.dot(V) / L
        
        # Apply!
        self.index = int(self._refIndex + n)
    
    
    ## Properties
    
    
    @PropWithDraw
    def index():
        """ The index of the slice in the volume to display.
        """
        def fget(self):
            return self._index
        def fset(self, value):
            # Check value
            if value < 0:
                value = 0
            maxIndex = self._dataRef3D.shape[self._axis] - 1
            if value > maxIndex:
                value = maxIndex
            # Set and update
            self._index = value
            self._SetData(self._dataRef3D)
        return locals()
    
    
    @PropWithDraw
    def axis():
        """ The axis of the slice in the volume to display.
        """
        def fget(self):
            return self._axis
        def fset(self, value):
            # Check value
            if value < 0 or value >= 3:
                raise ValueError('Invalid axis.')
            # Set and update index (can now be out of bounds.
            self._axis = value
            self.index = self.index
        return locals()
    
    
    @PropWithDraw
    def edgeColor():
        """ The color of the edge of the slice (can be None).
        """
        def fget(self):
            return self._edgeColor
        def fset(self, value):
            self._edgeColor = getColor(value)
        return locals()
    
    
    @PropWithDraw
    def edgeColor2():
        """ The color of the edge of the slice when interacting.
        """
        def fget(self):
            return self._edgeColor2
        def fset(self, value):
            self._edgeColor2 = getColor(value)
        return locals()
    

class SliceTextureProxy(Wobject, Colormapable):
    """ SliceTextureProxy(*sliceTextures)
    
    A proxi class for multiple SliceTexture instances. By making them
    children of an instance of this class, their properties can be
    changed simultaneously.
    
    This makes it possible to call volshow() and stay agnostic of how
    the volume is vizualized (using a 3D render, or with 3 slice
    textures); all public texture-specific methods and properties are
    transferred to all children automatically.
    
    """
    
    
    def SetData(self, *args, **kwargs):
        for s in self.children:
            s.SetData(*args, **kwargs)
    
    def Refresh(self, *args, **kwargs):
        for s in self.children:
            s.Refresh(*args, **kwargs)
    
    def SetClim(self, *args, **kwargs):
        for s in self.children:
            s.SetClim(*args, **kwargs)
    
    def _GetColormap(self):
        return self.children[0].colormap
    def _SetColormap(self, value):
        for s in self.children:
            s._SetColormap(value)
    
    def _EnableColormap(self, texUnit=0):
        return self.children[0]._EnableColormap(texUnit)
    def _DisableColormap(self):
        return self.children[0]._DisableColormap()
    
    def _GetClim(self):
        return self.children[0].clim
    def _SetClim(self, value):
        for s in self.children:
            s._SetClim(value)
    
    @Property
    def renderStyle():
        """ Not available for SliceTextures. This
        property is implemented to be able to produce a warning when
        it is used.
        """
        def fget(self):
            return 'None'
        def fset(self, value):
            print('Warning: SliceTexture instances have no renderStyle.')
        return locals()
    
    @Property
    def isoThreshold():
        """ Not available for SliceTextures. This
        property is implemented to be able to produce a warning when
        it is used.
        """
        def fget(self):
            return 0.0
        def fset(self, value):
            print('Warning: SliceTexture instances have no isoThreshold.')
        return locals()
    
    @Property
    def interpolate():
        """ Get/Set whether to interpolate the image when zooming in
        (using linear interpolation).
        """
        def fget(self):
            return self.children[0].interpolate
        def fset(self, value):
            for s in self.children:
                s.interpolate = value
        return locals()
    
    @Property
    def index():
        """ The index of the slice in the volume to display.
        """
        def fget(self):
            return self.children[0].index
        def fset(self, value):
            for s in self.children:
                s.index = value
        return locals()
    
    @Property
    def axis():
        """ The axis of the slice in the volume to display.
        """
        def fget(self):
            return self.children[0].axis
        def fset(self, value):
            for s in self.children:
                s.axis = value
        return locals()
    
    @Property
    def edgeColor():
        """ The color of the edge of the slice (can be None).
        """
        def fget(self):
            return self.children[0].edgeColor
        def fset(self, value):
            for s in self.children:
                s.edgeColor = value
        return locals()
    
    @Property
    def edgeColor2():
        """ The color of the edge of the slice when interacting.
        """
        def fget(self):
            return self.children[0].edgeColor2
        def fset(self, value):
            for s in self.children:
                s.edgeColor2 = value
        return locals()
