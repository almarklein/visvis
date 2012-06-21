
import OpenGL.GL as gl

import os
import numpy as np

import visvis
from visvis import ssdf
from visvis.utils.pypoints import Pointset
#
from visvis.core.misc import basestring , getResourceDir
from visvis.core.baseWibjects import Box

from .text_base import AtlasTexture, FontManager, Text, Label


class PrerenderedAtlas(AtlasTexture):
    pass


class Font:
    """ For the prerendered font system, the font consists of an atlas
    (one atlas per sans/serif/mono), and an info structure.
    """
    def __init__(self, info):
        self.info = info
        self.atlas = PrerenderedAtlas()
        self.atlas.SetData(info.data)


class PrerenderedFontManager(FontManager):
    
    def __init__(self):
        # load font data
        path = getResourceDir()
        self.s = ssdf.load(os.path.join(path, 'fonts.ssdf'))
        
        # list of fonts
        self.fonts = {}
    
    
    def GetFont(self, fontname):
        """ GetFont(fontname)
        
        Get a font instance. If that font was created earlier,
        that font is returned, otherwise it is created and stored
        for reuse. 
        
        """
        if fontname in self.fonts:
            return self.fonts[fontname]
        elif hasattr(self.s, fontname):
            tmp = Font(self.s[fontname])
            self.fonts[fontname] = tmp
            return tmp
        else:
            raise ValueError("Invalid font name.")
    
    
    def Compile(self, textObject):
        """ Create a series of glyphs from the text in the textObject.
        From these Glyphs. Also the relative vertices are calculated, 
        which are then corrected
        for angle and alignment in Position().
        """
        FontManager.Compile(self, textObject)
        
        # make invalid first
        textObject.Invalidate()
        
        # Get font object
        font = self.GetFont(textObject.fontName)
        
        # clear glyphs
        glyphs = [] 
        
        # Create reference character (used in Position)
        textObject._xglyph = Glyph(font, 'X', textObject.fontSize)     
        
        # Get text string with escaped text converted to Unicode
        tt = self.ConvertEscapedText(textObject.text)
        
        
        # build list of glyphs, take sub/super scripting into account.        
        escape = False
        styles = []
        style = None # Style to set
        for i in range(len(tt)):
            c = tt[i]            
            if escape:                
                g = Glyph(font, c, textObject.fontSize, styles)
                glyphs.append( g )
                escape = False
            elif c=='{':
                # Append style to the list
                if style:
                    styles.append(style)
                    style = None
            elif c=='}':
                # Remove style
                if styles:
                    styles.pop()                    
            elif c=='^':
                style = MiniStyle(2)
            elif c=='_':
                style = MiniStyle(1)
            elif c=='\x06':
                style = MiniStyle(0,False,True)
            elif c=='\x07':
                style = MiniStyle(0,True,False)
            elif c=='\\' and i+1<len(tt) and tt[i+1] in ['_^\x06\x07']:
                escape = True
            else:
                # create glyph (with new style (or not))
                g = Glyph(font, c, textObject.fontSize, styles+[style])
                glyphs.append( g )
                style = None
        
        # build arrays with vertices and coordinates        
        x1, y1, z = 0, 0, 0
        vertices = Pointset(3)
        texCords = Pointset(2)
        for g in glyphs:
            x2 = x1 + g.sizex
            y2 = g.sizey
            #y2 = y1 - g.sizey
            dy = g.dy
            
            # append texture coordinates
            texCords.append(g.s1, g.t1)
            texCords.append(g.s2, g.t1)
            texCords.append(g.s2, g.t2)
            texCords.append(g.s1, g.t2)
            
            # set skewing for position
            skew = textObject.fontSize * g.skewFactor
            
            # append vertices
            vertices.append(x1+skew, y1+dy, z)
            vertices.append(x2+skew, y1+dy, z)
            vertices.append(x2, y2+dy, z)
            vertices.append(x1, y2+dy, z)
            
            # prepare for next glyph
            x1 = x1 + g.width + 1     
        
        # store calculations
        textObject._SetCompiledData(vertices, texCords)
    
    
    def Position(self, textObject):
        """ The name is ment as a verb. The vertices are corrected
        for angle and alignment.
        """
        FontManager.Position(self, textObject)
        
        # get vertices
        vertices, texCords = textObject._GetCompiledData()
        if vertices is None:
            return
        vertices = vertices.copy()
        
        # scale text according to global text size property
        # todo: this should probably just set fontSize somewhere
        fig = textObject.GetFigure()
        if fig:
            vertices *= fig._relativeFontSize
        
        # obtain dimensions
        if len(vertices):
            x1, x2 = vertices[:,0].min(), vertices[:,0].max()
        else:
            x1, x2 = 0,0
        y1, y2 = 0, textObject._xglyph.sizey
        
        # set anchor
        if textObject.halign < 0:  anchorx = x1
        elif textObject.halign > 0:  anchorx = x2
        else: anchorx = x1 + (x2-x1)/2.0
        #
        if textObject.valign < 0:  anchory = y1
        elif textObject.valign > 0:  anchory = y2
        else: anchory = y1 + (y2-y1)/2.0
        
        # apply anchor
        angle = textObject.textAngle
        if isinstance(textObject, Text):
            # Text is a wobject, so must be flipped on y axis
            vertices[:,0] = vertices[:,0] - anchorx
            vertices[:,1] = -(vertices[:,1] - anchory)
        
        elif isinstance(textObject, Label):
            angle = -textObject.textAngle
            vertices[:,0] = vertices[:,0] - anchorx
            vertices[:,1] = vertices[:,1] - anchory
        
        # apply angle
        if angle != 0.0:
            cos_angle = np.cos(angle*np.pi/180.0)
            sin_angle = np.sin(angle*np.pi/180.0)
            vertices[:,0], vertices[:,1] = (
                vertices[:,0] * cos_angle - vertices[:,1] * sin_angle,
                vertices[:,0] * sin_angle + vertices[:,1] * cos_angle)
        
        # Move anchor in label
        if isinstance(textObject, Label):
            w,h = textObject.position.size
            # determine whether the text is vertical or horizontal
            halign, valign = textObject.halign, textObject.valign
            if textObject.textAngle > 135 or textObject.textAngle < -135:
                halign, valign = -halign, valign
            elif textObject.textAngle > 45:
                halign, valign = valign, -halign
            elif textObject.textAngle < -45:
                halign, valign = valign, halign
            # set anchor y
            if valign < 0:  anchory = 0
            elif valign > 0:  anchory = h
            else:  anchory = h/2.0
            # set anchor x
            if halign < 0:  anchorx = 0
            elif halign > 0:  anchorx = w
            else:  anchorx = w/2.0
            # apply
            vertices[:,0] = vertices[:,0] + anchorx
            vertices[:,1] = vertices[:,1] + anchory
        
        # store 
        textObject._SetFinalData(vertices, texCords)       
    
    
    def Draw(self, textObject, x=0, y=0, z=0):
        """ Draw the textobject.
        """
        FontManager.Draw(self, textObject)
        
        # Get texCords and vertices
        vertices, texCords = textObject._GetFinalData()
        if texCords is None or vertices is None:
            return
        
        # Translate
        if x or y or z:
            gl.glPushMatrix()
            gl.glTranslatef(x, y, z)
        
        # Get atlas
        atlas = self.GetFont(textObject.fontName).atlas
        
        # Enable texture atlas
        atlas.Enable()
        
        # init vertex and texture array
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glVertexPointerf(vertices.data)
        gl.glTexCoordPointerf(texCords.data)
        
        # draw
        if textObject.textColor and len(vertices):
            clr = textObject.textColor
            gl.glColor(clr[0], clr[1], clr[2])
            gl.glDrawArrays(gl.GL_QUADS, 0, len(vertices))
            gl.glFlush()
        
        # disable texture and clean up     
        if x or y or z:
            gl.glPopMatrix()   
        atlas.Disable()
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)



class Glyph(object):
    """ Glyph(font, char, size=12, styles=None)
    
    A glyph is a character. It is visualized by rendering
    the proper part from the texture stored in the Font object.
    
      * sizex and sizey represent the size of the glyph.
      * dy represents the offset in y direction (for sub/super scripts)
      * width specifies how much space there should be before the next char
      * s1 s2 t1 t2 represent texture coordinates
    
    """
    # the font.info contains
    # - a string of charcodes
    # - an array of origin 's
    # - an array of size's
    # - fontsize of the font in the data array
    
    def __init__(self, font, char, size=12, styles=None):
        
        # unwind the style for this glyph
        self.style = MiniStyle()
        if styles:
            for style in styles:
                self.style += style
        style = self.style
        
        # get info
        info = font.info
        
        # get asci code and check it
        if isinstance(char, basestring):
            ac = ord(char)
        elif isinstance(char, int):
            ac = char
        else:
            raise ValueError('To create a glyph, supply an int or character.')
        
        # do we have that char?
        if ac not in info.charcodes:#ac < 32 or ac > 255:
            print("Warning: Cannot draw character %i! " % ord(char))
            ac = 32 # make space
        
        # default
        infoSize, infoOrigin, infoWidth = info.size, info.origin, info.width
        # should and can we display in italic or bold?
        # Note: italic is now realized by printing it skewed rather using the
        # italic glyphs. The reason is that when using the texture one would
        # see artifacts from neighbouring characters. Additionally, it's now
        # possible to mix bold and italic text, and one can make any supported 
        # unicode character italic.
        #         if style.italic and ac in info.charcodes_i:
#             # italic text            
#             infoSize, infoOrigin, infoWidth = (
#                 info.size_i, info.origin_i, info.width_i)
        if style.bold and ac in info.charcodes_b:
            # bold text
            infoSize, infoOrigin, infoWidth = (
                info.size_b, info.origin_b, info.width_b)
        
        # Find position in texture, normalized to texture coordinates        
        x1 = infoOrigin[ac,0]
        x2 = x1 + infoSize[ac,0]        
        tmp = float(info.data.shape[1])
        self.s1, self.s2 = (x1) / tmp, (x2-1) / tmp
        y1 = infoOrigin[ac,1]
        y2 = y1 + infoSize[ac,1]
        tmp = float(info.data.shape[0])
        self.t1, self.t2 = (y1) / tmp, (y2-1) / tmp
        
        # Define skew factor to handle italics correctly
        self.skewFactor = 0.0
        if style.italic:
            self.skewFactor = 0.5
        
        # calculate width on screen, given the size
        factor = size / float(info.fontsize)
        self.sizex = infoSize[ac,0] * factor
        self.sizey = infoSize[ac,1] * factor        
        self.width = float(infoWidth[ac]) * factor # is spacing?
        
        smaller = 0.6
        self.dy = 0.0 # normal script        
        if style.script == 1:
            # sub script            
            self.dy = (1-smaller) * self.sizey        
        if style.script:
            # super or subscript
            self.skewFactor *= smaller
            self.sizex = self.sizex * smaller
            self.sizey = self.sizey * smaller
            self.width = self.width * smaller#- self.sizex * (1.0-smaller)


class MiniStyle:
    """ MiniStyle(script=0, bold=False, italic=False)
    
    Class that represents the style of characters (sub/super script,
    bold, and italic. Used when compiling the text.
    script = {0:'normal', 1:'sub', 2:'super'}
    
    """
    
    def __init__(self, script=0, bold=False, italic=False):
        self.script = script
        self.bold = bold
        self.italic = italic
    
    def __add__(self, other):
        # allow None
        if other is None:
            return self
        # set script
        script = other.script
        if script == 0:
            script = self.script
        # done
        return MiniStyle(   script, 
                            self.bold or other.bold, 
                            self.italic or other.italic )
    
    def __repr__(self):
        tmp = self.script, self.bold, self.italic
        return '<MiniStyle script:%i, bold:%i, italic:%i>' % tmp

