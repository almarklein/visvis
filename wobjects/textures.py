# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module textures

Defines the texture base class and the Texture2D and Texture3D
wobjects. 

2D textures can be visualized without using GLSL. If GLSL is enabled, it
allows using clim, colormap and antialiasing (aa property).

3D textures are rendered using GLSL shader programs. The shader can be
selected using texture3D.renderStyle = 'ray', where 'ray' can be the
name of any of the available fragment shaders.


"""

import OpenGL.GL as gl
import OpenGL.GLU as glu

import numpy as np
import math, time, os

from visvis.pypoints import Point, Pointset, Aarray, is_Aarray
#
from visvis import Range, Wobject, Colormapable
from visvis.core.misc import Property, PropWithDraw, DrawAfter, getColor
from visvis.core.misc import Transform_Translate, Transform_Scale, Transform_Rotate
from visvis.core.shaders import vshaders, fshaders, GlslProgram
#
from visvis.core import TextureObject, Colormap


# A correction for the clim. For a datatype of uint8, the fragents
# are mapped between 0 and 1 for 0 and 255 respectively. For int8
# the values are mapped between -1 and 1 for -127 and 128 respectively.
climCorrection = { 'uint8':2**8, 'int8':2**7, 'uint16':2**16, 'int16':2**15, 
                   'uint32':2**32, 'int32':2**31, 'float32':1, 'float64':1,
                   'bool':2**8}


def minmax(data):
    """ minmax(data)
    
    Get the min and max of the data, ignoring inf and nan.
    
    """
    
    # Check for inf and nan
    M1 = np.isnan(data)
    M2 = np.isinf(data)
    
    # Select all 'normal' elements 
    if np.any(M1) or np.any(M2):
        data2 = data[ ~(M1|M2) ]
    else:
        data2 = data
    
    # Return min and max
    return data2.min(), data2.max()


class TextureObjectToVisualize(TextureObject):
    """ TextureObjectToVisualize(ndim, data, interpolate=False)
    
    A texture object aimed towards visualization. 
    This is what is actually used in Texture2D and Texture3D objects.
    It has no propererties, but some private attributes
    which are set by the real interface (the Texture*D objects).
    Basically, it handles the color limits.
    
    """
    
    def __init__(self, ndim, data, interpolate=False):
        TextureObject.__init__(self, ndim)
        
        # interpolate?
        self._interpolate = interpolate
        
        # the limits
        self._clim = Range(0,1)
        self._climCorrection = 1.0
        self._climRef = Range(0,1) # the "original" range
        
        # init clim and colormap
        self._climRef.Set(*minmax(data))
        self._clim = self._climRef.Copy()
    
    
    def _UploadTexture(self, data, *args):
        """ "Overloaded" method to upload texture data
        """
        
        # Set alignment to 1. It is 4 by default, but my data array has no
        # strides, so in order for the image not to be distorted, I set it 
        # to 1. I assume graphics cards can still render in hardware. If 
        # not, I would have to add one or two rows to my data instead.
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT,1)
        
        # init transferfunctions and set clim to full range
        self._ScaleBias_init(data.dtype.name)
        
        # create texture
        TextureObject._UploadTexture(self, data, *args)
        
        # set interpolation and extrapolation parameters            
        tmp1 = gl.GL_NEAREST
        tmp2 = {False:gl.GL_NEAREST, True:gl.GL_LINEAR}[self._interpolate]
        gl.glTexParameteri(self._texType, gl.GL_TEXTURE_MIN_FILTER, tmp1)
        gl.glTexParameteri(self._texType, gl.GL_TEXTURE_MAG_FILTER, tmp2)
        gl.glTexParameteri(self._texType, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameteri(self._texType, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
        
        # reset transfer
        self._ScaleBias_afterUpload()
        
        # should we correct for downsampling?
        factor = self._dataRef.shape[0] / float(data.shape[0])
        if factor > 1:
            self._trafo_scale.sx *= factor 
            self._trafo_scale.sy *= factor
            if self._ndim==3:
                self._trafo_scale.sz *= factor
        
        # Set clamping. When testing the raycasting, comment these lines!
        if self._ndim==3:
            gl.glTexParameteri(self._texType, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
            gl.glTexParameteri(self._texType, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
            gl.glTexParameteri(self._texType, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP)
    
    
    def _UpdateTexture(self, data, *args):
        """ "Overloaded" method to update texture data
        """
        
        # init transferfunctions and set clim to full range
        self._ScaleBias_init(data.dtype.name)
        
        # create texture
        TextureObject._UpdateTexture(self, data, *args)
        
        # reset transfer
        self._ScaleBias_afterUpload()
    
    
    def _ScaleBias_init(self, datatype):
        """ Given the climRef (which is set to data.min() and data.max())
        in constructor, set the scale 
        and bias for copying data to opengl memory. Correct for the dataype.
        Also set the default value for clim to the full data range.
        
        More info: OpenGL will map the full range of the datatype
        to 0:1 for unsigned datatypes, and to -1:1 for signed datatypes.
        For floats, 0:1 is mapped to 0:1. We modify the scale, such that
        the full range of the data (not the datatype) is scaled between 0:1.
        This way we can also visualize float data with values other than 0:1.
        """
        # store data range as a reference and init clim with that
        #self._clim = self._climRef.Copy()
        # calculate scale and bias
        ran = self._climRef.range
        if ran==0:
            ran = 1.0
        scale = climCorrection[datatype] / ran
        bias = -self._climRef.min / ran
        # set transfer functions
        gl.glPixelTransferf(gl.GL_RED_SCALE, scale)
        gl.glPixelTransferf(gl.GL_GREEN_SCALE, scale)
        gl.glPixelTransferf(gl.GL_BLUE_SCALE, scale)
        gl.glPixelTransferf(gl.GL_RED_BIAS, bias)
        gl.glPixelTransferf(gl.GL_GREEN_BIAS, bias)
        gl.glPixelTransferf(gl.GL_BLUE_BIAS, bias)
    
    
    def _ScaleBias_afterUpload(self):
        """ Reset the transferfunctions. """
        gl.glPixelTransferf(gl.GL_RED_SCALE, 1.0)
        gl.glPixelTransferf(gl.GL_GREEN_SCALE, 1.0)
        gl.glPixelTransferf(gl.GL_BLUE_SCALE, 1.0)
        gl.glPixelTransferf(gl.GL_RED_BIAS, 0.0)
        gl.glPixelTransferf(gl.GL_GREEN_BIAS, 0.0)
        gl.glPixelTransferf(gl.GL_BLUE_BIAS, 0.0)
    
    
    def _ScaleBias_get(self):
        """ Given clim, get scale and bias to apply in shader."""
        # ger ranges and correct if zero
        r1, r2 = self._clim.range, self._climRef.range
        if r1==0:
            r1 = 1.0
        if r2==0:
            r2 = 1.0
        # calculate scale and bias
        scale = self._climRef.range / r1
        bias = (self._climRef.min - self._clim.min) / r2    
        return scale, bias


class BaseTexture(Wobject, Colormapable):
    """ BaseTexture(parent, data)
    
    Base texture class for visvis 2D and 3D textures. 
    
    """
    
    def __init__(self, parent, data):
        
        # Check data first
        if not isinstance(data, np.ndarray):
            raise ValueError('Textures can only be described using Numpy arrays.')
        
        # Instantiate as wobject (after making "sure" this texture can be ok)
        Wobject.__init__(self, parent)
        Colormapable.__init__(self)
        
        # create texture (remember, this is an abstract class)
        self._texture1 = None
        
        # create glsl program for this texture...
        self._program1 = program =  GlslProgram()
        
        # scale and translation transforms
        self._trafo_scale = Transform_Scale()
        self._trafo_trans = Transform_Translate()
        self.transformations.append(self._trafo_trans)
        self.transformations.append(self._trafo_scale)        
    
    
    @DrawAfter
    def SetData(self, data):
        """ SetData(data)
        
        (Re)Set the data to display. If the data has the same shape
        as the data currently displayed, it can be updated very
        efficiently. 
        
        If the data is an anisotripic array (vv.Aarray)
        the sampling and origin are (re-)applied.
        
        """ 
        
        # set data to texture
        self._SetData(data)
        
        # if Aarray, edit scaling and transform
        if is_Aarray(data):
            if hasattr(data,'_sampling') and hasattr(data,'_origin'):
                if data.ndim >= 3 and data.shape[2] > 4:
                    # Three dimensional
                    self._trafo_scale.sx = data.sampling[2]
                    self._trafo_scale.sy = data.sampling[1]
                    self._trafo_scale.sz = data.sampling[0]
                    #
                    self._trafo_trans.dx = data.origin[2]
                    self._trafo_trans.dy = data.origin[1]
                    self._trafo_trans.dz = data.origin[0]
                else:
                    # Two dimensional
                    self._trafo_scale.sx = data.sampling[1]
                    self._trafo_scale.sy = data.sampling[0]
                    #
                    self._trafo_trans.dx = data.origin[1]
                    self._trafo_trans.dy = data.origin[0]
    
    
    def _SetData(self, data):
        """ _SetData(data)
        
        Give reference to the raw data. For internal use. Inheriting 
        classes can override this to store data in their own way and
        update the OpenGL textures accordingly.
        
        """
        self._texture1.SetData(data)
    
    
    def _GetData(self):
        """ _GetData()
        
        Get a reference to the raw data. For internal use. Can return None.
        
        """
        return self._texture1._dataRef
    
    
    def Refresh(self):
        """ Refresh()
        
        Refresh the data. If the numpy array was changed, calling this 
        function will re-upload the data to OpenGl, making the change
        visible. This can be done efficiently.
        
        """
        data = self._GetData()
        if data is not None:
            self.SetData(data)
   
    
    def OnDestroyGl(self):
        # Clean up OpenGl resources.
        
        # remove texture from opengl memory
        self._texture1.DestroyGl()
        
        # clear shaders
        self._program1.DestroyGl()
        
        # remove colormap's texture from memory        
        if hasattr(self, '_colormap'):
            self._colormap.DestroyGl()
    
    
    def OnDestroy(self):
        # Clean up any resources.
        self._texture1.Destroy()
        if hasattr(self, '_colormap'):
            self._colormap.Destroy()
    
    
    def OnDrawFast(self):
        self.OnDraw(True)
    
    
    @PropWithDraw
    def interpolate():
        """ Get/Set whether to interpolate the image when zooming in 
        (using linear interpolation). 
        """
        def fget(self):
            return self._texture1._interpolate
        def fset(self, value):
            self._texture1._interpolate = bool(value)
            # bind the texture
            texType = self._texture1._texType            
            gl.glBindTexture(texType, self._texture1._texId)
            # set interpolation
            tmp = {False:gl.GL_NEAREST, True:gl.GL_LINEAR}[bool(value)]
            gl.glTexParameteri(texType, gl.GL_TEXTURE_MAG_FILTER, tmp)
    
    
    def _clim():
        """ Make the clim property use the _clim property of texture1
        """
        def fget(self):
            return self._texture1._clim
        def fset(self, value):
            self._texture1._clim = value
    
    
    @DrawAfter
    def SetClim(self, *mima):
        """ SetClim(min, max)
        
        Set the contrast limits. Different than the property clim, this
        re-uploads the texture using different transfer functions. You should
        use this if your data has a higher contrast resolution than 8 bits.
        Takes a bit more time than clim though (which basically takes no
        time at all).
        
        """
        if len(mima)==0:
            # set default values
            data = self._GetData()
            if data is None:
                return 
            mima = minmax(data)
        
        elif len(mima)==1:
            # a range was given
            mima = mima[0]
            
        # Set climref and clim
        self._texture1._climRef.Set(mima[0], mima[1])
        self._texture1._clim.Set(mima[0], mima[1])
        
        # Signal update, on next draw, it is uploaded again, using
        # the newly set climref.
        self._texture1._uploadFlag = abs(self._texture1._uploadFlag)




class Texture2D(BaseTexture):
    """ Texture2D(parent, data)
    
    A data type that represents structured data in
    two dimensions (an image). Supports grayscale, RGB, 
    and RGBA images.
    
    Texture2D objects can be created with the function vv.imshow().
    
    """
    
    def __init__(self, parent, data):
        BaseTexture.__init__(self, parent, data)
        
        # create texture and set data
        self._texture1 = TextureObjectToVisualize(2, data)
        self.SetData(data)
        
        # init antialiasing
        self.aa = 0
    
    
    def _CreateGaussianKernel(self):
        """ Create kernel values to use in the aa program.
        Returns 4 element list which should be applied using the
        following indices: 3 2 1 0 1 2 3
        """
        
        figure = self.GetFigure()
        axes = self.GetAxes()
        if not figure or not axes:
            return 1,0,0,0
        
        # determine relative kernel size
        w,h = figure.position.size
        cam = axes.camera
        sx = (cam.view_zoomx / 1.0 ) / w
        sy = (cam.view_zoomy / 1.0 ) / h
        # correct for fact that humans prefer sharpness
        tmp = 0.7
        sx, sy = sx*tmp, sy*tmp
        
        # keep >= 0 so we can devide
        if sx<0.01: sx = 0.01
        if sy<0.01: sy = 0.01
        
        # calculate kernel
        #  3 2 1 0 1 2 3
        k = [1.0,0,0,0] 
        k[1] = math.exp( -1.0 / (2*sx**2) )
        k[2] = math.exp( -2.0 / (2*sy**2) )
        k[3] = math.exp( -3.0 / (2*sy**2) )
        
        # normalize
        if self.aa == 1:
            l = k[0] + 2*k[1]
        elif self.aa == 2:
            l = k[0] + 2*k[1] + 2*k[2]
        elif self.aa == 3:
            l = k[0] + 2*k[1] + 2*k[2] + 2*k[3]
        else:
            l = k[0]
        k = [e/l for e in k]
        
        # done!        
        return k
    
    
    def OnDrawShape(self, clr):
        # Implementation of the OnDrawShape method.
        gl.glColor(clr[0], clr[1], clr[2], 1.0)
        self._DrawQuads()
    

    def OnDraw(self, fast=False):
        # Draw the texture.
        
        # set color to white, otherwise with no shading, there is odd scaling
        gl.glColor3f(1.0,1.0,1.0)
        
        # draw texture also from beneeth
        #gl.glCullFace(gl.GL_FRONT_AND_BACK)
        
        # enable texture
        self._texture1.Enable(0)
        
        # _texture._shape is a good indicator of a valid texture
        if not self._texture1._shape:
            return
        
        # fragment shader on
        if self._program1.IsUsable():
            self._program1.Enable()
            # textures        
            self._program1.SetUniformi('texture', [0])        
            self._colormap.Enable(1)
            self._program1.SetUniformi('colormap', [1])
            # uniform variables
            shape = self._texture1._shape # how it is in opengl
            k = self._CreateGaussianKernel()
            self._program1.SetUniformf('kernel', k)
            self._program1.SetUniformf('dx', [1.0/shape[0]])
            self._program1.SetUniformf('dy', [1.0/shape[1]])
            self._program1.SetUniformf('scaleBias', self._texture1._ScaleBias_get())
            self._program1.SetUniformi('applyColormap', [len(shape)==2])
        
        # do the drawing!
        self._DrawQuads()
        gl.glFlush()
        
        # clean up
        self._texture1.Disable()
        self._colormap.Disable()
        self._program1.Disable()
    
    
    def _DrawQuads(self):
        """ Draw the quads of the texture. 
        This is done in a seperate method to reuse code in 
        OnDraw() and OnDrawShape(). 
        """        
        if not self._texture1._shape:
            return        
        
        # The -0.5 offset is to center pixels/voxels. This works correctly
        # for anisotropic data.
        x1, x2 = -0.5, self._texture1._shape[1]-0.5
        y2, y1 = -0.5, self._texture1._shape[0]-0.5
        
        # draw
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0,0); gl.glVertex3d(x1, y2, 0.0)
        gl.glTexCoord2f(1,0); gl.glVertex3d(x2, y2, 0.0)
        gl.glTexCoord2f(1,1); gl.glVertex3d(x2, y1, 0.0)
        gl.glTexCoord2f(0,1); gl.glVertex3d(x1, y1, 0.0)
        gl.glEnd()
    
    
    def _GetLimits(self):
        """ Get the limits in world coordinates between which the object exists.
        """
        
        # Obtain untransformed coords 
        shape = self._texture1._dataRef.shape
        x1, x2 = -0.5, shape[1]-0.5
        y1, y2 = -0.5, shape[0]-0.5
        z1, z2 = 0, 0
        
        # There we are
        return Wobject._GetLimits(self, x1, x2, y1, y2, z1, z2)
    
    
    @PropWithDraw
    def aa():
        """ Get/Set anti aliasing.
          * 0 or False for no anti aliasing
          * 1 for minor anti aliasing
          * 2 for medium anti aliasing
          * 3 for much anti aliasing
          * a string to chose a shader (to allow home-made shaders)
        """
        def fget(self):
            return self._aa
        def fset(self, value):
            if not value:
                value = 0
            if isinstance(value, (int,float)):
                if value < 0 or value > 3:
                    print "Texture2D.aa: value should be 0,1,2,3 or a string."
                    return
                self._aa = value
                if self._aa == 1:
                    self._program1.SetFragmentShader(fshaders['aa1'])
                elif self._aa == 2:
                    self._program1.SetFragmentShader(fshaders['aa2'])
                elif self._aa == 3:
                    self._program1.SetFragmentShader(fshaders['aa3'])
                else:
                    self._program1.SetFragmentShader(fshaders['aa0'])
            elif isinstance(value, basestring):
                if value in fshaders:
                    self._program1.SetFragmentShader(fshaders[value])
                else:
                    print "Texture2D.aa: unknown shader, no action taken."
            else:
                raise ValueError("Texture2D.aa accepts integer or string.")
    

class Texture3D(BaseTexture):
    """ Texture3D(parent, data, renderStyle='mip')
    
    A data type that represents structured data in three dimensions (a volume).
    
    If the drawing hangs, your video drived decided to render in 
    software mode. This is unfortunately (as far as I know) not possible 
    to detect programatically. It might help if your data is shaped a 
    power of 2. The mip renderer is the 'easiest' for most systems to render.
    
    Texture3D objects can be created with the function vv.volshow().
    
    """
    
    def __init__(self, parent, data, renderStyle='mip'):
        BaseTexture.__init__(self, parent, data)
        
        # create texture and set data
        self._texture1 = TextureObjectToVisualize(3, data)
        self.SetData(data)
        
        # init interpolation
        self._texture1._interpolate = True # looks so much better
        
        # init iso shader param
        self._isoThreshold = 0.0
        
        # init vertex shader
        self._program1.SetVertexShader(vshaders['calculateray'])
        # init fragment shader, be robust if user gives invalid method
        self._renderStyle = ''
        self.renderStyle = renderStyle
        if not self._renderStyle:
            self.renderStyle = 'mip'
        
        # Attribute to store array of quads (vertices and texture coords)
        self._quads = None
        # Also store daspect, if this changes quads should be recalculated
        self._daspectStored = (1,1,1)
    
    
    def OnDrawShape(self, clr):
        # Implementation of the OnDrawShape method.
        gl.glColor(clr[0], clr[1], clr[2], 1.0)        
        self._DrawQuads()
    
    
    def OnDraw(self, fast=False):
        # Draw the texture.
        
        # enable this texture
        self._texture1.Enable(0)
        
        # _texture._shape is a good indicator of a valid texture
        if not self._texture1._shape:
            return
        
        # Prepare by setting things to their defaults. This might release some
        # memory so result in a bigger chance that the shader is run in 
        # hardware mode. On ATI, the line and point smoothing should be off
        # if you want to use gl_FragCoord. (Yeah, I do not see the connection
        # either...)
        gl.glPointSize(1)
        gl.glLineWidth(1)
        gl.glDisable(gl.GL_LINE_STIPPLE)
        gl.glDisable(gl.GL_LINE_SMOOTH)
        gl.glDisable(gl.GL_POINT_SMOOTH)
        
        # only draw front-facing parts
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        
        # Use texture matrix to supply a modelview matrix without scaling
#         gl.glPushMatrix()
#         axes = self.GetAxes()
#         if axes:
#             cam=axes._cameras['3d']
#             daspect = axes.daspect
#             gl.glScale( 1.0/daspect[0], 1.0/daspect[1] , 1.0/daspect[2] )
            
        # fragment shader on
        if self._program1.IsUsable():
            self._program1.Enable()
            
            # bind texture- and help-textures (create if it does not exist)
            self._program1.SetUniformi('texture', [0])        
            self._colormap.Enable(1)
            self._program1.SetUniformi('colormap', [1])
            
            # set uniforms: parameters
            shape = self._texture1._shape[:3] # as in opengl
            self._program1.SetUniformf('shape',reversed(list(shape)) )
            ran = self._texture1._climRef.range
            if ran==0:
                ran = 1.0
            th = (self._isoThreshold - self._texture1._climRef.min ) / ran
            self._program1.SetUniformf('th', [th]) # in 0:1
            if fast:
                self._program1.SetUniformf('stepRatio', [0.4])
            else:
                self._program1.SetUniformf('stepRatio', [1.0])
            self._program1.SetUniformf('scaleBias', self._texture1._ScaleBias_get())        
        
        # do the actual drawing
        self._DrawQuads()
        
        
#         gl.glPopMatrix()
        
        # clean up
        gl.glFlush()        
        self._texture1.Disable()
        self._colormap.Disable()
        self._program1.Disable()
        #
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glEnable(gl.GL_POINT_SMOOTH)
    
    
    def _CreateQuads(self):
        
        axes = self.GetAxes()
        if not axes:
            return
        
        # Store daspect so we can detect it changing
        self._daspectStored = axes.daspect
        
        # Note that we could determine the world coordinates and use
        # them directly here. However, the way that we do it now (using
        # the transformations) is to be preferred, because that way the
        # transformations are applied via the ModelView matrix stack,
        # and can easily be made undone in the raycaster.
        # The -0.5 offset is to center pixels/voxels. This works correctly
        # for anisotropic data.
        x0,x1 = -0.5, self._texture1._shape[2]-0.5
        y0,y1 = -0.5, self._texture1._shape[1]-0.5
        z0,z1 = -0.5, self._texture1._shape[0]-0.5
        
        # prepare texture coordinates
        t0, t1 = 0, 1
        
        # I previously swapped coordinates to make sure the right faces
        # were frontfacing. Now I apply culling to achieve the same 
        # result in a better way.
        
        # using glTexCoord* is the same as glMultiTexCoord*(GL_TEXTURE0)
        # Therefore we need to bind the base texture to 0.
        
        # draw. So we draw the six planes of the cube (well not a cube,
        # a 3d rectangle thingy). The inside is only rendered if the 
        # vertex is facing front, so only 3 planes are rendered at a        
        # time...                
        
        tex_coord, ver_coord = Pointset(3), Pointset(3)
        indices = [0,1,2,3, 4,5,6,7, 3,2,6,5, 0,4,7,1, 0,3,5,4, 1,7,6,2]
        
        # bottom
        tex_coord.append((t0,t0,t0)); ver_coord.append((x0, y0, z0)) # 0
        tex_coord.append((t1,t0,t0)); ver_coord.append((x1, y0, z0)) # 1
        tex_coord.append((t1,t1,t0)); ver_coord.append((x1, y1, z0)) # 2
        tex_coord.append((t0,t1,t0)); ver_coord.append((x0, y1, z0)) # 3
        # top
        tex_coord.append((t0,t0,t1)); ver_coord.append((x0, y0, z1)) # 4    
        tex_coord.append((t0,t1,t1)); ver_coord.append((x0, y1, z1)) # 5
        tex_coord.append((t1,t1,t1)); ver_coord.append((x1, y1, z1)) # 6
        tex_coord.append((t1,t0,t1)); ver_coord.append((x1, y0, z1)) # 7
        
        # Store quads
        self._quads = (tex_coord, ver_coord, np.array(indices,dtype=np.uint8))
    
    
    def _DrawQuads(self):
        """ Draw the quads of the texture. 
        This is done in a seperate method to reuse code in 
        OnDraw() and OnDrawShape(). 
        """        
        
        # Get axes
        axes = self.GetAxes()
        if not axes:
            return
        
        # should we draw?
        if not self._texture1._shape:
            return 
        
        # should we create quads?
        if not self._quads or self._daspectStored != axes.daspect:
            self._CreateQuads()
        
        # get data
        tex_coord, ver_coord, ind = self._quads
        
        # Set culling (take data aspect into account!)        
        tmp = 1        
        for i in axes.daspect:
            if i<0:
                tmp *= -1
        gl.glFrontFace({1:gl.GL_CW, -1:gl.GL_CCW}[tmp])        
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        
        # init vertex and texture array
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glVertexPointerf(ver_coord.data)
        gl.glTexCoordPointerf(tex_coord.data)
        
        # draw
        gl.glDrawElements(gl.GL_QUADS, len(ind), gl.GL_UNSIGNED_BYTE, ind)
        
        # disable vertex array        
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        #
        gl.glDisable(gl.GL_CULL_FACE)
    
    
    def _GetLimits(self):
        """ Get the limits in world coordinates between which the object exists.
        """
        
        # Obtain untransformed coords 
        shape = self._texture1._dataRef.shape
        x1, x2 = -0.5, shape[2]-0.5
        y1, y2 = -0.5, shape[1]-0.5
        z1, z2 = -0.5, shape[0]-0.5
        
        # There we are
        return Wobject._GetLimits(self, x1, x2, y1, y2, z1, z2)
    
    
    @PropWithDraw
    def renderStyle():
        """ Get/Set the render style to render the volumetric data:
          * mip: maximum intensity projection
          * iso: isosurface rendering
          * rays: ray casting (tip: use the ColormapEditor wibject to 
            control transparancy)
          * colormip: mip render with color (RGB or RGBA) data
          * coloriso: iso render for color data
        If drawing takes really long, your system renders in software
        mode. Try rendering data that is shaped with a power of two. This 
        helps on some cards.
        """
        def fget(self):
            return self._renderStyle
        def fset(self, style):            
            style = style.lower()
            # first try directly
            if style in fshaders:
                self._renderStyle = style
                self._program1.SetFragmentShader(fshaders[style])
            # then try aliases
            elif style in ['mip']:
                self._renderStyle = 'mip'
                self._program1.SetFragmentShader(fshaders['mip'])
            elif style in ['iso', 'isosurface']:
                self._renderStyle = 'isosurface'
                self._program1.SetFragmentShader(fshaders['isosurface'])
            elif style in ['coloriso', 'colorisosurface']:
                self._renderStyle = 'colorisosurface'
                self._program1.SetFragmentShader(fshaders['colorisosurface'])
            elif style in ['ray', 'rays', 'raycasting']:
                self._renderStyle = 'raycasting'
                self._program1.SetFragmentShader(fshaders['raycasting'])
            else:
                print "Unknown render style in Texture3d.renderstyle."

    @PropWithDraw
    def isoThreshold():
        """ Get/Set the isothreshold value used in the isosurface renderer.
        """
        def fget(self):
            return self._isoThreshold
        def fset(self, value):
            # make float
            value = float(value)
            # store
            self._isoThreshold = value


class MultiTexture3D(Texture3D):
    """ MultiTexture3D(parent, data1, data2)
    
    This is an example of what multi-texturing would look like
    in Visvis. Not tested.
    
    """
    
    def __init__(self, parent, data1, data2):
        Texture3D.__init__(self, parent, data1)
        
        # create second texture and set data
        self._texture2 = TextureObject(gl.GL_TEXTURE_3D)
        self.SetData(data2)
    
    
    def OnDraw(self, fast=False):
        # Draw the texture.
        
        # enable textures
        self._texture1.Enable(0)
        self._texture2.Enable(0)
        
        # _texture._shape is a good indicator of a valid texture
        if not self._texture1._shape or not self._texture2._shape:
            return
        
        # Prepare by setting things to their defaults. This might release some
        # memory so result in a bigger chance that the shader is run in 
        # hardware mode. On ATI, the line and point smoothing should be off
        # if you want to use gl_FragCoord. (Yeah, I do not see the connection
        # either...)
        gl.glPointSize(1)
        gl.glLineWidth(1)
        gl.glDisable(gl.GL_LINE_STIPPLE)
        gl.glDisable(gl.GL_LINE_SMOOTH)
        gl.glDisable(gl.GL_POINT_SMOOTH)
        
        # only draw front-facing parts
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        
        # fragment shader on
        if self._program1.IsUsable():
            self._program1.Enable()
            
            # bind texture- and help-textures (create if it does not exist)
            self._program1.SetUniformi('texture', [0])        
            self._colormap.Enable(1)
            self._program1.SetUniformi('colormap', [1])
            
            # set uniforms: parameters
            shape = self._texture1._shape # as in opengl
            self._program1.SetUniformf('shape',reversed(list(shape)) )
            ran = self._climRef.range
            if ran==0:
                ran = 1.0
            th = (self._isoThreshold - self._climRef.min ) / ran
            self._program1.SetUniformf('th', [th]) # in 0:1
            if fast:
                self._program1.SetUniformf('stepRatio', [0.4])
            else:
                self._program1.SetUniformf('stepRatio', [1.0])
            self._program1.SetUniformf('scaleBias', self._ScaleBias_get())        
        
        # do the actual drawing
        self._DrawQuads()
        
        # clean up
        gl.glFlush()        
        self._texture1.Disable()
        self._texture2.Disable()
        self._colormap.Disable()
        self._program1.Disable()
        #
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glEnable(gl.GL_POINT_SMOOTH)


    def OnDestroyGl(self):
        # Clean up OpenGl resources.
        
        # remove texture from opengl memory
        self._texture1.DestroyGl()
        self._texture2.DestroyGl()
        
        # clear shaders
        self._program1.DestroyGl()
        
        # remove colormap's texture from memory        
        if hasattr(self, '_colormap'):
            self._colormap.DestroyGl()
    
    
    def OnDestroy(self):
        # Clean up any resources.
        self._texture1.Destroy()
        self._texture2.Destroy()
        if hasattr(self, '_colormap'):
            self._colormap.Destroy()

