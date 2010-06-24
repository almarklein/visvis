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

""" Module events

Defines the events and a timer class.


"""

import sys
import time
import traceback
import weakref


class CallableObject:
    """ A class to hold a callable using weak references.
    It can distinguish between functions and methods. """
    def __init__(self, c):
        if hasattr(c,'im_func'):
            self._func = weakref.ref(c.im_func)
            self._ob = weakref.ref(c.im_self)
        else:
            self._func = weakref.ref(c)
            self._ob = None
    
    def isdead(self):
        if self._func() is None or (self._ob and self._ob() is None):
            return True
        else:
            return False
    
    def call(self, *args):
        func = self._func()
        if self._ob:
            return func(self._ob(), *args)
        else:
            return func(*args)
    
    def compare(self, other):
        # compare func
        if self._func() is not other._func():
            return False
        # compare object
        if self._ob and other._ob and self._ob() is other._ob():
            return True
        elif self._ob is None and other._ob is None:
            return True
        else:
            return False
    
    def __str__(self):
        return self._func().__str__()


class BaseEvent:
    """ The BaseEvent is the simplest type of event. 
    
    The purpose of the event class is to provide a way to bind/unbind 
    to events and to fire them. At the same time, it is the place where
     the properties of the event are stored (such mouse location, key 
    being pressed, ...).
    
    One can Bind or Unbind a callable to the event. When fired, all 
    handlers that are bind to this event are called, until the event is 
    handled (a handler returns True). The handlers are called with the 
    event object as an argument. The event.owner providesa reference of 
    what wobject/wibject sent the event.     
    """
    
    def __init__(self, owner):
        # users should not change type, owner or handlers.       
        self._owner = weakref.ref(owner)
        self._handlers = []
    
    
    def Set(self):
        """ Set() 
        Set the event properties before firing it. In the base event
        there are not properties to set.
        """
        pass
    
    
    @property
    def owner(self):
        """ The object that this event belongs to. """
        return self._owner()


    @property
    def type(self):
        """ The type (__class__) of this event. """
        return self.__class__
    
    
    def Bind(self, func):
        """ Bind(func)
        Add an eventhandler to the list.             
        func (the callback/handler) must be a callable. It is called
        with one argument: the event instance, which contains the mouse 
        location for the mouse event and the keycode for the key event.
        """
        
        # check
        if not hasattr(func, '__call__'):
            raise ValueError('Warning: can only bind callables.')
        
        # make callable object
        cnew = CallableObject(func)
        
        # check -> warn
        for c in self._handlers:
            if cnew.compare(c):
                print "Warning: handler %s already present for %s" %(func, self)
                return
        
        # add the handler
        self._handlers.append( cnew )


    def Unbind(self, func=None):
        """ Unbind(func=None)
        Unsubscribe a handler, If func is None, remove all handlers.      
        """
        if func is None:
            self._handlers[:] = []
        else:
            cref = CallableObject(func)
            for c in [c for c in self._handlers]:
                # remove if callable matches func or object is destroyed
                if c.compare(cref) or c.isdead():  
                    self._handlers.remove( c )
    
    
    def Fire(self):
        """ Fire()
        Fire the event, calling all functions that are bound
        to it, untill the event is handled (a handler returns True).
        """
        
        # remove dead weakrefs
        for c in [c for c in self._handlers]:
            if c.isdead():         
                self._handlers.remove( c )
        
        # get list of callable functions 
        L = self._handlers
        
        # call event handlers. Call last added first!
        handled = False
        for func in reversed( L ):
            if handled:
                break
            try:
                handled = func.call(self)
            except Exception, why:
                # get easier func name
                s = str(func)
                i = s.find("function")
                if i<0:
                    i = s.find("method")
                if i>= 0:
                    i1 = s.find(" ",i+1)
                    i2 = s.find(" ",i1+1)
                    if i1>=0 and i2>=0:
                        s = s[i1+1:i2]
                # get traceback
                type, value, tb = sys.exc_info()
                tblist = traceback.extract_tb(tb)                
                list = traceback.format_list(tblist[2:]) # remove "Fire"
                list.extend( traceback.format_exception_only(type, value) )
                # print
                print "ERROR calling '%s':" % s
                tmp = ""                
                for i in list:
                    tmp += i
                print tmp


class MouseEvent(BaseEvent):
    """ A MouseEvent is an event for things that happen 
    with the mouse.
    """
    
    def __init__(self, owner):
        BaseEvent.__init__(self, owner)
        
        self._x, self._y = 0, 0
        self._x2d, self._y2d = 0, 0
        self._but = 0
    
    
    def Set(self, absx, absy, but):
        """ Set(absx, absy, but)
        Set the event properties before firing it. 
        """
        
        # Set properties we can alway set
        self._absx = absx
        self._absy = absy
        self._but = but
        
        # Init other properties
        self._x = absx
        self._y = absy
        self._x2d = 0
        self._y2d = 0
        
        # Try getting more information on the owning object
        owner = self._owner()
        if owner:
            
            # Can we Set the event at all?
            if owner._destroyed:
                return
            
            # Determine axes (for Wobjects)
            axes = None
            if hasattr(owner, 'GetAxes'):
                axes = owner.GetAxes()
                if not axes:
                    return
            
            if hasattr(owner, 'position'):
                # A Wibject: use relative coordinates if not a figure
                if owner.parent:
                    self._x -= owner.position.absLeft
                    self._y -= owner.position.absTop
            elif axes:
                # A Wobject: use axes coordinates
                self._x -= axes.position.absLeft
                self._y -= axes.position.absTop
            
            if axes or hasattr(owner, '_cameras'):
                # Also give 2D coordinates
                if axes:
                    cam = axes._cameras['2d']                    
                else:
                    cam = owner._cameras['2d']
                if owner.parent: # or screen to world cannot be calculated
                    self._x2d, self._y2d = cam.ScreenToWorld((self._x, self._y))
    
    
    @property
    def absx(self):
        """ The absolute x position in screen coordinates when the event
        happened. """
        return self._absx
    
    @property
    def absy(self):
        """ The absolute y position in screen coordinates when the event
        happened. """
        return self._absy
    
    @property
    def x(self):
        """ The x position in screen coordinates relative to the owning object
        when the event happened. (For Wobjects, relative to the Axes.) """
        return self._x
    
    @property
    def y(self):
        """ The y position in screen coordinates relative to the owning object
        when the event happened. (For Wobjects, relative to the Axes.) """
        return self._y
    
    @property
    def x2d(self):
        """ The x position in 2D world coordinates when the event happened. 
        This is only valid when the used camera is 2D.
        """
        return self._x2d
    
    @property
    def y2d(self):
        """ The y position in 2D world coordinates when the event happened. 
        This is only valid when the used camera is 2D.
        """
        return self._y2d
    
    @property
    def button(self):
        """ The The mouse button that was pressed, 0=none, 1=left, 2=right. """
        return self._but


class KeyEvent(BaseEvent):
    """ A KeyEvent event is an event for things that happen 
    with the keyboard.
    """
    
    def __init__(self, owner):
        BaseEvent.__init__(self, owner)
        
        self._key = 0
        self._text = ''
    
    def Set(self, key, text=''):
        """ Set(key, text='')
        Set the event properties before firing it. 
        """
        self._key = key
        self._text = text
    
    @property
    def key(self):
        """ The integer keycode of the key. """
        return self._key
    
    @property
    def text(self):
        """ The text that the key represents (if available). """
        return self._text


## Specific events for all objects
# Make classes for each specific event that is standard for all object,
# to help introspection.

class EventMouseDown(MouseEvent):
    """ Fired when the mouse is pressed down on this object. (Also 
        fired the first click of a double click.) """
    pass
class EventMouseUp(MouseEvent):
    """ Fired when the mouse is released after having been clicked down
        on this object (even if the mouse is now not over the object). (Also
        fired on the first click of a double click.) """
    pass
class EventDoubleClick(MouseEvent):
    """ Fired when the mouse is double-clicked on this object. """
    pass
class EventEnter(MouseEvent):
    """ Fired when the mouse enters this object or one of its children. """
    pass
class EventLeave(MouseEvent):
    """ Fired when the mouse leaves this object (and is also not over any
        of it's children). """
    pass

class EventMotion(MouseEvent):
    """ Fired when the mouse is moved anywhere in the figure. """
    pass
class EventKeyDown(KeyEvent):
    """ Fired when a key is pressed down while the figure is active. """
    pass
class EventKeyUp(KeyEvent):
    """ Fired when a key is released while the figure is active. """
    pass

## Only for wibjects

class EventPosition(BaseEvent):
    """ Fired when the position (or size) of this wibject changes. """ 
    pass
    

## Processing events + timers

# For callLater function
_callLater_callables = {}

def processVisvisEvents():
    """ processVisvisEvents()
    
    Process all visvis events. Checks the status of all timers
    and fires the ones that need to be fired. This method
    needs to be called every now and then. 
    
    All backends implement a timer that periodically calls this function.
    
    To keep a figure responsive while running, periodically call 
    Figure.DrawNow() or vv.processEvents().
    """
    Timer._TestAllTimers()


class Timer(BaseEvent):
    """ Timer(owner, interval=1000, oneshot=True) 
    
    Time class. You can bind callbacks to the timer. The timer is 
    fired when it runs out of time. You can do one-shot runs and 
    continuous runs.
    
    Setting timer.nolag to True will prevent the timer from falling
    behind. If the previous Fire() was a bit too late the next Fire 
    will take place sooner. This will make that at an interval of 
    1000, 3600 events will have been fired in one hour. 
    """
    
    _timers = []    
    
    def __init__(self, owner, interval=1000, oneshot=True):
        # register
        Timer._timers.append( weakref.ref(self) )
        
        # store info being an event
        self._owner = weakref.ref(owner)
        self._handlers = []
        
        # store Timer specific properties        
        self.interval = interval
        self.oneshot = oneshot
        self.nolag = False
        self._running = False
        self._timestamp = 0


    def Start(self, interval=None, oneshot=None):
        """ Start the timer. 
        If interval end oneshot are not given, their current 
        values are used.
        """
        # set properties?
        if interval is not None:
            self.interval = interval
        if oneshot is not None:
            self.oneshot = oneshot
        
        # put on
        self._running = True
        self._timestamp = time.time() + (self.interval/1000.0)
    
    
    def Stop(self):
        """ Stop the timer from running. """
        self._running = False
    
    
    def Destroy(self):
        """ Destroy the timer, preventing it from ever getting called.
        """
        self.Stop()
        tmp = weakref.ref(self)
        if tmp in Timer._timers:
            Timer._timers.remove(tmp)
    
    @property
    def isRunning(self):
        """ Check whether the timer is running. """
        return self._running
    
    
    @classmethod
    def _TestAllTimers(self):
        """ Method used to test all timers whether they should be
        fired. If so, it fires them.
        """
        
        # test calLaters first        
        for calltime in _callLater_callables.keys():
            if calltime < time.time():
                callable, args, kwargs = _callLater_callables.pop(calltime)
                callable(*args, **kwargs)
        
        timersToRemove = []
        for timerRef in Timer._timers:
            timer = timerRef()
            
            # check if timer exists, otherwise remove.
            if timer is None:                
                timersToRemove.append(timerRef)
                continue
            
            # is it on?
            if not timer._running:
                continue
            
            # has the time passed yet?
            if time.time() > timer._timestamp:
                timer.Fire()
            else:
                continue
            
            # do we need to stop it?
            if timer.oneshot:
                timer._running = False
            else:
                if timer.nolag:
                    timer._timestamp += (timer.interval/1000.0)
                else:
                    timer._timestamp = time.time() + (timer.interval/1000.0)
        
        # clean up any dead references
        for timerRef in timersToRemove:
            try:
                Timer._timers.remove(timerRef)
            except Exception:
                pass

class App:
    """ Application class to wrap the GUI applications in a simple class
    with a simple interface.     
    
    This class should be implemented such that multiple instances can
    be created, and still wrap the same single GUI application instance.
    
    The method _GetUnderlyingApp() should be called in newFigure() to make
    sure (as late as possble) that there is a GUI application.
    """
    
    def _GetUnderlyingApp(self):
        raise NotImplemented()
    
    def ProcessEvents(self):
        raise NotImplemented()
    
    def Run(self):
        raise NotImplemented()
    