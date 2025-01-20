# -*- coding: utf-8 -*-
# Copyright (C) 2011, Nicolas P. Rougier
# Copyright (C) 2012, Almar Klein

""" visvis.text.freetype package.

A compact wrapper that only wraps what we need to draw text. No more, no less.

This code is based on Nicolas Rougier's freetype wrapper. The ft_xxx modules
were simply copied. I only modified the __init__.py to make it more to my
liking (not using any from x import *), and to make it much more compact
by reducing it to what we need in visvis.

"""

import ctypes
import ctypes.util
from ctypes import byref
import struct

# From six.py
import sys
PY3 = sys.version_info[0] == 3
if PY3:
    string_types = str,
else:
    string_types = basestring,  # noqa

# Imports from the low level freetype wrapper
# These names I collected by parsing this module for words starting with "FT_".
from visvis.text.freetype.ft_enums import (FT_LOAD_RENDER, FT_LOAD_FORCE_AUTOHINT,  # noqa
                                           FT_KERNING_DEFAULT, FT_KERNING_UNFITTED)  # noqa
from visvis.text.freetype.ft_types import FT_Int
from visvis.text.freetype.ft_errors import FT_Exception
from visvis.text.freetype.ft_structs import (FT_Face, FT_Glyph, FT_Matrix, FT_Vector,  # noqa
                                             FT_Library, FT_GlyphSlot, FT_Size_Metrics)  # noqa


## The actual library wrapper

def _looks_lib(fname):
    """ Returns True if the given filename looks like a dynamic library.
    Based on extension, but cross-platform and more flexible.
    """
    fname = fname.lower()
    if sys.platform.startswith('win'):
        return fname.endswith('.dll')
    elif sys.platform.startswith('darwin'):
        return fname.endswith('.dylib')
    else:
        return fname.endswith('.so') or '.so.' in fname


class FreeTypeWrapper(object):
    """ Class to find and load the FreeType dll.
    """
    
    def __init__(self):
        
        self._fname = None
        self._dll = None
        self._handle = None
        
        fname = self.find_library()
        self.load_library(fname)
    
    def find_library(self):
        
        # Get Python dirs to search (shared is for Pyzo)
        import os
        py_sub_dirs = ['shared', 'lib', 'DLLs']
        py_lib_dirs = [os.path.join(sys.prefix, d) for d in py_sub_dirs]
        if hasattr(sys, 'base_prefix'):
            py_lib_dirs += [os.path.join(sys.base_prefix, d) for d in py_sub_dirs]
        py_lib_dirs = [d for d in py_lib_dirs if os.path.isdir(d)]
        for py_lib_dir in py_lib_dirs:
            for fname in os.listdir(py_lib_dir):
                if 'freetype' in fname.lower() and _looks_lib(fname):
                    return os.path.join(py_lib_dir, fname)
        
        # Search in resources (only when frozen)
        if getattr(sys, 'frozen', None):
            from visvis.core.misc import getResourceDir
            import os
            for fname in os.listdir(getResourceDir()):
                if 'freetype' in fname.lower() and _looks_lib(fname):
                    return os.path.join(getResourceDir(), fname)
        
        # Try if ctypes knows where to find the freetype library
        fname = ctypes.util.find_library('freetype')
        
        # Try harder
        if not fname:
            if sys.platform.startswith('win'):
                NBITS = 8 * struct.calcsize("P")
                fname = ctypes.util.find_library('freetype6_'+str(NBITS))
            else:
                fname = 'libfreetype.so.6'
        
        # So far so good?
        if fname:
            return fname
        else:
            raise RuntimeError('Freetype library could not be found.')
    
    def load_library(self, fname):
         
        # Try loading it
        try:
            if sys.platform.startswith('win'):
                #dll = ctypes.windll.LoadLibrary(fname)
                dll = ctypes.cdll.LoadLibrary(fname)
            else:
                dll = ctypes.CDLL(fname)
        except OSError:
            raise RuntimeError('Freetype library could not be loaded.')
        
        # Store
        self._fname, self._dll = fname, dll
    
    def get_handle(self):
        '''
        Get unique FT_Library handle
        '''
        if not self._handle:
            self._handle = FT_Library( )
            error = self._dll.FT_Init_FreeType( byref(self._handle) )
            if error: raise FT_Exception(error)
        return self._handle
    
    def del_library(self):
        if self._handle:
            # No need to try-catch; an exception in a __del__ is never shown anyway
            self._dll.FT_Done_FreeType(self._handle)
            self._handle = None
    
    def __del__(self):
        self.del_library()

    @property
    def filename(self):
        return self._fname
    
    @property
    def version(self):
        '''
        Return the version of the FreeType library being used as a tuple of
        ( major version number, minor version number, patch version number )
        '''
        amajor = FT_Int()
        aminor = FT_Int()
        apatch = FT_Int()
        library = self.get_handle()
        self._dll.FT_Library_Version(library, byref(amajor), byref(aminor), byref(apatch))
        return (amajor.value, aminor.value, apatch.value)


# Instantiate wrapper
FT = FreeTypeWrapper()

# These functions are used in this module
FT_New_Face            = FT._dll.FT_New_Face
FT_Open_Face           = FT._dll.FT_Open_Face
FT_Done_Face           = FT._dll.FT_Done_Face
FT_Set_Char_Size       = FT._dll.FT_Set_Char_Size
FT_Set_Pixel_Sizes     = FT._dll.FT_Set_Pixel_Sizes
FT_Load_Char           = FT._dll.FT_Load_Char
FT_Set_Transform       = FT._dll.FT_Set_Transform
FT_Get_Kerning         = FT._dll.FT_Get_Kerning
FT_Get_Glyph           = FT._dll.FT_Get_Glyph
FT_Get_Char_Index      = FT._dll.FT_Get_Char_Index


## Higher level classes
# The classes below were simply copied from the __init__.py of Nicolas'
# freetype wrapper. I dont need all the methods, but in this way I can
# keep up to date by simply pasting the classes in.
#
# Note that GlyphSlot.GlyphSlot is broken. We dont use it, but let's keep the
# class intact.


# Direct wrapper (simple renaming)
Vector = FT_Vector
Matrix = FT_Matrix


class GlyphSlot( object ):
    '''
    FT_GlyphSlot wrapper.

    FreeType root glyph slot class structure. A glyph slot is a container where
    individual glyphs can be loaded, be they in outline or bitmap format.
    '''

    def __init__( self, slot ):
        '''
        Create GlyphSlot object from an FT glyph slot.

        Parameters:
        -----------
          glyph: valid FT_GlyphSlot object
        '''
        self._FT_GlyphSlot = slot

    # def get_glyph( self ):
    #     '''
    #     A function used to extract a glyph image from a slot. Note that the
    #     created FT_Glyph object must be released with FT_Done_Glyph.
    #     '''
    #     aglyph = FT_Glyph()
    #     error = FT_Get_Glyph( self._FT_GlyphSlot, byref(aglyph) )
    #     if error: raise FT_Exception( error )
    #     return Glyph( aglyph )

    def _get_bitmap( self ):
        return Bitmap( self._FT_GlyphSlot.contents.bitmap )
    bitmap = property( _get_bitmap,
       doc = '''This field is used as a bitmap descriptor when the slot format
                is FT_GLYPH_FORMAT_BITMAP. Note that the address and content of
                the bitmap buffer can change between calls of FT_Load_Glyph and
                a few other functions.''')

    def _get_next( self ):
        return GlyphSlot( self._FT_GlyphSlot.contents.next )
    next = property( _get_next,
     doc = '''In some cases (like some font tools), several glyph slots per
              face object can be a good thing. As this is rare, the glyph slots
              are listed through a direct, single-linked list using its 'next'
              field.''')

    advance = property( lambda self: self._FT_GlyphSlot.contents.advance,
        doc = '''This shorthand is, depending on FT_LOAD_IGNORE_TRANSFORM, the
                 transformed advance width for the glyph (in 26.6 fractional
                 pixel format). As specified with FT_LOAD_VERTICAL_LAYOUT, it
                 uses either the 'horiAdvance' or the 'vertAdvance' value of
                 'metrics' field.''')

    # def _get_outline( self ):
    #     return Outline( self._FT_GlyphSlot.contents.outline )
    # outline = property( _get_outline,
    #     doc = '''The outline descriptor for the current glyph image if its
    #              format is FT_GLYPH_FORMAT_OUTLINE. Once a glyph is loaded,
    #              'outline' can be transformed, distorted, embolded,
    #              etc. However, it must not be freed.''')

    format = property( lambda self: self._FT_GlyphSlot.contents.format,
       doc = '''This field indicates the format of the image contained in the
                glyph slot. Typically FT_GLYPH_FORMAT_BITMAP,
                FT_GLYPH_FORMAT_OUTLINE, or FT_GLYPH_FORMAT_COMPOSITE, but
                others are possible.''')

    bitmap_top  = property( lambda self:
                             self._FT_GlyphSlot.contents.bitmap_top,
            doc = '''This is the bitmap's top bearing expressed in integer
                     pixels. Remember that this is the distance from the
                     baseline to the top-most glyph scanline, upwards y
                     coordinates being positive.''')

    bitmap_left = property( lambda self:
                            self._FT_GlyphSlot.contents.bitmap_left,
            doc = '''This is the bitmap's left bearing expressed in integer
                     pixels. Of course, this is only valid if the format is
                     FT_GLYPH_FORMAT_BITMAP.''')

    linearHoriAdvance = property( lambda self:
                                  self._FT_GlyphSlot.contents.linearHoriAdvance,
                  doc = '''The advance width of the unhinted glyph. Its value
                           is expressed in 16.16 fractional pixels, unless
                           FT_LOAD_LINEAR_DESIGN is set when loading the glyph.
                           This field can be important to perform correct
                           WYSIWYG layout. Only relevant for outline glyphs.''')

    linearVertAdvance = property( lambda self:
                                  self._FT_GlyphSlot.contents.linearVertAdvance,
                  doc = '''The advance height of the unhinted glyph. Its value
                           is expressed in 16.16 fractional pixels, unless
                           FT_LOAD_LINEAR_DESIGN is set when loading the glyph.
                           This field can be important to perform correct
                           WYSIWYG layout. Only relevant for outline glyphs.''')

class SizeMetrics( object ):
    '''
    The size metrics structure gives the metrics of a size object.

    **Note**

    The scaling values, if relevant, are determined first during a size
    changing operation. The remaining fields are then set by the driver. For
    scalable formats, they are usually set to scaled values of the
    corresponding fields in Face.

    Note that due to glyph hinting, these values might not be exact for certain
    fonts. Thus they must be treated as unreliable with an error margin of at
    least one pixel!

    Indeed, the only way to get the exact metrics is to render all glyphs. As
    this would be a definite performance hit, it is up to client applications
    to perform such computations.

    The SizeMetrics structure is valid for bitmap fonts also.
    '''

    def __init__(self, metrics ):
        '''
        Create a new SizeMetrics object.

        Parameters:
        -----------
          metrics : a FT_SizeMetrics
        '''
        self._FT_Size_Metrics = metrics

    x_ppem = property( lambda self: self._FT_Size_Metrics.x_ppem,
       doc = '''The width of the scaled EM square in pixels, hence the term
                'ppem' (pixels per EM). It is also referred to as 'nominal
                width'.''' )

    y_ppem = property( lambda self: self._FT_Size_Metrics.y_ppem,
       doc = '''The height of the scaled EM square in pixels, hence the term
                'ppem' (pixels per EM). It is also referred to as 'nominal
                height'.''' )

    x_scale = property( lambda self: self._FT_Size_Metrics.x_scale,
        doc = '''A 16.16 fractional scaling value used to convert horizontal
                 metrics from font units to 26.6 fractional pixels. Only
                 relevant for scalable font formats.''' )

    y_scale = property( lambda self: self._FT_Size_Metrics.y_scale,
        doc = '''A 16.16 fractional scaling value used to convert vertical
                 metrics from font units to 26.6 fractional pixels. Only
                 relevant for scalable font formats.''' )

    ascender = property( lambda self: self._FT_Size_Metrics.ascender,
         doc = '''The ascender in 26.6 fractional pixels. See Face for the
                  details.''' )

    descender = property( lambda self: self._FT_Size_Metrics.descender,
          doc = '''The descender in 26.6 fractional pixels. See Face for the
                    details.''' )

    height = property( lambda self: self._FT_Size_Metrics.height,
       doc = '''The height in 26.6 fractional pixels. See Face for the details.''' )

    max_advance = property(lambda self: self._FT_Size_Metrics.max_advance,
            doc = '''The maximal advance width in 26.6 fractional pixels. See
                      Face for the details.''' )


class Bitmap(object):
    '''
    FT_Bitmap wrapper

    A structure used to describe a bitmap or pixmap to the raster. Note that we
    now manage pixmaps of various depths through the 'pixel_mode' field.

    Note:
    -----
    For now, the only pixel modes supported by FreeType are mono and
    grays. However, drivers might be added in the future to support more
    'colorful' options.
    '''
    def __init__(self, bitmap):
        '''
        Create a new Bitmap object.

        Parameters:
        -----------
        bitmap : a FT_Bitmap
        '''
        self._FT_Bitmap = bitmap

    rows = property(lambda self: self._FT_Bitmap.rows,
     doc = '''The number of bitmap rows.''')

    width = property(lambda self: self._FT_Bitmap.width,
      doc = '''The number of pixels in bitmap row.''')

    pitch = property(lambda self: self._FT_Bitmap.pitch,
      doc = '''The pitch's absolute value is the number of bytes taken by one
               bitmap row, including padding. However, the pitch is positive
               when the bitmap has a 'down' flow, and negative when it has an
               'up' flow. In all cases, the pitch is an offset to add to a
               bitmap pointer in order to go down one row.

               Note that 'padding' means the alignment of a bitmap to a byte
               border, and FreeType functions normally align to the smallest
               possible integer value.

               For the B/W rasterizer, 'pitch' is always an even number.

               To change the pitch of a bitmap (say, to make it a multiple of
               4), use FT_Bitmap_Convert. Alternatively, you might use callback
               functions to directly render to the application's surface; see
               the file 'example2.py' in the tutorial for a demonstration.''')

    def _get_buffer(self):
        data = [self._FT_Bitmap.buffer[i] for i in range(self.rows*self.pitch)]
        return data
    buffer = property(_get_buffer,
       doc = '''A typeless pointer to the bitmap buffer. This value should be
                aligned on 32-bit boundaries in most cases.''')

    num_grays = property(lambda self: self._FT_Bitmap.num_grays,
          doc = '''This field is only used with FT_PIXEL_MODE_GRAY; it gives
                   the number of gray levels used in the bitmap.''')

    pixel_mode = property(lambda self: self._FT_Bitmap.pixel_mode,
           doc = '''The pixel mode, i.e., how pixel bits are stored. See
                    FT_Pixel_Mode for possible values.''')
  
    palette_mode = property(lambda self: self._FT_Bitmap.palette_mode,
             doc ='''This field is intended for paletted pixel modes; it
                     indicates how the palette is stored. Not used currently.''')

    palette = property(lambda self: self._FT_Bitmap.palette,
        doc = '''A typeless pointer to the bitmap palette; this field is
                 intended for paletted pixel modes. Not used currently.''')


class Face( object ):
    '''
    FT_Face wrapper

    FreeType root face class structure. A face object models a typeface in a
    font file.
    '''
    def __init__( self, filename, index = 0 ):
        '''
        Build a new Face

        :param str filename:
            A path to the font file.
        :param int index:
               The index of the face within the font.
               The first face has index 0.
        '''
        library = FT.get_handle( )
        face = FT_Face( )
        self._FT_Face = None
        #error = FT_New_Face( library, filename, 0, byref(face) )
        u_filename = ctypes.c_char_p(filename)
        error = FT_New_Face( library, u_filename, index, byref(face) )
        if error: raise FT_Exception( error )
        self._filename = filename
        self._index = index
        self._FT_Face = face
    
    def __del__( self ):
        '''
        Discard  face object, as well as all of its child slots and sizes.
        '''
        if self._FT_Face is not None:
            FT_Done_Face( self._FT_Face )
    
    def set_char_size( self, width=0, height=0, hres=72, vres=72 ):
        '''
        This function calls FT_Request_Size to request the nominal size (in
        points).
        
        :param float width: The nominal width, in 26.6 fractional points.
        :param float height: The nominal height, in 26.6 fractional points.
        :param float hres: The horizontal resolution in dpi.
        :param float vres: The vertical resolution in dpi.

        **Note**

        If either the character width or height is zero, it is set equal to the
        other value.

        If either the horizontal or vertical resolution is zero, it is set
        equal to the other value.

        A character width or height smaller than 1pt is set to 1pt; if both
        resolution values are zero, they are set to 72dpi.

        Don't use this function if you are using the FreeType cache API.
        '''
        error = FT_Set_Char_Size( self._FT_Face, width, height, hres, vres )
        if error: raise FT_Exception( error)
    
    def set_pixel_sizes( self, width, height ):
        '''
        This function calls FT_Request_Size to request the nominal size (in
        pixels).

        Parameters:
        -----------
        width: The nominal width, in pixels.

        height: The nominal height, in pixels.
        '''
        error = FT_Set_Pixel_Sizes( self._FT_Face, width, height )
        if error: raise FT_Exception(error)
    
    def get_char_index( self, charcode ):
        '''
        Return the glyph index of a given character code. This function uses a
        charmap object to do the mapping.

        Parameters:
        -----------
        charcode: The character code.

        Note:
        -----
        If you use FreeType to manipulate the contents of font files directly,
        be aware that the glyph index returned by this function doesn't always
        correspond to the internal indices used within the file. This is done
        to ensure that value 0 always corresponds to the 'missing glyph'.
        '''
        if isinstance(charcode, string_types):
            charcode = ord( charcode )
        return FT_Get_Char_Index( self._FT_Face, charcode )

    def set_transform( self, matrix, delta ):
        '''
        A function used to set the transformation that is applied to glyph
        images when they are loaded into a glyph slot through FT_Load_Glyph.

        Parameters:
        -----------
        matrix: A pointer to the transformation's 2x2 matrix.
                Use 0 for the identity matrix.

        delta: A pointer to the translation vector.
               Use 0 for the null vector.

        Note:
        -----
        The transformation is only applied to scalable image formats after the
        glyph has been loaded. It means that hinting is unaltered by the
        transformation and is performed on the character size given in the last
        call to FT_Set_Char_Size or FT_Set_Pixel_Sizes.

        Note that this also transforms the 'face.glyph.advance'
        field, but not the values in 'face.glyph.metrics'.
        '''
        FT_Set_Transform( self._FT_Face,
                          byref(matrix), byref(delta) )

    def load_char( self, char, flags = FT_LOAD_RENDER ):
        '''
        A function used to load a single glyph into the glyph slot of a face
        object, according to its character code.

        Parameters:
        -----------
        char: The glyph's character code, according to the current charmap used
              in the face.

        flags: A flag indicating what to load for this glyph. The FT_LOAD_XXX
               constants can be used to control the glyph loading process
               (e.g., whether the outline should be scaled, whether to load
               bitmaps or not, whether to hint the outline, etc).

        Note:
        -----
        This function simply calls FT_Get_Char_Index and FT_Load_Glyph.
        '''

        if len(char) == 1:
            char = ord(char)
        error = FT_Load_Char( self._FT_Face, char, flags )
        if error: raise FT_Exception( error )
    
    def get_kerning( self, left, right, mode = FT_KERNING_DEFAULT ):
        '''
        Return the kerning vector between two glyphs of a same face.

        Parameters:
        -----------
        left: The index of the left glyph in the kern pair.
        
        right: The index of the right glyph in the kern pair.

        mode: See FT_Kerning_Mode for more information. Determines the scale
              and dimension of the returned kerning vector.

        Note:
        -----
        Only horizontal layouts (left-to-right & right-to-left) are supported
        by this method. Other layouts, or more sophisticated kernings, are out
        of the scope of this API function -- they can be implemented through
        format-specific interfaces.
        '''
        left_glyph = self.get_char_index( left )
        right_glyph = self.get_char_index( right )
        kerning = FT_Vector(0,0)
        error = FT_Get_Kerning( self._FT_Face,
                                left_glyph, right_glyph, mode, byref(kerning) )
        if error: raise FT_Exception( error )
        return kerning

    def _get_glyph( self ):
        return GlyphSlot( self._FT_Face.contents.glyph )
    
    glyph = property( _get_glyph,
      doc = '''The face's associated glyph slot(s).''')

    def _get_size( self ):
        size = self._FT_Face.contents.size
        metrics = size.contents.metrics
        return SizeMetrics(metrics)
    size = property( _get_size,
     doc = '''The current active size for this face.''')
