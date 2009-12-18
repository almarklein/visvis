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

""" Module base

Defines the Wibject and Wobject classes, and some other 
(relatively small classes). 

More complex datatypes (like Line and Texture)
are defined in seperate modules.

$Author$
$Date$
$Rev$

"""

import OpenGL.GL as gl
import OpenGL.GL.ARB.shader_objects as gla
import OpenGL.GLU as glu

import numpy as np
import math, time

from misc import Property, Range, OpenGLError, Position, Transform_Base
from misc import Transform_Translate, Transform_Scale, Transform_Rotate
from misc import getColor
from events import *

# get opengl version
_glVersion=[None]
def getGlVersion():
    """ getGlVersion()
    Get openGl version on this system. Note that this function will only
    return something of an openGl context is active. """
    if not _glVersion[0]:
        _glVersion[0] = gl.glGetString(gl.GL_VERSION)
    return _glVersion[0]

class BaseObject(object):
    """ The base class for wibjects and wobjects.
    Instances of classes inherited from this class represent 
    something that can be drawn. 
    
    Wibjects and wobjects can have children and have a parent 
    (which can be None in which case they are in orphan and never 
    drawn). To change the structure, use the ".parent" property. 
    They also can be set visible/invisible using the property ".visible". 
    """
    
    def __init__(self, parent):
        # whether or not to draw the object
        self._visible = True
        # whether the object can be clicked
        self._hitTest = False
        # the parent object
        self._parent = None        
        # the children of this object
        self._children = []
        # the id of this object (can change on every draw)
        # used to determine over which object the mouse is.
        self._id = 0
        
        # set parent
        self.parent = parent
        
        # create events
        self._eventEnter = EventEnter(self)
        self._eventLeave = EventLeave(self)
        self._eventMouseDown = EventMouseDown(self)        
        self._eventDoubleClick = EventDoubleClick(self)
    
    @property
    def eventEnter(self):
        return self._eventEnter
    @property
    def eventLeave(self):
        return self._eventLeave
    @property
    def eventMouseDown(self):
        return self._eventMouseDown
    @property
    def eventDoubleClick(self):
        return self._eventDoubleClick
    
    
    def _DrawTree(self, mode='normal', pickerHelper=None):
        """ Draw the wibject/wobject and all of its children. 
        shape can be an ObjectPickerHelper instance in which
        case only shape is drawn. 
        """
        # only draw if visible
        if not self.visible:
            return
        # transform
        gl.glPushMatrix()
        self._Transform()
        # draw self        
        if mode=='shape':
            if self.hitTest:
                clr = pickerHelper.GetColorFromId(self._id)
                self.OnDrawShape(clr)
        elif mode=='screen':
            self.OnDrawScreen()            
        elif mode=='fast':
            self.OnDrawFast()
        elif mode=='normal':
            self.OnDraw()
        else:
            raise Exception("Invalid mode for _DrawTree.")        
        # draw children
        for item in self._children:
            if hasattr(item, '_DrawTree'):
                item._DrawTree(mode,pickerHelper)
                
        # transform back
        gl.glPopMatrix()
    
    
    def Destroy(self):
        """ Destroy()
        Destroy the object.
        - Removes itself from the parent's children
        - Calls DestroyGl() on all its children
        - Calls Destroy() on all its children
        - Calls OnDestroy on itself
        Note1: do not overload, overload OnDestroy()
        Note2: it's best not to reuse destroyed objects. To temporary disable
        an object, better use "ob.parent=None", or "ob.visible=False".
        """
        # We must make this the current OpenGL context because OnDestroy 
        # methods of objects may want to remove textures etc.
        # When you do not do this, you can get really weird bugs.
        # This works nice, the children will not need to do this,
        # as when they try, THIS object is already detached and fig is None.
        fig = self.GetFigure()
        if fig:
            fig._SetCurrent()
        # leave home (using the property causes recursion)        
        if hasattr(self._parent, '_children'):
            while self in self._parent._children:
                self._parent._children.remove(self)                
        if hasattr(self._parent, '_wobjects'):
            while self in self._parent._wobjects:
                self._parent._wobjects.remove(self)
        self._parent = None
        # destroy children
        for child in self._children:
            child.Destroy()
        # clean up
        self.OnDestroy()
    
    
    def DestroyGl(self, setContext=True):
        """ DestroyGl() 
        Destroy the OpenGl objects managed by this object.
        - Calls DestroyGl() on all its children.
        - Calls OnDestroyGl() on itself.
        Note: do not overload, overload OnDestroyGl()
        """
        
        # make the right openGlcontext current
        if setContext:
            fig = self.GetFigure()
            if fig:
                fig._SetCurrent()
        # let children clean up their openGl stuff
        for child in self._children:
            child.DestroyGl(False)
        # clean up our own bits
        self.OnDestroyGl()
    
    
    def __del__(self):
        self.Destroy()
    
    
    def _Transform(self):
        """ Add transformations to modelview matrix such that the object
        is displayed properly. """
        pass # implemented diffently by the wibject and wobject class
    
    
    def OnDraw(self):
        """ Perform the opengl commands to draw this wibject/wobject. """    
        pass
    
    def OnDrawFast(self):
        """ Implement this to provide a faster version to draw (but
        less pretty), which is called when the scene is zoomed/translated.
        By default, this calls OnDraw()
        """
        self.OnDraw()    
    
    def OnDrawShape(self, color):
        """ Perform  the opengl commands to draw the shape of the object
        in the given color. 
        If not implemented, the object cannot be picked.
        """
        pass
    
    def OnDrawScreen(self):
        """ Draw in screen coordinates. To be used for wobjects that
        need drawing in screen coordinates (like text). Wibjects are 
        always drawn in screen coordinates (using OnDraw)."""
        pass
        
    def OnDestroy(self):
        """ Overload this to clean up any resources other than the GL objects. 
        """
        pass 
    
    def OnDestroyGl(self):
        """ Overload this to clean up any OpenGl resources. 
        """
        pass 
    
    @Property
    def visible():
        """ Set whether the object should be drawn or not. """
        def fget(self):
            return self._visible
        def fset(self, value):
            self._visible = bool(value)
    
    @Property
    def hitTest():
        """ Set whether the object can be clicked. """
        def fget(self):
            return self._hitTest
        def fset(self, value):
            self._hitTest = bool(value)
    
    
    @Property
    def parent():
        """ Get/Set the parent of this object.
        Be aware than when changing the parent to an object
        of another figure (i.e. an other OpenGL context) this
        might go wrong for some objects.
        """
        def fget(self):
            return self._parent
        def fset(self,value):
            
            # init lists to update
            parentChildren = None
            if hasattr(value, '_children'):
                parentChildren = value._children
            
            # check if this is a valid parent
            tmp = "Cannot change to that parent, "
            if value is None:
                # an object can be an orphan
                pass 
            elif value is self:
                # an object cannot be its own parent
                raise TypeError(tmp+"because that is the object itself!")
            elif isinstance(value, Wibject):
                # some wibject parents can hold wobjects
                if isinstance(self, Wobject):
                    if hasattr(value, '_wobjects'):
                        parentChildren = value._wobjects
                    else:
                        tmp2 = "a wobject can only have a wibject-parent "
                        raise TypeError(tmp+tmp2+"if it can hold wobjects!")
            elif isinstance(value, Wobject):
                # a wobject can only hold wobjects
                if isinstance(self, Wibject):
                    raise TypeError(tmp+"a wibject cant have a wobject-parent!")
            else:            
                raise TypeError(tmp+"it is not a wibject or wobject or None!")
            
            # remove from parents childrens list 
            if hasattr(self._parent, '_children'):
                while self in self._parent._children:
                    self._parent._children.remove(self)                
            if hasattr(self._parent, '_wobjects'):
                while self in self._parent._wobjects:
                    self._parent._wobjects.remove(self)
            
            # Should we destroy GL objects (because we are removed 
            # from an OpenGL context)? 
            figure1 = self.GetFigure()
            figure2 = None
            if hasattr(value, 'GetFigure'):
                figure2 = value.GetFigure()
            if figure1 and (figure1 is not figure2):
                self.DestroyGl()
            
            # set and add to new parent
            self._parent = value
            if parentChildren is not None:
                parentChildren.append(self)
    
    
    @property
    def children(self):
        """ children
        Get a shallow copy of the list of children. 
        """
        return [child for child in self._children]
    
    
    def GetFigure(self):
        """ Get the figure that this object is part of.
        The figure represents the OpenGL context.
        Returns None if it has no figure.
        """ 
        # init
        iter = 0
        object = self
        # search
        while hasattr(object,'parent'):
            iter +=1
            if object.parent is None:
                break
            if iter > 100:
                break
            object = object.parent
        # check
        if object.parent is None and hasattr(object, '_SwapBuffers'):
            return object
        else:
            return None


class Wibject(BaseObject):
    """ A visvis.Wibject (widget object) is a 2D object drawn in 
    screen coordinates. A Figure is a widget and so is an Axes or a 
    Legend. Using their structure, it is quite easy to build widgets 
    from the basic components. Wibjects have a position property to 
    set their location and size. They also have a background color 
    and multiple event attributes.
    
    This class may also be used as a container object for other wibjects.    
    """
    
    def __init__(self, parent):
        BaseObject.__init__(self, parent)
        
        # the position of the widget within its parent        
        self._position = Position( 10,10,50,50 )
        self._position._owner = self
        
        # colors and edge
        self._bgcolor = (0.8,0.8,0.8)
        
        # event for position
        self._eventPosition = EventPosition(self)
    
    
    @property
    def eventPosition(self):
        return self._eventPosition
    
    
    @Property
    def position():
        """ See docs of visvis.Position. 
        You can also give a 2-element tuple or list to only change
        the location (and maintain the size).
        """
        def fget(self):
            return self._position
        def fset(self, value):
            # allow setting x and y only
            if isinstance(value,(tuple,list)) and len(value) == 2:
                value = value[0], value[1], self._position.w, self._position.h
            # set!
            self._position = Position(value)
            # setting the owner is important to be able to
            # calculate the position in pixels, as we need
            # the parent for that!
            self._position._owner = self
            # notify the change
            self.eventPosition.Fire()
    
    
    @Property
    def bgcolor():
        """ Get/Set the background color of the wibject. """
        def fget(self):
            return self._bgcolor
        def fset(self, value):
            self._bgcolor = getColor(value, 'setting bgcolor')
    
    
    def GetSize(self):
        """ Return the size in pixels. """
        tmp = self.position.InPixels()
        return tmp.w, tmp.h
    
    
    def RelativeToAbsolute(self, *xy):
        """ Transform the given x-y coordinates from this wibject's
        relative coordinates to absolute figure coordinates. """
        if len(xy)==1:
            xy = xy[0]
        if self.parent:
            x,y = self.parent.RelativeToAbsolute(*xy)
            tmp = self.position.InPixels()
            return x+tmp.x, y+tmp.y
        else:
            return xy[0], xy[1]
    
    
    def AbsoluteToRelative(self, *xy):
        """ Transform the given x-y coordinates from absolute figure
        coordinates to this object's relative coordinates. """
        if len(xy)==1:
            xy = xy[0]        
        if self.parent:
            x,y = self.parent.AbsoluteToRelative(*xy)
            tmp = self.position.InPixels()
            return x-tmp.x, y-tmp.y
        else:
            return xy[0], xy[1]
    
    
    def _Transform(self):
        """ Apply a translation such that the wibject is 
        drawn in the correct place. """
        # skip if we are on top
        if not self.parent:
            return            
        # get posision in screen coordinates
        pos = self.position.InPixels()
        # apply
        gl.glTranslatef(pos.x,pos.y,0.0)


    def OnDrawShape(self, clr):
        """ Implementation of the OnDrawShape method.
        Defines the wibject's shape as a rectangle specified
        by position.
        """
        gl.glColor(clr[0], clr[1], clr[2], 1.0)
        w,h = self.GetSize()
        gl.glBegin(gl.GL_POLYGON)
        gl.glVertex2f(0,0)
        gl.glVertex2f(0,h)
        gl.glVertex2f(w,h)
        gl.glVertex2f(w,0)
        gl.glEnd()


class Wobject(BaseObject):
    """ A visvis.Wobject (world object) is a visual element that 
    is drawn in 3D world coordinates (in the scene). Wobjects can be 
    children of other wobjects or of an Axes object (which is a 
    wibject). 
    
    To each wobject, several transformations can be applied, 
    which are also applied to its children. This way complex models can 
    be build. For example in a robot arm the fingers would be children 
    of the hand, so if the hand moves or rotates, the fingers move along 
    automatically. The fingers can then also be moved without affecting 
    the hand or other fingers. 
    
    The transformations are represented by Transform_* objects in 
    the list named .transformations. The transformations are applied
    in the order as they appear in the list. Note that this means
    you probably want the order reversed.
    """
    
    def __init__(self, parent):
        BaseObject.__init__(self, parent)
        
        # the transformations applied to the object
        self.transformations = []
    
    
    def GetAxes(self):
        par = self.parent
        if par is None:
            return None# raise TypeError("Cannot find axes!")
        while not isinstance(par, Wibject):            
            par = par.parent
            if par is None:
                return None
                #tmp = "Cannot find axes, error in Wobject/Wibject tree!"
                #raise TypeError(tmp)
        return par

    
    def _Transform(self):
        """ Apply all listed transformations of this wobject. """        
        for t in self.transformations:
            if not isinstance(t, Transform_Base):
                continue
            elif isinstance(t, Transform_Translate):
                gl.glTranslate(t.dx, t.dy, t.dz)
            elif isinstance(t, Transform_Scale):
                gl.glScale(t.sx, t.sy, t.sz)
            elif isinstance(t, Transform_Rotate):
                gl.glRotate(t.angle, t.ax, t.ay, t.az)



## More simple wibjects and wobjects
# box must be defined here as it is used by textRender.Label
    
class Box(Wibject):
    """ A simple, multi-purpose, rectangle object.
    """
    def __init__(self, parent):
        Wibject.__init__(self, parent)
        self._edgeColor = (0,0,0)
        self._edgeWidth = 1.0
    
    @Property
    def edgeColor():
        """ Get/Set the edge color of the wibject. """
        def fget(self):
            return self._edgeColor
        def fset(self, value):
            self._edgeColor = getColor(value, 'setting edgeColor')
    
    @Property
    def edgeWidth():
        """ Get/Set the edge width of the wibject. """
        def fget(self):
            return self._edgeWidth
        def fset(self, value):            
            self._edgeWidth = float(value)
    
    def OnDraw(self, fast=False):
        
        # get dimensions        
        w,h = self.GetSize()
        
        # draw plane
        if self._bgcolor:        
            clr = self.bgcolor
            gl.glColor(clr[0], clr[1], clr[2], 1.0)            
            #
            gl.glBegin(gl.GL_POLYGON)
            gl.glVertex2f(0,0)
            gl.glVertex2f(0,h)
            gl.glVertex2f(w,h)
            gl.glVertex2f(w,0)
            gl.glEnd()
        
        # prepare                
        gl.glDisable(gl.GL_LINE_SMOOTH)
        
        # draw edges        
        if self.edgeWidth and self.edgeColor:
            clr = self.edgeColor
            gl.glColor(clr[0], clr[1], clr[2], 1.0)
            gl.glLineWidth(self.edgeWidth)
            #
            gl.glBegin(gl.GL_LINE_LOOP)
            gl.glVertex2f(0,0)
            gl.glVertex2f(0,h)
            gl.glVertex2f(w,h)
            gl.glVertex2f(w,0)
            gl.glEnd()
        
        # clean up        
        gl.glEnable(gl.GL_LINE_SMOOTH)