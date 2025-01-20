# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module baseTexture

Defines the base TextureObject class (which is not a wobject or wibject),
and the colormap class that derives from it. The default colormaps are
defined in core.constants.

This texture has functionality for auto-resizing if it does not fit in
memory and padding if the system requires the size to be a factor of two.

"""

import OpenGL.GL as gl
import numpy as np

from visvis.core.misc import getOpenGlCapable, PropWithDraw, Range


# Dict that maps numpy datatypes to openGL data types
dtypes = {  'uint8':gl.GL_UNSIGNED_BYTE,    'int8':gl.GL_BYTE,
            'uint16':gl.GL_UNSIGNED_SHORT,  'int16':gl.GL_SHORT,
            'uint32':gl.GL_UNSIGNED_INT,    'int32':gl.GL_INT,
            'float32':gl.GL_FLOAT }


def makePowerOfTwo(data, ndim):
    """ makePowerOfTwo(data, ndim)
    
    If necessary, pad the data with zeros, to make the shape
    a power of two. If it already is shaped ok, the original data
    is returned.
    
    Use this function for systems with OpenGl < 2.0.
    
    """
    def nearestN(n1):
        n2 = 2
        while n2 < n1:
            n2*=2
        return n2
    
    # get old and new shape
    s1 = [n for n in data.shape]
    s2 = [nearestN(n) for n in data.shape]
    s2[ndim:] = s1[ndim:] # for color images
    
    # if not required return original
    if s1 == s2:
        return data
    
    # create empty image
    data2 = np.zeros(s2,dtype=data.dtype)
    
    # fill in the original data
    if ndim==1:
        data2[:s1[0]] = data
    elif ndim==2:
        data2[:s1[0],:s1[1]] = data
    elif ndim==3:
        data2[:s1[0],:s1[1],:s1[2]] = data
    else:
        raise ValueError("Cannot downsample data of this dimension.")
    return data2


def downSample(data, ndim):
    """ downSample(data, ndim)
    
    Downsample the data. Peforming a simple form of smoothing to prevent
    aliasing.
    
    """
    
    if ndim==1:
        # Decimate
        data2 = data[::2] * 0.4
        # Average in x
        tmp = data[1::2] * 0.3
        data2[:tmp.shape[0]] += tmp
        data2[1:] += tmp[:data2.shape[0]-1]
    elif ndim==2:
        # Decimate
        data2 = data[::2,::2] * 0.4
        # Average in y
        tmp = data[1::2,::2] * 0.15
        data2[:tmp.shape[0],:] += tmp
        data2[1:,:] += tmp[:data2.shape[0]-1,:]
        # Average in x
        tmp = data[::2,1::2] * 0.15
        data2[:,:tmp.shape[1]] += tmp
        data2[:,1:] += tmp[:,:data2.shape[1]-1]
    elif ndim==3:
        # Decimate
        data2 = data[::2,::2,::2] * 0.4
        # Average in z
        tmp = data[1::2,::2,::2] * 0.1
        data2[:tmp.shape[0],:,:] += tmp
        data2[1:,:,:] += tmp[:data2.shape[0]-1,:,:]
        # Average in y
        tmp = data[::2,1::2,::2] * 0.1
        data2[:,:tmp.shape[1],:] += tmp
        data2[:,1:,:] += tmp[:,:data2.shape[1]-1,:]
        # Average in x
        tmp = data[::2,::2,1::2] * 0.1
        data2[:,:,:tmp.shape[2]] += tmp
        data2[:,:,1:] += tmp[:,:,:data2.shape[2]-1]
    else:
        raise ValueError("Cannot downsample data of this dimension.")
    return data2



class TextureObject(object):
    """ TextureObject(texType)
    
    Basic texture class that wraps an OpenGl texture. It manages the OpenGl
    class and exposes a rather high-level interface to it.
    
    texType is one of gl.GL_TEXTURE_1D, gl.GL_TEXTURE_2D, gl.GL_TEXTURE_3D
    and specifies whether this is a 1D, 2D or 3D texture.
    
    Exposed methods:
      * Enable() call be for using
      * Disable() call after using
      * SetData() update the data
      * DestroyGl() remove only the texture from OpenGl memory.
      * Destroy() remove textures and reference to data.
        
    Note: this is not a Wobject nor a Wibject.
    
    """
    
    # One could argue to use polymorphism to implement 3 classes: one for
    # each dimension. Yes you could, but the way to handle the data and
    # communicate with OpenGl is so similar I chose not to. I use the
    # texType to determine which function to call.
    
    def __init__(self, ndim):
        
        # Check given texture type
        if ndim not in [1,2,3]:
            raise ValueError('Texture ndim should be 1, 2 or 3.')
        
        # Store the number of dimensions. This attribute is used to make the
        # choices for which OpenGl functions to use etc.
        self._ndim = ndim
        
        # Store the texture type, as we can determine it easily.
        tmp = {1:gl.GL_TEXTURE_1D, 2:gl.GL_TEXTURE_2D, 3:gl.GL_TEXTURE_3D}
        self._texType = tmp[ndim]
        
        # Texture ID. This is an integer by which OpenGl identifies the
        # texture.
        self._texId = 0
        
        # To store the used texture unit so we can disable it properly.
        self._texUnit = -1
        self._useTexUnit = False # set to True if OpenGl version high enough
        
        # A reference (not a weak one) to the original data as given with
        # SetData. We need this in order to re-upload the texture if it is
        # moved to another OpenGl context (other figure).
        # Note that the self._shape does not have to be self._dataRef.shape.
        self._dataRef = None
        
        # The shape of the data as uploaded to OpenGl. Is None if no
        # data was uploaded. Note that the self._shape does not have to
        # be self._dataRef.shape; the data might be downsampled.
        self._shape = None
        
        # A flag to indicate that the data in self._dataRef should be uploaded.
        # 1 signifies an update is required.
        # 2 signifies an update is required, with padding zeros.
        # -1 signifies the current data uploaded ok.
        # -2 ignifies the current data uploaded ok with padding.
        # 0 signifies failure of uploading
        self._uploadFlag = 1
        
        # Flag to indicate whether we can use this
        self._canUse = False
    
    
    def Enable(self, texUnit=0):
        """ Enable(texUnit)
        
        Enable the texture, using the given texture unit (max 9).
        If necessary, will upload/update the texture in OpenGl memory now.
        
        If texUnit is -1, will not bind the texture.
        
        """
        
        # Did we fail uploading texture last time?
        troubleLastTime = (self._uploadFlag==0)
        
        # If texture invalid, tell to upload, but only if we have a chance
        if self._texId == 0 or not gl.glIsTexture(self._texId):
            if not troubleLastTime:
                # Only if not in failure mode
                self._uploadFlag = abs(self._uploadFlag)
        
        # Store texture-Unit-id, and activate. Do before calling _setDataNow!
        if texUnit >= 0:
            self._texUnit = texUnit
            self._useTexUnit = getOpenGlCapable('1.3')
            if self._useTexUnit:
                gl.glActiveTexture( gl.GL_TEXTURE0 + texUnit )   # Opengl v1.3
        
        # If we should upload/update, do that now. (SetData also sets the flag)
        if self._uploadFlag > 0:
            self._SetDataNow()
        
        # check if ok now
        if not gl.glIsTexture(self._texId):
            if not troubleLastTime:
                print("Warning enabling texture, the texture is not valid. " +
                        "(Hiding message for future draws.)")
            return
        
        # Enable texturing, and bind to texture
        if texUnit >= 0:
            gl.glEnable(self._texType)
            gl.glBindTexture(self._texType, self._texId)
    
    
    def Disable(self):
        """ Disable()
        
        Disable the texture. It's safe to call this, even if the texture
        was not enabled.
        
        """
        
        # No need to disable. Also, if disabled because system does not
        # know 3D textures, we can not call glDisable with that arg.
        if self._uploadFlag == 0:
            return
        
        # Select active texture if we can
        if self._texUnit >= 0 and self._useTexUnit:
            gl.glActiveTexture( gl.GL_TEXTURE0 + self._texUnit )
            self._texUnit = -1
        
        # Disable
        gl.glDisable(self._texType)
        
        # Set active texture unit to default (0)
        if self._useTexUnit:
            gl.glActiveTexture( gl.GL_TEXTURE0 )
    
   
    def SetData(self, data):
        """ SetData(data)
        
        Set the data to display. If possible, will update the data in the
        existing texture (is possible if of the same shape).
        
        """
        
        # check data
        if not isinstance(data, np.ndarray):
            raise ValueError("Data should be a numpy array.")
        
        # check shape (raises ValueError if not ok)
        try:
            self._GetFormat(data.shape)
        except ValueError:
            raise # reraise from here
        
        # ok, store data and raise flag
        self._dataRef = data
        self._uploadFlag = abs(self._uploadFlag)
    
    
    def _SetDataNow(self):
        """ Make sure the data in self._dataRef is uploaded to
        OpenGl memory. If possible, update the data rather than
        create a new texture object.
        """
        
        # Test whether padding to a factor of two is required
        needPadding = (abs(self._uploadFlag) == 2)
        needPadding = needPadding or not getOpenGlCapable('2.0')
        
        # Set flag in case of failure (set to success at the end)
        # If we tried without padding, we can still try with padding.
        # Note: In theory, getOpenGlCapable('2.0') should be enough to
        # determine if padding is required. However, bloody ATI drivers
        # sometimes need 2**n textures even if OpenGl > 2.0. (I've
        # encountered this with someones PC and verified that the current
        # solution solves this.)
        if needPadding:
            self._uploadFlag = 0 # Give up
        else:
            self._uploadFlag = 2 # Try with padding next time
        
        # Get data.
        if self._dataRef is None:
            return
        data = self._dataRef
        
        # older OpenGl versions do not know about 3D textures
        if self._ndim==3 and not getOpenGlCapable('1.2','3D textures'):
            return
        
        # Convert data type to one supported by OpenGL
        if data.dtype.name not in dtypes:
            # Long integers become floats; int32 would not have enough range
            if data.dtype in (np.int64, np.uint64):
                data = data.astype(np.float32)
            # Bools become bytes
            elif data.dtype == np.bool:
                data = data.astype(np.uint8)
            else:
                # Make singles in all other cases (e.g. np.float64, np.float128)
                # We cannot explicitly use float128, since its not always defined
                data = data.astype(np.float32)
        
        # Determine type
        thetype = data.dtype.name
        if not thetype in dtypes:
            # this should not happen, since we convert incompatible types
            raise ValueError("Cannot convert datatype %s." % thetype)
        gltype = dtypes[thetype]
        
        # Determine format
        internalformat, format = self._GetFormat(data.shape)
        
        # Can we update or should we upload?
        
        if (    gl.glIsTexture(self._texId) and
                self._shape and (data.shape == self._shape) ):
            # We can update.
            
            # Bind to texture
            gl.glBindTexture(self._texType, self._texId)
            
            # update
            self._UpdateTexture(data, internalformat, format, gltype)
        
        else:
            # We should upload.
            
            # Remove any old data.
            self.DestroyGl()
            
            # Create texture object
            self._texId = gl.glGenTextures(1)
            
            # Bind to texture
            gl.glBindTexture(self._texType, self._texId)
            
            # Should we make the image a power of two?
            if needPadding:
                data2 = makePowerOfTwo(data, self._ndim)
                if data2 is not data:
                    data = data2
                    print("Warning: the data was padded to make it a power of two.")
            
            # test whether it fits, downsample if necessary
            ok, count = False, 0
            while not ok and count<8:
                ok = self._TestUpload(data, internalformat,format,gltype)
                if not ok:
                    #if count<2 and data.shape[0]<1000: # for testing
                    data = downSample(data, self._ndim)
                    count += 1
            
            # give warning or error
            if count and not ok:
                raise MemoryError(  "Could not upload texture to OpenGL, " +
                                    "even after 8 times downsampling.")
            elif count:
                print(  "Warning: data was downscaled " + str(count) +
                        " times to fit it in OpenGL memory." )
            
            # upload!
            self._UploadTexture(data, internalformat, format, gltype)
            
            # keep reference of data shape (as loaded to opengl)
            self._shape = data.shape
        
        # flag success
        if needPadding:
            self._uploadFlag = -2
        else:
            self._uploadFlag = -1
    
    
    def _UpdateTexture(self, data, internalformat, format, gltype):
        """ Update an existing texture object. It should have been
        checked whether this is possible (same shape).
        """
        
        # define dict
        D = {   1: (gl.glTexSubImage1D, gl.GL_TEXTURE_1D),
                2: (gl.glTexSubImage2D, gl.GL_TEXTURE_2D),
                3: (gl.glTexSubImage3D, gl.GL_TEXTURE_3D)}
        
        # determine function and target from texType
        uploadFun, target = D[self._ndim]
        
        # Build argument list
        shape = [i for i in reversed( list(data.shape[:self._ndim]) )]
        args = [target, 0] + [0 for i in shape] + shape + [format,gltype,data]
        
        # Upload!
        uploadFun(*tuple(args))
    
    
    def _TestUpload(self, data, internalformat, format, gltype):
        """ Test whether we can create a texture of the given shape.
        Returns True if we can, False if we can't.
        """
        
        # define dict
        D = {   1: (gl.glTexImage1D, gl.GL_PROXY_TEXTURE_1D),
                2: (gl.glTexImage2D, gl.GL_PROXY_TEXTURE_2D),
                3: (gl.glTexImage3D, gl.GL_PROXY_TEXTURE_3D)}
        
        # determine function and target from texType
        uploadFun, target = D[self._ndim]
        
        # build args list
        shape = [i for i in reversed( list(data.shape[:self._ndim]) )]
        args = [target, 0, internalformat] + shape + [0, format, gltype, None]
        
        # do fake upload
        uploadFun(*tuple(args))
        
        # test and return
        ok = gl.glGetTexLevelParameteriv(target, 0, gl.GL_TEXTURE_WIDTH)
        return bool(ok)
    
    
    def _UploadTexture(self, data, internalformat, format, gltype):
        """ Upload a texture to the current texture object.
        It should have been verified that the texture will fit.
        """
        
        # define dict
        D = {   1: (gl.glTexImage1D, gl.GL_TEXTURE_1D),
                2: (gl.glTexImage2D, gl.GL_TEXTURE_2D),
                3: (gl.glTexImage3D, gl.GL_TEXTURE_3D)}
        
        # determine function and target from texType
        uploadFun, target = D[self._ndim]
        
        # build args list
        shape = [i for i in reversed( list(data.shape[:self._ndim]) )]
        args = [target, 0, internalformat] + shape + [0, format, gltype, data]
        
        # call
        uploadFun(*tuple(args))
    
    
    def _GetFormat(self, shape):
        """ Get internalformat and format, based on the self._ndim
        and the shape. If the shape does not match with the texture
        type, an exception is raised.
        """
        
        if self._ndim == 1:
            if len(shape)==1:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==2 and shape[1] == 1:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==2 and shape[1] == 3:
                iformat, format = gl.GL_RGB, gl.GL_RGB
            elif len(shape)==2 and shape[1] == 4:
                iformat, format = gl.GL_RGBA, gl.GL_RGBA
            else:
                raise ValueError("Cannot create 1D texture, data of invalid shape.")
        
        elif self._ndim == 2:
        
            if len(shape)==2:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==3 and shape[2]==1:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==3 and shape[2]==3:
                iformat, format = gl.GL_RGB, gl.GL_RGB
            elif len(shape)==3 and shape[2]==4:
                iformat, format = gl.GL_RGBA, gl.GL_RGBA
            else:
                raise ValueError("Cannot create 2D texture, data of invalid shape.")
        
        elif self._ndim == 3:
        
            if len(shape)==3:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==4 and shape[3]==1:
                iformat, format = gl.GL_LUMINANCE8, gl.GL_LUMINANCE
            elif len(shape)==4 and shape[3]==3:
                iformat, format = gl.GL_RGB, gl.GL_RGB
            elif len(shape)==4 and shape[3]==4:
                iformat, format = gl.GL_RGBA, gl.GL_RGBA
            else:
                raise ValueError("Cannot create 3D texture, data of invalid shape.")
        
        else:
            raise ValueError("Cannot create a texture with these dimensions.")
        
        return iformat, format
    
    
    def DestroyGl(self):
        """ DestroyGl()
        
        Removes the texture from OpenGl memory. The internal reference
        to the original data is kept though.
        
        """
        try:
            if self._texId > 0:
                gl.glDeleteTextures([self._texId])
        except Exception:
            pass
        self._texId = 0
    
    
    def Destroy(self):
        """ Destroy()
        
        Really destroy data.
        
        """
        # remove OpenGl bits
        self.DestroyGl()
        # remove internal reference
        self._dataRef = None
        self._shape = None
    
    
    def __del__(self):
        self.Destroy()


class Colormap(TextureObject):
    """ Colormap()
    
    A colormap represents a table of colors to map
    grayscale data.
    
    """
    
    # Note that the OpenGL imaging subset also implements a colormap,
    # but it is not guaranteed that the subset is available.
    
    def __init__(self):
        TextureObject.__init__(self, 1)
        
        # CT: (0,0,0,0.0), (1,0,0,0.002), (0,0.5,1,0.6), (0,1,0,1)
        self._current = [(0,0,0), (1,1,1)]
        self.SetMap(self._current)
    
    
    def _UploadTexture(self, data, *args):
        """ Overloaded version to upload the texture.
        """
        
        # let the original class do the work
        TextureObject._UploadTexture(self, data, *args)
        
        # set interpolation and extrapolation parameters
        tmp = gl.GL_NEAREST # gl.GL_NEAREST | gl.GL_LINEAR
        gl.glTexParameteri(gl.GL_TEXTURE_1D, gl.GL_TEXTURE_MIN_FILTER, tmp)
        gl.glTexParameteri(gl.GL_TEXTURE_1D, gl.GL_TEXTURE_MAG_FILTER, tmp)
        gl.glTexParameteri(gl.GL_TEXTURE_1D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
    
    
    def GetMap(self):
        """ GetMap()
        
        Get the current texture map, as last set with SetMap().
        
        """
        return self._current
    
    
    def GetData(self):
        """ GetData()
        
        Get the full colormap as a 256x4 numpy array.
        
        """
        return self._dataRef
    
    
    def SetMap(self, *args):
        """ SetMap(*args)
        
        Set the colormap data. This method accepts several arguments:
        
        A list/tuple of tuples where each tuple represents a RGB or RGBA color.
        
        A dict with keys 'red', 'green', 'blue', 'alpha' (or only the first
        letter). Each dict should contain a list of 2-element tuples that
        specify index and color value. Indices should be between 0 and 1.
        
        A numpy array specifying the RGB or RGBA tuples.
        
        """
        
        # one argument given?
        if len(args)==1:
            args = args[0]
        
        # store
        self._current = args
        
        # init
        data = None
        
        # parse input
        
        if isinstance(args, dict):
            # DICT
            
            # Allow several color names
            for key in list(args.keys()):
                if key.lower() in ['r', 'red']:
                    args['r'] = args[key]
                elif key.lower() in ['g', 'green']:
                    args['g'] = args[key]
                if key.lower() in ['b', 'blue']:
                    args['b'] = args[key]
                if key.lower() in ['a', 'alpha']:
                    args['a'] = args[key]
            # Init data, alpha 1
            data2 = np.zeros((256,4),np.float32)
            data2[:,3] = 1.0
            # For each channel ...
            for i in range(4):
                channel = 'rgba'[i]
                if not channel in args:
                    continue
                # Get value list and check
                values = args[channel]
                if not hasattr(values,'__len__'):
                    raise ValueError('Invalid colormap.')
                # Init interpolation
                data = np.zeros((len(values),), dtype=np.float32)
                x = np.linspace(0.0, 1.0, 256)
                xp = np.zeros((len(values),), dtype=np.float32)
                # Insert values
                count = -1
                for el in values:
                    count += 1
                    if not hasattr(el,'__len__') or len(el) != 2:
                        raise ValueError('Colormap dict entries must have 2 elements.')
                    xp[count] = el[0]
                    data[count] = el[1]
                # Interpolate
                data2[:,i] = np.interp(x, xp, data)
            # Set
            data = data2
        
        elif isinstance(args, (tuple, list)):
            # LIST
            
            data = np.zeros((len(args),4), dtype=np.float32)
            data[:,3] = 1.0 # init alpha to be all ones
            count = -1
            for el in args:
                count += 1
                if not hasattr(el,'__len__') or len(el) not in [3,4]:
                    raise ValueError('Colormap entries must have 3 or 4 elements.')
                elif len(el)==3:
                    data[count,:] = el[0], el[1], el[2], 1.0
                elif len(el)==4:
                    data[count,:] = el[0], el[1], el[2], el[3]
        
        elif isinstance(args, np.ndarray):
            # ARRAY
            
            if args.ndim != 2 or args.shape[1] not in [3,4]:
                raise ValueError('Colormap entries must have 3 or 4 elements.')
            elif args.shape[1]==3:
                data = np.ones((args.shape[0], 4), dtype=np.float32)
                data[:, 0:3] = args
            elif args.shape[1]==4:
                data = args
            else:
                raise ValueError("Invalid argument to set colormap.")
        
        # Apply interpolation (if required)
        if data is not None:
            if data.shape[0] == 256 and data.dtype == np.float32:
                data2 = data
            else:
                # interpolate first
                x = np.linspace(0.0, 1.0, 256)
                xp = np.linspace(0.0, 1.0, data.shape[0])
                data2 = np.zeros((256,4),np.float32)
                for i in range(4):
                    data2[:,i] = np.interp(x, xp, data[:,i])
            # store texture
            #self._data = data2
            self.SetData(data2)


class Colormapable(object):
    """ Mixer class for wobjects that can map scalar data to colors.
    
    Instances of this class have a colormap propery and a clim property.
    
    Inheriting classes can implement the following methods to overload
    the default behavior:
      * _GetColormap, _SetColormap(cmap)
      * _GetClim, _SetClim(clim)
      * _EnableColormap(texUnit=0), _DisableColormap
    
    """
    
    def __init__(self):
        self._colormap = Colormap()
        self._clim = Range(0,1)
    
    @PropWithDraw
    def colormap():
        """ Get/get the colormap. This can be:
          * A tuple/list of element which each have 3 or 4 values (RGB/RGBA)
          * A Nx3 or Nx4 numpy array
          * A dict with names R,G,B,A, where each value is a list. Each
            element in the list is a tuple (index, color-value).
        
        Visvis defines a number of standard colormaps named by vv.CM_*. A few
        examples are CM_GRAY, CM_HOT, CM_JET, CM_SUMMER, CM_CT1. See
        vv.colormaps for a dict with all available default colormaps.
        """
        def fget(self):
            return self._GetColormap()
        def fset(self, value):
            self._SetColormap(value)
        return locals()
    
    @PropWithDraw
    def clim():
        """ Get/set the contrast limits. For a gray colormap, clim.min
        is black, clim.max is white.
        """
        def fget(self):
            return self._GetClim()
        def fset(self, value):
            if not isinstance(value, Range):
                value = Range(value)
            self._SetClim(value)
        return locals()
    
    def _GetColormap(self):
        return self._colormap.GetMap()
    def _SetColormap(self, value):
        self._colormap.SetMap(value)
    
    def _EnableColormap(self, texUnit=0):
        self._colormap.Enable(texUnit)
    def _DisableColormap(self):
        self._colormap.Disable()
    
    def _GetClim(self):
        return self._clim
    def _SetClim(self, value):
        self._clim = value
