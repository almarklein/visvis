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
import textures
from cameras import TwoDCamera, PolarCamera, FlyCamera
from misc import Position, Property, Range, OpenGLError
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
        self.items = []     # variable to list the found items
        
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
        #x,y = 0,0
        #w,h = figure.GetSize()
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
        self.items = [figure]  # figure is always at the bottom
        if id:
            self._walkTree(id, figure._children)
            #print id
        
        # return result
        return self.items
       
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
    
    def _walkTree(self, id, children):
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
                self.items.append(child)
                break
            elif id > child._id:
                if not child2:
                    # last child
                    self.items.append(child)
                    if hasattr(child,'_wobjects'):
                        self._walkTree(id, child._wobjects)
                    self._walkTree(id, child._children)
                elif id < child2._id:
                    # the child is a subchild!                    
                    self.items.append(child)
                    if hasattr(child,'_wobjects'):
                        self._walkTree(id, child._wobjects)
                    self._walkTree(id, child._children)
                else:
                    continue



class BaseFigure(base.Wibject):
    """ Figure class - the root of all wibjects.
    A Figure is a wrapper around the OpenGL widget in
    which it is drawn. This way different backends are possible. 
    Events native to the GUI library used are translated to visvis 
    events.
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
        self._isdestroyed = False
        
        # to prevent recursion
        self._resizing = False
        
        # init background
        self.bgcolor = 0.8,0.8,0.8  # bgcolor is a property
        
        # Location of the mouse (in pixel coordinates).
        # It is the implementing class' responsibility to 
        # continously updated this.
        self._mousepos = (0,0)
        
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
        self._drawTimer.fast = False
        self._drawtime = time.time() # to calculate fps
    
    @property
    def eventMouseUp(self):
        return self._eventMouseUp
    @property
    def eventMotion(self):
        return self._eventMotion
    @property
    def eventKeyDown(self):
        return self._eventKeyDown
    @property
    def eventKeyUp(self):
        return self._eventKeyUp    
    @property
    def eventClose(self):
        return self._eventClose
    @property
    def eventAfterDraw(self):
        return self._eventAfterDraw
    
    
    def _Register(self):
        """ Register the figure. """ 
        
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
        """ Make this scene the current OpenGL context. 
        """
        raise NotImplemented()
    
    def _SwapBuffers(self):
        """ Swap the memory and screen buffer such that
        what we rendered appears on the screen """
        raise NotImplemented()
    
    def _ProcessEvents(self):
        """ Process all events in the event queue.
        This is usefull when calling Draw() while an algorithm is 
        running. The figure is then still responsive. 
        """
        raise NotImplemented()
        
    def _SetTitle(self, title):
        """ Set the title of the figure. Note that this
        does not have to work if the Figure is uses as
        a widget in an application.
        """
        raise NotImplemented()
    
    def _SetPosition(self, x, y, w, h):
        """ Set the position of the widget. """        
        raise NotImplemented()
    
    def _GetPosition(self):
        """ Get the position of the widget. """        
        raise NotImplemented()
    
    
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
        """ Get the number of this figure. """
        for key in BaseFigure._figures:
            if BaseFigure._figures[key] is self:
                return key
    
    @property
    def currentAxes(self):
        """ Get the currently active axes of this figure. 
        Return None if no axes are present.
        """
        
        # init 
        ca = None       
        
        # check 
        for child in self._children:
            if not isinstance(child, Axes):
                continue
            if not ca:
                ca = child
            if child is self._currentAxes:
                ca = child
                break                
        
        # update and return
        self._currentAxes = ca
        return ca
        
    
    @property
    def underMouse(self):
        """ Get the object currently under the mouse. Can be None."""
        if not self._underMouse:
            return None
        return self._underMouse[-1]
    
    @property
    def mousepos(self):
        """ Get the position of the mouse in the figure. """
        return self._mousepos
    
    @Property
    def position():
        """ The position for the figure works a bit different than for
        other wibjects. For one, it only works with absolute values.
        It represents the position on screen or the position in the 
        parent widget in an application. """
        def fget(self):
            self._position = pos = Position(self._GetPosition())
            pos._owner = self
            return pos
        def fset(self,value):
            # allow setting x and y only
            if isinstance(value,(tuple,list)) and len(value) == 2:
                value = value[0], value[1], self._position.w, self._position.h
            # make pos 
            self._position = Position(value)
            # don't make absolute: negative screen coordinates may also occur!
            # apply            
            self.eventPosition.Fire()
    
    def _OnPositionChange(self,event=None):
        """ When the position was programatically changed, we should
        change the position of the window. 
        But ONLY if it was really changed (or we get into infinite loops).
        """
        
        #if self._resizing:
        #    return
        pos1 = self._GetPosition()
        pos2 = tuple( [int(i) for i in self._position.AsTuple()] )
        if pos1 != pos2:
            self._SetPosition( *pos2 )
    
    def _OnResize(self, event=None):
        """ Called when the figure is resized.
        This should initiate the event_position event, but not by firing
        the event_position of this object, otherwise it is not propagated.
        """        
        self.position._Changed()
    
    
    ## Extra methods
    
    def GetSize(self):
        """ Get the size of the figure. """
        # overload from wibject to deal with the position that 
        # is a bit different
        pos = self._GetPosition()
        return pos[2], pos[3]
    
    def Clear(self):
        """ Clear the figure. """        
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
        """ Clean up. """
        # set flag, also make a draw in the next 10 ms, to
        # remove the reference to the widget
        self._isdestroyed = True
        self.Draw()
        # remove from list
        for nr in BaseFigure._figures.keys():
            if BaseFigure._figures[nr] is self:
                BaseFigure._figures.pop(nr)
                BaseFigure._currentFigure = None
                break
    
    
    def Draw(self, fast=False):
        """ Draw the figure. Collects draw commands
        and only draws every 10 ms.
        """
        # set fast (use the timer for that)
        self._drawTimer.fast = fast        
        # if never drawn, draw now, this is required in WX, otherwise
        # a lot of OpenGL functions won't work...
        if not hasattr(self._drawTimer, '_drawnonce'):
            # call directly
            self._drawTimer._drawnonce= True
            self.OnDraw()
        if not self._drawTimer.isRunning:
            # restart timer
            self._drawTimer.Start()

    def DrawNow(self, fast=False):
        """ Draw the figure now and let the GUI toolkit process its events.
        Use this if you want to update your figure while running some
        algorithm, the figure stays responsive if you call this method now
        and then. Does not seem to work for wx though.
        """
        # proccess events
        self.OnDraw(fast)
        self._ProcessEvents()
    
    
    def OnDraw(self, event=None):
        """ This is the actual draw entry point. But we will 
        call _Draw() to draw first the beatiful pictures and then
        again to only draw the shapes for picking. 
        """
        # are we alive?
        if self._isdestroyed:           
            return
        
        # calculate fps
        dt = time.time() - self._drawtime
        self._drawtime = time.time()
        if printFPS:
            print 'FPS: ', 1.0/dt  # for testing
        
        # get fast
        fast = self._drawTimer.fast
        
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
        
        # make sure the part to draw to is ok               
        w,h = self.GetSize()
        
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
            if isinstance(child, Axes):
                child._DrawTree(mode, pickerHelper)
        
        ## Draw more
        
        # prepare for flat drawing
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glViewport(0, 0, w, h)
        
        # set camera
        gl.glMatrixMode(gl.GL_PROJECTION)        
        gl.glLoadIdentity()        
        gl.glOrtho( 0, w, h, 0, -100000, 100000 )
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # draw other children
        for child in self._children:
            if not isinstance(child, Axes):
                child._DrawTree(mode, pickerHelper)

    
    def _GenerateMouseEvent(self, eventName, x, y, button=0):
        """ For the backend to generate mouse events. 
        """
        
        # make lower
        eventName = eventName.lower()
        # get items now under the mouse
        items1 = self._underMouse
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
            
            # update
            self._underMouse = items2
        
        elif items1 and eventName.count("down"):            
            item = items1[-1]
            events.append( ( item, item.eventMouseDown) )
        elif items1 and eventName.count("up"):
            item = items1[0]
            events.append( ( item, item.eventMouseUp) )
        elif items1 and eventName.count("double"):
            item = items1[-1]
            events.append( ( item, item.eventDoubleClick) )
        
        # fire events
        for item,ev in events:
            # determine axes
            if isinstance(item, base.Wobject):
                axes = item.GetAxes()
                if not axes:
                    continue
            ev.Clear()
            ev.button = button
            if isinstance(item, base.Wibject):
                # use relative coordinates
                ev.x, ev.y = item.AbsoluteToRelative(x, y)
            elif isinstance(item, base.Wobject):
                # use axes coordinates
                ev.x, ev.y = axes.AbsoluteToRelative(x, y)
            if isinstance(item, (base.Wobject, Axes )):
                # also give 2D coordinates
                if isinstance(item, Axes):
                    cam = item._cameras['2d']
                else:
                    cam = axes._cameras['2d']
                if item.parent: # or screen to world cannot be calculated
                    ev.x2d, ev.y2d = cam.ScreenToWorld((ev.x, ev.y))
            ev.Fire()


class Axes(base.Wibject):
    """ An Axes contains a scene with a local coordinate frame 
    in which stuff can be drawn. The camera used determines
    how the data is visualized and how the user can interact
    with the data.
    
    The daspect property gives the aspect ratio of the data. It is a three 
    element tuple. The sign of the elements indicate axes being flipped.
    """ 
    
    def __init__(self, figure):
        
        # check that the parent is a figure
        if not isinstance(figure, BaseFigure):
            raise Exception("The given parent for an Axes should be a Figure.")
        base.Wibject.__init__(self, figure)
        
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
        self._tickFontSize = 10
        self._gridLineStyle = ':'
        self._xticks, self._yticks, self._zticks = None, None, None
        self._xgrid, self._ygrid, self._zgrid = False, False, False
        self._xminorgrid, self._yminorgrid, self._zminorgrid =False,False,False
        self._box =  True
        self._axis = True
        
        # create cameras and select one
        self._cameras = {   'twod': TwoDCamera(self), 
                            'polar': PolarCamera(self),
                            'fly': FlyCamera(self)}        
        self._cameras['3d'] = self._cameras['polar']
        self.camera = self._cameras['2d'] = self._cameras['twod']
        
        # init the background color of this axes
        self.bgcolor = 1,1,1  # remember that bgcolor is a property
        
        # bind to event
        self.eventMouseDown.Bind(self._OnMouseDown)
        
        # create Axis and legend
        Axis(self) # is a wobject
        self._legend = Legend(self) # is a wibject
        
        # make current
        figure._currentAxes = self
    
    
    ## Define more methods

    
    def SetLimits(self, rangeX=None, rangeY=None, rangeZ=None):
        """ SetLimits(rangeX=None, rangeY=None, rangeZ=None)
        Set the limits for data visualisation. These are taken as hints 
        to set the camera view. Each range can be None, a 2 element iterable,
        or a visvis.Range object.
        """
        
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
            for ob in self._wobjects:
                
                if isinstance(ob, Line):
                    pp = ob._points
                    if len(pp)==0: continue
                    tmpX = Range( pp[:,0].min(), pp[:,0].max() )
                    tmpY = Range( pp[:,1].min(), pp[:,1].max() )
                    tmpZ = Range( pp[:,2].min(), pp[:,2].max() )
                    
                elif isinstance(ob, textures.Texture2D):
                    if ob._texture1._dataRef is None:
                        continue
                    a = ob._texture1._dataRef
                    if hasattr(a, 'sampling') and hasattr(a, 'origin'):
                        tmpX = Range( a.origin[1], a.shape[1] * a.sampling[1] )
                        tmpY = Range( a.origin[0], a.shape[0] * a.sampling[0] )
                    else:
                        tmpX = Range( 0, a.shape[1] )
                        tmpY = Range( 0, a.shape[0] )
                    tmpZ = None
                
                elif isinstance(ob, textures.Texture3D):
                    if ob._texture1._dataRef is None:
                        continue 
                    a = ob._texture1._dataRef
                    if hasattr(a, 'sampling') and hasattr(a, 'origin'):
                        tmpX = Range( a.origin[2], a.shape[2] * a.sampling[2] )
                        tmpY = Range( a.origin[1], a.shape[1] * a.sampling[1] )
                        tmpZ = Range( a.origin[0], a.shape[0] * a.sampling[0] )
                    else:
                        tmpX = Range( 0, a.shape[2] )
                        tmpY = Range( 0, a.shape[1] )
                        tmpZ = Range( 0, a.shape[0] )
                
                else:
                    continue
                
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
        if not rangeX:
            margin = rX.range * 0.02
            if margin == 0: margin = 0.02
            rX = Range( rX.min-margin, rX.max+margin )
        if not rangeY:
            margin = rY.range * 0.02
            if margin == 0: margin = 0.02
            rY = Range( rY.min-margin, rY.max+margin )
        if not rangeZ:
            margin = rZ.range * 0.02
            if margin == 0: margin = 0.02
            rZ = Range( rZ.min-margin, rZ.max+margin )
        
        # apply to each camera
        for cam in self._cameras.values():
            cam.SetLimits(rX, rY, rZ)
    
    
    def GetLimits(self):
        """ Get the limits of the axes as displayed now. This can differ
        from what was set by SetLimits if the daspectAuto is False. 
        Returns a tuple of limits for x and y, respectively.
        This limits are queried from the twod camera model, even if this
        is not the currently used camera.
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


    def Reset(self):
        """ Reset the cameras. """
        for camera in self._cameras:
            camera.Reset()
    
    
    def Draw(self, fast=False):
        """ Draw contents to screen. 
        Actually calls Draw() on its figure, as the total opengl canvas 
        has to be redrawn. This might change in the future though... """
        figure = self.GetFigure()
        if figure:
            figure.Draw(fast)
    
    
    def Clear(self):
        """ Clear the axes. Removing all wobjects in the scene.
        """
        # remove wobjects
        for w in self.wobjects:
            if hasattr(w,'Destroy'):
                w.Destroy()
        self._wobjects[:] = []
        # remake axis object
        Axis(self)
        # reset other stuff
        self.legend = []
    
    
    @property
    def wobjects(self):
        """ wobjects
        Get a shallow copy of the list of wobjects in the scene. 
        """
        return [child for child in self._wobjects]
    
    
    ## Define more properties

    @Property
    def cameraType():
        """ Get or set the camera to use.
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
        """ Get position of mouse in screen pixels, relative to this
        axes.
        """
        figure = self.GetFigure()
        if not figure:
            return 0,0
        x,y = figure.mousepos
        pos = self.position.InPixels()
        return x-pos[0], y-pos[1]
    
    
    @Property
    def daspect():
        """ Set/Get the data aspect ratio. """
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
        """ If True, the axis are scaled independently, and only the sign
        of the axpect ratio is taken into account. """
        def fget(self):
            return self._daspectAuto
        def fset(self, value):
            self._daspectAuto = bool(value)
    
    
    @Property
    def gridLineStyle():
        """ Show the grid of the axis. """
        def fget(self):
            return self._gridLineStyle
        def fset(self, value):
            if value not in lineStyles:
                raise ValueError("Invalid lineStyle for grid lines")
            self._gridLineStyle = value
            
    @Property
    def showGridX():
        """ Show the grid of the axis. """
        def fget(self):
            return self._xgrid
        def fset(self, value):
            self._xgrid = bool(value)
    
    @Property
    def showGridY():
        """ Show the grid of the axis. """
        def fget(self):
            return self._ygrid
        def fset(self, value):
            self._ygrid = bool(value)
    
    @Property
    def showGridZ():
        """ Show the grid of the axis. """
        def fget(self):
            return self._zgrid
        def fset(self, value):
            self._zgrid = bool(value)
    
    @Property
    def showGrid():
        """ Show/hide the x,y and z grid.  """
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
        """ Show the minor grid of the axis. """
        def fget(self):
            return self._xminorgrid
        def fset(self, value):
            self._xminorgrid = bool(value)
    
    @Property
    def showMinorGridY():
        """ Show the minor grid of the axis. """
        def fget(self):
            return self._yminorgrid
        def fset(self, value):
            self._yminorgrid = bool(value)
    
    @Property
    def showMinorGridZ():
        """ Show the minor grid of the axis. """
        def fget(self):
            return self._zminorgrid
        def fset(self, value):
            self._zminorgrid = bool(value)
    
    @Property
    def showMinorGrid():
        """ Show the minor grid of the axis. """
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
        """ Ticks for the x dimension. If None, they are determined
        automatically. """
        def fget(self):
            return self._xticks
        def fset(self, value):
            self._xticks = value
    
    @Property
    def yTicks():
        """ Ticks for the y dimension. If None, they are determined
        automatically. """
        def fget(self):
            return self._yticks
        def fset(self, value):
            self._yticks = value
    
    @Property
    def zTicks():
        """ Ticks for the z dimension. If None, they are determined
        automatically. """
        def fget(self):
            return self._zticks
        def fset(self, value):
            self._zticks = value
    
    
    @Property
    def showAxis():
        """ Show the the axis. """
        def fget(self):
            return self._axis
        def fset(self, value):
            self._axis = bool(value)
    
    
    @Property
    def showBox():
        """ Show the box of the axis. """
        def fget(self):
            return self._box
        def fset(self, value):
            self._box = bool(value)
    
    @Property
    def tickFontSize():
        """ The font size of the tick marks. """
        def fget(self):
            return self._tickFontSize
        def fset(self, value):
            self._tickFontSize = value
    
    
    @Property
    def xLabel():
        """ The label for the x-dimension. """
        def fget(self):
            return self._xlabel
        def fset(self, value):
            self._xlabel = value
    
    @Property
    def yLabel():
        """ The label for the y-dimension. """
        def fget(self):
            return self._ylabel
        def fset(self, value):
            self._ylabel = value
    
    @Property
    def zLabel():
        """ The label for the z-dimension. """
        def fget(self):
            return self._zlabel
        def fset(self, value):
            self._zlabel = value
    
    @Property
    def legend():
        """ The string labels for the legend. """
        def fget(self):
            return self._legend._stringList            
        def fset(self, value):
            self._legend.SetStrings(value)
    
    @property
    def legendWibject(self):
        """ Get the legend wibject, so for exampe its position
        can be changed programatically. """
        return self._legend
    
    ## Implement methods
    
    def OnDestroy(self):
        """ Clean up. """
        self.Clear()
        # the wibjects are destoyed automatically by the Destroy command.
   
    def OnDraw(self, mode='normal'):
        """ Draw the background of the axes and the wobjects in it.
        """
        
        # size of figure ...
        w,h = self.parent.GetSize()
        
        # find actual position in pixels
        pos = self.position.InPixels((w,h))
        
        # set viewport (note that OpenGL has origin in lower-left, visvis
        # in upper-left)
        gl.glViewport(pos.x, h-pos.y2, pos.w, pos.h)        
        
        gl.glDisable(gl.GL_DEPTH_TEST)
        
        # draw bg
        gl.glMatrixMode(gl.GL_PROJECTION)        
        gl.glLoadIdentity()        
        gl.glOrtho( 0, 1, 0, 1, -1, 1 )
        
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
        
        # draw other stuff        
        for item in self._wobjects:
            if isinstance(item, (Line,)):
                pass # draw later
            else:
                item._DrawTree(mode)
        
        # draw lines AFTER textures, otherwise they don't blend right
        for item in self._wobjects:
            if isinstance(item, Line):
                item._DrawTree(mode)
        
        # set camera to screen coordinates.
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho( pos.x, pos.x2 , h-pos.y2, h-pos.y, -100000, 100000 )
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
            gl.glOrtho(0,w,0,h, -100000, 100000 )
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
        gl.glOrtho( 0, w, h, 0, -1, 1 )
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        self._Transform()
    
    
    def OnDrawShape(self, clr):
        """ Draw shapes of wobjects. """
        
        # get shape
        mode = 'shape'
        pickerHelper = self.GetFigure()._pickerHelper
        
        # get position
        w,h = self.parent.GetSize()
        pos = self.position.InPixels((w,h))
        
        # set viewport (note that OpenGL has origin in lower-left, visvis
        # in upper-left)
        gl.glViewport(pos.x, h-pos.y2, pos.w, pos.h) 
        
        # prepare for drawing background
        gl.glMatrixMode(gl.GL_PROJECTION)        
        gl.glLoadIdentity()        
        gl.glOrtho( 0, 1, 0, 1, -1, 1 )        
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
        gl.glOrtho( 0, pos.w, pos.h, 0, -1, 1 )        
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
    
    
    def OnDrawFast(self):
        self.OnDraw(mode='fast')
        
    def OnDrawPre(self):
        self.OnDraw(mode='pre')
    
    
    def _OnMouseDown(self, event):
        # make current axes
        f = self.GetFigure()
        if f:
            f._currentAxes = self
        

class Axis(base.Wobject):
    """ An Axis object represents the lines and ticks that make
    up an axis. Not to be confused with an Axes, which represents
    a scene and is a Wibject."""
    
    def __init__(self, parent):
        base.Wobject.__init__(self, parent)
        self._color = 0,0,0
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
                tmp = self._children
                for child in tmp:
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
                
                # get range expressed in coords and screen pixels                
                rc = lim.range #vector_c.Norm()
                if rc == 0:
                    continue
                rs = ( vector_s.x**2 + vector_s.y**2 ) ** 0.5
                pixelsPerUnit = rs/rc
                
                # Try all tickunits, starting from the smallest, until we find 
                # one which results in a distance between ticks more that 
                # X pixels.
                try:
                    for tickUnit in self._tickUnits:
                        if tickUnit * pixelsPerUnit >= self._minTickDist:
                            break
                    # if the numbers are VERY VERY large (which is very unlikely)
                    if tickUnit*pixelsPerUnit < self._minTickDist:
                        raise ValueError
                except (ValueError, TypeError):
                    # too small
                    continue
                
                # Calculate all ticks
                if ticksPerDim[d] is not None:
                    ticks = ticksPerDim[d]
                else:
                    ticks = self._GetTicks(tickUnit, lim)
                
                # Get index of corner to put ticks at
                i0 = 0; bestVal = 999999999
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
                    t = textDict[key]
                    t.text = labels[d]
                    t.x, t.y, t.z = p1.x, p1.y, p1.z
                    del textDict[key] # remove from dict
                else:
                    #t = Text(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                    t = AxisLabel(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                    t.fontSize=10
                newTextDicts[d][key] = t                
                t.halign = 0
                # move up front
                if not t in self._children[-3:]:                    
                    self._children.remove(t) 
                    self._children.append(t)
                # get vec to calc angle
                vec = Point(vector_s.x, vector_s.y)
                if vec.x < 0:
                    vec = vec * -1                
                t.textAngle = float(vec.Angle() * 180/np.pi)
                t._textDict = newTextDicts[d] # keep up to date
                
                # Apply Ticks
                for tick in ticks:
                    # get tick location
                    p1 = firstCorner.Copy()
                    p1[d] = tick                    
                    # get little tail to indicate tick
                    p2 = p1.Copy()                    
                    p2 = p2 - tv
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
                    # put textlabel at tick                    
                    text = '%1.4g' % tick                    
                    textDict = self._textDicts[d]
                    if text in textDict and textDict[text] in self._children:
                        t = textDict[text]
                        t.x, t.y, t.z = p2.x, p2.y, p2.z
                        del textDict[text] # remove from dict
                    else:
                        t = Text(self,text, p2.x,p2.y,p2.z, 'sans')
                    # add to dict 
                    newTextDicts[d][text] = t                    
                    # set other properties right
                    if t.fontSize != axes.tickFontSize:
                        t.fontSize = axes.tickFontSize
                    if d==2:
                        t.valign = 0
                        t.halign = 1
                    else: 
                        if d==1 and isTwoDCam:
                            t.halign = 1
                            t.valign = 0
                        elif vector_s.y*vector_s.x >= 0:
                            t.halign = -1
                            t.valign = -1
                        else:
                            t.halign = 1
                            t.valign = -1
                
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
            clr = self._color
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
            clr = self._color
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
        """ Actually draw the axis. """
        axes = self.GetAxes()
        if not axes:
            return
        if not axes._axis:
            return
        
        # get pointset
        if not hasattr(self, '_pps'):
            return
        pps = self._pps
        pps[:,2] = 100000 - pps[:,2] * 200000
        
        # prepare for drawing lines
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(pps.data)
        if axes.camera is axes._cameras['twod']:
            gl.glDisable(gl.GL_LINE_SMOOTH)
        # draw lines
        clr = self._color
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
    """ A special label that moves itself just past the tickmarks. 
    The _textDict attribute should contain the Text objects of the tickmarks.
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



class Legend(base.Box):
    """ A legend is a wibject that should be the child of an axes.
    It displays a description for each line in the axes, and is
    draggable.
    """
    
    def __init__(self, parent, axes=None):
        base.Box.__init__(self, parent)
        
        # store reference to axes object
        if axes:
            self._axes = axes
        else:
            self._axes = parent
        
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
        
        # make me draggable
        self._moving = None
        self.hitTest = True
        f = self.GetFigure()
        self.eventMouseDown.Bind(self._OnDown)
        f.eventMotion.Bind(self._OnMove)
        f.eventMouseUp.Bind(self._OnUp)
    
    
    def _OnDown(self, event):
        f = self.GetFigure()
        tmp = self.position.InPixels()
        self._moving = tmp.x - f.mousepos[0], tmp.y-f.mousepos[1]
    
    def _OnMove(self, event):
        if not self._moving:
            return
        else:
            self.position.x = max([ event.x + self._moving[0], 0 ])
            self.position.y = max([ event.y + self._moving[1], 0 ])
            event.owner.Draw()
    
    def _OnUp(self, event):
        self._moving=None
    
    
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
        """ Set the strings of the legend labels """
        
        # test
        if len(stringList)==1 and isinstance(stringList[0],(tuple,list)):
            stringList = stringList[0]
        for value in stringList:
            if not isinstance(value, basestring):
                raise ValueError("Legend string list should only contain strings.")
        
        # store
        self._stringList = stringList
        
        # clean up labels and lines
        for line in self._wobjects:
            line.Destroy()
        for label in self._children:
            label.Destroy()
        
        # create new lines and labels
        maxWidth = 0
        for ob in self._axes._wobjects:
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
            pos =label.position
            self.position.w = maxWidth + pos.x + self._xoffset
            self.position.h = pos.bottom + self._yoffset
            self.visible = True
        else:
            self.visible = False
    
    
    def OnDraw(self):
        
        # draw box 
        base.Box.OnDraw(self)
        
        # draw lines        
        for line in self._wobjects:
            line.OnDraw()
        
        # reset some stuff that was set because it was thinking it was drawing
        # in world coordinates.
        gl.glDisable(gl.GL_DEPTH_TEST)
    