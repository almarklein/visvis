# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module events

Defines the events and a timer class.


"""

import sys
import time
import traceback
import weakref


# the CallableObject class is now equal

class CallableObject(object):
    """ CallableObject(callable)
    
    A class to hold a callable. If it is a plain function, its reference
    is held (because it might be a closure). If it is a method, we keep
    the function name and a weak reference to the object. In this way,
    having for instance a signal bound to a method, the object is not
    prevented from being cleaned up.
    
    """
    __slots__ = ['_ob', '_func']  # Use __slots__ to reduce memory footprint
    
    def __init__(self, c):
        
        # Check
        if not hasattr(c, '__call__'):
            raise ValueError('Error: given callback is not callable.')
        
        # Store funcion and object
        if hasattr(c, '__self__'):
            # Method, store object and method name
            self._ob = weakref.ref(c.__self__)
            self._func = c.__func__.__name__
        elif hasattr(c, 'im_self'):
            # Method in older Python
            self._ob = weakref.ref(c.im_self)
            self._func = c.im_func.__name__
        else:
            # Plain function
            self._func = c
            self._ob = None
    
    def isdead(self):
        """ Get whether the weak ref is dead.
        """
        if self._ob:
            # Method
            return self._ob() is None
        else:
            return False
    
    def compare(self, other):
        """ compare this instance with another.
        """
        if self._ob and other._ob:
            return (self._ob() is other._ob()) and (self._func == other._func)
        elif not (self._ob or other._ob):
            return self._func == other._func
        else:
            return False
    
    def __str__(self):
        return self._func.__str__()
    
    def call(self, *args, **kwargs):
        """ call(*args, **kwargs)
        Call the callable. Exceptions are caught and printed.
        """
        if self.isdead():
            return
        
        # Get function
        try:
            if self._ob:
                func = getattr(self._ob(), self._func)
            else:
                func = self._func
        except Exception:
            return
        
        # Call it
        return func(*args, **kwargs)


class BaseEvent:
    """ The BaseEvent is the simplest type of event.
    
    The purpose of the event class is to provide a way to bind/unbind
    to events and to fire them. At the same time, it is the place where
    the properties of the event are stored (such mouse location, key
    being pressed, ...).
    
    In Qt speak, an event is a combination of an event and a signal.
    Multiple callbacks can be registered to an event (signal-paradigm).
    A callback may chose to override previously registered callbacks
    by using setHandled(). If there are no handlers, or if the event
    is explicitly ignored (using the Ignore method) by *all* handlers,
    the event is propagated to the parent object (event paradigm).
    
    To register or unregister a callback, use the Bind and Unbind methods
    When fired, all handlers that are bind to this event are called,
    until the event is set as handled. The handlers are called with the
    event object as an argument. The event.owner provides a reference of
    what wobject/wibject fired the event.
    
    """
    
    _PROPAGATE = False
    
    def __init__(self, owner):
        self._owner = weakref.ref(owner)
        self._handlers = []
        
        # For propagation to parent and sibling handlers
        self._accepted = True
        self._isHandled = False
        
        # Properties
        self._modifiers = ()
    
    
    @property
    def owner(self):
        """ The object that this event belongs to.
        """
        return self._owner()


    @property
    def type(self):
        """ The type (__class__) of this event.
        """
        return self.__class__
    
    @property
    def eventName(self):
        """ The name of this event.
        """
        className = self.__class__.__name__
        return className[0].lower() + className[1:]
    
    @property
    def hasHandlers(self):
        """ Get whether this event has handlers registered to it.
        """
        return bool(self._handlers)
    
    def Accept(self):
        """ Accept()
        Accept the event, preventing it from being propagated to
        the parent object. When an event handler is called, the event
        is accepted by default.
        """
        self._accepted = True
    
    def Ignore(self):
        """ Ignore()
        Clears the accept flag parameter of the event object. Clearing the
        accept parameter indicates that the event receiver does not want
        the event. If none of the handlers for this event do not want it,
        the event might be propagated to the parent object.
        """
        self._accepted = False
    
    def SetHandled(self, isHandled=True):
        """ SetHandled(isHandled=True)
        Mark the event as handled, preventing any subsequent handlers
        from being called. Use this in a custom handler to override the
        existing  handler. The same behavior is obtained when the handler
        returns True.
        """
        self._isHandled = bool(isHandled)
    
    
    def Bind(self, func):
        """ Bind(func)
        
        Add an eventhandler to this event.
        
        The callback/handler (func) must be a callable. It is called
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
                print("Warning: handler %s already present for %s" %(func, self))
                return
        
        # add the handler
        self._handlers.append( cnew )
        
        self._UpdateOwner()
    

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
        
        self._UpdateOwner()
    
    
    def Fire(self, *eventArgs):
        """ Fire(*eventArgs)
        
        Fire the event, calling all functions that are bound
        to it, untill the event is handled (a handler returns True).
        
        If no handlers are present or if the event is explicitly ignored,
        the event is propagated to the owners parent. This only apples
        to events for which this is approprioate and only if eventArgs
        are given.
        
        """
        self._isFired = True # Flag used by BaseFigure
        
        # If event args given, set first
        if eventArgs:
            self.Set(*eventArgs)
        
        # remove dead weakrefs
        for c in [c for c in self._handlers]:
            if c.isdead():
                self._handlers.remove( c )
                self._UpdateOwner()
        
        # get list of callable functions
        L = self._handlers
        
        # Init handled and accepted
        # In the event, the event is accepted if one of the handlers
        # accepted (i.e. did not ignore) it
        accepted = False
        handled = False
        
        # call event handlers. Call last added first! ...
        func = None
        for func in reversed( L ):
            try:
                # Init handled and accepted for next call
                self._isHandled = False
                self._accepted = True # Default is accepted if handled
                # Do the call and determine if handled
                res = func.call(self)
                handled = res or self._isHandled
            except Exception:
                # On error, notify, allow postmortem debugging and also break
                self._HandleExceptionInCallback(func)
            # Handle accepted and handled
            accepted = accepted or self._accepted
            if handled:
                break
        
        if self._PROPAGATE and eventArgs and not accepted:
            # The event is not properly handled yet, try the parent object
            ob = self.owner
            if (ob is not None) and (ob.parent is not None):
                # Try getting the event object with the same name
                parentEvent = getattr(ob.parent, self.eventName, None)
                if parentEvent is not None:
                    # Fire parent events with given event arguments
                    parentEvent.Fire(*eventArgs)
    
    
    def _HandleExceptionInCallback(self, func):
        """ Print a nice message of what went wrong and also set sys.last_*
        for postmortem debugging.
        """
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
        # get traceback and store
        type, value, tb = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        sys.last_traceback = tb
        # Show traceback
        tblist = traceback.extract_tb(tb)
        list = traceback.format_list(tblist[2:]) # remove "Fire"
        list.extend( traceback.format_exception_only(type, value) )
        # print
        print("ERROR calling '%s':" % s)
        tmp = ""
        for i in list:
            tmp += i
        print(tmp)
    
    
    def _UpdateOwner(self):
        """ Update the hitTest property of the object.
        """
        owner = self.owner
        if owner and hasattr(owner, '_testWhetherShouldDrawShape'):
            owner._testWhetherShouldDrawShape()
    
    # Event properties:
    
    @property
    def modifiers(self):
        """ The modifier keys active when the event occurs.
        """
        return self._modifiers
    
    # Event classes should overload this
    def Set(self, modifiers=()):
        """ Set(modifiers)
        
        Set the event properties before firing it. In the base event
        the only property is the modifiers state, a tuple of the
        modifier keys currently pressed.
        
        """
        self._modifiers = modifiers
    


class MouseEvent(BaseEvent):
    """ MouseEvent(owner)
    
    A MouseEvent is an event for things that happen  with the mouse.
    
    """
    
    def __init__(self, owner):
        BaseEvent.__init__(self, owner)
        self._x, self._y = 0, 0
        self._x2d, self._y2d = 0, 0
        self._but = 0
    
    
    def Set(self, absx, absy, but, modifiers=()):
        """ Set(absx, absy, but, modifiers=())
        
        Set the event properties before firing it.
        
        """
        BaseEvent.Set(self, modifiers)
        
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
                if not hasattr(axes, '_cameras'):
                    axes = None # For example a legend
            
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
                    cam = axes._cameras['TwoDCamera']
                else:
                    cam = owner._cameras['TwoDCamera']
                if owner.parent: # or screen to world cannot be calculated
                    self._x2d, self._y2d = cam.ScreenToWorld((self._x, self._y))
    
    
    @property
    def absx(self):
        """ The absolute x position in screen coordinates when the event
        happened.
        """
        return self._absx
    
    @property
    def absy(self):
        """ The absolute y position in screen coordinates when the event
        happened.
        """
        return self._absy
    
    @property
    def x(self):
        """ The x position in screen coordinates relative to the owning object
        when the event happened. (For Wobjects, relative to the Axes.)
        """
        return self._x
    
    @property
    def y(self):
        """ The y position in screen coordinates relative to the owning object
        when the event happened. (For Wobjects, relative to the Axes.)
        """
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
        """ The The mouse button that was pressed, 0=none, 1=left, 2=right.
        """
        return self._but


class KeyEvent(BaseEvent):
    """ KeyEvent(owner)
    
    A KeyEvent event is an event for things that happen with the keyboard.
    
    """
    
    def __init__(self, owner):
        BaseEvent.__init__(self, owner)
        self._key = 0
        self._text = ''
    
    def Set(self, key, text='', modifiers=()):
        """ Set(key, text='')
        
        Set the event properties before firing it.
        
        """
        BaseEvent.Set(self, modifiers)
        self._key = key
        self._text = text
    
    @property
    def key(self):
        """ The integer keycode of the key.
        """
        return self._key
    
    @property
    def text(self):
        """ The text that the key represents (if available).
        """
        return self._text


## Specific events for all objects
# Make classes for each specific event that is standard for all object,
# to help introspection.

class EventMouseDown(MouseEvent):
    """ EventMouseDown(owner)
    
    Fired when the mouse is pressed down on this object, or on any of its
    children and not being handled.
    (Also fired the first click of a double click.)
    
    """
    _PROPAGATE = True
    def Fire(self, *eventArgs):
        if self.owner:
            self.owner._mousePressedDown = True
        MouseEvent.Fire(self, *eventArgs)

class EventMouseUp(MouseEvent):
    """ EventMouseUp(owner)
    
    Fired when the mouse is released after having been clicked down
    on this object (even if the mouse is now not over the object). (Also
    fired on the first click of a double click.)
    
    """
    _PROPAGATE = False
    def Fire(self, *eventArgs):
        if self.owner:
            self.owner._mousePressedDown = False
        MouseEvent.Fire(self, *eventArgs)

class EventDoubleClick(MouseEvent):
    """ EventDoubleClick(owner)
    
    Fired when the mouse is double-clicked on this object, or on any of its
    children and not being handled.
    
    """
    _PROPAGATE = True

class EventEnter(MouseEvent):
    """ EventEnter(owner)
    
    Fired when the mouse enters this object or any of its children.
    
    """
    _PROPAGATE = False

class EventLeave(MouseEvent):
    """ EventLeave(owner)
    
    Fired when the mouse was previously over the object or any of its
    children, and is now not.
    
    """
    _PROPAGATE = False

class EventMotion(MouseEvent):
    """ EventMotion(owner)
    
    Fired when the mouse is moved over the object, or over any of its
    children and not being handled. This event is also always called
    when the mouse is pressed down on the object.
    """
    _PROPAGATE = False

class EventScroll(MouseEvent):
    """ EventScroll(owner)
    
    Fired when the scroll wheel is used while over the object, or on any of its
    children and not being handled. The value of the button property is
    undefined for this event. The amount of scrolling is available as the
    horizontalSteps and verticalSteps properties.
    
    """
    _PROPAGATE = True
    
    def __init__(self, owner):
        MouseEvent.__init__(self, owner)
        self._horizontalSteps = 0.0
        self._verticalSteps = 0.0
    
    def Set(self, absx, absy, horizontalSteps, verticalSteps, modifiers=()):
        """ Set(absx, absy, horizontalSteps, verticalSteps, modifiers=())
        """
        MouseEvent.Set(self, absx, absy, 0, modifiers) # Button is 0
        self._horizontalSteps = horizontalSteps
        self._verticalSteps = verticalSteps

    @property
    def horizontalSteps(self):
        """ Get the amount of scrolling in the horizontal direction
        (can be positive or negative) .
        """
        return self._horizontalSteps
    
    @property
    def verticalSteps(self):
        """ Get the amount of scrolling in the vertical direction
        (can be positive or negative) .
        """
        return self._verticalSteps


class EventKeyDown(KeyEvent):
    """ EventKeyDown(owner)
    
    Fired when a key is pressed down while the figure is active.
    
    """
    _PROPAGATE = True

class EventKeyUp(KeyEvent):
    """ EventKeyUp(owner)
    
    Fired when a key is released while the figure is active.
    
    """
    _PROPAGATE = True

## Only for wibjects

class EventPosition(BaseEvent):
    """ EventPosition(owner)
    
    Fired when the position (or size) of this wibject changes.
    
    """
    _PROPAGATE = False
    

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
    
    Timer class. You can bind callbacks to the timer. The timer is
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
        """ Start(interval=None, oneshot=None)
        
        Start the timer. If interval end oneshot are not given,
        their current values are used.
        
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
        """ Stop()
        
        Stop the timer from running.
        
        """
        self._running = False
    
    
    def Destroy(self):
        """ Destroy()
        
        Destroy the timer, preventing it from ever fyring again.
        
        """
        self.Stop()
        tmp = weakref.ref(self)
        if tmp in Timer._timers:
            Timer._timers.remove(tmp)
    
    @property
    def isRunning(self):
        """ Get whether the timer is running.
        """
        return self._running
    
    
    @classmethod
    def _TestAllTimers(self):
        """ Method used to test all timers whether they should be
        fired. If so, it fires them.
        """
        
        # test calLaters first
        for calltime in [key for key in _callLater_callables.keys()]:
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
    """ App()
    
    The App class wraps a GUI backend  with a simple interface that is
    the same for all backends. It can be used to start the GUI toolkit's
    main-loop, or process all pending events.
    
    To obtain an instance of this class, the user should call vv.use().
    
    """
    
    def __repr__(self):
        name = self.GetBackendName()
        if not name:
            name = 'undefined'
        return '<Visvis app that wraps the %s GUI toolkit>' % name
    
    
    def GetBackendName(self):
        """ GetBackendName()
        
        Get the name of the GUI backend that this app wraps.
        
        """
        if hasattr(self, '_backend'):
            return self._backend
        else:
            return ''
    
    
    def GetFigureClass(self):
        """ GetFigureClass()
        
        Get the Figure class for this backend.
        
        """
        backendModule = sys.modules[self.__module__]
        return backendModule.Figure
    
    
    def Create(self):
        """ Create()
        
        Create the native application object. When embedding visvis in an
        application, call this method before instantiating the main window.
        
        """
        # Make sure the app exists
        self._GetNativeApp()
    
    
    def ProcessEvents(self):
        """ ProcessEvents()
        
        Process all pending GUI events. This should be done regularly
        to keep the visualization interactive and to keep the visvis
        event system running.
        
        When using IPython or IEP with the right settings, GUI events
        will be processed automatically. However, in a running script,
        this is not the case; be then regularly calling this method,
        the figures will stay responsive.
        
        """
        self._ProcessEvents()
    
    
    def Run(self):
        """ Run()
        
        Enter the native GUI event loop.
        
        """
        self._Run()
    
    
    # Implement these methods. Be using this redirection scheme, we keep
    # the documentation intact.
    def _GetNativeApp(self):
        raise NotImplementedError()
    
    def _ProcessEvents(self):
        raise NotImplementedError()
    
    def _Run(self):
        raise NotImplementedError()
