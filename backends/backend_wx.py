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

""" The WX backend.

$Author$
$Date$
$Rev$

"""

# NOTICE: wx has the same general problem with OpenGl being kinda 
# unmanaged and frames not being drawn on Gnome. However, wx seems
# relatively well workable with only applying a Refresh command 
# on each Activate command of the main window.

from visvis import BaseFigure, events, constants

import wx
from wx.glcanvas import GLCanvas


KEYMAP = {  wx.WXK_SHIFT: constants.KEY_SHIFT, 
            wx.WXK_ALT: constants.KEY_ALT,
            wx.WXK_CONTROL: constants.KEY_CONTROL,
            wx.WXK_LEFT: constants.KEY_LEFT,
            wx.WXK_UP: constants.KEY_UP,
            wx.WXK_RIGHT: constants.KEY_RIGHT,
            wx.WXK_DOWN: constants.KEY_DOWN,
            wx.WXK_PAGEUP: constants.KEY_PAGEUP,
            wx.WXK_PAGEDOWN: constants.KEY_PAGEDOWN,
            wx.WXK_RETURN: constants.KEY_ENTER,
            wx.WXK_ESCAPE: constants.KEY_ESCAPE
            }


class GLWidget(GLCanvas):
    """ Implementation of the WX GLCanvas, which passes a number of
    events to the Figure object that wraps it.
    """
    
    def __init__(self, figure, parent, *args, **kwargs):     
        # make sure the window is double buffered (Thanks David!)
        kwargs.update({'attribList' : [wx.glcanvas.WX_GL_RGBA, 
            wx.glcanvas.WX_GL_DOUBLEBUFFER]})
        # call GLCanvas' init method
        GLCanvas.__init__(self, parent, *args, **kwargs)        
        
        self.figure = figure
        
        # find root window
        root = self.Parent
        while root.Parent:
            root = root.Parent
        
        # make bindings for events
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
        self.Bind(wx.EVT_RIGHT_DCLICK, self.OnDoubleClick)
        #        
        self.Bind(wx.EVT_MOTION, self.OnMotion)        
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)    
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        root.Bind(wx.EVT_CLOSE, self.OnClose) # Note root
        #
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        root.Bind(wx.EVT_ACTIVATE, self.OnActivate) # Note root
        
        # if lost, tough luck (thus the comment)
        #self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnMouseUp)
        
        # create timer to enable timers in visvis
        self._timer = wx.Timer(self)
        self._timer.Start(10, True)
        self.Bind(wx.EVT_TIMER, self.OnUpdateTimer)
        
        
        # onpaint is called when shown is called by figure() function.
        

    def OnLeftDown(self, event):
        x,y = event.GetPosition()
        self.CaptureMouse() # make sure to capture release outside
        self.figure._GenerateMouseEvent('down', x, y, 1)

    def OnLeftUp(self, event):
        x,y = event.GetPosition()
        try:
            self.ReleaseMouse()
        except:
            pass
        self.figure._GenerateMouseEvent('up', x, y, 1)

    def OnRightDown(self, event):
        x,y = event.GetPosition()
        self.CaptureMouse() # make sure to capture release outside
        self.figure._GenerateMouseEvent('down', x, y, 2)

    def OnRightUp(self, event):
        x,y = event.GetPosition()  
        try:
            self.ReleaseMouse()
        except:
            pass        
        self.figure._GenerateMouseEvent('up', x, y, 2)
    
    def OnDoubleClick(self, event):
        but = 0
        x,y = event.GetPosition()
        if event.LeftDClick():
            but = 1            
        elif event.RightDClick():
            but = 2
        self.figure._GenerateMouseEvent('double', x, y, but)
    
    def OnMotion(self, event):
        # update position
        x,y = event.GetPosition()
        self.figure._mousepos = x,y
        # poduce event
        self.figure._GenerateMouseEvent('motion', x, y, 0)
    
    def OnKeyDown(self, event):
        key, text = self._ProcessKey(event)
        ev = self.figure.eventKeyDown
        ev.Clear()
        ev.key = key
        ev.text = text
        ev.Fire()
    
    def OnKeyUp(self, event):        
        key, text = self._ProcessKey(event)        
        ev = self.figure.eventKeyUp
        ev.Clear()
        ev.key = key
        ev.text = text
        ev.Fire()
    
    def _ProcessKey(self,event):
        """ evaluates the keycode of wx, and transform to visvis key.
        Also produce text version.
        return key, text. """
        key = event.GetKeyCode()
        # special cases for shift control and alt -> map to 17 18 19
        if key in KEYMAP:
            return KEYMAP[key], ''
        else:
            # other key, try producing text            
            if (65 <= key <= 90) and not event.ShiftDown():
                key += 32
            try:
                return key, chr(key)
            except ValueError:
                return key, ''
    
    def OnEnter(self, event):    
        if self.figure:
            ev = self.figure.eventEnter
            ev.Clear()
            ev.Fire()
    
    def OnLeave(self, event):    
        if self.figure:
            ev = self.figure.eventLeave
            ev.Clear()
            ev.Fire()
        
    def OnResize(self, event):
        if self.figure:
            self.figure._OnResize()
            event.Skip()
    
    def OnClose(self, event):        
        if self.figure:
            self.figure.Destroy()             
            parent = self.Parent
            self.Destroy() # Hide and delete window
            # Prevent frame from sticking when there is not wx event loop
            if isinstance(parent, FigureFrame):
                parent.Hide()
        event.Skip()
    
    def OnFocus(self, event):
        if self.figure:
            BaseFigure._currentNr = self.figure.nr
            event.Skip()

    def OnPaint(self, event):
        # I read that you should always create a PaintDC when implementing
        # an OnPaint event handler.        
        a = wx.PaintDC(self) 
        if self.GetContext(): 
            self.figure.OnDraw()
        event.Skip()
    
    def OnActivate(self, event):
        # When the title bar is dragged in ubuntu
        if event.GetActive():
            self.Refresh()
        event.Skip()
    
    def OnEraseBackground(self, event):
        pass # This prevents flicker on Windows
    
    def OnUpdateTimer(self, event):
        events.processVisvisEvents()
        self._timer.Start() # restart (with same timeout)


class Figure(BaseFigure):
    
    def __init__(self, parent, *args, **kwargs):
        
        # create widget
        self._widget = GLWidget(self, parent, *args, **kwargs)
        
        # call original init AFTER we created the widget
        BaseFigure.__init__(self)
    
    
    def _SetCurrent(self):
        """ make this scene the current context """
        if not self._destroyed and self._widget is not None:            
            try:
                self._widget.SetCurrent()
            except Exception:
                # can happen when trying to call this method after            
                # the window was destroyed.
                pass 
    
    
    def _SwapBuffers(self):
        """ Swap the memory and screen buffer such that
        what we rendered appears on the screen """
        if not self._destroyed:
            self._widget.SwapBuffers()

    def _SetTitle(self, title):
        """ Set the title of the figure... """
        if not self._destroyed:
            window = self._widget.Parent
            if hasattr(window,'SetTitle'):
                title = title.replace('Figure', 'wx_Figure')
                window.SetTitle(title)
    
    def _SetPosition(self, x, y, w, h):
        """ Set the position of the widget. """
        # select widget to resize. If it 
        if not self._destroyed:            
            widget = self._widget
            if isinstance(widget.Parent, FigureFrame):
                widget = widget.Parent
            # apply
            #widget.SetDimensions(x, y, w, h)
            widget.MoveXY(x,y)
            widget.SetClientSizeWH(w,h)
    
    def _GetPosition(self):
        """ Get the position of the widget. """
        # select widget to resize. If it 
        if not self._destroyed:
            widget = self._widget
            if isinstance(widget.Parent, FigureFrame):
                widget = widget.Parent
            # get and return
            #tmp = widget.GetRect()        
            #return tmp.left, tmp.top, tmp.width, tmp.height
            size = widget.GetClientSizeTuple()
            pos = widget.GetPositionTuple()
            return pos[0], pos[1], size[0], size[1]
    
    
    def _RedrawGui(self):
        self._widget.Refresh()
    
    
    def _ProcessGuiEvents(self):
        app.ProcessEvents()
    
    
    def _Close(self, widget):
        if widget is None:
            widget = self._widget
        if widget and widget.Parent:
            try:
                widget.Parent.Close()
            except PyAssertionError:
                # Prevent "wxEVT_MOUSE_CAPTURE_LOST not being processed" error.
                pass 


class FigureFrame(wx.Frame):
    """ Define a Frame. This is only to be able to tell whether
    the Figure object is used as a widget or as a Figure on its
    own. """
    pass


def newFigure():
    """ Create a window with a figure widget.
    """
    # Make sure the app works
    app._GetUnderlyingApp()
    
    # Create figure
    frame = FigureFrame(None, -1, "Figure", size=(560, 420))
    figure = Figure(frame)
    # Show AFTER canvas is added
    frame.Show() 
    
    # Apply a draw, so that OpenGl can initialize before we will really
    # do some drawing. Otherwis textures end up showing in black.
    figure.DrawNow()
    return figure


class App(events.App):
    """ Application class to wrap the wx.App instance in a simple class
    with a simple interface.     
    """
    
    def _GetUnderlyingApp(self):
        app = wx.GetApp()
        if not app:
            # No application instance has been made, so we have to 
            # make it. 
            wx.app_instance = app = wx.PySimpleApp()
        return app
    
    def ProcessEvents(self):
        app = self._GetUnderlyingApp()
        
        # Keep reference of old eventloop instance
        old = wx.EventLoop.GetActive()
        # Create new eventloop and process
        eventLoop = wx.EventLoop()
        wx.EventLoop.SetActive(eventLoop)                        
        while eventLoop.Pending():
            eventLoop.Dispatch()
        # Process idle
        app.ProcessIdle() # otherwise frames do not close
        # Set back the original
        wx.EventLoop.SetActive(old)  
    
    def Run(self):
        app = self._GetUnderlyingApp()
        app.MainLoop()

app = App()
