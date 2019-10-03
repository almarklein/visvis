# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module baseFigure

Defines the BaseFigure class, which is the root of the drawing context,
and is associated with an OpenGL context.

This module also defines a few helper classes for the Figure.

"""

import OpenGL.GL as gl

import time
import numpy as np

import visvis
#
from visvis.core import base
from visvis.core.base import DRAW_NORMAL, DRAW_FAST, DRAW_SHAPE, DRAW_SCREEN  # noqa
from visvis.core.misc import Property, PropWithDraw, DrawAfter
from visvis.core.misc import getOpenGlInfo
from visvis.core import events
#
from visvis.core.cameras import ortho
from visvis.text import BaseText
from visvis.core.line import MarkerManager
from visvis.core.axes import _BaseFigure, AxesContainer, Axes, Legend
from visvis.core.axes import _Screenshot


# a variable to indicate whether to show FPS, for testing
printFPS = False


class ObjectPickerHelper(object):
    """ ObjectPickerHelper()
    
    A simple class to help picking of the objects.
    An instance of this is attached to each figure.
    
    Picking in visvis is done using the approach proposed in chapter 14 of
    the 6th edition of the Red Book: rendering to the backbuffer using a
    particular color per object.
    
    Another possible approach is gluPickMatrix. Although the backbuffer
    approach might be a bit slower, it is easier than the pickmatrix approach
    and allows more control over what objects you want to be able to pick.
    
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
    
    def CaptureScreen(self):
        self.screen = np.flipud( _Screenshot() )
    
    def ClearScreen(self):
        self.screen = None
    
    def GetItemsUnderMouse(self, figure):
        """ Detect over which objects the mouse is now.
        """
        # make sure screen exists
        if self.screen is None:
            self.screen = np.zeros((1,1),dtype=np.float32)
        
        # get shape and position of mouse
        shape = self.screen.shape
        x, y = figure.mousepos
        x = int(x * figure._devicePixelRatio)
        y = int(y * figure._devicePixelRatio)
         
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
            #print(id)
        
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



class BaseFigure(_BaseFigure):
    """ BaseFigure()
    
    Abstract class representing the root of all wibjects.
    
    A Figure is a wrapper around the OpenGL widget in which it is drawn;
    this way different backends are possible. Each backend inherits this
    class and implements the required methods and makes sure all GUI
    events are translated to visvis events.
    
    Since the figure represents the OpenGl context and is the root
    of the visualization tree; a Figure Wibject does not have a parent.
    
    A Figure can be created with the function vv.figure() or vv.gcf().
    
    """
    
    # dictionary of all figures objects: int -> Figure instance
    _figures = {}
    # the current figure object
    _currentNr = None
    
    def __init__(self):
        """ The init will be oveloaded in the subclasses,
        but they should call this init from there.
        """
        base.Wibject.__init__(self, None)
        
        # register
        self._Register()
        
        # Make sure we have _devicePixelRatio
        if not hasattr(self, "_devicePixelRatio"):
            self._devicePixelRatio = 1.0
        
        # to prevent recursion
        self._resizing = False
        
        # create a timer to handle the drawing better
        self._drawTimer = events.Timer(self, 10, oneshot=True)
        self._drawTimer.Bind(self._DrawTimerTimeOutHandler)
        self._drawtime = time.time() # to calculate fps
        self._drawWell = -1
        
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
        self._fontManager = visvis.text.FontManager()
        self._relativeFontSize = visvis.settings.defaultRelativeFontSize
        
        # Whether to enable user interaction
        self._enableUserInteraction = True
        
        # To store the markers used in this figure
        self._markerManager = MarkerManager()
        
        # keep track of the currently active axes of this figure.
        self._currentAxes = None
        
        # Create events that only the figure has
        self._eventClose = events.BaseEvent(self)
        self._eventAfterDraw = events.BaseEvent(self)
        
        # Bind to events
        self.eventPosition.Bind(self._OnPositionChange)
    
    
    @property
    def eventClose(self):
        """ Fired when the figure is closed.
        """
        return self._eventClose
    
    @property
    def eventAfterDraw(self):
        """ Fired after each drawing pass.
        """
        return self._eventAfterDraw
    
    
    def _Register(self):
        """ _Register()
        
        Register the figure with the list of figures.
        
        """
        
        # get keys
        nrs = list(BaseFigure._figures.keys())
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
    
    
    def _dpi_aware_viewport(self, x, y, w, h):
        pr = self._devicePixelRatio
        gl.glViewport(int(x * pr), int(y * pr), int(w * pr), int(h * pr))
    
    def _normal_ortho(self, *args):
        # For when drawing in screen coords
        ortho(*args)
    
    def _dpi_aware_ortho(self, *args):
        # For when drawing in screen coords
        pr = self._devicePixelRatio
        #gl.glScale(pr, pr, 1.0)
        args = [a * pr for a in args]
        ortho(*args)
        
    ## Methods to overload
    # To create a subclass for a specific backend:
    # - Overload the methods below.
    # - Make sure Draw() is called on each paint request.
    # - Pass the events on and keep visvis timers running.
    
    def _SetCurrent(self):
        """ _SetCurrent()
        
        Make the figure the current OpenGL context. This is required before
        drawing and before doing anything with OpenGl really.
        
        """
        raise NotImplementedError()
    
    def _SwapBuffers(self):
        """ _SwapBuffers()
        
        Swap the memory and screen buffer such that
        what we rendered appears on the screen.
        
        """
        raise NotImplementedError()
    
    def _ProcessGuiEvents(self):
        """ _ProcessGuiEvents()
        
        Process all events in the event queue.
        This is usefull when calling Draw() while an algorithm is
        running. The figure is then still responsive.
        
        """
        raise NotImplementedError()
        
    def _SetTitle(self, title):
        """ _SetTitle(title)
        
        Set the title of the figure. Note that this
        does not have to work if the Figure is used as
        a widget in an application.
        
        """
        raise NotImplementedError()
    
    def _SetPosition(self, x, y, w, h):
        """ _SetPosition(x, y, w, h)
        
        Set the position of the widget. The x and y represent the
        screen coordinates when the figure is a toplevel widget.
        
        For embedded applications they represent the position within
        the parent widget.
        
        """
        raise NotImplementedError()
    
    def _GetPosition(self):
        """ _GetPosition()
        
        Get the position of the widget. The result must be a
        four-element tuple (x,y,w,h).
        
        """
        raise NotImplementedError()
    
    
    def _Close(self):
        """ _Close()
        
        Close the widget, also calls Destroy().
        
        """
        raise NotImplementedError()
    
    ## Properties
    
    @PropWithDraw
    def devicePixelRatio():
        """ The scale factor for high-DPI displays. This value is usually
        1 (for normal display) or 2 (for retina displays). When using a Qt-based
        backend, this value will usually be set correctly.
        """
        def fget(self):
            return self._devicePixelRatio
        def fset(self, value):
            self._devicePixelRatio = float(value)
        return locals()
    
    @Property
    def parent():
        """ The parent of a figure always returns None and cannot be set.
        """
        def fget(self):
            return None
        def fset(self, value):
            pass
            #raise AttributeError("The parent of a figure cannot be set.")
            # do not raise an exception, as the parent is always ste in
            # the constructor of the BaseObject.
        return locals()
    
    @property
    def nr(self):
        """ Get the number (id) of this figure.
        """
        for key in BaseFigure._figures:
            if BaseFigure._figures[key] is self:
                return key
    
    @PropWithDraw
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
        return locals()
    
    
    def MakeCurrent(self):
        """ MakeCurrent()
        
        Make this the current figure.
        Equivalent to "vv.figure(fig.nr)".
        
        """
        BaseFigure._currentNr = self.nr
    
    
    @PropWithDraw
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
                self._currentAxes = curNew.GetWeakref()
            else:
                self._currentAxes = None
            return curNew
        
        def fset(self, value):
            if value is None:
                self._currentAxes = None
            elif isinstance(value, Axes):
                self._currentAxes = value.GetWeakref()
            else:
                raise ValueError('currentAxes must be an Axes instance (or None).')
        
        return locals()
    
    
    @property
    def underMouse(self):
        """ Get the object currently under the mouse. Can be None.
        """
        if not self._underMouse:
            return None
        return self._underMouse[-1]()
    
    @property
    def mousepos(self):
        """ Get the position of the mouse in figure coordinates.
        """
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
    
    @Property # Moving a figure always invokes an update from the window manager
    def position():
        """ The position for the figure works a bit different than for
        other wibjects: it only works with absolute values and it
        represents the position on screen or the position in the
        parent widget in an application.
        """
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
        
        return locals()
    
    
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
        # Draw, but not too soon.
        self.Draw(timeout=200)
    
    
    @PropWithDraw
    def relativeFontSize():
        """ The (global) relative font size; all texts in this figure
        are scaled by this amount. This is intended to (slighly) increase
        or descrease font size in the figure for publication purposes.
        """
        def fget(self):
            return self._relativeFontSize
        def fset(self, value):
            # Set value
            self._relativeFontSize = float(value)
            # Update all text objects
            for ob in self.FindObjects(BaseText):
                ob.Invalidate()
            # Update all legend objects
            for ob in self.FindObjects(Legend):
                ob.SetStrings(ob._stringList)
        return locals()
    
    @Property
    def enableUserInteraction():
        """ Whether to allow user interaction. The default is True. This
        property can be set to False to improve performance (expensive
        calls to glDrawPixels can be omitted).
        """
        def fget(self):
            return self._enableUserInteraction
        def fset(self, value):
            self._enableUserInteraction = bool(value)
        return locals()
    
    ## Extra methods
    
    @DrawAfter
    def Clear(self):
        """ Clear()
        
        Clear the figure, removing all wibjects inside it and clearing all
        callbacks.
        
        """
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
        # Restore some event bindings
        self.eventPosition.Bind(self._OnPositionChange)
    
    ## Implement methods
    
    
    def Destroy(self):
        """ Destroy()
        
        Close the figure and clean up all children.
        
        """
        if self._widget is None:
            #raise RuntimeError('Attempt to Destroy a dead Figure.')
            # Do not raise error, because we make Wibject.__del__ call Destroy
            return
        
        # Fire event to notify closing while everything is still intact
        self.eventClose.Fire()
        
        # Clean up
        base.Wibject.Destroy(self)
        
        # Detach reference to backend widget. We need to keep the widget
        # alive because we are not allowed to destroy it during its
        # callback.
        # So we place a reference somewhere, meaning that the widget (and
        # thus the Figure instance can be cleaned up after a second figure
        # has been destroyed. In other words, there will never be more than
        # one destroyed alive Figure instance (if the user cleans up its
        # references).
        # Note that WX really removes the widget and replaces it with a
        # dummy wrapper.
        BaseFigure._lastClosedWidget = w = self._widget
        self._widget = None
        w.figure = None
        
        # Close widget
        self._Close(w)
    
    
    def OnDestroy(self):
        # remove from list
        for nr in list(BaseFigure._figures.keys()):
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
        
        # Only if not currently being drawn
        if self._isbeingdrawn:
            return False
        
        # Get whether the request is to draw well
        well = not fast
        
        # Set draw well (is reciprocal of fast, to handle it easier.)
        # -1 means it is unset, and when a paint event occurs, will draw well
        # 0 means to draw fast, will only occur if only Draw(True) calls
        # 1 means draw well.
        if self._drawWell == -1:
            self._drawWell = well
        else:
            self._drawWell = self._drawWell or well
        
        # Restart timer if we need to
        if not self._drawTimer.isRunning:
            self._drawTimer.Start(timeout)
        
        # Done
        return True
    
    
    def _DrawTimerTimeOutHandler(self, event=None):
        self._RedrawGui() # post event
    
    
    def DrawNow(self, fast=False):
        """ DrawNow(fast=False)
        
        Draw the figure right now and let the GUI toolkit process its events.
        Call this from time to time if you want to update your figure while
        running some algorithm, and let the figure stay responsive.
        
        """
        self._drawWell = not bool(fast)
        self._RedrawGui() # post event
        self._ProcessGuiEvents() # process all events (including our draw)
    
    
    def OnDraw(self, event=None):
        """ OnDraw()
        
        Perform the actual drawing. Called by the GUI toolkit paint event
        handler. Users should not call this method, but use
        Draw() or DrawNow().
        
        """
        # This is the actual draw entry point. But we will
        # call _Draw() to draw first the beatiful pictures and then
        # again to only draw the shapes for picking.
        
        # are we alive?
        if self._destroyed:
            return
        
        # Init drawing
        self._isbeingdrawn = True
        
        try:
            # calculate fps
            dt = time.time() - self._drawtime
            self._drawtime = time.time()
            if printFPS:
                print('FPS: %1.1f' % (1.0/dt))  # for testing
            
            # get whether to draw fast and reset drawWell flag
            fast = self._drawWell == 0
            self._drawWell = -1
            
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
            if self._enableUserInteraction:
                self._Draw(DRAW_SHAPE)
                gl.glFinish() # call finish, normally swapbuffers does this...
            
            # read screen (of backbuffer)
            # We can improve performance if we do not capture the screen here
            if self._enableUserInteraction:
                self._pickerHelper.CaptureScreen()
            else:
                self._pickerHelper.ClearScreen()
            #self._SwapBuffers() # uncomment to see the color coded objects
            
            # draw picture
            mode = [DRAW_NORMAL, DRAW_FAST][bool(fast)]
            self._Draw(mode)
            
            # write the output to the screen
            self._SwapBuffers()
            
            # Notify
            self.eventAfterDraw.Fire()
        
        finally:
            self._isbeingdrawn = False
    
    
    def _Draw(self, mode):
        """ _Draw(mode)
        
        This method performs a single drawing pass. Used by OnDraw().
        
        """
        
        # make sure the part to draw to is ok
        w,h = self.position.size
        
        # clear screen
        
        # init pickerhelper as one
        pickerHelper = None
        
        if mode==DRAW_SHAPE:
            # clear
            clr = (0,0,0)
            gl.glClearColor(0.0 ,0.0 ,0.0, 0.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            
            # do not blend not light
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
            
            # Set lighting model properties.
            # - We do not use the global ambient term
            # - We do not use local viewer mode
            # - We want to allow people to see also backfaces correctly
            # - We want to be texture-proof for specular highlights
            # Note: Individual lights are set in the camera class.
            glVersion = getOpenGlInfo()[0]
            gl.glLightModelfv(gl.GL_LIGHT_MODEL_AMBIENT, (0,0,0,1))
            gl.glLightModelf(gl.GL_LIGHT_MODEL_LOCAL_VIEWER, 0.0)
            gl.glLightModelf(gl.GL_LIGHT_MODEL_TWO_SIDE, 1.0)
            if glVersion >= '1.2':
                gl.glLightModelf(gl.GL_LIGHT_MODEL_COLOR_CONTROL,
                    gl.GL_SEPARATE_SPECULAR_COLOR)
            
            # enable blending, so lines and points can be antialiased
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            #gl.glEnable(gl.GL_MULTISAMPLE)
            # smooth lines
            gl.glEnable(gl.GL_LINE_SMOOTH)
            if mode==DRAW_FAST:
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
                self._PrepateForFlatDrawing(w, h)
                child._DrawTree(mode, pickerHelper)
        
        # Draw other children
        self._PrepateForFlatDrawing(w, h)
        for child in self._children:
            if not isinstance(child, (Axes, AxesContainer)):
                child._DrawTree(mode, pickerHelper)

    
    def _PrepateForFlatDrawing(self, w, h):
        
        # Set viewport
        gl.glDisable(gl.GL_DEPTH_TEST)
        self._dpi_aware_viewport(0, 0, w, h)
        
        # set camera
        # Flip up down because we want y=0 to be on top.
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        self._normal_ortho(0, w, h, 0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
    
    
    def _GenerateKeyEvent(self, eventName, *eventArgs):
        """ _GenerateKeyEvent(eventName, *eventArgs)
        
        For the backend to generate key events.
        
        """
        if not self._enableUserInteraction:
            return
        
        # make lower
        eventName = eventName.lower()
        # get items now under the mouse
        items1 = [item() for item in self._underMouse if item()]
        # init list of events to fire
        events = []
        eventToAlwaysFire = None
        
        # Check what to fire
        if eventName.count('down'):
            eventToAlwaysFire = self.eventKeyDown
            if items1:
                events.append(items1[-1].eventKeyDown)
        elif eventName.count('up'):
            eventToAlwaysFire = self.eventKeyUp
            if items1:
                events.append(items1[-1].eventKeyUp)
        
        # Fire events. We use an approach to ensure that the key event
        # is always fired for the Figure, but only once, not if that event
        # was fired because it propagated from its children.
        if eventToAlwaysFire:
            eventToAlwaysFire._isFired = False
        for event in events:
            event.Fire(*eventArgs)
        if eventToAlwaysFire and not eventToAlwaysFire._isFired:
            eventToAlwaysFire.Fire(*eventArgs)
    
    
    def _GenerateMouseEvent(self, eventName, *eventArgs):
        """ _GenerateMouseEvent(eventName, *eventArgs)
        
        For the backend to generate mouse events.
        
        """
        if not self._enableUserInteraction:
            return
        
        # make lower
        eventName = eventName.lower()
        # get items now under the mouse
        items1 = [item() for item in self._underMouse if item()]
        # init list of events to fire
        events = []
        
        if eventName.count("motion") or eventName.count("move"):
            
            # Set current mouse pos, so that it's up to date
            self._mousepos = eventArgs[0], eventArgs[1]
            
            # also get new version of items under the mouse
            items2 = self._pickerHelper.GetItemsUnderMouse(self)
            
            # init event list
            events = []
            
            # analyse for enter and leave events
            for item in items1:
                if item not in items2:
                    events.append(item.eventLeave)
            for item in items2:
                if item not in items1:
                    events.append(item.eventEnter)
            
            # Generate motion events for any objects that have handlers
            # for the motion event. Note that this excludes "self".
            items = self.FindObjects(lambda i:i.eventMotion.hasHandlers)
            events.extend([item.eventMotion for item in items])
            
            # Always generate motion event from figure
            events.append(self.eventMotion)
            
            # Update items under the mouse
            self._underMouse = [item.GetWeakref() for item in items2]
            
            # Note: how to handle motionEvents
            # It feels nicer (and is more Qt-ish) to fire the events only
            # from the objects that have their mouse pressed down. However,
            # someone may want to be notified of motion regardless of the
            # state of the mouse. Qt has setMouseTracking(True).
            # But then there's a problem. This version of eventMotion we *do*
            # want to propate to parent objects if not handled. But then
            # an object may get an event twice if the mouse is pressed down.
            # Surely these things can be overcome, but I think its easier
            # for everyone if we stick to the old approach: the eventMotion
            # is fired for all objects that have handlers registered to it.
        
        elif eventName.count("up"):
            # Find objects that are currently clicked down
            items = self.FindObjects(lambda i:i._mousePressedDown)
            if self._mousePressedDown: items.append(self)
            events.extend([item.eventMouseUp for item in items])
            # todo: Also generate event where the mouse is now over - MouseDrop?
            #if items[-1] not in items:
            #    events.append( items[-1].eventMouseDrop)
        
        elif items1 and eventName.count("down"):
            events.append(items1[-1].eventMouseDown)
        
        elif items1 and eventName.count("double"):
            # Note: we cannot detect double clicking by timing the down-events,
            # because the toolkit won't fire a down event for the second click.
            events.append(items1[-1].eventDoubleClick)
        
        elif items1 and eventName.count('scroll'):
            events.append(items1[-1].eventScroll)
        
        # Fire events
        for event in events:
            event.Fire(*eventArgs)
