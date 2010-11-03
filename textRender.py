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
#   Copyright (C) 2010 Almar Klein

""" Module textRender

For rendering text in visvis.
Produces a wibject and a wobject: Label and Text,
which are both able to produce a single line of text
oriented at a certain angle.

Characters are available for the following unicode sets:
u0020 - u003f  numbers
u0040 - u00bf  alphabet
u00c0 - u037f  latin
u0380 - u03ff  greek
u2000 - u23ff  symbols

Text can be formatted using the following constructs (which can be mixed):
hello^2 or hello^{there}, makes one or more charactes superscript.
hello_2 or hello_{there}, makes one or more charactes subscript.
hell\io or hell\i{ohoo}, makes one or more charactes italic.
hell\bo or hell\b{ohoo}, makes one or more charactes bold.
hello\_there,  a backslash escapes, thus keeping the _^ or \ after it.

There are several escape sequences for (mathematical) characters
that can be inserted using the backslash (for example '\infty').
People familiar with Latex know what they do:
Re          Im          null        infty
int         iint        iiint       forall
leq         geq         approx      approxeq        ne          in
leftarrow   uparrow     rightarrow  downarrow
Leftarrow   Uparrow     Rightarrow  Downarrow
leftceil    rightceil   leftfloor   rightfloor
times       cdot        pm
oplus       ominus      otimes      oslash

Note: In case one needs a character that is not in this list, 
one can always look up its unicode value and use that instead.

Letters from the greek alfabet can be inserted in the same 
way (By starting the name with an uppercase letter, the
corresponding upper case greek letter is inserted):
alpha       beta        gamma       delta
epsilon     zeta        eta         theta
iota        kappa       lambda      mu
nu          xi          omicron     pi
rho         varsigma    sigma       tau
upsilon     phi         chi         psi
omega
    
"""


import os
import ssdf
from points import Point, Pointset

import OpenGL.GL as gl
import OpenGL.GLU as glu
import numpy as np

from textures import TextureObject
from base import Wobject, Wibject, Box
from misc import Property, PropWithDraw, DrawAfter 
from misc import getResourceDir, getColor
from cameras import depthToZ

class TextException(Exception):
    pass


escapes = {
    # upper case greek
    'Alpha':0x0391, 'Beta':0x0392, 'Gamma':0x0393, 'Delta':0x0394, 
    'Epsilon':0x0395, 'Zeta':0x0396, 'Eta':0x0397, 'Theta':0x0398, 
    'Iota':0x0399, 'Kappa':0x039A, 'Lambda':0x039B, 'Mu':0x039C, 
    'Nu':0x039D, 'Xi':0x039E, 'Omicron':0x039F, 
    'Pi':0x03A0, 'Rho':0x03A1,             'Sigma':0x03A3, 'Tau':0x03A4, 
    'Upsilon':0x03A5, 'Phi':0x03A6, 'Chi':0x03A7, 'Psi':0x03A8, 'Omega':0x03A9,
    # lower case greek
    'alpha':0x03B1, 'beta':0x03B2, 'gamma':0x03B3, 'delta':0x03B4, 
    'epsilon':0x03B5, 'zeta':0x03B6, 'eta':0x03B7, 'theta':0x03B8, 
    'iota':0x03B9, 'kappa':0x03BA, 'lambda':0x03BB, 'mu':0x03BC, 
    'nu':0x03BD, 'xi':0x03BE, 'omicron':0x03BF, 
    'pi':0x03C0, 'rho':0x03C1, 'varsigma':0x03C2, 'sigma':0x03C3, 
    'tau':0x03C4, 'upsilon':0x03C5,
    'phi':0x03C6, 'chi':0x03C7, 'psi':0x03C8, 'omega':0x03C9,
    # some math
    'Re':0x211c, 'Im':0x2111, 'null':0x2300, 'infty':0x221e, 
    'int':0x222b, 'iint':0x222c, 'iiint':0x222d, 
    'forall':0x2200,
    'leq':0x22dc, 'geq':0x22dd, 'approx':0x2248, 'approxeq':0x2243, 'ne':0x2260,
    'in':0x22f9,
    'leftarrow':0x2190,'uparrow':0x2191,'rightarrow':0x2192,'downarrow':0x2193,
    'Leftarrow':0x21D0,'Uparrow':0x21D1,'Rightarrow':0x21D2,'Downarrow':0x21D3,
    'leftceil':0x2308,'rightceil':0x2309,'leftfloor':0x230A,'rightfloor':0x230B,
    'times':0x2217, 'cdot':0x2219, 'pm':0x00b1,
    'oplus':0x2295, 'ominus':0x2296, 'otimes':0x2297, 'oslash':0x2298,     
    }

# sort the keys, such that longer names are replaced first
escapesKeys = escapes.keys()
escapesKeys.sort( lambda x,y:len(y)-len(x))


class Font(TextureObject):
    """ A Font object holds the texture that contains all the
    characters. """
    
    def __init__(self, info):
        TextureObject.__init__(self, 2)
        
        # store font information
        self.info = info
        
        # set data
        self.SetData(self.info.data)
    
    def _UploadTexture(self, data, *args):
        """ Overload to make it an alpha map. """
        
        # Add lumincance channel
        data2 = np.zeros((data.shape[0],data.shape[1],2), dtype=np.uint8)
        data2[:,:,0] = 255
        data2[:,:,1] = data
        
        shape = data.shape
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, 2, shape[1],shape[0], 0,
        #    gl.GL_ALPHA, gl.GL_UNSIGNED_BYTE, data)
            gl.GL_LUMINANCE_ALPHA, gl.GL_UNSIGNED_BYTE, data2)
        
        tmp1 = gl.GL_LINEAR
        tmp2 = gl.GL_LINEAR
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, tmp1)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, tmp2)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)



class FontManager:
    """ Manager of fonts. 
    There should be only one instance of this class for each figure/context. 
    """
    
    def __init__(self):
        # load font data
        path = getResourceDir()
        self.s = ssdf.load(os.path.join(path, 'fonts.ssdf'))
        
        # list of fonts
        self.fonts = {}
        
    def GetFont(self, fontname):
        """ Get a font instance. If that font was created earlier,
        that font is returned, otherwise it is created and stored
        for reuse. """
        if fontname in self.fonts:
            return self.fonts[fontname]
        elif hasattr(self.s, fontname):
            tmp = Font(self.s[fontname])
            self.fonts[fontname] = tmp
            return tmp
        else:
            raise ValueError("Invalid font name.")


class Glyph(object):
    """ A glyph is a character. It is visualized by rendering
    the proper part from the texture stored in the Font object.
    sizex, sizey - Represent the size of the glyph
    dy - offset in y direction (for sub/super scripts)
    width - specifies how much space there should be before the next char
            is printed.
    s1 s2 t1 t2 - Represent texture coordinates
    
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
        
        # store font
        self.font = font
        info =  self.font.info
        
        # get asci code and check it
        if isinstance(char, basestring):
            ac = ord(char)
        elif isinstance(char, int):
            ac = char
        else:
            raise ValueError('To create a glyph, supply an int or character.')
        
        # do we have that char?
        if ac not in info.charcodes:#ac < 32 or ac > 255:
            print "Warning: Cannot draw character %i! " % ord(char)
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
    """ Class that represents the style of characters (sub/super script,
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



class BaseText(object):
    """ Base object for the Text wobject and Label wibject.
    fontname may be 'mono', 'sans', or 'serif'.
    """
    
    def __init__(self, text='', fontname='sans'):        
        
        # init drawing data        
        self._texCords = None  # coords in the font texture
        self._vertices1 = None  # the coords in screen coordinates (raw)
        self._vertices2 = None  # dito, but corrected for angle and alignment
        
        # relative position of edges in pixels. (taking angle into account)
        self._deltax = 0,0
        self._deltay = 0,0
        
        # store text
        self._text = text
        
        # more properties
        self._size = 9
        self._fontname = fontname
        self._color = (0,0,0)
        self._angle = 0
        self._halign = -1
        self._valign = 0
        self._charSpacing = 1
    
    
    def _Invalidate(self):
        """ Invalidate this object, such that the text is recompiled
        the next time it is drawn. """
        self._texCords = None
        self._vertices1 = None
        self._vertices2 = None
    
    
    @Property # Smart draw
    def text():
        """Get/Set the text to display. """
        def fget(self):
            return self._text
        def fset(self, value):
            if value != self._text:
                self._text = value
                self._Invalidate() # force recalculation
                self.Draw()
    
    
    @Property  # Smart draw
    def textAngle():
        """Get/Set the angle of the text in degrees."""
        def fget(self):
            return self._angle
        def fset(self, value):
            if value != self._angle:
                self._angle = value
                self._vertices2 = None # force recalculation
                self.Draw()
    
    
    @Property
    def textSpacing():
        """Get/Set the spacing between characters."""
        def fget(self):
            return self._charSpacing  
        def fset(self, value):
            if value != self._charSpacing:
                self._charSpacing = value
                self._Invalidate() # force recalculation
                self.Draw()
    
    
    @Property
    def fontSize():
        """Get/Set the size of the text."""
        def fget(self):
            return self._size
        def fset(self, value):
            if value != self._size:
                self._size = value
                self._Invalidate() # force recalculation
                self.Draw()
    
    
    @Property
    def fontName():
        """Get/Set the font type by its name."""
        def fget(self):
            return self._fontname
        def fset(self, value):
            if value != self._fontname:
                self._fontname = value
                self._Invalidate() # force recalculation
                self.Draw()
    
    
    @Property
    def textColor():
        """Get/Set the color of the text."""
        def fget(self):
            return self._color
        def fset(self, value):
            value = getColor(value,'setting textColor')
            self.Draw()
    
    
    @Property
    def halign():
        """Get/Set the horizontal alignment. Specify as:
        left, center, right, or
        -1  ,   0   , 1
        """
        def fget(self):
            return self._halign
        def fset(self, value):
            if isinstance(value, int):
                pass
            elif isinstance(value, basestring):                
                value = value.lower()
                tmp = {'left':-1,'center':0,'centre':0,'right':1 }
                if not value in tmp:
                    raise ValueError('Invalid value for halign.')
                value = tmp[value.lower()]
            else:
                raise ValueError('halign must be an int or string.')
            value = int(value>0) - int(value<0)
            if value != self._halign:
                self._halign = value
                self._vertices2 = None # force recalculation
                self.Draw()
    
    @Property
    def valign():
        """Get/Set the vertical alignment. Specify as:
        up, center, down, or
        top, center, bottom, or
        -1  ,   0   , 1
        """
        def fget(self):
            return self._valign
        def fset(self, value):
            if isinstance(value, int):
                pass
            elif isinstance(value, basestring):                
                value = value.lower()
                tmp={'up':-1,'top':-1,'center':0,'centre':0,'down':1,'bottom':1}
                if not value in tmp:
                    raise ValueError('Invalid value for valign.')
                value = tmp[value.lower()]
            else:
                raise ValueError('valign must be an int or string.')
            value = int(value>0) - int(value<0)
            if value != self._valign:
                self._valign = value
                self._vertices2 = None # force recalculation
                self.Draw()
    
    
    def _Compile(self):
        """ Create a series of glyphs from the given text. From these Glyphs
        the textureCords in the font texture can be calculated.
        Also the relative vertices are calculated, which are then corrected
        for angle and alignment in _PositionText().
        -> Produces _vertices1 (and is called when that is None)
        """
        
        # make invalid first
        self._Invalidate()
        
        # get font instance from figure
        f = self.GetFigure()
        if not f:
            return
        font = f._fontManager.GetFont(self._fontname)
        
        # clear glyphs
        glyphs = [] 
        self._xglyph = Glyph(font, 'X', self._size)     
        
        tt = self._text        
        
        # transform greek characters that were given without double backslash
        tt = tt.replace('\alpha', unichr(escapes['alpha']))
        tt = tt.replace('\beta', unichr(escapes['beta']))                
        tt = tt.replace('\rho', unichr(escapes['rho']))
        tt = tt.replace('\theta', unichr(escapes['theta']))        
        # transform other chars
        tt = tt.replace(r'\\', '\t') # double backslashes do not escape
        for c in escapesKeys:            
            tt = tt.replace('\\'+c, unichr(escapes[c]))
        tt = tt.replace('\t', r'\\')
        
        # get italic and bold modifiers
        tt = tt.replace('\i', '\x06') # just use some char that is no string
        tt = tt.replace('\b', '\x07')
        
        # build list of glyphs, take sub/super scripting into account.        
        escape = False
        styles = []
        style = None # Style to set
        for i in range(len(tt)):
            c = tt[i]            
            if escape:                
                g = Glyph(font, c, self._size, styles)
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
                g = Glyph(font, c, self._size, styles+[style])
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
            texCords.Append(g.s1, g.t1)
            texCords.Append(g.s2, g.t1)
            texCords.Append(g.s2, g.t2)
            texCords.Append(g.s1, g.t2)
            
            # set skewing for position
            skew = self._size * g.skewFactor
            
            # append vertices
            vertices.Append(x1+skew, y1+dy, z)
            vertices.Append(x2+skew, y1+dy, z)
            vertices.Append(x2, y2+dy, z)
            vertices.Append(x1, y2+dy, z)
            
            # prepare for next glyph
            x1 = x1 + g.width + self._charSpacing          
        
        # store
        self._texCords = texCords
        self._vertices1 = vertices
    
    
    def _PositionText(self, event=None):
        """ The name is ment as a verb. The vertices1 are corrected
        for angle and alignment. 
        -> produces _vertices2 from _vertices1 
           (and is called when the first is None)
        """
        
        # get figure
        fig = self.GetFigure()
        
        # get vertices
        if self._vertices1 is None:
            return
        vertices = self._vertices1.Copy()
        
        # scale text according to global text size property
        vertices *= fig._relativeFontSize
        
        # obtain dimensions
        if len(vertices):
            x1, x2 = vertices[:,0].min(), vertices[:,0].max()
        else:
            x1, x2 = 0,0
        y1, y2 = 0, self._xglyph.sizey
        
        # set anchor
        if self._halign < 0:  anchorx = x1
        elif self._halign > 0:  anchorx = x2
        else: anchorx = x1 + (x2-x1)/2.0
        #
        if self._valign < 0:  anchory = y1
        elif self._valign > 0:  anchory = y2
        else: anchory = y1 + (y2-y1)/2.0
        
        # apply anchor
        angle = self._angle
        if isinstance(self, Text):
            # Text is a wobject, so must be flipped on y axis
            vertices[:,0] = vertices[:,0] - anchorx
            vertices[:,1] = -(vertices[:,1] - anchory)
        
        elif isinstance(self, Label):
            angle = -self._angle
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
        if isinstance(self, Label):
            w,h = self.position.size
            # determine whether the text is vertical or horizontal
            halign, valign = self._halign, self._valign
            if self._angle > 135 or self._angle < -135:
                halign, valign = -halign, valign
            elif self._angle > 45:
                halign, valign = valign, -halign
            elif self._angle < -45:
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
        self._vertices2 = vertices
        
        # calculate edges (used by for example the AxisLabel class)
        if vertices is not None and len(vertices):
            self._deltax = vertices[:,0].min(), vertices[:,0].max()
            self._deltay = vertices[:,1].min(), vertices[:,1].max()
    
    
    def _DrawText(self, x=0, y=0, z=0):
        
        # Translate
        if x or y or z:
            gl.glPushMatrix()
            gl.glTranslatef(x, y, z)
        
        # make sure the glyphs are created
        if self._vertices1 is None or self._texCords is None:
            self._Compile()
        if self._vertices2 is None:
            self._PositionText()
        
        # get font instance from figure
        fig = self.GetFigure()
        if not fig:
            return
        font = fig._fontManager.GetFont(self._fontname)
        
        # enable texture
        font.Enable()
        
        # prepare
        texCords = self._texCords#.Copy()
        vertices = self._vertices2#.Copy()
        
        # init vertex and texture array
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glVertexPointerf(vertices.data)
        gl.glTexCoordPointerf(texCords.data)
        
        # draw
        if self.textColor and len(vertices):
            clr = self.textColor
            gl.glColor(clr[0], clr[1], clr[2])
            gl.glDrawArrays(gl.GL_QUADS, 0, len(vertices))
            gl.glFlush()
        
        # disable texture and clean up     
        if x or y or z:
            gl.glPopMatrix()   
        font.Disable()
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
    
    
    
class Text(Wobject, BaseText):
    """ Text(parent, text='', x=0, y=0, z=0, fontname='sans')
    A wobject representing a string of characters. The text has 
    a certain position in the scene.
    """
    
    def __init__(self, parent, text='', x=0, y=0, z=0, fontname='sans'):
        Wobject.__init__(self, parent)
        BaseText.__init__(self, text, fontname)
        
        # store coordinates
        self._x, self._y, self._z = x, y, z
        
        # for internal use
        self._screenx, self._screeny, self._screenz = 0, 0, 0
    
    
    @PropWithDraw
    def x():
        """Get/Set the x position of the text."""
        def fget(self):
            return self._x
        def fset(self, value):
            self._x = value
        
    @PropWithDraw
    def y():
        """Get/Set the y position of the text."""
        def fget(self):
            return self._y
        def fset(self, value):
            self._y = value
    
    @PropWithDraw
    def z():
        """Get/Set the z position of the text."""
        def fget(self):
            return self._z
        def fset(self, value):
            self._z = value
    
    
    def OnDraw(self):
        # get screen position and store
        tmp = glu.gluProject(self._x, self._y, self._z)        
        self._screenx, self._screeny, self._screenz = tuple(tmp)
        # make integer (to prevent glitchy behaviour), but not z!
        self._screenx = int(self._screenx+0.5)
        self._screeny = int(self._screeny+0.5)
    
    
    def OnDrawScreen(self):
        self._DrawText( self._screenx, self._screeny, depthToZ(self._screenz) )
    
    
class Label(Box, BaseText):    
    """ Label(parent, text='', fontname='sans'
    A wibject (inherits from box) with text inside. 
    """
    
    def __init__(self, parent, text='', fontname='sans'):
        Box.__init__(self, parent)
        BaseText.__init__(self, text, fontname)
        
        # no edge        
        self.edgeWidth = 0
        
        # init position (this is to set the size)
        self.position = 10,10,100,16
        
        # we need to know about position changes to update alignment
        self.eventPosition.Bind(self._PositionText)
    
    
    def OnDraw(self):
        
        # Draw the box
        Box.OnDraw(self)
        
        # Draw the text
        self._DrawText()
        