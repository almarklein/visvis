# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


import OpenGL.GL as gl
import OpenGL.GLU as glu

import numpy as np

import visvis
#
from visvis.core.baseTexture import TextureObject
from visvis.core.base import Wobject
from visvis.core.misc import Property, PropWithDraw, basestring, unichr 
from visvis.core.misc import getResourceDir, getColor
#
from visvis.core.cameras import depthToZ
from visvis.core.baseWibjects import Box


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
    'leq':0x2264, 'geq':0x2265, 'approx':0x2248, 'approxeq':0x2243, 'ne':0x2260,
    'in':0x2208,
    'leftarrow':0x2190,'uparrow':0x2191,'rightarrow':0x2192,'downarrow':0x2193,
    'Leftarrow':0x21D0,'Uparrow':0x21D1,'Rightarrow':0x21D2,'Downarrow':0x21D3,
    'leftceil':0x2308,'rightceil':0x2309,'leftfloor':0x230A,'rightfloor':0x230B,
    'times':0x00d7, 'cdot':0x2219, 'pm':0x00b1,
    'oplus':0x2295, 'ominus':0x2296, 'otimes':0x2297, 'oslash':0x2298,     
    }

# sort the keys, such that longer names are replaced first
escapesKeys = list(escapes.keys())
escapesKeys.sort( key=len, reverse=True)



class AtlasTexture(TextureObject):
    """ Class to represent a texture that contains characters.
    """
    
    def __init__(self):
        TextureObject.__init__(self, 2)
    
    def _UploadTexture(self, data, *args):
        """ Overload to make it an alpha map. 
        """
        
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




class FontManager(object):
    """ The font manager is a class that can generate text.
    There is one fontmanager per context (i.e. Figure).
    """
    
    def ConvertEscapedText(self, tt):
        tt = tt.replace(r'\\', unichr(0))
        # Catch valid escape codes that were supposed to be greek letters 
        # (a b f n r t v)
        tt = tt.replace('\alpha', unichr(escapes['alpha']))
        tt = tt.replace('\beta', unichr(escapes['beta']))
        tt = tt.replace('\null', unichr(escapes['null']))
        tt = tt.replace('\nu', unichr(escapes['nu']))
        tt = tt.replace('\rho', unichr(escapes['rho']))
        tt = tt.replace('\theta', unichr(escapes['theta']))
        tt = tt.replace('\tau', unichr(escapes['tau']))
        tt = tt.replace('\forall', unichr(escapes['forall']))
        tt = tt.replace('\approxeq', unichr(escapes['approxeq']))
        tt = tt.replace('\approx', unichr(escapes['approx']))
        tt = tt.replace('\ne', unichr(escapes['ne']))
        tt = tt.replace('\rightarrow', unichr(escapes['rightarrow']))
        tt = tt.replace('\rightceil', unichr(escapes['rightceil']))
        tt = tt.replace('\rightfloor', unichr(escapes['rightfloor']))
        tt = tt.replace('\times', unichr(escapes['times']))
        for c in escapesKeys:
            tt = tt.replace('\\'+c, unichr(escapes[c]))
        # get italic and bold modifiers
        tt = tt.replace('\i', '\x06') # just use some char that is no string
        tt = tt.replace('\b', '\x07') # Note that '\i' == r'\i', but '\b' != r'\b'
        tt = tt.replace(r'\b', '\x07')
        tt = tt.replace(unichr(0), r'\\')
        return tt
    
    
    def GetFont(self, fontName, fontSize, bold=False, italic=False):
        """ Returns something that Compile() can work with.
        """
        raise NotImplementedError()
    
    def Compile(self, textObject):
        pass
    
    def Position(self, textObject):
        if textObject._texCords1 is None or textObject._vertices1 is None:
            self.Compile(textObject)
    
    def Draw(self, textObject, x=0, y=0, z=0):
        if textObject._texCords2 is None or textObject._vertices2 is None:
            self.Position(textObject)
    


class BaseText(object):
    """ BaseText(text='', fontName=None, fontSize=9, color='k')
    
    Base object for the Text wobject and Label wibject.
    fontname may be 'mono', 'sans', 'serif' or None, in which case
    the vv.settings.defaultFontName is used.
    """
    
    # The idea is that the FontManager produces the _texCords and _vertices1
    # for this object in its Compile method. In its Position method it 
    # will create _verticices 
    def __init__(self, text='', fontName=None, fontSize=9, color='k'):
        
        # Check fontname
        if fontName is None:
            fontName = visvis.settings.defaultFontName
        
        # Store arguments
        self._text = text
        self._fontName = fontName.lower()
        self._fontSize = fontSize
        self._color = None
        self.textColor = color
        
        # Set more parameters
        self._halign = -1
        self._valign = 0
        self._angle = 0
        
        # The data used for drawing. 
        # 1) The preliminary (relative) vertex coordinates
        # 2) The final (absolute) vertex coordinates
        self._texCords1 = None
        self._texCords2 = None 
        self._vertices1 = None 
        self._vertices2 = None
        
        # Try getting the font manager now
        self._lastFontManager = None
        self._GetFontManager()
    
    
    def _GetFontManager(self):
        """ Convienence function to obtain a reference to the font manager.
        The font manager is stored at the figure; there is one font 
        manager per OpenGl contex.
        """
        fig = self.GetFigure()
        if fig:
            self._lastFontManager = fig._fontManager
        return self._lastFontManager
    
    
    def Invalidate(self):
        """ Invalidate this object, such that the text is recompiled
        the next time it is drawn. 
        """
        self._texCords1 = None
        self._texCords2 = None
        self._vertices1 = None
        self._vertices2 = None
    
    def _SetInitialData(self, texCords, vertices):
        self._texCords1 = texCords
        self._vertices1 = vertices
    
    def _GetInitialData(self):
        return self._texCords1, self._vertices1
    
    def _SetFinalData(self, texCords, vertices):
        self._texCords2 = texCords
        self._vertices2 = vertices
    
    
    def _GetFinalData(self):
        return self._texCords2, self._vertices2
    
    
    def GetVertexLimits(self):
        """ Get the limits of the vertex data.
        Returns (xmin, xmax), (ymin, ymax)
        """
        # Make sure we have vertices
        if self._vertices2 is None:
            self.UpdatePosition()
        vertices = self._vertices2
        # Return the limits or a dummy
        if vertices is not None and len(vertices):
            deltax = vertices[:,0].min(), vertices[:,0].max()
            deltay = vertices[:,1].min(), vertices[:,1].max() 
            return deltax, deltay
        else:
            return (0,0), (0,0)
        
    
    def UpdatePosition(self, *args):
        """ Updates the position now, Compiles the text if necessary.
        """ 
        fm = self._GetFontManager()
        if fm:
            fm.Position(self) # Calls Compile() if necessary
    
    @property
    def isCompiled(self):
        return self._vertices1 is not None and len(self._vertices1)
    
    @property
    def isPositioned(self):
        return self._vertices2 is not None and len(self._vertices2)
    
    
    @Property # Smart draw
    def text():
        """Get/Set the text to display. 
        """
        def fget(self):
            return self._text
        def fset(self, value):
            if value != self._text:
                self._text = value
                self.Invalidate() # force recalculation
                self.Draw()
        return locals()
    
    
    @Property  # Smart draw
    def textAngle():
        """Get/Set the angle of the text in degrees.
        """
        def fget(self):
            return self._angle
        def fset(self, value):
            if value != self._angle:
                self._angle = value
                self._vertices2 = None # force recalculation
                self.Draw()
        return locals()
    
    
    # todo: remove in future version
    @Property
    def textSpacing():
        """Get/Set the spacing between characters.
        """
        def fget(self):
            print('textSpacing property is deprecated.')
            return 1
        def fset(self, value):
            print('textSpacing property is deprecated.')
        return locals()
    
    
    @Property
    def fontSize():
        """Get/Set the size of the text.
        """
        def fget(self):
            return self._fontSize
        def fset(self, value):
            if value != self._fontSize:
                self._fontSize = value
                self.Invalidate() # force recalculation
                self.Draw()
        return locals()
    
    
    @Property
    def fontName():
        """Get/Set the font type by its name.
        """
        def fget(self):
            return self._fontName
        def fset(self, value):
            if value != self._fontName:
                self._fontName = value
                self.Invalidate() # force recalculation
                self.Draw()
        return locals()
    
    
    @Property
    def textColor():
        """Get/Set the color of the text.
        """
        def fget(self):
            return self._color
        def fset(self, value):
            value = getColor(value,'setting textColor')
            if value != self._color:
                self._color = value
                self.Draw()
        return locals()
    
    
    @Property
    def halign():
        """Get/Set the horizontal alignment. Specify as:
          * 'left', 'center', 'right'
          * -1, 0, 1
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
        return locals()
    
    
    @Property
    def valign():
        """Get/Set the vertical alignment. Specify as:
          * 'up', 'center', 'down'
          * 'top', 'center', 'bottom'
          * -1, 0, 1
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
        return locals()



# Label and Text class must be defined here because we need to be able
# to do isinstance() in some methods of Font Managers.

class Text(Wobject, BaseText):
    """ Text(parent, text='', x=0, y=0, z=0, fontName=None, fontSize=9, color='k')
    
    A wobject representing a string of characters. The text has 
    a certain position in the scene. The fontname can be
    'mono', 'sans' or 'serif'. If not given, the vv.settings.defaultFontName
    is used.
    
    """
    
    def __init__(self, parent, text='', x=0, y=0, z=0,
                            fontName=None, fontSize=9, color='k'):
        Wobject.__init__(self, parent)
        BaseText.__init__(self, text, fontName, fontSize, color)
        
        # store coordinates
        self._x, self._y, self._z = x, y, z
        
        # for internal use
        self._screenx, self._screeny, self._screenz = 0, 0, 0
    
    
    @PropWithDraw
    def x():
        """Get/Set the x position of the text.
        """
        def fget(self):
            return self._x
        def fset(self, value):
            self._x = value
        return locals()
    
    @PropWithDraw
    def y():
        """Get/Set the y position of the text.
        """
        def fget(self):
            return self._y
        def fset(self, value):
            self._y = value
        return locals()
    
    @PropWithDraw
    def z():
        """Get/Set the z position of the text.
        """
        def fget(self):
            return self._z
        def fset(self, value):
            self._z = value
        return locals()
    
    
    def OnDraw(self):
        # get screen position and store
        tmp = glu.gluProject(self._x, self._y, self._z)        
        self._screenx, self._screeny, self._screenz = tuple(tmp)
#         # make integer (to prevent glitchy behaviour), but not z!
#         self._screenx = int(self._screenx+0.5)
#         self._screeny = int(self._screeny+0.5)
    
    
    def OnDrawScreen(self):
        fm = self._GetFontManager()
        if fm:
            fm.Draw(self,
                    self._screenx, self._screeny, depthToZ(self._screenz) )



class Label(Box, BaseText):    
    """ Label(parent, text='', fontName=None, fontSize=9, color='k')
    
    A wibject (inherits from box) with text inside. 
    The fontname can be 'mono', 'sans' or 'serif'. If not given, the 
    vv.settings.defaultFontName is used.
    
    """
    
    def __init__(self, parent, text='', fontName=None, fontSize=9, color='k'):
        Box.__init__(self, parent)
        BaseText.__init__(self, text, fontName, fontSize, color)
        
        # no edge        
        self.edgeWidth = 0
        
        # init position (this is to set the size)
        self.position = 10,10,100,16
        
        # we need to know about position changes to update alignment
        self.eventPosition.Bind(self.UpdatePosition)
    
    
    def OnDraw(self):
        
        # Draw the box
        Box.OnDraw(self)
        
        # Draw the text
        fm = self._GetFontManager()
        if fm:
            fm.Draw(self)
