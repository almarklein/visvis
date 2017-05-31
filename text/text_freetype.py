# -*- coding: utf-8 -*-
# Copyright (C) 2011, Nicolas P. Rougier
# Copyright (C) 2012, Robert Schroll
# Copyright (C) 2012, Almar Klein
#
# This module contains code taken from freetype-py, which was modified
# to integrate with visvis.

""" Text rendering using the FreeType font renderer.

A note about availability of fonts:
  * We make sure that there is always a "sans" font by shipping it with visvis.
    This also makes for consistent looks.
  * We try our best to also provide a "serif" and "mono" font.
  * Any other font requires fc-match (which is usually available on Linux)

"""

import os
import sys
import math
import numpy as np
import OpenGL.GL as gl

from visvis.core.misc import getResourceDir, getOpenGlCapable

import subprocess

from visvis.core.shaders import Shader, ShaderCodePart

from visvis.text.text_base import AtlasTexture, FontManager
from visvis.text.text_base import correctVertices, simpleTextureDraw

from visvis.text.freetype import (Face, Vector, Matrix, FT_KERNING_UNFITTED,
                                  FT_LOAD_RENDER, FT_LOAD_FORCE_AUTOHINT )

try:
    n2_16 = long(0x10000)  # noqa
except Exception:
    n2_16 = 0x10000

# The scale factor for textures. The texture glyphs are made TEX_SCALE times
# bigger than the screen resolution. This means that we prevent very blurry
# pieces for small text. The text becomes a bit too crisp I think, but
# I suspect that when we apply the full screen aliasing, the text will look
# great!
TEX_SCALE = 2.5

# todo: have pyzo ship freeType lib on Windows and use that if possible.
# todo: When we implement full screen antialiasing, we can remove the shader here

FRAGMENT_SHADER_ = """
// Uniforms obtained from OpenGL
    uniform sampler2D texture; // The 3D texture
    uniform vec2 shape; // And its shape (as in OpenGl)
    
    void main()
    {
        // Get centre location
        vec2 pos = gl_TexCoord[0].xy;
        
        // Init value
        vec4 color1 = vec4(0.0, 0.0, 0.0, 0.0);
        
        // Init kernel and number of steps
        vec4 kernel = vec4 (0.2, 0.2, 0.1 , 0.1);
        //vec4 kernel = vec4 (0.3, 0.2, 0.1 , 0.0);
        int sze = 3;
        
        // Init step size in tex coords
        float dx = 1.0/shape.x;
        float dy = 1.0/shape.y;
        
        // Convolve
        for (int y=-sze; y<sze+1; y++)
        {
            for (int x=-sze; x<sze+1; x++)
            {
                float k = kernel[int(abs(float(x)))] * kernel[int(abs(float(y)))];
                vec2 dpos = vec2(float(x)*dx, float(y)*dy);
                color1 += texture2D(texture, pos+dpos) * k;
            }
        }
        gl_FragColor = color1 * gl_Color;
        
    }
"""
FRAGMENT_SHADER = """
// Uniforms obtained from OpenGL
    uniform sampler2D texture; // The 3D texture
    uniform vec2 shape; // And its shape (as in OpenGl)
    
    void main()
    {
        // Get centre location
        vec2 pos = gl_TexCoord[0].xy;
        
        // Define kernel. Chose such that k0+2*k1 == 1
        // k0 >> k1 is sharp   k0 ~ k1 is blurry
        // Optimal values depend on TEX_SCALE too!
        float k0 = 0.5;
        float k1 = 0.25;
        
        // Init step size in tex coords
        float dx = 1.0/shape.x;
        float dy = 1.0/shape.y;
        
        vec4 color1 = vec4(0.0, 0.0, 0.0, 0.0);
        
        color1 += texture2D(texture, pos+vec2(-dx,-dy) ) * k1 * k1;
        color1 += texture2D(texture, pos+vec2(-dx,0.0) ) * k1 * k0;
        color1 += texture2D(texture, pos+vec2(-dx,+dy) ) * k1 * k1;
        
        color1 += texture2D(texture, pos+vec2(0.0,-dy) ) * k0 * k1;
        color1 += texture2D(texture, pos+vec2(0.0,0.0) ) * k0 * k0;
        color1 += texture2D(texture, pos+vec2(0.0,+dy) ) * k0 * k1;
        
        color1 += texture2D(texture, pos+vec2(+dx,-dy) ) * k1 * k1;
        color1 += texture2D(texture, pos+vec2(+dx,0.0) ) * k1 * k0;
        color1 += texture2D(texture, pos+vec2(+dx,+dy) ) * k1 * k1;
        
        // Set final color
        gl_FragColor = color1 * gl_Color;
        
    }
"""

class FreeTypeAtlas(AtlasTexture):
    '''
    Taken from freetype-py's TextureAtlas
    Group multiple small data regions into a larger texture.

    The algorithm is based on the article by Jukka Jylänki : "A Thousand Ways
    to Pack the Bin - A Practical Approach to Two-Dimensional Rectangle Bin
    Packing", February 27, 2010. More precisely, this is an implementation of
    the Skyline Bottom-Left algorithm based on C++ sources provided by Jukka
    Jylänki at: http://clb.demon.fi/files/RectangleBinPack/

    Example usage:
    --------------

    atlas = TextureAtlas(512,512,3)
    region = atlas.get_region(20,20)
    ...
    atlas.set_region(region, data)
    '''

    def __init__(self, width=1024, height=1024, depth=1):
        '''
        Initialize a new atlas of given size.

        Parameters
        ----------

        width : int
            Width of the underlying texture

        height : int
            Height of the underlying texture

        depth : 1 or 3
            Depth of the underlying texture
        '''
        AtlasTexture.__init__(self)
        
        self.width  = int(math.pow(2, int(math.log(width, 2) + 0.5)))
        self.height = int(math.pow(2, int(math.log(height, 2) + 0.5)))
        self.depth  = depth
        self.nodes  = [ (0,0,self.width), ]
        self.data   = np.zeros((self.height, self.width, self.depth),
                               dtype=np.uint8)
        
        self.used   = 0
    
    
    def upload(self):
        '''
        Upload atlas data into video memory.
        '''
        # Note that we only uplad one channel
        self.SetData(self.data[:,:,0])

    

    def set_region(self, region, data):
        '''
        Set a given region width provided data.

        Parameters
        ----------

        region : (int,int,int,int)
            an allocated region (x,y,width,height)

        data : numpy array
            data to be copied into given region
        '''

        x, y, width, height = region
        self.data[y:y+height,x:x+width, :] = data



    def get_region(self, width, height):
        '''
        Get a free region of given size and allocate it

        Parameters
        ----------

        width : int
            Width of region to allocate

        height : int
            Height of region to allocate

        Return
        ------
            A newly allocated region as (x,y,width,height) or (-1,-1,0,0)
        '''
        width, height = int(width), int(height)  # issue #89
        best_height = self.data.shape[0] * 10
        best_index = -1
        best_width = self.data.shape[1] * 10
        region = 0, 0, width, height

        for i in range(len(self.nodes)):
            y = self.fit(i, width, height)
            if y >= 0:
                node = self.nodes[i]
                if (y+height < best_height or (y+height == best_height and node[2] < best_width)):
                    best_height = y+height
                    best_index = i
                    best_width = node[2]
                    region = node[0], y, width, height

        if best_index == -1:
            return -1,-1,0,0
        
        node = region[0], region[1]+height, width
        self.nodes.insert(best_index, node)

        i = best_index+1
        while i < len(self.nodes):
            node = self.nodes[i]
            prev_node = self.nodes[i-1]
            if node[0] < prev_node[0]+prev_node[2]:
                shrink = prev_node[0]+prev_node[2] - node[0]
                x,y,w = self.nodes[i]
                self.nodes[i] = x+shrink, y, w-shrink
                if self.nodes[i][2] <= 0:
                    del self.nodes[i]
                    i -= 1
                else:
                    break
            else:
                break
            i += 1

        self.merge()
        self.used += width*height
        return region



    def fit(self, index, width, height):
        '''
        Test if region (width,height) fit into self.nodes[index]

        Parameters
        ----------

        index : int
            Index of the internal node to be tested

        width : int
            Width or the region to be tested

        height : int
            Height or the region to be tested

        '''

        node = self.nodes[index]
        x,y = node[0], node[1]
        width_left = width
        
        if x+width > self.width:
            return -1

        i = index
        while width_left > 0:
            node = self.nodes[i]
            y = max(y, node[1])
            if y+height > self.height:
                return -1
            width_left -= node[2]
            i += 1
        return y



    def merge(self):
        '''
        Merge nodes
        '''

        i = 0
        while i < len(self.nodes)-1:
            node = self.nodes[i]
            next_node = self.nodes[i+1]
            if node[1] == next_node[1]:
                self.nodes[i] = node[0], node[1], node[2]+next_node[2]
                del self.nodes[i+1]
            else:
                i += 1



class FreeTypeFontManager(FontManager):
    
    def __init__(self):
        FontManager.__init__(self)
        
        self._font_names = {}
        self._fonts = {}
        self.atlas = FreeTypeAtlas(1024, 1024, 1)
        
        # Create shader
        self._shader = None
    
    @property
    def shader(self):
        if self._shader is None:
            if not getOpenGlCapable('2.0', 'Antialiased text'):
                self._shader = self
                self.Enable = lambda: None
                self.Disable = lambda: None
                global TEX_SCALE
                TEX_SCALE = 1.5 # Make text more blurry
            else:
                # Create shader
                self._shader = Shader()
                # Set fragment code, vertex code is empty
                self._shader.vertex.Clear()
                fragment = ShaderCodePart('textaa', '', FRAGMENT_SHADER)
                self._shader.fragment.AddPart(fragment)
                # Set uniform
                shape = self.atlas.data.shape[:2]
                uniform_shape = [float(s) for s in reversed(list(shape))]
                self.shader.SetStaticUniform('shape', uniform_shape)
        
        return self._shader
    
    def GetFont(self, fontname, size, bold=False, italic=False):
        fontfile = self.get_font_file(fontname, bold, italic)
        sig = fontfile, size
        if sig not in self._fonts:
            self._fonts[sig] = TextureFont(self.atlas, fontfile, size)
        return self._fonts[sig]
    
    def get_font_file(self, fontname, bold, italic):
        
        sig = (fontname, bold, italic)
        if not sig in self._font_names:
            
            # Did we ship this font with visvis?
            if True:
                fname = self.get_font_file_in_resources(fontname, bold, italic)
            
            # Try getting it in a smarter way (platform dependent)
            if not fname:
                if sys.platform.startswith('win'):
                    fname = self.get_font_file_with_windows(fontname, bold, italic)
                else:
                    fname = self.get_font_file_with_fcmatch(fontname, bold, italic)
            
            # Check. If not known, use sans
            if not fname:
                print('Warning: cannot retrieve font file fole for %s.' % fontname)
                fname = self.get_font_file('sans', bold, italic)
            
            # Store
            self._font_names[sig] = fname
        
        # Done
        return self._font_names[sig]
    
    def get_font_file_in_resources(self, fontname, bold, italic):
        
        # Normalize name and attributes
        fontname = fontname[0].upper() + fontname[1:].lower()
        bold = 'Bold' if bold else ''
        italic = 'Oblique' if italic else ''
        
        # Be a bit smart
        if fontname in ['Xkcd', 'Humor']:
            fname = 'HumorSans.otf'  # xkcd-style font
        else:
            fname = 'Free' + fontname + bold + italic + '.otf'  # Freetype font
        
        # Check if exist
        fname = os.path.join( getResourceDir(), fname )
        if os.path.exists(fname):
            return fname
        else:
            return ''
    
    def get_font_file_with_fcmatch(self, fontname, bold, italic):
        # fc-match is (almost?) always present in Linux.
        # fc-match is available on Mac, not sure if installed by default
        
        weight = 200 if bold else 80
        slant = 100 if italic else 0
        try:
            args = ['fc-match', '-f', '%{file}',
                        '%s:weight=%i:slant=%i' % (fontname, weight, slant)]
            fname, err = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()
            #py3k only: fname = subprocess.check_output(args)
            return fname.decode('utf-8') # Return as string
        except OSError:
            return ''
    
    def get_font_file_with_windows(self, fontname, bold, italic):
        
        # On Windows we know some fonts
        M = {'sans': 'arial', 'serif': 'times', 'mono': 'cour'}
        
        # Prepare
        postfix = ''
        if bold and italic: postfix = 'bi'
        elif bold: postfix = 'bd' # What is the d for?
        elif italic: postfix = 'i'
        
        # Select
        fname = M.get(fontname.lower(), '')
        if fname:
            fname = 'C:/Windows/Fonts/' + fname + postfix + '.ttf'
        else:
            # Just use the given name
            fname = 'C:/Windows/Fonts/' + fontname + '.ttf'
        
        # Check and return
        if not os.path.isfile(fname):
            fname = ''
        return fname
    
    def Compile(self, textObject):
        
        # Get text string with escaped text converted to Unicode
        tt = self.ConvertEscapedText(textObject.text)
        
        # Init arrays
        vertices = np.zeros((len(tt)*4,3), dtype=np.float32)
        texcoords = np.zeros((len(tt)*4,2), dtype=np.float32)
        
        # Prepare
        textObject._shift = None
        pen = [0,0]
        prev = None
        
        # Calculate font size
        # note: I can also imagine doing it the other way around; i.e. textSize
        # becomes as FreeType sees it, and we scale the fonts in the
        # prerendered text renderer. We'd have to change all the
        # uses fontSize though. So this is simply easier.
        fontSize = textObject.fontSize * 1.4 * TEX_SCALE
        fig = textObject.GetFigure()
        if fig:
            fontSize *= fig._relativeFontSize
        
        # Store tex_scale, integer fontsize and residu
        textObject._tex_scale = TEX_SCALE
        textObject._actualFontSize = int(round(fontSize))
        
        fonts = [(self.GetFont(textObject.fontName, textObject._actualFontSize), 0, False, False)]
        font, voffset, bold, italic = fonts[-1]
        escaped = False
        for i,charcode in enumerate(tt):
            if not escaped:
                if charcode == '_':
                    font = self.GetFont(textObject.fontName, font.size*0.7, bold, italic)
                    voffset -= 0.1*font.size
                    prev = None  # Disable kerning
                    continue
                elif charcode == '^':
                    font = self.GetFont(textObject.fontName, font.size*0.7, bold, italic)
                    voffset += 0.5*font.size
                    prev = None
                    continue
                elif charcode == '\x06':
                    italic = True
                    font = self.GetFont(textObject.fontName, font.size, bold, italic)
                    continue
                elif charcode == '\x07':
                    bold = True
                    font = self.GetFont(textObject.fontName, font.size, bold, italic)
                    continue
                elif charcode == '{':
                    fonts.append((font, voffset, bold, italic))
                    continue
                elif charcode == '}':
                    if len(fonts) > 1:
                        fonts.pop()
                        font, voffset, bold, italic = fonts[-1]
                        continue
                elif charcode == '\\':
                    if i < len(tt)-1 and tt[i+1] in '_^{}':
                        escaped = True
                        continue
            glyph = font[charcode]
            if glyph is None:
                continue # Character not available
            kerning = glyph.get_kerning(prev)
            x0 = pen[0] + glyph.offset[0] + kerning
            y0 = pen[1] + glyph.offset[1] + voffset
            x1 = x0 + glyph.size[0]
            y1 = y0 - glyph.size[1]
            u0 = glyph.texcoords[0]
            v0 = glyph.texcoords[1]
            u1 = glyph.texcoords[2]
            v1 = glyph.texcoords[3]

            # index     = i*4
            _vertices  = [[x0,y0,1],[x0,y1,1],[x1,y1,1], [x1,y0,1]]
            _texcoords = [[u0,v0],[u0,v1],[u1,v1], [u1,v0]]

            vertices[i*4:i*4+4] = _vertices
            texcoords[i*4:i*4+4] = _texcoords
            pen[0] = pen[0]+glyph.advance[0]/64.0 + kerning
            pen[1] = pen[1]+glyph.advance[1]/64.0
            prev = charcode
            font, voffset, bold, italic = fonts[-1]
            escaped = False
        
        # Flip and shift vertices
        vertices /= TEX_SCALE
        vertices *= (1, -1, 1)
        vertices += (0, font.ascender/TEX_SCALE, 0)
        
        # Store width
        if False:  # glyph is not None: # Not used
            textObject.width = pen[0]-glyph.advance[0]/64.0+glyph.size[0] if tt else 0
        
        # Update dynamic texture
        self.atlas.upload()
        
        # Store data.
        textObject._SetCompiledData(vertices, texcoords)
    
    
    def Position(self, textObject):
        FontManager.Position(self, textObject)
        
        # Get data
        vertices, texcoords = textObject._GetCompiledData()
        vertices = vertices.copy()
        
        # Use default algorithm to correct the vertices for alginment and angle
        font = self.GetFont(textObject.fontName, textObject._actualFontSize)
        correctVertices(textObject, vertices, font.height/TEX_SCALE)
        
        # Store
        textObject._SetFinalData(vertices, texcoords)
    
    
    def Draw(self, textObject, x=0, y=0, z=0):
        # Check if we need to recompile in case TEX_SCALE was changed
        if hasattr(textObject, '_tex_scale') and textObject._tex_scale != TEX_SCALE:
            textObject.Invalidate()
        
        FontManager.Draw(self, textObject)
        
        # Get data
        vertices, texCords = textObject._GetFinalData()
        
        # Translate
        if x or y or z:
            gl.glPushMatrix()
            gl.glTranslatef(x, y, z)
        
        # Draw
        self.shader.Enable()
        simpleTextureDraw(vertices, texCords, self.atlas, textObject.textColor)
        self.shader.Disable()
        
        # Un-translate
        if x or y or z:
            gl.glPopMatrix()
    

class TextureFont:
    '''
    A texture font gathers a set of glyph relatively to a given font filename
    and size.
    '''

    def __init__(self, atlas, filename, size):
        '''
        Initialize font

        Parameters:
        -----------

        atlas: TextureAtlas
            Texture atlas where glyph texture will be stored

        filename: str
            Font filename
        
        size : float
            Font size
        '''
        self.atlas = atlas
        self.filename = filename.encode('utf-8') # Make bytes
        self.size = size
        self.glyphs = {}
        face = Face( self.filename )
        face.set_char_size( int(self.size*64))
        self._dirty = False
        metrics = face.size
        self.ascender  = metrics.ascender/64.0
        self.descender = metrics.descender/64.0
        self.height    = metrics.height/64.0
        self.linegap   = self.height - self.ascender + self.descender
        self.depth = atlas.depth
    

    def __getitem__(self, charcode):
        '''
        x.__getitem__(y) <==> x[y]
        '''
        if charcode not in self.glyphs.keys():
            self.load('%c' % charcode)
        return self.glyphs.get(charcode, None)

 
    def load(self, charcodes = ''):
        '''
        Build glyphs corresponding to individual characters in charcodes.

        Parameters:
        -----------
        
        charcodes: [str | unicode]
            Set of characters to be represented
        '''
        face = Face( self.filename )
        try:
            return self._load(charcodes, face)
        finally:
            # Make sure to clear the face. I've seen some pretty bad
            # crashes on Windows when an exception was thrown in the code
            # in _load(), because the hold all the variables, preventing the
            # face from being cleared.
            face.__del__()
            face._FT_Face = None
    
    def _load(self, charcodes, face):
        pen = Vector(0,0)
        hres = 16*72
        hscale = 1.0/16
        # todo: use set_pixel_sizes?
        for charcode in charcodes:
            face.set_char_size( int(self.size * 64), 0, hres, 72 )
            matrix = Matrix( int((hscale) * n2_16), int((0.0) * n2_16),
                             int((0.0)    * n2_16), int((1.0) * n2_16) )
            face.set_transform( matrix, pen )
            if charcode in self.glyphs.keys():
                continue

            self.dirty = True
            flags = FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT

            face.load_char( charcode, flags )
            bitmap = face.glyph.bitmap
            left   = face.glyph.bitmap_left
            top    = face.glyph.bitmap_top
            width  = face.glyph.bitmap.width
            rows   = face.glyph.bitmap.rows
            pitch  = face.glyph.bitmap.pitch
            padding = 1 # Extra space for neighboring pixels to join in aa
            margin = 1 # Extra space to prevent overlap from other glyphs
            padmarg = padding + margin
            
            x,y,w,h = self.atlas.get_region(width/self.depth+2*padmarg,
                                                        rows+2*padmarg)
            if x < 0:
                print('Missed !')
                continue
            x,y = x+padmarg, y+padmarg
            w,h = w-2*padmarg, h-2*padmarg
            data = []
            for i in range(rows):
                data.extend(bitmap.buffer[i*pitch:i*pitch+width])
            data = np.array(data,dtype=np.ubyte).reshape(h,w,self.depth)
            gamma = 1.5
            Z = ((data/255.0)**(gamma))
            data = (Z*255).astype(np.ubyte)
            if True: # Add an extra pixel, otherwise there's no room for the aa
                # Note that we can do this because we asked for a larger region anyway
                data2 = np.zeros((  data.shape[0]+2*padding,
                                    data.shape[1]+2*padding,
                                    data.shape[2]), np.ubyte)
                data2[padding:-padding,padding:-padding,:] = data
                data = data2
                x,y = x-padding, y-padding
                w,h = w+2*padding, h+2*padding
            
            self.atlas.set_region((x,y,w,h), data)

            # Build glyph
            size   = w,h
            offset = left, top
            advance= face.glyph.advance.x, face.glyph.advance.y

            u0     = (x +     0.0)/float(self.atlas.width)
            v0     = (y +     0.0)/float(self.atlas.height)
            u1     = (x + w - 0.0)/float(self.atlas.width)
            v1     = (y + h - 0.0)/float(self.atlas.height)
            texcoords = (u0,v0,u1,v1)
            glyph = TextureGlyph(charcode, size, offset, advance, texcoords)
            self.glyphs[charcode] = glyph

            # Generate kerning
            for g in self.glyphs.values():
                # 64 * 64 because of 26.6 encoding AND the transform matrix used
                # in texture_font_load_face (hres = 64)
                kerning = face.get_kerning(g.charcode, charcode, mode=FT_KERNING_UNFITTED)
                if kerning.x != 0:
                    glyph.kerning[g.charcode] = kerning.x/(64.0*64.0)
                kerning = face.get_kerning(charcode, g.charcode, mode=FT_KERNING_UNFITTED)
                if kerning.x != 0:
                    g.kerning[charcode] = kerning.x/(64.0*64.0)

            # High resolution advance.x calculation
            # gindex = face.get_char_index( charcode )
            # a = face.get_advance(gindex, FT_LOAD_RENDER | FT_LOAD_TARGET_LCD)/(64*72)
            # glyph.advance = a, glyph.advance[1]


class TextureGlyph:
    '''
    A texture glyph gathers information relative to the size/offset/advance and
    texture coordinates of a single character. It is generally built
    automatically by a TextureFont.
    '''

    def __init__(self, charcode, size, offset, advance, texcoords):
        '''
        Build a new texture glyph

        Parameter:
        ----------

        charcode : char
            Represented character

        size: tuple of 2 ints
            Glyph size in pixels

        offset: tuple of 2 floats
            Glyph offset relatively to anchor point

        advance: tuple of 2 floats
            Glyph advance

        texcoords: tuple of 4 floats
            Texture coordinates of bottom-left and top-right corner
        '''
        self.charcode = charcode
        self.size = size
        self.offset = offset
        self.advance = advance
        self.texcoords = texcoords
        self.kerning = {}


    def get_kerning(self, charcode):
        ''' Get kerning information

        Parameters:
        -----------

        charcode: char
            Character preceding this glyph
        '''
        if charcode in self.kerning.keys():
            return self.kerning[charcode]
        else:
            return 0
