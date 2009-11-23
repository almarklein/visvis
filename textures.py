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
#   Copyright (C) 2009 Almar Klein

""" Module textures

Defined the texture base class and the Texture2D and Texture3D
wobjects. 

3D textures are rendered in two stages. First the coordinates of
the back faces are rendered and stored. This is done in the OnDrawPre
phase of the Visvis drawing system. These coordinates are used in the
eventual drawing to determine how (and how far) the rays should travel.
GLSL programs are used for rendering the 3D textures. 

$Author: almar@SAS $
$Date: 2009-11-23 16:20:59 +0100 (Mon, 23 Nov 2009) $
$Rev: 1308 $

"""

import OpenGL.GL as gl
import OpenGL.GL.ARB.shader_objects as gla
import OpenGL.GLU as glu

import numpy as np
import math, time, os

from misc import getResourceDir
from misc import Property, Range, OpenGLError, Position
from events import *
from base import Wobject
from misc import Transform_Translate, Transform_Scale, Transform_Rotate


#import visvis.shading as shading
import points


class Shading:
    """ Shading class. A single instance of this class should be
    created, which holds the code for the shading code programs. """
    def __init__(self):
        path = getResourceDir()
        
        for filename in os.listdir(path):
        
            # only glsl files
            if not filename.endswith('.glsl'):
                continue
            
            # read code
            f = open( os.path.join(path, filename) )
            tekst = f.read()
            f.close()
            
            # insert into this namespace
            varname = filename.rstrip('.glsl')
            self.__dict__[varname] = tekst
            #g = globals()
            #g[varname] = tekst

shading = Shading()


class GlslProgram:
    """ GLSL program
    A class representing a GLSL (OpenGL Shading Language) program.
    It provides an easy interface for adding vertex and fragment shaders
    and setting variables used in them.
    """
    # todo: detect and handle if a computer cannot handle shading code.
    
    def __init__(self):
        # ids
        self._programId = 0
        self._shaderIds = []
        
        # code for the shaders        
        self._fragmentCode = ''
        self._vertexCode = ''
        
#         # determine if we can do this at all
#         tmp = gl.glGetString(gl.GL_VERSION)
#         self._version = int(tmp[0])
    
    
    def _IsValid(self):
        return ( self._programId>0 and gl.glIsProgram(self._programId) )
    
    
    def Enable(self):
        """ Start using the program. """
        if (self._fragmentCode or self._vertexCode) and not self._IsValid():
            self._CreateProgramAndShaders()
        
        if self._IsValid():
            gla.glLinkProgramARB(self._programId)
            self._checkForOpenglError('Link')
            gla.glUseProgramObjectARB(self._programId)
            self._checkForOpenglError('Use')
        else:
            gla.glUseProgramObjectARB(0)
    
    def Disable(self):
        """ Stop using the program. """
        gla.glUseProgramObjectARB(0)
    
    
    def SetVertexShader(self, code):
        """ Create a vertex shader from code and attach to the program.
        """
        self._vertexCode = code
        self.Clear()


    def SetFragmentShader(self, code):
        """ Create a fragment shader from code and attach to the program.
        """
        self._fragmentCode = code
        self.Clear()
    
    
    def SetVertexShaderFromFile(self, path):
        try:
            f = open(path, 'r')
            code = f.read()
            f.close()
        except Exception, why:
            print "Could not create shader: ", why.message            
        self.SetVertexShader(code)
    
    
    def SetFagmentShaderFromFile(self, path):
        try:
            f = open(path, 'r')
            code = f.read()
            f.close()            
        except Exception, why:
            print "Could not create shader: ", why.message            
        self.SetFragmentShader(code)
   
    
    def _CreateProgramAndShaders(self):
        # clear any old programs and shaders
        
        if self._programId < 0:
            return
        
        # clear to be sure
        self.Clear()
        
        if not self._fragmentCode and not self._vertexCode:
            self._programId = -1  # don't make a shader object
            return
        
        try:
            # create program object
            self._programId = gla.glCreateProgramObjectARB()
            self._checkForOpenglError('CreateProgram')
            
            # the two shaders
            codes = [self._fragmentCode, self._vertexCode]
            types = [gl.GL_FRAGMENT_SHADER, gl.GL_VERTEX_SHADER]
            for code, type in zip(codes, types):
                # only attach shaders that do something
                if not code:
                    continue
                
                # create shader object            
                myshader = gla.glCreateShaderObjectARB(type)            
                self._checkForOpenglError('CreateShader')
                self._shaderIds.append(myshader)
                
                # set its source            
                gla.glShaderSourceARB(myshader, [code])
                self._checkForOpenglError('ShaderSource')
                
                # compile shading code
                gla.glCompileShaderARB(myshader)
                self._checkForOpenglError('CompileShader')
                
                # errors?
                if not self._ProcessErrors(myshader):
                    gla.glAttachObjectARB(self._programId, myshader)
                    self._checkForOpenglError('AttachShader')
            
        except Exception, why:
            self._programId = -1
            print "Unable to initialize shader code.", why.message
    
    
    def SetUniformf(self, varname, values):
        """ A uniform is a parameter for shading code.
        Set the parameters right after enabling the program.
        values should be a list of up to four floats ( which 
        are converted to float32).
        """
        if not self._IsValid():
            return
        
        # convert to floats
        values = [float(v) for v in values]
        
        # get loc
        loc = gla.glGetUniformLocationARB(self._programId, varname)        
        
        # set values
        if len(values) == 1:
            gl.glUniform1f(loc, values[0])
        elif len(values) == 2:
            gl.glUniform2f(loc, values[0], values[1])            
        elif len(values) == 3:
            gl.glUniform3f(loc, values[0], values[1], values[2])
        elif len(values) == 4:
            gl.glUniform4f(loc, values[0], values[1], values[2], values[3])
    
    
    def SetUniformi(self, varname, values):
        """ A uniform is a parameter for shading code.
        Set the parameters right after enabling the program.
        values should be a list of up to four ints ( which 
        are converted to int).
        """
        if not self._IsValid():
            return
        
        # convert to floats
        values = [int(v) for v in values]
        
        # get loc
        loc = gla.glGetUniformLocationARB(self._programId, varname)        
        
        # set values
        if len(values) == 1:
            gla.glUniform1iARB(loc, values[0])
        elif len(values) == 2:
            gl.glUniform2iARB(loc, values[0], values[1])            
        elif len(values) == 3:
            gl.glUniform3iARB(loc, values[0], values[1], values[2])
        elif len(values) == 4:
            gl.glUniform4iARB(loc, values[0], values[1], values[2], values[3])
    
    
    def _checkForOpenglError(self, s):
        e = gl.glGetError()
        if (e != gl.GL_NO_ERROR):
            raise OpenGLError('GLERROR: ' + s + ' ' + glu.gluErrorString(e))
    
    
    def _ProcessErrors(self, glObject):
        log = gla.glGetInfoLogARB(glObject)
        if log:
            print "Warning in shading code:", log
            return True
        else:
            return False
    
    
    def Clear(self):
        """ Clear the program. """
        # clear OpenGL stuff
        if self._programId>0:
            try: gla.glDeleteObjectARB(self._programId)
            except Exception: pass
        for shaderId in self._shaderIds:
            try:  gla.glDeleteObjectARB(shaderId)
            except Exception: pass
        # reset
        self._programId = 0
        self._shaderIds[:] = []
    
    
    def __del__(self):
        " You never know when this is called."
        self.Clear()


def uploadTexture(dimensions, data, editTexture=None):
    """ Upload data to opengl texture. 
    If editTexture is None, creates a new texture. This is done 
    in a save way by first trying with a proxy. editTexture can
    also be given (it should be the id of the texture to edit),
    in which case the data can be uploaded much faster. It is the
    responsibility of the caller to make sure that the data to
    change has the exact same dimension.
    
    The dimensions must be given, otherwise there is ambiguety 
    for NxNx3 data (is it 3D or 2D color?).
    """
    
    # make singles if doubles (sadly opengl does not know about doubles)
    if data.dtype == np.float64:
        data = data.astype(np.float32)
    # dito for bools
    if data.dtype == np.bool:
        data = data.astype(np.uint8)
    
    # determine type
    thetype = data.dtype.name
    try:
        gltype = dtypes[thetype]
    except Exception:
        raise ValueError("Cannot convert datatype %s." % thetype)
    
    # process depending on data shape and given dimensions
    shape = data.shape 
    
    if dimensions==1:        
        
        if len(shape)==1:
            internalformat = gl.GL_LUMINANCE8
            format = gl.GL_LUMINANCE
        elif len(shape)==2 and shape[1] == 1:
            internalformat = gl.GL_LUMINANCE8
            format = gl.GL_LUMINANCE
        elif len(shape)==2 and shape[1] == 3:
            internalformat = gl.GL_RGB
            format = gl.GL_RGB
        elif len(shape)==2 and shape[1] == 4:
            internalformat = gl.GL_RGBA
            format = gl.GL_RGBA
        else:
            raise ValueError("Cannot create 1D texture, data of invalid shape.")
        
        if editTexture:
            # edit data for existing texture
            gl.glBindTexture(gl.GL_TEXTURE_1D, editTexture)
            gl.glTexSubImage1D(gl.GL_TEXTURE_1D, 0, 
                0, shape[0], format, gltype, data)
        else:        
            # test
            ptarget = gl.GL_PROXY_TEXTURE_1D
            gl.glTexImage1D(ptarget, 0, internalformat, 
                shape[0], 0, format, gltype, None)
            width = gl.glGetTexLevelParameteriv(ptarget,0,gl.GL_TEXTURE_WIDTH)
            if width==0:
                raise MemoryError("Not enough memory to create 1D texture.")
            
            # apply
            gl.glTexImage1D(gl.GL_TEXTURE_1D, 0, internalformat, 
                shape[0], 0, format, gltype, data)
        
    elif dimensions==2:
        
        if len(shape)==2:
            internalformat = gl.GL_LUMINANCE8
            format = gl.GL_LUMINANCE
        elif len(shape)==3 and shape[2]==1:
            internalformat = gl.GL_LUMINANCE8
            format = gl.GL_LUMINANCE
        elif len(shape)==3 and shape[2]==3:
            internalformat = gl.GL_RGB
            format = gl.GL_RGB
        elif len(shape)==3 and shape[2]==4:
            internalformat = gl.GL_RGBA
            format = gl.GL_RGBA
        else:
            raise ValueError("Cannot create 2D texture, data of invalid shape.")
        
        if editTexture:
            # edit data for existing texture
            gl.glBindTexture(gl.GL_TEXTURE_2D, editTexture)
            gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, 
                0, 0, shape[1], shape[0], format, gltype, data)
        else: 
            # test
            ptarget = gl.GL_PROXY_TEXTURE_2D
            gl.glTexImage2D(ptarget, 0, internalformat, 
                shape[1], shape[0], 0, format, gltype, None)
            width = gl.glGetTexLevelParameteriv(ptarget,0,gl.GL_TEXTURE_WIDTH)
            if width==0:
                raise MemoryError("Not enough memory to create 2D texture.")
            
            # apply
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, internalformat, 
                shape[1], shape[0], 0, format, gltype, data)
    
    elif dimensions==3 and len(shape)==3:
        
        if len(shape)==3:
            internalformat = gl.GL_LUMINANCE8
            format = gl.GL_LUMINANCE
        elif len(shape)==4 and shape[3]==1:
            internalformat = gl.GL_LUMINANCE8
            format = gl.GL_LUMINANCE
        elif len(shape)==4 and shape[3]==3:
            internalformat = gl.GL_RGB
            format = gl.GL_RGB
        elif len(shape)==4 and shape[3]==4:
            internalformat = gl.GL_RGBA
            format = gl.GL_RGBA
        else:
            raise ValueError("Cannot create 3D texture, data of invalid shape.")
        
        if editTexture:
            # edit data for existing texture
            gl.glBindTexture(gl.GL_TEXTURE_3D, editTexture)
            gl.glTexSubImage3D(gl.GL_TEXTURE_3D, 0, 
                0, 0, 0, shape[2], shape[1], shape[0], format, gltype, data)
        else:
            # test
            ptarget = gl.GL_PROXY_TEXTURE_3D
            gl.glTexImage3D(ptarget, 0, internalformat, 
                shape[2], shape[1], shape[0], 0, format, gltype, None)
            width = gl.glGetTexLevelParameteriv(ptarget,0,gl.GL_TEXTURE_WIDTH)
            if width==0:
                raise MemoryError("Not enough memory to create 3D texture.")
            
            # apply
            gl.glTexImage3D(gl.GL_TEXTURE_3D, 0, internalformat, 
                shape[2], shape[1], shape[0], 0, format, gltype, data)
    
    else:
        raise ValueError("Cannot create texture, data shape does not match dimensions.")
    
    


class MixTexture(object):
    """ Very basic texture class that is later mixed with Wobject to
    produce actual visvis textures. This class can be used to manage
    openGl textures though...
    """
    
    def __init__(self):
        # texture ID               
        self._texId = 0
        
        # store the used texture unit for easier disabling
        self._texUnit = -1
        
        # the texture type (the inheriting class must make sure to set this!)
        self._textype = gl.GL_TEXTURE_2D
    
    
    def _TexEnable(self, texUnit=0):
        """ Enable the texture, using the given texture unit (max 9).
        """ 
        # check
        if not gl.glIsTexture(self._texId):
            print "warning enabling texture, the texture is not valid!"
        # store
        self._texUnit = texUnit
        # select this unit               
        gl.glActiveTexture( gl.GL_TEXTURE0 + texUnit )        
        # enable texturing 
        gl.glEnable(self._textype)
        # bind the specified texture
        gl.glBindTexture(self._textype, self._texId)
    
    
    def _TexDisable(self):
        """ Disable the texture.
        """
        if self._texUnit >= 0:
            gl.glActiveTexture( gl.GL_TEXTURE0 + self._texUnit )
            gl.glDisable(self._textype)
            self._texUnit = -1
        # set active texture unit to default (0)
        gl.glActiveTexture( gl.GL_TEXTURE0 )
    
    
    def __del__(self):
        try:
            gl.glDeleteTextures([self._texId])
        except Exception:
            pass
    

class CoordBackFaceHelper(MixTexture):
    """ A helper class to store the texture coordinates of the backfaces
    of a 3D texture. """
    
    def __init__(self):
        MixTexture.__init__(self)
        self._textype = gl.GL_TEXTURE_2D
    
    def CaptureScreen(self):
        """ Capture the screen of the backbuffer. It should
        contain texture coordinates coded in the R,G,B channels.
        """
        # delete if exist
        # todo: If possible, don't do this
        if self._texId>0 or gl.glIsTexture(self._texId):
            try:
                gl.glDeleteTextures([self._texId])
                self._texId = 0
            except Exception:
                pass
        
        # create if it does not exist
        if self._texId==0 or not gl.glIsTexture(self._texId):
            self._texId = gl.glGenTextures(1)
        
        # bind to texture
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._texId)
        
        # determine rectangle to sample        
        xywh = gl.glGetIntegerv(gl.GL_VIEWPORT)
        x,y,w,h = xywh[0], xywh[1], xywh[2], xywh[3]
        
        # read texture!
        gl.glReadBuffer(gl.GL_BACK)
        gl.glCopyTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, 
            x, y, w, h, 0)
        
        # Set interpolation parameters. Use linear such that the proper
        # coordinate is sampled even though the coords are stored in 8 bits.
        tmp = gl.GL_LINEAR
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, tmp)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, tmp)
        
#         data = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_FLOAT)
#         print 'capturing', data.min(), data.max(), data.mean()
    

dtypes = {  'uint8':gl.GL_UNSIGNED_BYTE,    'int8':gl.GL_BYTE,
            'uint16':gl.GL_UNSIGNED_SHORT,  'int16':gl.GL_SHORT, 
            'uint32':gl.GL_UNSIGNED_INT,    'int32':gl.GL_INT, 
            'float32':gl.GL_FLOAT }

# A correction for the clim. For a datatype of uint8, the fragents
# are mapped between 0 and 1 for 0 and 255 respectively. For int8
# the values are mapped between -1 and 1 for -127 and 128 respectively.
climCorrection = { 'uint8':2**8, 'int8':2**7, 'uint16':2**16, 'int16':2**15, 
                   'uint32':2**32, 'int32':2**31, 'float32':1, 'float64':1,
                   'bool':2**8}


class BaseTexture(Wobject, MixTexture):
    """ Base texture class for visvis 2D and 3D textures. """
    
    def __init__(self, parent, data):
        Wobject.__init__(self, parent)
        MixTexture.__init__(self)
        
        # the data and its shape
        self._shape = None
        self._data = None
        
        # interpolate?
        self._interpolate = False
        
        # the limits
        self._clim = Range(0,1)
        self._climCorrection = 1.0
        self._climRef = Range(0,1) # the "original" range
        
        # init
        self._climRef.Set(data.min(), data.max())
        self.clim = self._climRef.Copy()
        
        # create glsl program for this texture...
        self._program1 = program =  GlslProgram()
        self._program2  =  GlslProgram()
        
        # scale and translation transforms
        self._trafo_scale = Transform_Scale()
        self._trafo_trans = Transform_Translate()
        self.transformations.append(self._trafo_trans)
        self.transformations.append(self._trafo_scale)        
        
        # set data
        self.SetData(data)

    
    def SetData(self, data):
        """ Set the data to display. """ 
        # make the figure the current opengl context
        figure = self.axes.GetFigure()
        if not figure:
            return
        else:
            figure._SetCurrent()
        # ...
        data2, ii = self._data, isinstance
        if not ( ii(data, np.ndarray) and ii(data2, np.ndarray) ):
            # if data is set to None, remove reference
            self.OnDestroy()
        elif gl.glIsTexture(self._texId) and (data.shape == self._data.shape):
            # ok, we can upload fast!            
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT,1)
            self._ScaleBias_init(data.dtype.name)
            if self._textype == gl.GL_TEXTURE_1D:
                uploadTexture(1, data, self._texId)
            elif self._textype == gl.GL_TEXTURE_2D:
                uploadTexture(2, data, self._texId)
            elif self._textype == gl.GL_TEXTURE_3D:
                uploadTexture(3, data, self._texId)
            else:
                raise RuntimeError("Invalid texture type!")
            self._ScaleBias_afterUpload()
        else:
            # remove old data. This will make textUpload to be called
            # on the first time the texture needs to be drawn.
            self._OnDestroyOpenGlTexture()  # data is uploaded on next draw
        # keep reference of data
        self._data = data
    
    
    def Refresh(self):
        """ Refresh the data. Updates the OpenGL texture that we kept 
        a reference of. same as t.SetData(t._data)"""
        if self._data is not None:
            self.SetData(self._data)
    

    def _TexUpload(self):
        """ Implement this. """
        raise NotImplementedError
        
    
    def _OnDestroyOpenGlTexture(self):    
        """ Destroy texture, delete the texture from OpenGL memory. """
        #print "Destroying texture (", self, "), ", 
        if self._texId > 0:
            try:
                gl.glDeleteTextures([self._texId])
                self._program1.Clear()
                self._program2.Clear()
                #print "texture destroyed",
            except Exception:
                pass
            self._texId = 0
        #print ""
    
    
    def OnDestroy(self):
        # remove opengl texture data
        self._OnDestroyOpenGlTexture()
        # remove reference to data so it can be cleaned up (important)
        self._data = None 
    
    
    def OnDrawFast(self):
        self.OnDraw(True)


    @Property
    def interpolate():
        """ Interpolate the image when zooming in (using linear interpolation).
        """
        def fget(self):
            return self._interpolate
        def fset(self, value):
            self._interpolate = bool(value)
            # bind the texture
            gl.glBindTexture(gl.GL_TEXTURE_2D, self._texId)
            # set interpolation
            tmp = {False:gl.GL_NEAREST, True:gl.GL_LINEAR}[self._interpolate]
            gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, tmp)
    
    
    @Property
    def clim():
        """ Get/Set the contrast limits. For a gray colormap, clim.min is black,
        clim.max is white.
        """
        def fget(self):
            return self._clim
        def fset(self, value):
            if not isinstance(value, Range):
                value = Range(value)
            self._clim = value
    
    
    def SetClim(self, *minmax):
        """ Set the contrast limits. Different than the property clim, this
        re-uploads the texture using different transfer functions. You should
        use this if your data has a higher contrast resolution than 8 bits.
        Takes a bit more time than clim though (which basically takes no
        time at all).
        """
        if len(minmax)==1:
            minmax = minmax[0]
        # Set climref.
        self._climRef.Set(minmax[0], minmax[1])
        self._clim.Set(minmax[0], minmax[1])
        # Clear texture, on next draw, it is uploaded again, using
        # the newly set climref.
        self._OnDestroyOpenGlTexture()
    
    
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
        #self.clim = self._climRef.Copy()
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
        r1, r2 = self.clim.range, self._climRef.range
        if r1==0:
            r1 = 1.0
        if r2==0:
            r2 = 1.0
        # calculate scale and bias
        scale = self._climRef.range / r1
        bias = (self._climRef.min - self.clim.min) / r2    
        return scale, bias


class Texture2D(BaseTexture):
    """ A data type that represents structured data in
    two dimensions (an image). Supports grayscale, RGB, 
    and RGBA images.
    """
    
    def __init__(self, parent, data):
        BaseTexture.__init__(self, parent, data)
        
        # set antialiasing
        self._aa = 0
        self._textype = gl.GL_TEXTURE_2D
    
    def _TexUpload(self):
        """ Upload the texture in OpenGL memory.
        """
        
        # get data
        data = self._data
        if data is None or self._texId<0:
            return
        
        # store shape
        self._shape = shape = data.shape
        
        # test shape
        if len(shape) == 3:
            if shape[2] not in [3,4]:
                self._texId=-1 # prevent keeping printing this message
                raise ValueError("Cannot create texture, texture is not 2D!")
        elif len(shape) == 2:            
            pass # ok
        else:
            self._texId=-1 # prevent keeping printing this message
            raise ValueError("Cannot Create texture, texture is not 2D!")
                
        # if we get here, we hope to get no errors
        
        # generate texture id
        self._texId = gl.glGenTextures(1)
        
        # bind the texture
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._texId)
        
        # Set alignment to 1. It is 4 by default, but my data array has no
        # strides, so in order for the image not to be distorted, I set it 
        # to 1. I assume graphics cards can still render in hardware. If 
        # not, I would have to add one or two rows to my data instead.
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT,1)
        
        # init transferfunctions and set clim to full range
        self._ScaleBias_init(data.dtype.name)
        
        # create texture
        try:
            uploadTexture(2,data)
        except Exception, why:
            print "Warning: ", why.message
            self._texId=-1 # prevent keeping printing this message
        
        # set interpolation and extrapolation parameters            
        tmp = gl.GL_NEAREST # gl.GL_NEAREST | gl.GL_LINEAR
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, tmp)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, tmp)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
        
        # reset transfer
        self._ScaleBias_afterUpload()
    
    
    def _CreateGaussianKernel(self):
        """ Create kernel values to use in the aa program.
        Returns 4 element list which should be applied using the
        following indices: 3 2 1 0 1 2 3
        """
        
        if not self.axes:
            return 1,0,0,0
        
        # determine relative kernel size
        figure = self.axes.GetFigure()
        if not figure:
            return 1,0,0,0
        w,h = figure.GetSize()
        cam = self.axes.camera
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
        """ Implementation of the OnDrawShape method.
        Defines the texture's shape as a rectangle.
        """        
        gl.glColor(clr[0], clr[1], clr[2], 1.0)
        self._DrawQuads()
    

    def OnDraw(self, fast=False):
        """ Draw the texture.
        """
        
        # set color to white, otherwise with no shading, there is odd scaling
        gl.glColor3f(1.0,1.0,1.0)
        
        # create if it does not exist
        if self._texId==0 or not gl.glIsTexture(self._texId):
            self._TexUpload()
        
        # enable texture
        self._TexEnable(0)
        
        # draw texture also from beneeth
        #gl.glCullFace(gl.GL_FRONT_AND_BACK)
        
        # fragment shader on        
        self._program1.Enable()
        self._program1.SetUniformi('texture', [0])
        k = self._CreateGaussianKernel()
        self._program1.SetUniformf('kernel', k)
        self._program1.SetUniformf('dx', [1.0/self._shape[0]])
        self._program1.SetUniformf('dy', [1.0/self._shape[1]])  
        self._program1.SetUniformf('scaleBias', self._ScaleBias_get())
        #self._program1.SetUniformf('scaleBias', [1.0, 0.0])
        
        # do the drawing!
        self._DrawQuads()
        
        # fragment shader off
        self._program1.Disable()
        
        gl.glFlush()
        self._TexDisable()

    
    def _DrawQuads(self):
        """ Draw the quads of the texture. 
        This is done in a seperate method to reuse code in 
        OnDraw() and OnDrawShape(). """        
        if not self._shape:
            return        
        
        # prepare (note the 0.5 offset to make sure the center of the pixel
        # is in the correct position)
        x1,y2 = -0.5,-0.5
        x2,y1 = self._shape[1]-0.5, self._shape[0]-0.5
        
        # draw
        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0,0); gl.glVertex3d(x1, y2, 0.0)
        gl.glTexCoord2f(1,0); gl.glVertex3d(x2, y2, 0.0)
        gl.glTexCoord2f(1,1); gl.glVertex3d(x2, y1, 0.0)
        gl.glTexCoord2f(0,1); gl.glVertex3d(x1, y1, 0.0)
        gl.glEnd()
    
    
    def _Transform(self):
        # edit scaling and transform
        data = self._data
        if isinstance(data, points.Aarray):
            if hasattr(data,'_sampling') and hasattr(data,'_origin'):
                self._trafo_scale.sx = data.sampling[1]
                self._trafo_scale.sy = data.sampling[0]
                #
                self._trafo_trans.dx = data.origin[1]
                self._trafo_trans.dy = data.origin[0]                
        # call base transform method
        Wobject._Transform(self)
    
    
    @Property
    def aa():
        """ Set anti aliasing.
        0 or False for no anti aliasing
        1 for minor anti aliasing
        2 for medium anti aliasing
        3 for much anti aliasing
        """
        def fget(self):
            return self._aa
        def fset(self, value):
            if not value:
                value = 0
            self._aa = value
            if self._aa == 1:
                self._program1.SetFragmentShader(shading.aa1)
            elif self._aa == 2:
                self._program1.SetFragmentShader(shading.aa2)
            elif self._aa >= 3:
                self._program1.SetFragmentShader(shading.aa3)
            else:
                self._program1.SetFragmentShader(shading.aa0)
                #self._program1.SetFragmentShader("")
    

class Texture3D(BaseTexture):
    """ A data type that represents structured data in
    three dimensions (a volume).
    """
    
    def __init__(self, parent, data):
        BaseTexture.__init__(self, parent, data)
        
        self._textype = gl.GL_TEXTURE_3D
        
        # init render style
        self._renderStyle = 'mip'
        self._program1.SetFragmentShader(shading.mip)
        self._isoThreshold = 0.0
        
        # for backfacing texture coords
        self._program2.SetFragmentShader(shading.coord3d)
        self._coordHelper = CoordBackFaceHelper()


    def _TexUpload(self):
        """ Upload the texture in OpenGL memory.
        """
        
        # get data
        data = self._data
        if data is None or self._texId<0:
            return
        
        # store shape
        self._shape = shape = data.shape
        
        # test shape
        if len(shape) != 3:
            self._texId=-1 # prevent keeping printing this message
            raise ValueError("Given data is not 3D.")
        
        # generate texture id
        self._texId = gl.glGenTextures(1)
        
        # bind the texture        
        gl.glBindTexture(gl.GL_TEXTURE_3D, self._texId)
        
        # Set alignment to 1. It is 4 by default, but my data array has no
        # strides, so in order for the image not to be distorted, I set it 
        # to 1. I assume graphics cards can still render in hardware. If 
        # not, I would have to add one or two rows to my data instead.
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT,1)
        
        # init transferfunctions and set clim to full range
        self._ScaleBias_init(data.dtype.name)
        
        # create texture
        try:
            uploadTexture(3,data)
        except Exception, why:
            print "Warning: ", why.message
            self._texId=-1 # prevent keeping printing this message
        
        # set interpolation and extrapolation parameters            
        tmp = gl.GL_NEAREST # gl.GL_NEAREST | gl.GL_LINEAR
        gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MIN_FILTER, tmp)
        gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_MAG_FILTER, tmp)
        
        # Set clamping off. When testing the raycasting, comment these lines!
        gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
        gl.glTexParameteri(gl.GL_TEXTURE_3D, gl.GL_TEXTURE_WRAP_R, gl.GL_CLAMP)
        
        # reset transfer
        self._ScaleBias_afterUpload()
    
    
    def OnDrawShape(self, clr):
        """ Implementation of the OnDrawShape method.
        Defines the texture's shape as a rectangle.
        """
        gl.glColor(clr[0], clr[1], clr[2], 1.0)        
        self._DrawQuads()
    
    
    def OnDraw(self, fast=False):
        """ Draw the texture.
        """
        
        # get viewport
        xywh = gl.glGetIntegerv(gl.GL_VIEWPORT)
        
        # only draw front-facing parts
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        
        # create if it does not exist
        if self._texId==0 or not gl.glIsTexture(self._texId):
            self._TexUpload()
       
        # fragment shader on
        self._program1.Enable()
        
        # enable the texture- and help-textures                
        self._TexEnable(0)
        self._program1.SetUniformi('texture', [0])
        self._coordHelper._TexEnable(1)
        self._program1.SetUniformi('backCoords', [1])
        
        # set uniforms: parameters
        self._program1.SetUniformf('shape',reversed(list(self._shape)) )
        daspect = [abs(i) for i in self.axes.daspect]        
        self._program1.SetUniformf('daspect', daspect)
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
        self._program1.SetUniformf('viewport', xywh)
        
        # do the actual drawing
        self._DrawQuads()
        
        # clean up
        gl.glFlush()        
        self._program1.Disable()
        self._TexDisable()
        self._coordHelper._TexDisable()
        gl.glDisable(gl.GL_CULL_FACE)
    
    
    def _DrawQuads(self):
        """ Draw the quads of the texture. 
        This is done in a seperate method to reuse code in 
        OnDraw() and OnDrawShape(). """        
        if not self._shape:
            return 
        
        # prepare world coordinates
        x0,x1 = -0.5, self._shape[2]-0.5
        y0,y1 = -0.5, self._shape[1]-0.5
        z0,z1 = -0.5, self._shape[0]-0.5
        
        # prepare texture coordinates
        t0, t1 = 0, 1        
        # if any axis are flipped, make sure the correct polygons are front
        # facing
        tmp = 1
        for i in self.axes.daspect:
            if i<0:
                tmp*=-1        
        if tmp==1:
            t0, t1 = t1, t0
            x0, x1 = x1, x0
            y0, y1 = y1, y0
            z0, z1 = z1, z0
        
        # using glTexCoord* is the same as glMultiTexCoord*(GL_TEXTURE0)
        # Therefore we need to bind the base texture to 0.
        
        # draw. So we draw the six planes of the cube (well not a cube,
        # a 3d rectangle thingy). The inside is only rendered if the 
        # vertex is facing front, so only 3 planes are rendered at a        
        # time...                
        gl.glBegin(gl.GL_QUADS)
        # bottom
        gl.glTexCoord3f(t0,t0,t0); gl.glVertex3d(x0, y0, z0)
        gl.glTexCoord3f(t1,t0,t0); gl.glVertex3d(x1, y0, z0)
        gl.glTexCoord3f(t1,t1,t0); gl.glVertex3d(x1, y1, z0)
        gl.glTexCoord3f(t0,t1,t0); gl.glVertex3d(x0, y1, z0)
        # top
        gl.glTexCoord3f(t0,t0,t1); gl.glVertex3d(x0, y0, z1)        
        gl.glTexCoord3f(t0,t1,t1); gl.glVertex3d(x0, y1, z1)
        gl.glTexCoord3f(t1,t1,t1); gl.glVertex3d(x1, y1, z1)
        gl.glTexCoord3f(t1,t0,t1); gl.glVertex3d(x1, y0, z1)
        # front
        gl.glTexCoord3f(t0,t1,t0); gl.glVertex3d(x0, y1, z0)
        gl.glTexCoord3f(t1,t1,t0); gl.glVertex3d(x1, y1, z0)
        gl.glTexCoord3f(t1,t1,t1); gl.glVertex3d(x1, y1, z1)
        gl.glTexCoord3f(t0,t1,t1); gl.glVertex3d(x0, y1, z1)
        # back
        gl.glTexCoord3f(t0,t0,t0); gl.glVertex3d(x0, y0, z0)
        gl.glTexCoord3f(t0,t0,t1); gl.glVertex3d(x0, y0, z1)
        gl.glTexCoord3f(t1,t0,t1); gl.glVertex3d(x1, y0, z1)
        gl.glTexCoord3f(t1,t0,t0); gl.glVertex3d(x1, y0, z0)        
        # left
        gl.glTexCoord3f(t0,t0,t0); gl.glVertex3d(x0, y0, z0)
        gl.glTexCoord3f(t0,t1,t0); gl.glVertex3d(x0, y1, z0)
        gl.glTexCoord3f(t0,t1,t1); gl.glVertex3d(x0, y1, z1)
        gl.glTexCoord3f(t0,t0,t1); gl.glVertex3d(x0, y0, z1)
        # right
        gl.glTexCoord3f(t1,t0,t0); gl.glVertex3d(x1, y0, z0)
        gl.glTexCoord3f(t1,t0,t1); gl.glVertex3d(x1, y0, z1)
        gl.glTexCoord3f(t1,t1,t1); gl.glVertex3d(x1, y1, z1)
        gl.glTexCoord3f(t1,t1,t0); gl.glVertex3d(x1, y1, z0)
        # 
        gl.glEnd()
    
    
    def _Transform(self):
        # edit scaling and transform
        data = self._data
        if isinstance(data, points.Aarray):
            if hasattr(data,'_sampling') and hasattr(data,'_origin'):
                self._trafo_scale.sx = data.sampling[2]
                self._trafo_scale.sy = data.sampling[1]
                self._trafo_scale.sz = data.sampling[0]
                #
                self._trafo_trans.dx = data.origin[2]
                self._trafo_trans.dy = data.origin[1]
                self._trafo_trans.dz = data.origin[0]
        # call base transform method
        Wobject._Transform(self)
    
    
    @Property
    def renderStyle():
        """ Get or set the render style to render the volumetric data:
            - mip: maximum intensity projection
            - iso: isosurface rendering
            - rays: ray casting
        """
        def fget(self):
            return self._renderStyle
        def fset(self, style):            
            style = style.lower()            
            if style in ['mip']:
                self._renderStyle = style
                self._program1.SetFragmentShader(shading.mip)
            elif style in ['iso', 'isosurface']:
                self._renderStyle = style
                self._program1.SetFragmentShader(shading.isosurface)
            elif style in ['coord3d', 'coord']:
                self._renderStyle = style
                self._program1.SetFragmentShader(shading.coord3d)
            elif style in ['oldmip']:
                self._renderStyle = style
                self._program1.SetFragmentShader(shading.oldmip)
            elif style in ['ray', 'rays', 'raycasting']:
                self._renderStyle = style
                self._program1.SetFragmentShader(shading.raycasting1)
            else:
                print "Unknown render style in Texture3d.SetRenderstyle."

    @Property
    def isoThreshold():
        def fget(self):
            return self._isoThreshold
        def fset(self, value):
            # make float
            value = float(value)
            # store
            self._isoThreshold = value
    
    
    def OnDrawPre(self):
        
        # only draw back-facing parts
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_FRONT)
        
        # create if it does not exist
        if self._texId==0 or not gl.glIsTexture(self._texId):
            self._TexUpload()
        
        # textures and fragment shader on
        self._TexEnable(0)
        self._program2.Enable()        
        self._program2.SetUniformi('texture', [0])
        
        # disable depth test for now
        gl.glDisable(gl.GL_DEPTH_TEST)
        
        # do the actual drawing
        self._DrawQuads()
        
        # fetch buffer        
        gl.glFlush()
        self._coordHelper.CaptureScreen()
        
        # clean up
        self._program2.Disable()        
        #gl.glDisable(gl.GL_TEXTURE_3D)
        self._TexDisable()        
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glEnable(gl.GL_DEPTH_TEST)
        
        

