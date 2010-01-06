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

""" Module events

Defines the events and a timer class.

$Author$
$Date$
$Rev$

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
            func(self._ob(), *args)
        else:
            func(*args)
    
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
    """ Base event object
    Contains information about the event: mouse location, mouse button,
    key being pressed, text of the key. 
    One can Bind or Unbind a callable to the event. 
    When fired, all handlers that are bind to this event are called, 
    until the event is handled (a handler returns True). The handlers
    are called with the event object as an argument. The event.owner 
    provides information of what wobject/wibject sent the event. 
    """
    def __init__(self, owner):
        # users should not change type, owner or handlers.       
        self._owner = weakref.ref(owner)
        self._handlers = []
        self.Clear()
    
    def Clear(self):
        """ Clear the properties of the event. Do this before setting
        them and firing the event. """
        self.x = 0
        self.y = 0
        self.x2d = 0
        self.y2d = 0
        self.button = 0
        self.key = 0
        self.text = ""

    @property
    def owner(self):
        """ The object that this event belongs to. """
        return self._owner()


    @property
    def type(self):
        """ The type (__class__) of this event. """
        return self.__class__
    
    
    def Bind(self, func):
        """ Add an eventhandler to the list.             
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
        """ Unsubscribe a handler, If func is None, remove all handlers.      
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
        """ Fire the event, calling all functions that are bound
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


# events for all 
class EventMouseDown(BaseEvent):
    """ Fires when the mouse is pressed down while over the 
    object. Not fired when over a child of the object. """
    pass
class EventMouseUp(BaseEvent):
    """ Fires when the mouse is released while over the 
    object. NOTE: in most cases you'd best use the eventMouseUp
    of the figure, otherwise you won't detect mouse-ups when the mouse
    is moved away from the object while holding it down. """
    pass
class EventDoubleClick(BaseEvent):
    """ Fires when the mouse is dubble clicked over the object. """
    pass
class EventEnter(BaseEvent):
    """ Fires when the mouse enters the object or one of its children."""
    pass
class EventLeave(BaseEvent):
    """ Fires when the mouse leaves the object. This does not fire when
    it moves over a child of the object. """
    pass

class EventMotion(BaseEvent):
    """ Fires when the mouse is moved over the object. Not fired when
    the mouse is over one of its children. """
    pass

# only for wibjects

class EventPosition(BaseEvent):
    """ Fires when the posision of a wibject changes. """
    pass
    
# only available for figures

class EventKeyDown(BaseEvent):
    """ Fires when a key is pressed down. """
    pass
class EventKeyUp(BaseEvent):
    """ Fires when a key is released. """
    pass
class EventResize(BaseEvent):
    """ Fires when the figure is resied. """
    pass
class EventClose(BaseEvent): 
    """ Fires when the figure is closed. """
    pass
class EventAfterDraw(BaseEvent): 
    """ Fires right after the figure is drawn. """
    pass


_callLater_callables = {}

def callLater(delay, callable, *args, **kwargs):
    """ callLater(delay, callable, *args, **kwargs)
    Call a callable after a specified amount of time, with the
    specified args and kwargs. If delay = 0, the callable is called
    right after the current processing has returned to the main loop."""
    calltime = time.clock() + delay
    _callLater_callables[calltime]= (callable, args, kwargs)


def processEvents():
    """ Process all events. Checks the status of all timers
    and fires the ones that need to be fired. This method
    needs to be called every now and then. 
    (The backend's processEvents function is modified to do 
    this).
    """
    Timer._TestAllTimers()

class Timer(BaseEvent):
    """ Timer(interval=1000, oneshot=True) 
    
    Time class. You can bind callbacks to the timer. The timer is 
    fired when it runs out of time. You can do one-shot runs and 
    continouos runs.
    
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
        self._timestamp = time.clock() + (self.interval/1000.0)
    
    
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
            if calltime < time.clock():
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
            if time.clock() > timer._timestamp:
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
                    timer._timestamp = time.clock() + (timer.interval/1000.0)
        
        # clean up any dead references
        for timerRef in timersToRemove:
            try:
                Timer._timers.remove(timerRef)
            except Exception:
                pass
                
    