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

from visvis import BaseFigure, Timer, processEvents, constants

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
            }


class GLWidget(GLCanvas):
    """ Implementation of the WX GLCanvas, which passes a number of
    events to the Figure object that wraps it.
    """
    
    def __init__(self, figure, parent, *args, **kwargs):     
        GLCanvas.__init__(self, parent, *args, **kwargs)        
        self.figure = figure
        
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
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnClose)
        #
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SET_FOCUS, self.OnFocus)
        
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
        ev = self.figure.eventEnter
        ev.Clear()
        ev.Fire()
    
    def OnLeave(self, event):    
        ev = self.figure.eventLeave
        ev.Clear()
        ev.Fire()
    
    def OnResize(self, event):      
        self.figure._OnResize()
        self.figure.Draw()
        event.Skip()
    
    def OnClose(self, event):
        ev = self.figure.eventClose
        ev.Clear()
        ev.Fire()                
        self.figure.Destroy()
        #self.Destroy() is allready done
    
    def OnFocus(self, event):
        BaseFigure._currentNr = self.figure.nr
        event.Skip()

    def OnPaint(self, event):
        event.Skip()
        self.figure.Draw()
    
    def OnUpdateTimer(self, event):
        processEvents()
        self._timer.Start() # restart (with same timeout)


class Figure(BaseFigure):
    
    def __init__(self, parent, *args, **kwargs):
        
        # create widget
        self.widget = GLWidget(self, parent, *args, **kwargs)
        
        # call original init AFTER we created the widget
        BaseFigure.__init__(self)
    
    def _SetCurrent(self):
        """ make this scene the current context """
        try:
            self.widget.SetCurrent()
        except Exception:
            # can happen when trying to call this method after            
            # the window was destroyed.
            pass 
        
    def _SwapBuffers(self):
        """ Swap the memory and screen buffer such that
        what we rendered appears on the screen """
        self.widget.SwapBuffers()

    def _SetTitle(self, title):
        """ Set the title of the figure... """
        window = self.widget.Parent
        if hasattr(window,'SetTitle'):
            window.SetTitle(title)
    
    def _SetPosition(self, x, y, w, h):
        """ Set the position of the widget. """
        # select widget to resize. If it 
        widget = self.widget
        if isinstance(widget.Parent, FigureFrame):
            widget = widget.Parent
        # apply
        #widget.SetDimensions(x, y, w, h)
        widget.MoveXY(x,y)
        widget.SetClientSizeWH(w,h)

    def _GetPosition(self):
        """ Get the position of the widget. """
        # select widget to resize. If it 
        widget = self.widget
        if isinstance(widget.Parent, FigureFrame):
            widget = widget.Parent
        # get and return
        #tmp = widget.GetRect()        
        #return tmp.left, tmp.top, tmp.width, tmp.height
        size = widget.GetClientSizeTuple()
        pos = widget.GetPositionTuple()
        return pos[0], pos[1], size[0], size[1]

    def _ProcessEvents(self):
        # I have no idea why, but the application is not capable of
        # processing mouse events.
        app = wx.GetApp()
        app.ProcessPendingEvents()
        while app.ProcessIdle():
           pass


class FigureFrame(wx.Frame):
    """ Define a Frame. This is only to be able to tell whether
    the Figure object is used as a widget or as a Figure on its
    own. """
    pass


def newFigure():
    """ Create a window with a figure widget.
    """
    frame = FigureFrame(None, -1, "Figure", size=(560, 420))
    figure = Figure(frame)
    frame.Show() # Show AFTER canvas is added
    return figure


class App:
    """ Application instance of wx app, with a visvis API. """
    def __init__(self):
        # try obtaining the existing app if possible, else create new.        
        self._app = wx.GetApp()
        if self._app is None:
            self._app = wx.PySimpleApp()
    def run(self):
        wx.GetApp().MainLoop()
