This document provides information on how to implement a backend in
Visvis, and explains how the backend GUI interacts with Visvis.

Notice: This document is probably outdated, and since its intended audience is so small, I feel no urge to update it right now. However, it should give you a good idea of how the backends are implemented. For more information I recommend looking at the source code of the currently implemented backends.


## Introduction ##

Each backend consists of a single module that implements four things:
  * An OpenGL widget (let's call it the GLCanvas)
  * A class called "Figure" that implements vv.BaseFigure
  * A function called newFigure()
  * An App class that implements vv.events.App. In instance of this class must be instantiated in the module namespace and called "app".

The purpose of the GLCanvas is to provide a drawing context. Further it should pass on a lot of GUI events (key events, mouse events, drawing, closing) to the Figure class. This widget is hidden from the user, so method names can be chosen freely.

The purpose of the Figure class is to represent a Figure. It wraps
a GLCanvas widget. There are a series of (private) method that
need to be overloaded (see below). This class is exposed to the user,
so don't make a mess.

The newFigure class should create a Figure instance with a GLCanvas as a toplevel widget. If necessary, the widget must be wrapped in a mainwindow class (see the wx backend).

The App instance gives visvis (and the users) a way to use the GUI application in a uniform way. It is used to process GUI events and
start the GUI event loop.

Below you'll find the details of the backend implementation. Also see
the already existing backends implementations for working examples.


## Methods that require overloading ##

Here is a piece of code from the BaseFigure class, that shows which methods should be overloaded, and what the should do:

```
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
    
    def _ProcessGuiEvents(self):
        """ _ProcessGuiEvents()
        
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
        """ _SetPosition(x, y, w, h)
        
        Set the position of the widget. The x and y represent the
        screen coordinates when the figure is a toplevel widget. 
        
        For embedded applications they represent the position within
        the parent widget.
        
        """
        raise NotImplemented()
    
    def _GetPosition(self):
        """ _GetPosition()
        
        Get the position of the widget. The result must be a 
        four-element tuple (x,y,w,h).
        
        """        
        raise NotImplemented()
    
    
    def _Close(self):
        """ _Close()
        
        Close the widget, also calls Destroy(). 
        
        """
        raise NotImplemented()
```


## Interaction between GUI and Visvis ##

### Drawing ###

Draw commands can come from two sources: from the GUI because the
widget was resized or previously occluded, and from within Visvis,
because something was changed (for example while zooming).
The following pseudocode explains how these both result in visvis
drawing the scene.

```
Figure.Draw(self):
  # Entry point for draw requests from within Visvis.
  # Consequetive draw requests result in a single draw.
  if not self._drawTimer.IsRunning():
    self._drawTimer.Start()

Figure._DrawTimerTimeOutHandler(self):
  self._RedrawGui()

Figure._RedrawGui():
  # This method needs to be implemented to call the right
  # update function, as the name differs per toolkit.
  self._widget.MethodToRequestRedraw()

GlCanvas.MethodToRequestRedraw(self): 
  # Entry point for draw requests from the GUI.
  # This method is always implemented by the GUI toolkit.
  # Will post an event to fire GlCanvas.MethodToReallyDraw() 
  ...

GlCanvas.MethodToReallyDraw(self):
  # Draw Now. Sometimes this method needs to be overloaded, sometimes
  # one has to bind to a draw event.  
  self.figure.OnDraw()

Figure.OnDraw(self):
  # This method will perform all OpenGl commands.
  # The whole tree of wibjects and wobjects get a chance to draw
  # themselves here.
  ...
```


### Closing ###

Simularly, closing the figure may also be done via two ways: by
clicking on the cross of the widget's title bar, or by calling
Figure.Destroy(). In the following pseudocode the mechanisms
behind closing and cleaning up are explained:

```
Figure.Destroy(self):
  # Calls OnDestroy() of all children of the figure to clean up, 
  # and then calls OnDestroy() on itself.
  ...
  self.OnDestroy()

Figure.OnDestroy(self):
  if self._widget:
    self.eventClose.Fire()
    # Detach
    self._widget.figure = None
    self._widget = None
    # Make the window disappear
    self._Close()
    # Remove figure from list of figures
    ...

Figure._Close(self):
  # This method needs to be implemented to call the right
  # update function, as the name differs per toolkit.
  # In FLTK, GlCanvas.MethodToReallyClose() is called directly.
  self._widget.MethodToRequestClose()

GlCanvas.MethodToRequestClose(self):  
  # Entry point for close requests from the GUI.
  # This method is always implemented by the GUI toolkit.
  # Will post an event to fire GlCanvas.MethodToReallyClose() 
  ...
  
GlCanvas.MethodToReallyClose(self):
  # Close Now. Sometimes this method needs to be overloaded, sometimes
  # one has to bind to a close event.
  if self.figure:
    self.figure.Destroy()
  self.hide()
```


## Interaction of the event systems ##


### The App class ###


Each backend should implement an App class that wraps the GUI toolkit's
application instance. This class should inherit from vv.events.App and
implement the methods "_GetNativeApp", "_ProcessEvents" and "_Run".
The_GetNativeApp method should reuse an existing application instance.

One instance of this class should be created in the backend-module
namespace. This instance should be called "app"

The backend should make sure to call app.Create() to ensure that the
underlying GUI app exists. This should be done as late as possible
though. Calling it in init of the Figure class is sufficient in
most cases.

This gives visvis (and the users) a way to use the GUI application in
a uniform way. Users can get the app instance by calling vv.use().
Visvis keeps track of what is the current backend, and uses its app
instance in the vv.processEvents().


### Event handling ###

To keep visvis' event system to run, the backend should make sure
to periodically call vv.events.processVisvisEvents(). This can usually
be done using a timer by the instance of the App class.

Further, GUI events such as mouse motion should be translated to visvis events. This is the task of the GLCanvas. See the existing backend implementation for details on which events should be passed on.

### Notes on the GUI event loop ###

The events of the underlying widget toolkit need to be periodically
processed too. When the GUI mainloop is running (for example when
visvis is embedded in an application)this works fine, but for interactive
use, this mainloop has to be simulated.

IPython solves this by starting a GUI eventloop in a seperate thread.
That means using visvis with the wx backend requires using the -wthread
option. For the qt4 backend, the -q4thread option can be used, although
it does not seem necessary, because IPython updates the tk evens, and
somehow qt is able to hook into that (I'm not sure how this works
exactly). IPython does AFAIK not support processing FLTK events.

In IEP, the events can be processed for qt, wx, gtk and fltk. In contrast
to IPython, the events are processed when the kernel is idle (waiting for
user input), this means that the GUI's (and visvis) become unresponsive
if the process is running some algorithm.