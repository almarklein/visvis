# -*- coding: utf-8 -*-
# Copyright (C) 2011, Nicolas P. Rougier
# Copyright (C) 2012, Robert Schroll
# Copyright (C) 2012, Almar Klein
#
# This module contains code taken from freetype-py, which was modified
# to integrate with visvis.

import sys
import math
import numpy as np
import OpenGL.GL as gl

from .text_base import AtlasTexture, FontManager, Text, Label
from .text_base import correctVertices, simpleTextureDraw

from .freetype import ( Face, Vector, Matrix,
                        set_lcd_filter,
                        FT_LOAD_RENDER, FT_LCD_FILTER_LIGHT, 
                        FT_LOAD_FORCE_AUTOHINT, FT_LOAD_TARGET_LCD, 
                        FT_KERNING_UNSCALED, FT_KERNING_UNFITTED
                      )
import subprocess

try:
    n2_16 = long(0x10000)
except Exception:
    n2_16 = 0x10000


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
        # todo: make the atlas work on just one channel?
        # for LCD subpixel stuff we probably need the colors
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

        best_height = self.data.shape[0] * 10
        best_index = -1
        best_width = self.data.shape[1] * 10
        region = 0, 0, width, height

        for i in range(len(self.nodes)):
            y = self.fit(i, width, height)
            if y >= 0:
                node = self.nodes[i]
                if (y+height < best_height or
                    (y+height == best_height and node[2] < best_width)):
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
        self.atlas = FreeTypeAtlas(1024, 1024, 3)
    
    def GetFont(self, fontname, size, bold=False, italic=False):
        fontfile = self.get_font_file(fontname, bold, italic)
        sig = fontfile, size
        if sig not in self._fonts:
            self._fonts[sig] = TextureFont(self.atlas, fontfile, size)
        return self._fonts[sig]
    
    def get_font_file(self, fontname, bold, italic):
        sig = (fontname, bold, italic)
        if not sig in self._font_names:
            weight = 200 if bold else 80
            slant = 100 if italic else 0
            # todo: ship freeSans etc.
            self._font_names[sig] = subprocess.check_output(['fc-match', '-f', '%{file}',
                                        '%s:weight=%i:slant=%i' % (fontname, weight, slant)])
        return self._font_names[sig]

    
    def Compile(self, textObject):
        
        # Get text string with escaped text converted to Unicode
        tt = self.ConvertEscapedText(textObject.text)
        
        # Init arrays
        vertices = np.zeros((len(tt)*4,3), dtype=np.float32)
        indices  = np.zeros((len(tt)*6, ), dtype=np.uint)
        colors   = np.zeros((len(tt)*4,4), dtype=np.float32)
        texcoords = np.zeros((len(tt)*4,2), dtype=np.float32)
        
        # Prepare
        textObject._shift = None
        pen = [0,0]
        prev = None
        
        # Calculate font size
        fontSize = textObject.fontSize
        fig = textObject.GetFigure()
        if fig:
            fontSize *= fig._relativeFontSize
        textObject._actualFontSize = fontSize
        
        fonts = [(self.GetFont(textObject.fontName, fontSize), 0, False, False)]
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

            index     = i*4
            _indices   = [index, index+1, index+2, index, index+2, index+3]
            _vertices  = [[x0,y0,1],[x0,y1,1],[x1,y1,1], [x1,y0,1]]
            _texcoords = [[u0,v0],[u0,v1],[u1,v1], [u1,v0]]
            _colors    = [textObject.textColor + (1.0,),]*4

            vertices[i*4:i*4+4] = _vertices
            indices[i*6:i*6+6] = _indices
            texcoords[i*4:i*4+4] = _texcoords
            colors[i*4:i*4+4] = _colors
            pen[0] = pen[0]+glyph.advance[0]/64.0 + kerning
            pen[1] = pen[1]+glyph.advance[1]/64.0
            prev = charcode
            font, voffset, bold, italic = fonts[-1]
            escaped = False
        
        # Flip and shift vertices
        vertices *= (1, -1, 1)
        vertices += (0, font.ascender, 0)
        
        # Store width
        if False: #glyph is not None: # Not used
            textObject.width = pen[0]-glyph.advance[0]/64.0+glyph.size[0] if tt else 0
        
        # Update dynamic texture
        self.atlas.upload()
        
        # Store data. 
        # todo: Why did we calculate indices anc colors. We dont need these, right?
        textObject._SetCompiledData(vertices, indices, texcoords, colors)
    
    
    def Position(self, textObject):
        FontManager.Position(self, textObject)
        
        # Get data
        vertices, indices, texcoords, colors = textObject._GetCompiledData()
        vertices = vertices.copy()
        
        # Use default algorithm to correct the vertices for alginment and angle
        font = self.GetFont(textObject.fontName, textObject._actualFontSize)
        correctVertices(textObject, vertices, font.height)
        
        # Store
        textObject._SetFinalData(vertices, indices, texcoords, colors)
    
    
    def Draw(self, textObject, x=0, y=0, z=0):
        FontManager.Draw(self, textObject)
        
        # Get data
        vertices, indices, texCords, colors = textObject._GetFinalData()
        
        # Translate
        if x or y or z:
            gl.glPushMatrix()
            gl.glTranslatef(x, y, z)
        
        # Draw
        simpleTextureDraw(vertices, texCords, self.atlas, textObject.textColor)
        
        # Un-translate
        if x or y or z:
            gl.glPopMatrix()   
        
#         # Enable texture atlas
#         self.atlas.Enable()
#         
#         # init vertex and texture array
#         gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
#         gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
#         gl.glVertexPointerf(vertices)
#         gl.glTexCoordPointerf(texCords)
#         
#         gl.glColorPointer(4, gl.GL_FLOAT, 0, colors)
#         
#         # draw
#         if textObject.textColor and len(vertices):
#             clr = textObject.textColor
#             gl.glColor(clr[0], clr[1], clr[2])
#             gl.glDrawArrays(gl.GL_QUADS, 0, len(vertices))
#             #gl.glDrawElements(gl.GL_TRIANGLES, len(indices),
#             #              gl.GL_UNSIGNED_INT, indices)
#             gl.glFlush()
#         
#         # disable texture and clean up     
#         if x or y or z:
#             gl.glPopMatrix()   
#         self.atlas.Disable()
#         gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
#         gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
    
    
    def Draw_sub(self, textObject, x=0, y=0, z=0):
        FontManager.Draw(self, textObject)
        
        # Get data
        vertices, indices, texcoords, colors = textObject._GetFinalData()
        
        # Set up the subpixel rendering.  The basic idea is that the vertices
        # should be shifted to integers to align with the pixel grid, and the
        # error accounted for in the vertex attribute.  This is complicated by
        # Labels, with may have a fractional pixel offset already (stored in
        # textObject._xoffset), so we shift the vertices to have a negative offset to
        # line them back up with pixel grid.
        vertices = vertices + np.array([x+textObject._shift[0], y+textObject._shift[1], z], dtype=np.float32)
        xint = np.floor(vertices[:,0] + textObject._xoffset)
        attrib = vertices[:,0] + textObject._xoffset - xint
        vertices[:,0] = xint - textObject._xoffset
        attrib.shape = (-1,1)
        
        self.atlas.Enable()
        
        gl.glEnable( gl.GL_TEXTURE_2D )
        gl.glDisable( gl.GL_DEPTH_TEST )

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, vertices)
        gl.glColorPointer(4, gl.GL_FLOAT, 0, colors)
        gl.glTexCoordPointer(2, gl.GL_FLOAT, 0, texcoords)

        alpha = 1
        gl.glEnable( gl.GL_COLOR_MATERIAL )
        gl.glBlendFunc( gl.GL_CONSTANT_COLOR_EXT,
                        gl.GL_ONE_MINUS_SRC_COLOR )
        gl.glEnable( gl.GL_BLEND )
        gl.glColor3f( alpha, alpha, alpha )
        gl.glBlendColor( 1-alpha, 1-alpha, 1-alpha, 1 )
        gl.glEnableVertexAttribArray( 1 );
        gl.glVertexAttribPointer( 1, 1, gl.GL_FLOAT, gl.GL_FALSE, 0, attrib)
#         shader = get_shader()
#         shader.bind()
#         shader.uniformi('texture', 0)
#         shader.uniformf('pixel', 1.0/512, 1.0/512)
        gl.glDrawElements(gl.GL_TRIANGLES, len(indices),
                          gl.GL_UNSIGNED_INT, indices)
#         shader.unbind()
        
        self.atlas.Disable()
        gl.glDisableVertexAttribArray( 1 );
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glDisable( gl.GL_TEXTURE_2D )
        gl.glDisable( gl.GL_BLEND )
    

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
        self.filename = filename
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
        set_lcd_filter(FT_LCD_FILTER_LIGHT)


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
        pen = Vector(0,0)
        hres = 16*72
        hscale = 1.0/16

        for charcode in charcodes:
            face.set_char_size( int(self.size * 64), 0, hres, 72 )
            matrix = Matrix( int((hscale) * n2_16), int((0.0) * n2_16),
                             int((0.0)    * n2_16), int((1.0) * n2_16) )
            face.set_transform( matrix, pen )
            if charcode in self.glyphs.keys():
                continue

            self.dirty = True
            flags = FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT
            flags |= FT_LOAD_TARGET_LCD

            face.load_char( charcode, flags )
            bitmap = face.glyph.bitmap
            left   = face.glyph.bitmap_left
            top    = face.glyph.bitmap_top
            width  = face.glyph.bitmap.width
            rows   = face.glyph.bitmap.rows
            pitch  = face.glyph.bitmap.pitch

            x,y,w,h = self.atlas.get_region(width/self.depth+2, rows+2)
            if x < 0:
                print('Missed !')
                continue
            x,y = x+1, y+1
            w,h = w-2, h-2
            data = []
            for i in range(rows):
                data.extend(bitmap.buffer[i*pitch:i*pitch+width])
            data = np.array(data,dtype=np.ubyte).reshape(h,w,3)
            gamma = 1.5
            Z = ((data/255.0)**(gamma))
            data = (Z*255).astype(np.ubyte)
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
