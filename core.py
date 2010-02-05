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

""" Module core

The core module that defines the BaseFigure and Axes classes.
Also helper classes for the Figure and Axes (ObjectPickerHelper, 
Legend, Axis, etc.) are defined here.

$Author$
$Date$
$Rev$

"""

import OpenGL.GL as gl
import OpenGL.GLU as glu

import time
from points import Point, Pointset
import numpy as np

import base
import simpleWibjects
import textures
from cameras import (ortho, depthToZ, TwoDCamera, PolarCamera, FlyCamera)
from misc import Property, Range, OpenGLError, getColor
from events import *
from textRender import FontManager, Text, Label
from line import MarkerManager, Line, lineStyles

# a variable to indicate whether to print FPS, for testing
printFPS = False


class ObjectPickerHelper(object):
    """ A simple class to help picking of the objects.
    An instance of this is attached to each figure. 
    """
    
    def __init__(self):
        self.bits_r, self.bits_g, self.bits_b = 8, 8, 8
        self.curid = 0
        self.screen = None  # the screenshot
    
    def GetId(self):
        """ Get an id.  """        
        self.curid += 1
        return self.curid
    
    def GetColorFromId(self,id):
        # make int to be sure
        id = int(id)
        # get factors
        fr, fg, fb = 2**self.bits_r, 2**self.bits_g, 2**self.bits_b
        # get an id for each color
        idr = id // (fg*fb)
        id  = id % (fg*fb)
        idg = id // fb
        idb = id % fb
        if idr>fr:
            # this will probably never happen
            raise Exception("Your id exceededs what you can express in color!")
        # return        
        return float(idr)/(fr-1), float(idg)/(fg-1), float(idb)/(fb-1)
    
    def GetIdFromColor(self,r,g,b):        
        # get factors        
        fr, fg, fb = 2**self.bits_r, 2**self.bits_g, 2**self.bits_b        
        idr, idg, idb = int(r*fr), int(g*fg), int(b*fb)
        #idr, idg, idb = int(r), int(g), int(b)
        id =  (idr*fg + idg)*fb + idb
        return int(id)

    
    def CaptureScreen(self, figure):
        """ Capture the screen as a numpy array to use it later to determine
        which item is under the mouse. """
        gl.glReadBuffer(gl.GL_BACK)
        xywh = gl.glGetIntegerv(gl.GL_VIEWPORT)
        x,y,w,h = xywh[0], xywh[1], xywh[2], xywh[3]
        #im = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
        #im = np.fromstring(im,dtype=np.uint8)
        im = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_FLOAT)
        # use floats to prevent strides etc. uint8 caused crash on qt backend.
        # reshape, flip, and store
        im.shape = h,w,3
        self.screen = np.flipud(im)
    
    
    def GetItemsUnderMouse(self, figure):
        """ Detect over which objects the mouse is now.
        """
        # make sure screen exists
        if self.screen is None:
            self.screen = np.zeros((1,1),dtype=np.float32)
        
        # get shape and position of mouse
        shape = self.screen.shape
        x,y = figure.mousepos
        
        # get id of the object under the mouse
        if x < 0 or x >= shape[1] or y < 0 or y >= shape[0]:
            id = 0
        else:
            clr = self.screen[y, x]
            id = self.GetIdFromColor(clr[0],clr[1],clr[2])
        
        # search the object
        items = [figure]  # figure is always at the bottom
        if id:
            self._walkTree(id, figure._children, items)
            #print id
        
        # return result
        return items
    
       
    def AssignIds(self, figure):
        self.curid = 0
        self._walkTreeAssign(figure._children)
    
    def _walkTreeAssign(self, children):
        """ The walker to assign ids to all objects.
        This walker walks in the same order as the walker that 
        searches for the objec given an id. This way we do not 
        have to test each object, but only go down the branches
        where it is in. """        
        for child in children:            
            id = self.GetId()
            child._id = id            
            # proceed to children
            if hasattr(child,'_wobjects'):
                self._walkTreeAssign(child._wobjects)
            self._walkTreeAssign(child._children)
    
    def _walkTree(self, id, children, items):
        """ The walker. """        
        for i in range(len(children)):
            # define child and next child
            child = children[i]
            child2 = None
            if i+1 < len(children):                
                child2 = children[i+1]
            # compare id's
            if id == child._id:                
                # found it!
                items.append(child)
                break
            elif id > child._id:
                if not child2:
                    # last child
                    items.append(child)
                    if hasattr(child,'_wobjects'):
                        self._walkTree(id, child._wobjects, items)
                    self._walkTree(id, child._children, items)
                elif id < child2._id:
                    # the child is a subchild!                    
                    items.append(child)
                    if hasattr(child,'_wobjects'):
                        self._walkTree(id, child._wobjects, items)
                    self._walkTree(id, child._children, items)
                else:
                    continue



class BaseFigure(base.Wibject):
    """ BaseFigure - the root of all wibjects.
    
    A Figure is a wrapper around the OpenGL widget in which it is drawn; 
    this way different backends are possible. Each backend inherits this
    class and implements the required methods and makes sure all GUI
    events are translated to visvis events.
    
    Since the figure represents the OpenGl context, it is also the root
    of the visualization tree; a figure wibject does not have a parent.
    
    """
    
    # dictionary of all figures objects: int -> Figure instance
    _figures = {}
    # the current figure object
    _currentNr = None
    
    def __init__(self):
        """ The init will be oveloaded in the subclasses,
        but they should call this init from there!
        """
        base.Wibject.__init__(self, None)
        
        # register
        self._Register()
        
        # to prevent recursion
        self._resizing = False
        
        # init background
        self.bgcolor = 0.8,0.8,0.8  # bgcolor is a property
        
        # Location of the mouse (in pixel coordinates).
        # It is the implementing class' responsibility to 
        # continously updated this.
        self._mousepos = (0,0)
        
        # The title
        self._title = ''
        
        # Each figure directly corresponds to an openGL context.
        # Therefore figure instances function as a place for 
        # keeping objects that should exist per context...
        
        # For keeping track of mouse and picking.        
        self._pickerHelper = ObjectPickerHelper()        
        self._underMouse = []
        
        # To store the fonts used in this figure.
        self._fontManager = FontManager()
        
        # To store the markers used in this figure
        self._markerManager = MarkerManager()
        
        # keep track of the currently active axes of this figure.
        self._currentAxes = None
        
        # Create events that only the figure has
        self._eventMouseUp = EventMouseUp(self)
        self._eventMotion = EventMotion(self)
        self._eventKeyDown = EventKeyDown(self)
        self._eventKeyUp = EventKeyUp(self)        
        self._eventClose = EventClose(self)
        self._eventAfterDraw = EventAfterDraw(self)
        
        # know when the position changes, so we can apply it.
        self.eventPosition.Bind(self._OnPositionChange)
        
        # create a timer to handle the drawing better
        self._drawTimer = Timer(self, 10, oneshot=True)
        self._drawTimer.Bind(self.OnDraw)        
        self._drawtime = time.time() # to calculate fps
        self._drawWell = False
    
    @property
    def eventMouseUp(self):
        """ Fired when the mouse is released.
        (Also on the first click of a double click.) 
        This event is also fired when the mouse is released over any of the
        figure's children."""
        return self._eventMouseUp
    @property
    def eventMotion(self):
        """ Fired when the mouse is moved. 
        This event is also fired when the mouse is released over any of the
        figure's children."""
        return self._eventMotion
    @property
    def eventKeyDown(self):
        """ Fired when a key is pressed down. """
        return self._eventKeyDown
    @property
    def eventKeyUp(self):
        """ Fired when a key is released. """
        return self._eventKeyUp    
    @property
    def eventClose(self):
        """ Fired when the figure is closed. """
        return self._eventClose
    @property
    def eventAfterDraw(self):
        """ Fired after each drawing pass. """
        return self._eventAfterDraw
    
    
    def _Register(self):
        """ _Register()
        Register the figure with the list of figures. 
        """ 
        
        # get keys
        nrs = BaseFigure._figures.keys()        
        nrs.sort()
        nr = 0 # the number...
        # check if a spot was prepared for us (override if so)
        for i in nrs:
            if BaseFigure._figures[i] is None:
                nr = i
                break
        # should we try finding our own number?
        if not nr:
            # empty?
            if not nrs:            
                nrs.append(0) 
            # check if there is a spot free
            for i in range(1,len(nrs)+1):            
                if not i==nrs[i-1]:
                    nr = i
                    break            
            else:
                # no, append to the end
                nr = nrs[-1]+1
        # set
        BaseFigure._figures[nr] = self        
        # make current
        BaseFigure._currentNr = nr

    
    ## Methods to overload
    # To create a subclass for a specific backend:
    # - Overload the methods below.
    # - Make sure Draw() is called on each paint request.
    # - Pass the events on and keep visvis timers running.
    # - Keep ._mousePos up to date.
    
    def _SetCurrent(self):
        """ _SetCurrent()
        Make the figure the current OpenGL context. This is required before
        drawing and before doing anything with OpenGl really.
        """
        raise NotImplemented()
    
    def _SwapBuffers(self):
        """ _SwapBuffers()
        Swap the memory and screen buffer such that
        what we rendered appears on the screen.
        """
        raise NotImplemented()
    
    def _ProcessEvents(self):
        """ _ProcessEvents()
        Process all events in the event queue.
        This is usefull when calling Draw() while an algorithm is 
        running. The figure is then still responsive. 
        """
        raise NotImplemented()
        
    def _SetTitle(self, title):
        """ _SetTitle(title)
        Set the title of the figure. Note that this
        does not have to work if the Figure is used as
        a widget in an application.
        """
        raise NotImplemented()
    
    def _SetPosition(self, x, y, w, h):
        """ Set the position of the widget. """        
        raise NotImplemented()
    
    def _GetPosition(self):
        """ Get the position of the widget. """        
        raise NotImplemented()
    
    
    def _Close(self):
        """ Close the widget, also calls Destroy(). """
    
    ## Properties
    
    @Property
    def parent():
        """ The parent of a figure always returns None and
        cannot be set. """
        def fget(self):
            return None
        def fset(self, value):
            pass
            #raise AttributeError("The parent of a figure cannot be set.")
            # do not raise an exception, as the parent is always ste in
            # the constructor of the BaseObject.
    
    @property
    def nr(self):
        """ Get the number (id) of this figure. """
        for key in BaseFigure._figures:
            if BaseFigure._figures[key] is self:
                return key
    
    @Property
    def title():
        """ Get/Set the title of the figure. If an empty string or None, 
        will display "Figure X", with X the figure nr.
        """
        def fget(self):
            return self._title
        def fset(self, value):
            if value:
                value = str(value)
                self._SetTitle(value)
            else:
                value = ''
                self._SetTitle("Figure "+str(self.nr))
            self._title = value
            
    
    @Property
    def currentAxes():
        """ Get/Set the currently active axes of this figure. 
        Returns None if no axes are present. 
        """
        def fget(self):
            
            # init 
            curNew = None
            curOld = self._currentAxes
            if curOld:
                curOld = curOld() # because is weak ref            
            
            # check 
            for child in self._children:
                if not isinstance(child, AxesContainer):
                    continue
                child = child.GetAxes()
                if not child:
                    continue
                if not curNew:
                    curNew = child
                if child is curOld:
                    curNew = child
                    break                
            
            # update and return
            if curNew:
                self._currentAxes = weakref.ref( curNew )
            else:
                self._currentAxes = None
            return curNew
        
        def fset(self, value):
            if value is None:
                self._currentAxes = None
            elif isinstance(value, Axes):                
                self._currentAxes = weakref.ref( value )
            else:
                raise ValueError('currentAxes must be an Axes instance (or None).')
    
    @property
    def underMouse(self):
        """ Get the object currently under the mouse. Can be None."""
        if not self._underMouse:
            return None
        return self._underMouse[-1]()
    
    @property
    def mousepos(self):
        """ Get the position of the mouse in figure coordinates. """
        return self._mousepos
    
    # ===== Notes about positioning figures.  =====
    # Moving a figure by dragging it with the mouse or programatically 
    # using the undelying widget directly does not fire a position event.
    # On resizing it does, because all backends call _OnResize() when this
    # happens. Setting the position using the position property simply
    # updates the position, which will make the eventPosition being fired
    # which makes the bound _OnPositionChange() being called, which updates
    # the actual position and or size of the underlying widget (via the
    # backend-implemented _SetPosition().
    
    @Property
    def position():
        """ The position for the figure works a bit different than for
        other wibjects: it only works with absolute values and it 
        represents the position on screen or the position in the 
        parent widget in an application. """
        def fget(self):
            # Update the position by asking the backend
            # Note we need to use privates to avoid position.Update() being
            # called
            thepos = self._GetPosition()
            self._position._x, self._position._y = thepos[0], thepos[1]
            self._position._w, self._position._h = thepos[2], thepos[3]
            self._position._inpixels = tuple(thepos)
            self._position._absolute = tuple(thepos)
            return self._position
        
        def fset(self,value):
            # check input
            value = [int(v) for v in value]
            if len(value) not in [2,4]:
                raise ValueError("Position must consist of 2 or 4 elements.")
            for v in value[2:]:
                if v < 2:
                    raise ValueError(   "Figure heigh and weight " +
                                        "must be given in absolute pixels.")
            # allow setting x and y only            
            if len(value) == 2:
                value = value[0], value[1], self._position.w, self._position.h
            # make pos 
            self._position = base.Position( value[0], value[1], 
                                            value[2], value[3], self)
            self._position._Changed()
    
    
    def _OnPositionChange(self,event=None):
        """ _OnPositionChange(event=None)
        When the position was programatically changed, we should
        change the position of the window. 
        But ONLY if it was really changed (or we get into infinite loops).
        """
        
        #if self._resizing:
        #    return
        pos1 = self._GetPosition()
        pos2 = tuple( [int(i) for i in self._position] )
        if pos1 != pos2:
            self._SetPosition( *pos2 )
    
    
    def _OnResize(self, event=None):
        """ _OnResize(event=None)
        Called when the figure is resized.
        This should initiate the event_position event, but not by firing
        the event_position of this object, otherwise it is not propagated.
        """        
        # Allow position tree to update
        self.position._Changed()
        # Draw, but not too often. Note that QT only calls this AFTER the
        # resizing, while wx can often call this DURING resizing, thus
        # the relatively large delay.
        self.Draw(timeout=200)
    
    
    ## Extra methods
    
    def Clear(self):
        """ Clear()
        Clear the figure, removing all wibjects inside it and clearing all
        callbacks. """        
        # remove children
        while self._children:
            child = self._children.pop()
            if hasattr(child, 'Destroy'):
                child.Destroy()
        # remove callbacks
        for fieldName in self.__dict__:
            if fieldName.startswith('_event'):
                event = self.__dict__[fieldName]
                if hasattr(event,'Unbind'):
                    event.Unbind()
        # restore some stuf
        self.eventPosition.Bind(self._OnPositionChange)
    
    ## Implement methods
    
    def OnDestroy(self):
        # Clean up. This method is called when calling Destroy().
        
        base.Wibject.OnDestroy(self)
        
        # close the figure instance
        if not self._destroyed:
            self._Close()
        
        # set flag
        self._destroyed = True
        
        # Detach reference to backend widget. We need to keep the widget
        # alive because we are not allowed to destroy it during its callback.
        # So we place a reference somewhere, meaning that the widget (and 
        # thus the Figure instance can be cleaned up after a second figure
        # has been destroyed. In other words, there will never be more than
        # one destroyed alive Figure instance (if the user cleans up its
        # references).
        # Note that WX really removes the widget and replaces it with a
        # dummy wrapper.
        BaseFigure._lastClosedWidget = self._widget
        self._widget = None
        
        # remove from list
        for nr in BaseFigure._figures.keys():
            if BaseFigure._figures[nr] is self:
                BaseFigure._figures.pop(nr)
                BaseFigure._currentFigure = None
                break
    
    
    def Draw(self, fast=False, timeout=10):
        """ Draw(fast=False, timeout=10)
        Draw the figure within 10 ms (if the events are handled). 
        Multiple calls in a short amount of time will result in only
        one redraw.
        """
        # Set draw well (is reciprocal of fast, this is to handle it easier.)
        well = not fast
        self._drawWell = self._drawWell or well
        # If never drawn before, draw now, this is required in WX, otherwise
        # a lot of OpenGL functions won't work...
        if not hasattr(self._drawTimer, '_drawnonce'):
            # call directly
            self._drawTimer._drawnonce= True
            self.OnDraw()
        if not self._drawTimer.isRunning:
            # restart timer
            self._drawTimer.Start(timeout)
    
    
    def DrawNow(self, fast=False):
        """ DrawNow(fast=False)
        Draw the figure right now and let the GUI toolkit process its events.
        Call this from time to time if you want to update your figure while 
        running some algorithm, and let the figure stay responsive.         
        """        
        self._drawWell = not fast
        self.OnDraw()
        self._ProcessEvents()
    
    
    def OnDraw(self, event=None):
        # This is the actual draw entry point. But we will 
        # call _Draw() to draw first the beatiful pictures and then
        # again to only draw the shapes for picking. 
        
        # are we alive?
        if self._destroyed:            
            return
        
        # calculate fps
        dt = time.time() - self._drawtime
        self._drawtime = time.time()
        if printFPS:
            print 'FPS: ', 1.0/dt  # for testing
        
        # get fast
        fast = not self._drawWell
        self._drawWell = False
        
        # make sure to draw to this canvas/widget
        self._SetCurrent()
        
        # get bits for this buffer
        self._pickerHelper.bits_r = rb = gl.glGetIntegerv(gl.GL_RED_BITS)
        self._pickerHelper.bits_g = gb = gl.glGetIntegerv(gl.GL_GREEN_BITS)
        self._pickerHelper.bits_b = bb = gl.glGetIntegerv(gl.GL_BLUE_BITS)
        if 0 in [rb, gb, bb]:
            raise RuntimeError('OpenGL context not set.')
        
        # set ids
        self._pickerHelper.AssignIds(self)
        
        # draw shape (to backbuffer)
        self._Draw('shape')        
        gl.glFinish() # call finish, normally swapbuffers does this...
        
        # read screen (of backbuffer)
        self._pickerHelper.CaptureScreen(self)
        #self._SwapBuffers() # uncomment to see the color coded objects
        
        # draw picture
        mode = 'normal'
        if fast:
            mode = 'fast'
        self._Draw(mode)
        
        # write the output to the screen
        self._SwapBuffers()
        
        # notify
        self.eventAfterDraw.Clear()
        self.eventAfterDraw.Fire()
        
    
    def _Draw(self, mode):
        """ _Draw(mode)
        This method performs a single drawing pass. Used by OnDraw().
        """
        
        # make sure the part to draw to is ok               
        w,h = self.position.size
        
        # clear screen
        
        # init pickerhelper as one
        pickerHelper = None
        
        if mode=='shape':
            # clear 
            clr = (0,0,0)
            gl.glClearColor(0.0 ,0.0 ,0.0, 0.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            # do not blend
            gl.glDisable(gl.GL_BLEND)
            
            # nor smooth
            gl.glDisable(gl.GL_POINT_SMOOTH)
            gl.glDisable(gl.GL_LINE_SMOOTH)
            
            # get pickerhelper
            pickerHelper = self._pickerHelper
        
        else:
            # clear
            clr = self.bgcolor
            gl.glClearColor(clr[0], clr[1], clr[2], 0.0)    
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        
            # enable blending, so lines and points can be antialiased
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            
            # smooth lines            
            gl.glEnable(gl.GL_LINE_SMOOTH)
            if mode=='fast':
                gl.glHint(gl.GL_POINT_SMOOTH_HINT, gl.GL_FASTEST)
                gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_FASTEST)
            else:
                gl.glHint(gl.GL_POINT_SMOOTH_HINT, gl.GL_NICEST)
                gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        
        
        # can we draw at all?
        if not (w>0 and h>0):
            return
        
        # Draw axes. Each axes specifies the viewport for itself and draws
        # all wobjects in it. Then it prepares for the wibjects, which are 
        # drawn (via _DrawTree) in the same viewport.
        for child in self._children:
            if isinstance(child, (Axes, AxesContainer) ):
                child._DrawTree(mode, pickerHelper)
        
        ## Draw more
        
        # prepare for flat drawing
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glViewport(0, 0, w, h)
        
        # set camera
        gl.glMatrixMode(gl.GL_PROJECTION)        
        gl.glLoadIdentity()        
        ortho( 0, w, h, 0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # draw other children
        for child in self._children:
            if not isinstance(child, (Axes, AxesContainer)):
                child._DrawTree(mode, pickerHelper)

    
    def _GenerateMouseEvent(self, eventName, x, y, button=0):
        """ _GenerateMouseEvent(eventName, x, y, button=0)
        For the backend to generate mouse events. 
        """
        
        # make lower
        eventName = eventName.lower()
        # get items now under the mouse
        items1 = [item() for item in self._underMouse if item()]
        # init list of events to fire
        events = []
        
        if eventName.count("motion") or eventName.count("move"):
            
            # also get new version of items under the mouse           
            items2 = self._pickerHelper.GetItemsUnderMouse(self)
            
            # init event list
            events = []
            
            # analyse for enter and leave events
            for item in items1:
                if item not in items2:
                    events.append( (item, item.eventLeave) )
            for item in items2:
                if item not in items1:
                    events.append( (item, item.eventEnter) )
            
            # always generate motion event from figure
            events.append( (self, self.eventMotion) ) 
            
            # generate motion events for any axes too
            for item in items2:
                if isinstance(item, Axes):
                    events.append( (item, item.eventMotion) ) 
            
            # update items under the mouse
            self._underMouse = [item.GetWeakref() for item in items2]        
        
        elif items1 and eventName.count("up"):
            # always generate up event from figure
            item = items1[0]
            events.append( ( item, item.eventMouseUp) )
            # generate up events for any axes too
            for item in items1:
                if isinstance(item, Axes):
                    events.append( (item, item.eventMouseUp) ) 
        
        elif items1 and eventName.count("down"):            
            item = items1[-1]
            events.append( ( item, item.eventMouseDown) )        
        
        elif items1 and eventName.count("double"):
            item = items1[-1]
            events.append( ( item, item.eventDoubleClick) )
        
        # fire events
        for item,ev in events:
            # can we fire an event at all
            if item._destroyed:
                continue
            # determine axes
            if isinstance(item, base.Wobject):
                axes = item.GetAxes()
                if not axes:
                    continue
            ev.Clear()
            ev.button = button
            if isinstance(item, base.Wibject):
                if item.parent: # use relative coordinates if not a figure
                    ev.x, ev.y = x-item.position.absLeft, y-item.position.absTop
                else:
                    ev.x, ev.y = x, y
            elif isinstance(item, base.Wobject):
                # use axes coordinates
                ev.x, ev.y = x-axes.position.absLeft, y-axes.position.absTop
            if isinstance(item, (base.Wobject, Axes )):
                # also give 2D coordinates
                if isinstance(item, Axes):
                    cam = item._cameras['2d']
                else:
                    cam = axes._cameras['2d']
                if item.parent: # or screen to world cannot be calculated
                    ev.x2d, ev.y2d = cam.ScreenToWorld((ev.x, ev.y))
            ev.Fire()


class AxesContainer(base.Wibject):
    """ AxesContainer(parent)
    
    A simple container wibject class to contain one Axes instance.
    Each Axes in contained in an AxesContainer instance. By default
    the axes position is expressed in pixel coordinates, while the
    container's position is expressed in unit coordinates. This 
    enables advanced positioning of the Axes.
    
    When there is one axes in a figure, the container position will
    be "0,0,1,1". For subplots however, the containers are positioned
    to devide the figure in equal spaces. The contained Axes instances
    are positioned (relative to the container instance) such that there
    is margin for the ticks and labels etc.
    
    The only correct way to create (and obtain a reference to) 
    an AxesContainer instance is to use:
    axes = vv.Axes(figure)
    container = axes.parent
    
    This container is automatically destroyed once the axes is removed. 
    You can attach wibjects to an instance of this class, but note that
    the container object is destroyed as soon as the axes is gone.
    """
    
    def __init__(self, parent, *args, **kwargs):
        
        # check that the parent is a Figure 
        if not isinstance(parent, BaseFigure):
            raise Exception("The given parent for an AxesContainer " +
                            "should be a Figure.")
        base.Wibject.__init__(self, parent, *args, **kwargs)
        self.position = 0,0,1,1
    
    
    def GetAxes(self):
        """ GetAxes()
        Get the axes. Creates a new axes object if it has none. 
        """
        if self._children:
            child = self._children[0]
            if isinstance(child, Axes):
                return child
        return None
    
    
    def _DrawTree(self, *args, **kwargs):
        """ _DrawTree(*args, **kwargs)
        Pass on, but Destroy itself if axes is gone. """
        axes = self.GetAxes()
        if axes:
            base.Wibject._DrawTree(self, *args, **kwargs)
        else:
            self.Destroy()
    

class Axes(base.Wibject):
    """ Axes(parent)
    
    An Axes instance represents the scene with a local coordinate system 
    in which wobjects can be drawn. It has various properties to influence 
    the appearance of the scene, like for example whether to show gridlines,
    in what color to draw the tickmarks, labels to be shown, etc.
    
    The cameraType determines how the data is visualized and how the user 
    can interact with the data.
    
    The daspect property represents the aspect ratio of the data as a
    three element tuple. The sign of the elements indicate dimensions 
    being flipped. (The function imshow() for example flips the 
    y-dimension). If daspectAuto is False, all dimensions are always
    equally zoomed (The function imshow() sets this to False).
    """ 
    
    def __init__(self, parent):
        
        # check that the parent is a Figure or AxesContainer
        if isinstance(parent, AxesContainer):
            figure = parent.parent 
        elif isinstance(parent, BaseFigure):            
            figure = parent
            parent = AxesContainer(figure)
        else:
            raise Exception("The given parent for an Axes " +
                            "should be a Figure or AxesContainer.")
        
        # call base __init__
        base.Wibject.__init__(self, parent)
        
        # motion event
        self._eventMotion = EventMotion(self)
        self._eventMouseUp = EventMouseUp(self)
        
        # objects in the scene. The Axes is the only wibject that
        # can contain wobjects. Basically, the Axes is the root
        # for all the wobjects in it.    
        self._wobjects = []
        
        # data aspect ratio. If daspectAuto is True, the values
        # of daspect are ignored (only the sign is taken into account)
        self._daspect = (1.0,1.0,1.0)
        self._daspectAuto = True
        
        # make clickable
        self.hitTest = True
        
        # axis properties                
        self._xlabel, self._ylabel, self._zlabel = '','',''
        self._xCorr, self._yCorr = 0, 0
        self._tickFontSize = 9
        self._gridLineStyle = ':'
        self._xticks, self._yticks, self._zticks = None, None, None
        self._xgrid, self._ygrid, self._zgrid = False, False, False
        self._xminorgrid, self._yminorgrid, self._zminorgrid =False,False,False
        self._box =  True
        self._axis = True
        self._axisColor = (0,0,0)
        
        # create cameras and select one
        self._cameras = {   'twod': TwoDCamera(self), 
                            'polar': PolarCamera(self),                            
                            'fly': FlyCamera(self)}        
        self._cameras['3d'] = self._cameras['polar']        
        self.camera = self._cameras['2d'] = self._cameras['twod']
        
        # init the background color of this axes
        self.bgcolor = 1,1,1  # remember that bgcolor is a property
        
        # bind to event (no need to unbind because it's our own)
        self.eventMouseDown.Bind(self._OnMouseDown)
        
        # create Axis and legend
        Axis(self) # is a wobject
        
        # make current
        figure.currentAxes = self
    
    
    ## Define more methods

    
    def SetLimits(self, rangeX=None, rangeY=None, rangeZ=None, margin=0.02):
        """ SetLimits(rangeX=None, rangeY=None, rangeZ=None, margin=0.02)
        
        Set the limits of the scene. These are taken as hints to set 
        the camera view, and determine where the axis is drawn for the
        polar (3d) camera.
        
        Each range can be None, a 2 element iterable, or a visvis.Range 
        object. If a range is None, the range is obtained from the 
        wobjects currently in the scene. To set the range that will fit
        all wobjects, simply use "SetLimits()"
        
        The margin represents the fraction of the range to add (default 2%).
        """
        
        # Check margin
        if margin and not isinstance(margin, float):
            raise ValueError('In SetLimits(): margin should be a float.')
            
        # if tuples, convert to ranges
        if rangeX is None or isinstance(rangeX, Range):
            pass # ok
        elif hasattr(rangeX,'__len__') and len(rangeX)==2:            
            rangeX = Range(rangeX[0], rangeX[1])
        else:
            raise ValueError("Limits should be Ranges or two-element iterables.")
        if rangeY is None or isinstance(rangeY, Range):
            pass # ok
        elif hasattr(rangeY,'__len__') and len(rangeY)==2:            
            rangeY = Range(rangeY[0], rangeY[1])
        else:
            raise ValueError("Limits should be Ranges or two-element iterables.")
        if rangeZ is None or isinstance(rangeZ, Range):
            pass # ok
        elif hasattr(rangeZ,'__len__') and len(rangeZ)==2:            
            rangeZ = Range(rangeZ[0], rangeZ[1])
        else:
            raise ValueError("Limits should be Ranges or two-element iterables.")
        
        rX, rY, rZ = rangeX, rangeY, rangeZ
        
        if None in [rX, rY, rZ]:
            
            # find outmost range
            wobjects = self.FindObjects(base.Wobject)
            for ob in wobjects:
                
                # Ask object what it's limits are
                tmp = ob._GetLimits()
                if not tmp:
                    continue                
                tmpX, tmpY, tmpZ = tmp
                
                # update min/max
                if rangeX:
                    pass
                elif tmpX and rX:
                    rX = Range( min(rX.min, tmpX.min), max(rX.max, tmpX.max) )
                elif tmpX:
                    rX = tmpX
                if rangeY:
                    pass
                elif tmpY and rY:
                    rY = Range( min(rY.min, tmpY.min), max(rY.max, tmpY.max) )
                elif tmpY:
                    rY = tmpY
                if rangeZ:
                    pass
                elif tmpZ and rZ:
                    rZ = Range( min(rZ.min, tmpZ.min), max(rZ.max, tmpZ.max) )
                elif tmpX:
                    rZ = tmpZ
        
        # default values
        if rX is None:
            rX = Range(-1,1)
        if rY is None:
            rY = Range(0,1)
        if rZ is None:
            rZ = Range(0,1)
        
        # apply margins
        if margin:
            # x
            tmp = rX.range * margin
            if tmp == 0: tmp = margin
            rX = Range( rX.min-tmp, rX.max+tmp )
            # y
            tmp = rY.range * margin
            if tmp == 0: tmp = margin
            rY = Range( rY.min-tmp, rY.max+tmp )
            # z
            tmp = rZ.range * margin
            if tmp == 0: tmp = margin
            rZ = Range( rZ.min-tmp, rZ.max+tmp )
        
        # apply to each camera
        for cam in self._cameras.values():
            cam.SetLimits(rX, rY, rZ)
    
    
    def GetLimits(self):
        """ GetLimits()
        Get the limits of the axes as displayed now. This can differ
        from what was set by SetLimits if the daspectAuto is False. 
        Returns a tuple of limits for x and y, respectively.
        
        Note: the limits are queried from the twod camera model, even 
        if this is not the currently used camera.
        """
        # get camera
        cam = self._cameras['twod']
        
        # calculate limits
        tmp = cam._fx/2 / self.daspect[0]
        xlim = Range( cam.view_loc[0] - tmp, cam.view_loc[0] + tmp )
        tmp = cam._fy/2 / self.daspect[1]
        ylim = Range( cam.view_loc[1] - tmp, cam.view_loc[1] + tmp )
        
        # return
        return xlim, ylim
    
    
    def GetView(self):
        """ GetView()
        Get a structure with the camera parameters. The parameters are
        named so they can be changed in a natural way and fed back using
        SetView(). Note that the parameters can differ for different camera
        types.
        """
        return self.camera.GetViewParams()
    
    
    def SetView(self, s=None):
        """ SetView(s=None)
        Set the camera view using the given structure with camera parameters.
        If s is None, the camera is reset to its initial state.
        """
        if s:
            self.camera.SetViewParams(s)
        else:
            self.camera.Reset()
    
    
    
    def Draw(self, fast=False):
        """ Draw(fast=False)
        Calls Draw(fast) on its figure, as the total opengl canvas 
        has to be redrawn. This might change in the future though. """
        figure = self.GetFigure()
        if figure:
            figure.Draw(fast)
    
    
    def Clear(self, clearForDestruction=False):
        """ Clear()
        Clear the axes. Removing all wobjects in the scene.
        """
        # remove wobjects
        for w in self.wobjects:
            if hasattr(w,'Destroy'):
                w.Destroy()
        self._wobjects[:] = []
        # remake axis and legend?
        if not clearForDestruction:
            Axis(self)
    
    @property
    def wobjects(self):
        """ Get a shallow copy of the list of wobjects in the scene. 
        """
        return [child for child in self._wobjects]
    
    
    def _CorrectPositionForLabels(self):
        """ _CorrectPositionForLabels()
        Correct the position for the labels and title etc. """
        
        # init correction
        xCorr, yCorr = 0, 0
        
        # correction should be applied for 2D camera and a valid label
        if self.camera is self._cameras['2d']:
            if self.showAxis:
                yCorr += 20
                xCorr += 60 # there's already a margin of 10 by default
                if self.xLabel:
                    yCorr += 20
                if self.yLabel:
                    xCorr += 20
        
        # check the difference
        if xCorr != self._xCorr or yCorr != self._yCorr:
            dx = self._xCorr - xCorr
            dy = self._yCorr - yCorr
            self._xCorr, self._yCorr = xCorr, yCorr
            # apply
            self.position.Correct(-dx, 0, dx, dy)
    
    ## Define more properties
    
    @property
    def eventMotion(self):
        """ Fired when the mouse is moved. 
        This event is also fired when the mouse is released over any of the
        axes's children. """
        return self._eventMotion
    @property
    def eventMouseUp(self):
        """ Fired when the mouse is released. 
        (Also on the first click of a double click.) 
        This event is also fired when the mouse is released over any of the
        axes's children. """
        return self._eventMouseUp
    
    @Property
    def cameraType():
        """ Get/Set the camera type to use. Currently supported are:
          * '2d' - a two dimensional camera that looks down the z-dimension.
          * '3d' - a three dimensional (polar) camera.
          * 'fly' - a camera like a flight sim. Not recommended.
        """
        def fget(self):
            for key in self._cameras:
                if self._cameras[key] is self.camera:
                    return key
            else:
                return ''
        def fset(self, cameraName):        
            cameraName = cameraName.lower()
            if not self._cameras.has_key(cameraName):
                raise Exception("Unknown camera type!")
            self.camera = self._cameras[cameraName]
        
    
    @property
    def mousepos(self):
        """ Get position of mouse in screen pixels, relative to this axes. """
        figure = self.GetFigure()
        if not figure:
            return 0,0
        x,y = figure.mousepos
        pos = self.position
        return x-pos.absLeft, y-pos.absTop
    
    
    @Property
    def daspect():
        """ Get/Set the data aspect ratio as a three element tuple. 
        A two element tuple can also be given (then z is assumed 1).
        Values can be negative, in which case the corresponding dimension
        is flipped. Note that if daspectAuto is True, only the sign of the
        daspect is taken into account.
        """
        def fget(self):            
            return self._daspect
        def fset(self, value):        
            if not value:
                self._daspect = 0
                return
            try:
                l = len(value)
            except TypeError:
                raise Exception("You can only set daspect with a sequence!")
            if 0 in value:
                raise Exception("The given daspect contained a zero!")
            if l==2:            
                self._daspect = (float(value[0]), float(value[1]), 1.0)
            elif l==3:
                self._daspect = (float(value[0]), 
                    float(value[1]), float(value[2]))
            else:            
                raise Exception("daspect should be a length 2 or 3 sequence!")
            # we could normalize... but we dont have to...    
            self.Draw()
    
    @Property
    def daspectAuto():
        """ Get/Set whether to scale the dimensions independently.
        If True, the dimensions are scaled independently, and only the sign
        of the axpect ratio is taken into account. If False, the dimensions
        have the scale specified by the daspect property.
        """
        def fget(self):
            return self._daspectAuto
        def fset(self, value):
            self._daspectAuto = bool(value)
    
    
    @Property
    def gridLineStyle():
        """ Get/Set the style of the gridlines as a single char similar
        to the lineStyle (ls) property of the line wobject (or in plot). """
        def fget(self):
            return self._gridLineStyle
        def fset(self, value):
            if value not in lineStyles:
                raise ValueError("Invalid lineStyle for grid lines")
            self._gridLineStyle = value
            
    @Property
    def showGridX():
        """ Get/Set whether to show a grid for the x dimension. """
        def fget(self):
            return self._xgrid
        def fset(self, value):
            self._xgrid = bool(value)
    
    @Property
    def showGridY():
        """ Get/Set whether to show a grid for the y dimension. """
        def fget(self):
            return self._ygrid
        def fset(self, value):
            self._ygrid = bool(value)
    
    @Property
    def showGridZ():
        """ Get/Set whether to show a grid for the z dimension. """
        def fget(self):
            return self._zgrid
        def fset(self, value):
            self._zgrid = bool(value)
    
    @Property
    def showGrid():
        """ Show/hide the grid for the x,y and z dimension. """
        def fget(self):
            return self._xgrid, self._ygrid, self._zgrid
        def fset(self, value):
            if isinstance(value, tuple):
                value = tuple([bool(v) for v in value])
                self._xgrid, self._ygrid, self._zgrid = value
            else:
                self._xgrid = self._ygrid = self._zgrid = bool(value)
    
    @Property
    def showMinorGridX():
        """ Get/Set whether to show a minor grid for the x dimension. """
        def fget(self):
            return self._xminorgrid
        def fset(self, value):
            self._xminorgrid = bool(value)
    
    @Property
    def showMinorGridY():
        """ Get/Set whether to show a minor grid for the y dimension. """
        def fget(self):
            return self._yminorgrid
        def fset(self, value):
            self._yminorgrid = bool(value)
    
    @Property
    def showMinorGridZ():
        """ Get/Set whether to show a minor grid for the z dimension. """
        def fget(self):
            return self._zminorgrid
        def fset(self, value):
            self._zminorgrid = bool(value)
    
    @Property
    def showMinorGrid():
        """ Show/hide the minor grid for the x, y and z dimension. """
        def fget(self):
            return self._xminorgrid, self._yminorgrid, self._zminorgrid
        def fset(self, value):
            if isinstance(value, tuple):
                tmp = tuple([bool(v) for v in value])
                self._xminorgrid, self._yminorgrid, self._zminorgridd = tmp
            else:
                tmp = bool(value)
                self._xminorgrid = self._yminorgrid = self._zminorgrid = tmp
    
    
    @Property
    def xTicks():
        """ Get/Set the ticks for the x dimension. 
        If None, they are determined automatically. """
        def fget(self):
            return self._xticks
        def fset(self, value):
            self._xticks = value
    
    @Property
    def yTicks():
        """ Get/Set the ticks for the y dimension. 
        If None, they are determined automatically. """
        def fget(self):
            return self._yticks
        def fset(self, value):
            self._yticks = value
    
    @Property
    def zTicks():
        """ Get/Set the ticks for the z dimension. 
        If None, they are determined automatically. """
        def fget(self):
            return self._zticks
        def fset(self, value):
            self._zticks = value
    
    
    @Property
    def axisColor():
        """ Get/Set the color of the box, ticklines and tick marks. """
        def fget(self):
            return self._axisColor
        def fset(self, value):
            self._axisColor = getColor(value, 'setting bgcolor')
    
    
    @Property
    def showAxis():
        """ Get/Set whether to show the the axis. If False will also
        hide the grid, minorgrid and box. """
        def fget(self):
            return self._axis
        def fset(self, value):
            self._axis = bool(value)
    
    
    @Property
    def showBox():
        """ Get/Set whether to show the box of the axis. """
        def fget(self):
            return self._box
        def fset(self, value):
            self._box = bool(value)
    
    @Property
    def tickFontSize():
        """ Get/Set the font size of the tick marks. """
        def fget(self):
            return self._tickFontSize
        def fset(self, value):
            self._tickFontSize = value
    
    
    @Property
    def xLabel():
        """ Get/Set the label for the x dimension. """
        def fget(self):
            return self._xlabel
        def fset(self, value):
            self._xlabel = value
    
    @Property
    def yLabel():
        """ Get/Set the label for the y dimension. """
        def fget(self):
            return self._ylabel
        def fset(self, value):
            self._ylabel = value
    
    @Property
    def zLabel():
        """ Get/Set the label for the z dimension. """
        def fget(self):
            return self._zlabel
        def fset(self, value):
            self._zlabel = value
    
    @Property
    def legend():
        """ Get/Set the string labels for the legend. Upon setting,
        a legend wibject is automatically shown. """
        def fget(self):
            return self.legendWibject._stringList
        def fset(self, value):            
            self.legendWibject.SetStrings(value)
    
    @property
    def legendWibject(self):
        """ Get the legend wibject, so for exampe its position
        can be changed programatically. """
        legendWibjects = self.FindObjects(Legend)
        if not legendWibjects:
            legendWibjects = [Legend(self)] # create legend object
        return legendWibjects[-1]
    
    
    ## Implement methods
    
    def OnDestroy(self):
        # Clean up.
        base.Wibject.OnDestroy(self)
        self.Clear(True)
        self.camera = None
        self._cameras = {}
        # container is destroyed as soon as it notices the axes is gone
        # any wibjects are destoyed automatically by the Destroy command.
        
    
    
    def OnDraw(self, mode='normal'):
        # Draw the background of the axes and the wobjects in it.
        
        # size of figure ...
        w,h = self.GetFigure().position.size
        
        # correct size for labels
        self._CorrectPositionForLabels()
        
        # Find actual position in pixels, do not allow negative values
        pos = self.position.InPixels()
        pos.w, pos.h = max(pos.w, 1), max(pos.h, 1)
        
        # set viewport (note that OpenGL has origin in lower-left, visvis
        # in upper-left)
        gl.glViewport(pos.absLeft, h-pos.absBottom, pos.w, pos.h)        
        
        gl.glDisable(gl.GL_DEPTH_TEST)
        
        # draw bg
        gl.glMatrixMode(gl.GL_PROJECTION)        
        gl.glLoadIdentity()        
        ortho( 0, 1, 0, 1)
        
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        # draw background
        if self.bgcolor:
            clr = self.bgcolor
            gl.glColor3f(clr[0], clr[1], clr[2])
            gl.glBegin(gl.GL_POLYGON)
            gl.glVertex2f(0,0)
            gl.glVertex2f(0,1)
            gl.glVertex2f(1,1)
            gl.glVertex2f(1,0)
            gl.glEnd()
        gl.glEnable(gl.GL_DEPTH_TEST)
        
        # setup the camera
        self.camera.SetView()
        
        # Draw other stuff, but wait with lines     
        for item in self._wobjects:
            if isinstance(item, (Line,)):
                pass # draw later
            else:
                item._DrawTree(mode)
        
        # Lines are special case. In order to blend them well, we should
        # draw textures, meshes etc, first.
        for item in self._wobjects:
            if isinstance(item, Line):
                item._DrawTree(mode)
        
        # set camera to screen coordinates.
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        ortho( pos.absLeft, pos.absRight, h-pos.absBottom, h-pos.absTop)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # allow wobjects to draw in screen coordinates
        gl.glEnable(gl.GL_DEPTH_TEST)
        for item in self._wobjects:
            if not isinstance(item, Axis):
                item._DrawTree('screen')
        
        # let axis object draw in screen coordinates in the full viewport.
        # (if the twod camera is used)
        if self.camera is self._cameras['twod']:
            gl.glViewport(0,0,w,h)
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            ortho(0,w,0,h)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glDisable(gl.GL_DEPTH_TEST)
        else:
            gl.glEnable(gl.GL_DEPTH_TEST)
        for item in self._wobjects:
            if isinstance(item, Axis):
                item._DrawTree('screen')                
        
        # prepare for wibject children (draw in full viewport)
        gl.glViewport(0,0,w,h)
        gl.glDisable(gl.GL_DEPTH_TEST)                
        gl.glMatrixMode(gl.GL_PROJECTION)        
        gl.glLoadIdentity()
        ortho( 0, w, h, 0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        self.parent._Transform() # Container
        self._Transform() # Self
    
    
    def OnDrawShape(self, clr):
        # Draw the shapes of wobjects.
        
        # get shape
        mode = 'shape'
        pickerHelper = self.GetFigure()._pickerHelper
        
        # get position
        w,h = self.GetFigure().position.size
        pos = self.position.InPixels()
        pos.w, pos.h = max(pos.w, 1), max(pos.h, 1)
        
        # set viewport (note that OpenGL has origin in lower-left, visvis
        # in upper-left)
        gl.glViewport(pos.absLeft, h-pos.absBottom, pos.w, pos.h) 
        
        # prepare for drawing background
        gl.glMatrixMode(gl.GL_PROJECTION)        
        gl.glLoadIdentity()        
        ortho( 0, 1, 0, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        # draw background        
        gl.glColor3f(clr[0], clr[1], clr[2])
        gl.glBegin(gl.GL_POLYGON)
        gl.glVertex2f(0,0)
        gl.glVertex2f(0,1)
        gl.glVertex2f(1,1)
        gl.glVertex2f(1,0)
        gl.glEnd()
        
        #setup the camera
        self.camera.SetView()
        
        # draw other stuff        
        for item in self._wobjects:
            if isinstance(item, Line):
                pass # draw later
            else:
                item._DrawTree(mode, pickerHelper)
        
        # draw lines AFTER textures
        # note that this does not work if lines textures are children
        # of each-other. in that case they should be added to the scene
        # in the correct order.
        for item in self._wobjects:
            if isinstance(item, Line):
                item._DrawTree(mode, pickerHelper)
        
        # prepare for wibject children
        gl.glDisable(gl.GL_DEPTH_TEST)        
        gl.glMatrixMode(gl.GL_PROJECTION)        
        gl.glLoadIdentity()        
        ortho( 0, pos.w, pos.h, 0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        # No need to call transform
    
    def OnDrawFast(self):
        self.OnDraw(mode='fast')
        
    def OnDrawPre(self):
        self.OnDraw(mode='pre')
    
    
    def _OnMouseDown(self, event):
        # make current axes
        f = self.GetFigure()
        if f:
            f.currentAxes = self
        

# A note about tick labels. We format these using '%1.4g', which means
# they will have 4 significance, and will automatically displayed in
# exp notation if necessary. This means that the largest string is
# x.xxxE+yyy -> 10 characters. 
# In practice, the exp will hardly ever be larger than 2 characters. So we
# strip the zeros in the exponent and assume the (in practice) max string
# to be "-0.001e+99". With a fontsize of 9, this needs little less than 70
# pixels. The correction applied when visualizing axis (and ticks) is 60,
# because the default offset is 10 pixels for axes.

# create tick units
_tickUnits = []
for e in range(-10, 21):
    for i in [10, 20, 25, 50]:
        _tickUnits.append( i*10**e)


def GetTicks(p0, p1, lim, minTickDist=40, ticks=None):
    """ GetTicks(p0, p1, lim, minTickDist=40, ticks=None)
    Get the tick values, position and texts.
    These are calculated from a start end end position and the range
    of values to map between these two points (which can be 2d or 3d). 
    if ticks is given, use these values instead.
    """
    
    # Vector from start to end point
    vec = p1-p0
    
    # Calculate all ticks if not given
    if ticks is None:
        
        # Get pixels per unit
        if lim.range == 0:
            return [],[],[]
        pixelsPerUnit = vec.Norm() / lim.range
        
        # Try all tickunits, starting from the smallest, until we find 
        # one which results in a distance between ticks more than
        # X pixels.
        try:
            for tickUnit in _tickUnits:
                if tickUnit * pixelsPerUnit >= minTickDist:
                    break
            # if the numbers are VERY VERY large (which is very unlikely)
            if tickUnit*pixelsPerUnit < minTickDist:
                raise ValueError
        except (ValueError, TypeError):
            # too small
            return [],[],[]
        
        # Calculate the ticks (the values) themselves
        ticks = []    
        firstTick = np.ceil(  lim.min/tickUnit ) * tickUnit
        lastTick  = np.floor( lim.max/tickUnit ) * tickUnit
        count = 0
        ticks = [firstTick]
        while ticks[-1] < lastTick-tickUnit/2:
            count += 1
            ticks.append( firstTick + count*tickUnit )
    
    # Calculate tick positions and text
    ticksPos, ticksText = [], []
    for tick in ticks:
        pos = p0 + vec * ( (tick-lim.min) / lim.range )
        text = '%1.4g' % tick
        iExp = text.find('e')
        if iExp>0:
            front = text[:iExp+2]
            text = front + text[iExp+2:].lstrip('0')
        # Store
        ticksPos.append( pos )
        ticksText.append( text )
    
    # Done
    return ticks, ticksPos, ticksText
    

class Axis(base.Wobject):
    """ Axis(parent)
    An Axis object represents the lines, ticks and grid that make
    up an axis. Not to be confused with an Axes, which represents
    a scene and is a Wibject.
    
    This is a helper class used by the Axes class.
    """
    
    def __init__(self, parent):
        base.Wobject.__init__(self, parent)
        self._lineWidth = 0.8
        self._minTickDist = 40
        
        # create tick units
        self._tickUnits = []
        for e in range(-10, 21):
            for i in [10, 20, 25, 50]:
                self._tickUnits.append( i*10**e)
        
        # corners of a cube in relative coordinates
        self._corners = tmp = Pointset(3)
        tmp.Append(0,0,0);  tmp.Append(1,0,0);  tmp.Append(0,1,0);  
        tmp.Append(0,0,1);  tmp.Append(1,1,0);  tmp.Append(1,0,1); 
        tmp.Append(0,1,1);  tmp.Append(1,1,1); 
        
        # Indices of the base corners for each dimension. 
        # The order is very important, don't mess it up...
        self._cornerIndicesPerDirection = [ [0,2,6,3], [3,5,1,0], [0,1,4,2] ]
        
        # Dicts to be able to optimally reuse text objects; creating new
        # text objects or changing the text takes a relatively large amount
        # of time (if done every draw).
        self._textDicts = [{},{},{}]
    
    
    def OnDraw(self):
        axes = self.GetAxes()
        if not axes:
            return
        if not axes.showAxis:
            if self._children:                
                for child in self.children:
                    child.Destroy()
            return
        
        try:
            
            # determine whether the used camera is a twoD camera
            cam = axes.camera
            isTwoDCam = cam is axes._cameras['twod']
            
            # get parameters
            drawGrid = [v for v in axes.showGrid]
            drawMinorGrid = [v for v in axes.showMinorGrid]
            ticksPerDim = [axes.xTicks, axes.yTicks, axes.zTicks]
            
            # get limits
            if isTwoDCam:
                lims = axes.GetLimits()
                lims = [lims[0], lims[1], cam.zlim]
                maxd = 2
            else:
                lims = [cam.xlim, cam.ylim, cam.zlim]
                maxd = 3
            
            # get labels
            labels = [axes.xLabel, axes.yLabel, axes.zLabel]
            
            # To translate to real coordinates            
            pmin = Point(lims[0].min, lims[1].min, lims[2].min)
            pmax = Point(lims[0].max, lims[1].max, lims[2].max)        
            def relativeToCoord(p):
                pi = Point(1,1,1) - p
                return pmin*pi + pmax*p
            
            # Get the 8 corners of the cube in real coords and screen pixels
            proj = glu.gluProject
            corners8_c = [relativeToCoord(p) for p in self._corners]            
            corners8_s = [Point(proj(p.x,p.y,p.z)) for p in corners8_c]
            
            # the new text object dictionaries
            newTextDicts = [{},{},{}]
            
            # pointsets for drawing lines and gridlines            
            ppc = Pointset(3) # lines in real coords
            pps = Pointset(3) # lines in screen pixels
            ppg = Pointset(3) # dotted lines in real coords
            
            # we use this later to determine the order of the corners
            self._delta = 1 
            for i in axes.daspect:
                if i<0: self._delta*=-1   
            
            # for each dimension ...
            for d in range(maxd): # d for dimension/direction
                lim = lims[d]
                
                # get the four corners that are of interest for this dimension
                tmp = self._cornerIndicesPerDirection[d]
                corners4_c = [corners8_c[i] for i in tmp]
                corners4_s = [corners8_s[i] for i in tmp]
                
                # if 2D, use only those corners
                if isTwoDCam:
                    tmp1, tmp2 = [],[]
                    for i in [0,1,0,1]:
                        tmp1.append(corners4_c[i])
                        tmp2.append(corners4_s[i])
                    corners4_c, corners4_s = tmp1, tmp2
                
                # Get directional vectors in real coords and screen pixels. 
                # Easily calculated since the first _corner elements are 
                # 000,100,010,001
                vector_c = corners8_c[d+1] -corners8_c[0]
                vector_s = corners8_s[d+1] -corners8_s[0]
                
                # Should we correct tick Dist?
                minTickDist = self._minTickDist
                if isTwoDCam and d==0:
                    mm = max(abs(lim.min),abs(lim.max))
                    if mm >= 10000:
                        minTickDist = 80 
                
                # Calculate tick distance in units
                minTickDist *= vector_c.Norm() / vector_s.Norm()
                
                # Get index of corner to put ticks at
                i0 = 0; bestVal = 999999999999999999999999
                for i in range(4):
                    if d==2: val = corners4_s[i].x
                    else: val = corners4_s[i].y
                    if val < bestVal:
                        i0 = i
                        bestVal = val
                
                # Get indices of next corners in line               
                i1 = self._NextCornerIndex(i0, d, vector_s)
                i2 = self._NextCornerIndex(i1, d, vector_s)
                # get first corner and grid vectors
                firstCorner = corners4_c[i0]
                gv1 = corners4_c[i1] - corners4_c[i0]
                gv2 = corners4_c[i2] - corners4_c[i1]
                # get tick vector to indicate tick
                gv1s = corners4_s[i1] - corners4_s[i0]
                #tv = gv1 * (5 / gv1s.Norm() )
                npixels = ( gv1s.x**2 + gv1s.y**2 ) ** 0.5 + 0.000001
                tv = gv1 * (5.0 / npixels )
                
                # Always draw these corners
                pps.Append(corners4_s[i0])
                pps.Append(corners4_s[i0]+vector_s)
                # Add line pieces to draw box
                if axes.showBox:
                    for i in range(4):
                        if i is not i0:
                            corner = corners4_s[i]
                            pps.Append(corner)
                            pps.Append(corner+vector_s)
                
                # Apply label
                textDict = self._textDicts[d]
                p1 = corners4_c[i0] + vector_c * 0.5
                key = '_label_'
                if key in textDict and textDict[key] in self._children:
                    t = textDict.pop(key)
                    t.text = labels[d]
                    t.x, t.y, t.z = p1.x, p1.y, p1.z
                else:
                    #t = Text(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                    t = AxisLabel(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                    t.fontSize=10
                newTextDicts[d][key] = t                
                t.halign = 0
                t.textColor = axes._axisColor
                # move up front
                if not t in self._children[-3:]:                    
                    self._children.remove(t) 
                    self._children.append(t)
                # get vec to calc angle
                vec = Point(vector_s.x, vector_s.y)
                if vec.x < 0:
                    vec = vec * -1                
                t.textAngle = float(vec.Angle() * 180/np.pi)
                # keep up to date (so label can move itself just beyond ticks)
                t._textDict = newTextDicts[d] 
                
                # Get ticks stuff
                tickValues = ticksPerDim[d] # can be None
                p1, p2 = firstCorner.Copy(), firstCorner+vector_c                
                tmp = GetTicks(p1,p2, lim, minTickDist, tickValues)
                ticks, ticksPos, ticksText = tmp
                
                # Apply Ticks
                for tick, pos, text in zip(ticks, ticksPos, ticksText):
                    # get little tail to indicate tick
                    p1 = pos
                    p2 = pos - tv
                    # Add tick lines
                    if isTwoDCam:
                        factor = ( tick-firstCorner[d] ) / vector_c[d]
                        p1s = corners4_s[i0] + vector_s * factor
                        tmp = Point(0,0,0)
                        tmp[int(not d)] = 4
                        pps.Append(p1s)
                        pps.Append(p1s-tmp)
                    else:
                        ppc.Append(p1)
                        ppc.Append(p2)
                    # z-axis has valign=0, thus needs extra space
                    if d==2:
                        text+='  '
                    # put textlabel at tick                     
                    textDict = self._textDicts[d]
                    if tick in textDict and textDict[tick] in self._children:
                        t = textDict.pop(tick)
                        t.x, t.y, t.z = p2.x, p2.y, p2.z
                    else:
                        t = Text(self,text, p2.x,p2.y,p2.z, 'sans')
                    # add to dict 
                    newTextDicts[d][tick] = t                    
                    # set other properties right
                    t.visible = True
                    if t.fontSize != axes._tickFontSize:
                        t.fontSize = axes._tickFontSize
                    t.textColor = axes._axisColor
                    if d==2:
                        t.valign = 0
                        t.halign = 1
                    else: 
                        if isTwoDCam:
                            if d==1:
                                t.halign = 1
                                t.valign = 0
                            else:
                                t.halign = 0
                                t.valign = -1
                        elif vector_s.y*vector_s.x >= 0:
                            t.halign = -1
                            t.valign = -1
                        else:
                            t.halign = 1
                            t.valign = -1
                
                # We should hide this last tick if it sticks out
                if isTwoDCam and d==0:
                    # prepare text object to produce _vertices and _screenx
                    t._Compile()
                    t.OnDraw()
                    # get positions
                    fig = axes.GetFigure()
                    if fig:
                        tmp1 = fig.position.width
                        tmp2 = t._screenx + t._vertices1[:,0].max() / 2
                        # apply
                        if t._vertices1 and tmp1 < tmp2:
                            t.visible = False
                
                # get gridlines
                if drawGrid[d] or drawMinorGrid[d]:
                    # get more gridlines if required
                    if drawMinorGrid[d]:
                        ticks = self._GetTicks(tickUnit/5, lim)
                    # get positions
                    for tick in ticks:
                        # get tick location
                        p1 = firstCorner.Copy()
                        p1[d] = tick
                        # add gridlines
                        p3 = p1+gv1
                        p4 = p3+gv2
                        ppg.Append(p1);  ppg.Append(p3)
                        if not isTwoDCam:
                            ppg.Append(p3);  ppg.Append(p4)
            
            # correct gridlines if twodcam so they are all at 0
            # the grid is always exactly at 0. Images are at -0.1 or less.
            # lines and poins are at 0.1
            if isTwoDCam:
                ppg.data[:,2] = 0.0
            
            # clean up the text objects that are left
            for tmp in self._textDicts:                
                for t in tmp.values():
                    t.Destroy()
            
            # for next time ...
            self._textDicts = newTextDicts
            
            # store drawing set for screen coordinate
            self._pps = pps
            
            # prepare for drawing lines
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)        
            gl.glVertexPointerf(ppc.data)        
            # draw lines
            clr = axes._axisColor
            gl.glColor(clr[0], clr[1], clr[2])
            gl.glLineWidth(self._lineWidth)
            gl.glDrawArrays(gl.GL_LINES, 0, len(ppc))        
            # clean up
            gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
            
            # prepare for drawing grid
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)        
            gl.glVertexPointerf(ppg.data)        
            # set stipple pattern
            if not axes.gridLineStyle in lineStyles:
                stipple = False
            else:
                stipple = lineStyles[axes.gridLineStyle]
            if stipple:
                gl.glEnable(gl.GL_LINE_STIPPLE)
                gl.glLineStipple(1, stipple)
            # draw gridlines
            clr = axes._axisColor
            gl.glColor(clr[0], clr[1], clr[2])
            gl.glLineWidth(self._lineWidth)            
            gl.glDrawArrays(gl.GL_LINES, 0, len(ppg))        
            # clean up
            gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
            gl.glDisable(gl.GL_LINE_STIPPLE)
            
        except Exception:
            self.Destroy()
            raise
        
    
    
    def OnDrawScreen(self):
        # Actually draw the axis
        
        axes = self.GetAxes()
        if not axes:
            return
        if not axes._axis:
            return
        
        # get pointset
        if not hasattr(self, '_pps'):
            return
        pps = self._pps
        pps[:,2] = depthToZ( pps[:,2] )
        
        # prepare for drawing lines
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(pps.data)
        if axes.camera is axes._cameras['twod']:
            gl.glDisable(gl.GL_LINE_SMOOTH)
        # draw lines
        clr = axes._axisColor
        gl.glColor(clr[0], clr[1], clr[2])
        gl.glLineWidth(self._lineWidth)
        gl.glDrawArrays(gl.GL_LINES, 0, len(pps))
        # clean up
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnable(gl.GL_LINE_SMOOTH)
    
    
    def _GetTicks(self, tickUnit, lim):
        firstTick = np.ceil(  lim.min/tickUnit ) * tickUnit
        lastTick  = np.floor( lim.max/tickUnit ) * tickUnit
        count = 0
        ticks = [firstTick]
        while ticks[-1] < lastTick-tickUnit/2:
            count += 1
#             tmp = firstTick + count*tickUnit
#             if abs(tmp/tickUnit) < 10**-10:
#                 tmp = 0 # due round-off err, 0 can otherwise be 0.5e-17 or so
#             ticks.append(tmp)
            ticks.append( firstTick + count*tickUnit )
        return ticks
    
    def _NextCornerIndex(self, i, d, vector_s):
        if d<2 and vector_s.x >= 0:
            i+=self._delta
        elif d==2 and vector_s.y < 0:
            i+=self._delta
        else:
            i-=self._delta
        if i>3: i=0
        if i<0: i=3
        return i


class AxisLabel(Text):
    """ AxisLabel(parent, text)
    A special label that moves itself just past the tickmarks. 
    The _textDict attribute should contain the Text objects of the tickmarks.
    
    This is a helper class.
    """
    
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self._textDict = {}
        self._move = 0
    
    def OnDrawScreen(self):
        
        # get current position
        pos = Point(self._screenx, self._screeny)
        
        # get normal vector eminating from that position
        if int(self.textAngle) == 90:            
            a = (self.textAngle + 90) * np.pi/180
            self.valign = 1
            distance = 8
        else:
            a = (self.textAngle - 90) * np.pi/180
            self.valign = -1
            distance = 3
        normal = Point(np.cos(a), np.sin(a)).Normalize()
        
        # project the corner points of all text objects to the normal vector.
        def project(p,normal):
            p = p-pos
            phi = abs(normal.Angle(p))
            return float( p.Norm()*np.cos(phi) )
        # apply
        alpha = []          
        for text in self._textDict.values():
            if text is self:
                continue
            if text._vertices2 is None or not len(text._vertices2):
                continue            
            x,y = text._screenx, text._screeny
            xmin, xmax = text._deltax
            ymin, ymax = text._deltay
            alpha.append( project(Point(x+xmin, y+ymin), normal) )
            alpha.append( project(Point(x+xmin, y+ymax), normal) )
            alpha.append( project(Point(x+xmax, y+ymin), normal) )
            alpha.append( project(Point(x+xmax, y+ymax), normal) )
        
        # establish the amount of pixels that we should move along the normal.
        if alpha:
            self._move = distance+max(alpha)
        
        # move in the direction of the normal
        tmp = pos + normal * self._move
        self._screenx, self._screeny = int(tmp.x+0.5), int(tmp.y+0.5)
        
        # draw and reset position
        Text.OnDrawScreen(self)
        self._screenx, self._screeny = pos.x, pos.y
        
#         # debug ...
#         if True:
#             pp=Pointset(2)
#             pp.Append(pos)
#             pp.Append(pos+normal*60)
#             for a in alpha:            
#                 pp.Append(pos+normal*a)            
#             if not hasattr(self, '_tmp'):
#                 self._tmp =Line(self, pp)
#             else:
#                 self._tmp.points = pp
#             self._tmp.OnDraw()



class Legend(simpleWibjects.DraggableBox):
    """ Legend(parent)
    A legend is a wibject that should be a child (does not have
    to be the direct child) of an axes. It displays a description for 
    each line in the axes, and is draggable.
    """
    
    def __init__(self, parent):
        simpleWibjects.DraggableBox.__init__(self, parent)
        
        # params for the layout
        self._linelen = 40
        self._xoffset = 10        
        self._yoffset = 3        
        self._yspacing = 16
        
        # position in upper left by default
        self.position = 10, 10
        self.bgcolor = 'w'
        
        # start with nothing
        self._stringList = []
        self.visible = False
        
        # by creating a _wobjects attribute, we are allowed to hold
        # wobjects, but our ourselves responsible for drawing them
        self._wobjects = []
    
    
    def _AddLineAndLabel(self):
        """ Add a line and label to our pool. """
        # get y position
        index = len(self._wobjects)
        y = self._yoffset + self._yspacing * (index)        
        # create label
        label = Label(self)
        label.bgcolor=''
        label.position = self._xoffset*2 + self._linelen, y        
        y2 = label.position.h / 2
        # create 2-element pointset
        pp = Pointset(2)
        pp.Append(self._xoffset, y + y2)
        pp.Append(self._xoffset + self._linelen, y + y2)
        # create line
        line = Line(self, pp) # line has no parent        
        # return
        return line, label
    
    
    def SetStrings(self, *stringList):
        """ SetStrings(*stringList)
        Set the strings of the legend labels.
        """
        
        # test
        if len(stringList)==1 and isinstance(stringList[0],(tuple,list)):
            stringList = stringList[0]
        for value in stringList:
            if not isinstance(value, basestring):
                raise ValueError("Legend string list should only contain strings.")
        
        # store
        self._stringList = stringList
        
        # clean up labels and lines
        for line in [line for line in self._wobjects]:
            line.Destroy()
        for label in self.children:
            label.Destroy()
        
        # find axes
        axes = self.parent
        while axes and not isinstance(axes, Axes):
            axes = axes.parent
        if not axes:
            return
        
        # create new lines and labels
        maxWidth = 0
        for ob in axes._wobjects:
            if len(self._wobjects) >= len(stringList):
                break
            if not isinstance(ob, Line):
                continue
            # get new line and label
            line, label = self._AddLineAndLabel() # adds to lists
            # apply line properties
            line.ls, line.lc, line.lw = ob.ls, ob.lc, ob.lw
            line.ms, line.mc, line.mw = ob.ms, ob.mc, ob.mw
            line.mec, line.mew = ob.mec, ob.mew
            # apply text to label
            nr = len(self._wobjects)-1
            label.text = stringList[nr]
            label._Compile()
            label._PositionText()
            label.position.w = (label._deltax[1]-label._deltax[0])+2
            maxWidth = max([maxWidth, label.position.w ])
        
        # make own size ok
        if self._wobjects:
            pos = label.position
            self.position.w = maxWidth + pos.x + self._xoffset
            self.position.h = pos.bottom + self._yoffset
            self.visible = True
        else:
            self.visible = False
    
    
    def OnDraw(self):
        
        # draw box 
        simpleWibjects.DraggableBox.OnDraw(self)
        
        # draw lines        
        for line in self._wobjects:
            line.OnDraw()
        
        # reset some stuff that was set because it was thinking it was drawing
        # in world coordinates.
        gl.glDisable(gl.GL_DEPTH_TEST)
    
    
    def OnDestroy(self):
        simpleWibjects.DraggableBox.OnDestroy(self)
        
        # clear lines and such
        for ob in [ob for ob in self._wobjects]:
            ob.Destroy()
    