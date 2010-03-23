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

""" The FLTK backend.

$Author$
$Date$
$Rev$

"""

from visvis import BaseFigure, events, constants

import fltk

KEYMAP = {  fltk.FL_SHIFT: constants.KEY_SHIFT, 
            fltk.FL_Shift_L: constants.KEY_SHIFT, 
            fltk.FL_Shift_R: constants.KEY_SHIFT, 
            fltk.FL_ALT : constants.KEY_ALT,
            fltk.FL_Alt_L : constants.KEY_ALT,
            fltk.FL_Alt_R : constants.KEY_ALT,
            fltk.FL_Control_L: constants.KEY_CONTROL,
            fltk.FL_Control_R: constants.KEY_CONTROL,
            fltk.FL_Left: constants.KEY_LEFT,
            fltk.FL_Up: constants.KEY_UP,
            fltk.FL_Right: constants.KEY_RIGHT,
            fltk.FL_Down: constants.KEY_DOWN,
            fltk.FL_Page_Up: constants.KEY_PAGEUP,
            fltk.FL_Page_Down: constants.KEY_PAGEDOWN,
            }

class GLWidget(fltk.Fl_Gl_Window):
    """ Implementation of the GL_window, which passes a number of
    events to the Figure object that wraps it.
    """
    
    def __init__(self, figure, *args, **kwargs):     
        fltk.Fl_Gl_Window.__init__(self, *args, **kwargs)        
        self.figure = figure
        
        # Callback when closed
        self.callback(self.OnClose)
        
        # Keep visvis up to date
        fltk.Fl.add_timeout(0.01,self.OnTimerFire)
    
    
    def handle(self, event):
        """ All events come in here. """
        
        # map fltk buttons to visvis buttons
        buttons = [0,1,0,2,0,0,0]
        
        if event == fltk.FL_PUSH:
            x, y = fltk.Fl.event_x(), fltk.Fl.event_y()
            but = buttons[fltk.Fl.event_button()]
            self.figure._GenerateMouseEvent('down', x, y, but)
        
        elif event == fltk.FL_RELEASE:            
            x, y = fltk.Fl.event_x(), fltk.Fl.event_y()
            but = buttons[fltk.Fl.event_button()]
            if fltk.Fl.event_clicks() == 1:
                # double click                
                self.figure._GenerateMouseEvent('double', x, y, but)
            else:
                # normal release                
                self.figure._GenerateMouseEvent('up', x, y, but)            
        
        elif event in [fltk.FL_MOVE, fltk.FL_DRAG]:
            w,h = self.w(), self.h()
            self.OnMotion(None)
        elif event == fltk.FL_ENTER:
            ev = self.figure.eventEnter
            ev.Clear()
            ev.Fire()
        elif event == fltk.FL_LEAVE:
            ev = self.figure.eventLeave
            ev.Clear()
            ev.Fire()
        elif event == fltk.FL_KEYDOWN:
            self.OnKeyDown(None)
        elif event == fltk.FL_KEYUP:
            self.OnKeyUp(None)
        elif event == fltk.FL_CLOSE:
            self.OnClose(None)
        
        elif event == fltk.FL_FOCUS:
            self.OnFocus(None)        
        else:
            return 1 # maybe someone else knows what to do with it
        return 1 # event was handled.
    
    
    def resize(self, x, y, w, h):
        # Overload resize function to also draw after resizing
        fltk.Fl_Gl_Window.resize(self, x, y, w, h)
        self.figure._OnResize()
    
    def draw(self):
        # Do the draw commands now
        self.figure.OnDraw() 
    
    
    def OnMotion(self, event):
        # update position
        x, y = fltk.Fl.event_x(), fltk.Fl.event_y()
        self.figure._mousepos = x, y
        # prepare and fire event
        self.figure._GenerateMouseEvent('motion', x, y, 0)
    
    def OnKeyDown(self, event):
        key, text = self._ProcessKey()
        ev = self.figure.eventKeyDown
        ev.Clear()
        ev.key = key
        ev.text = text
        ev.Fire()
    
    def OnKeyUp(self, event):        
        key, text = self._ProcessKey()        
        ev = self.figure.eventKeyUp
        ev.Clear()
        ev.key = key
        ev.text = text
        ev.Fire()
    
    def _ProcessKey(self):
        """ evaluates the keycode of fltk, and transform to visvis key.
        Also produce text version.
        return key, text. """
        key = fltk.Fl.event_key()
        if isinstance(key,basestring):
            key = ord(key)
        # special cases for shift control and alt -> map to 17 18 19
        if key in KEYMAP:
            return KEYMAP[key], ''
        else:
            # other key, try producing text            
            #print key, self._shiftDown
            if (97 <= key <= 122) and fltk.Fl.event_shift():
                key -= 32                
            try:
                print chr(key)
            except ValueError:
                return key, ''
    
    
    def OnClose(self, event=None):    
        if self.figure:
            self.figure.Destroy()
        self.hide()        
    
    
    def OnFocus(self, event):
        BaseFigure._currentNr = self.figure.nr
        
    
    def OnTimerFire(self, event=None):
        events.processVisvisEvents()
        fltk.Fl.add_timeout(0.01,self.OnTimerFire)
    

class Figure(BaseFigure):
    
    def __init__(self, *args, **kwargs):
        
        # create widget
        self._widget = GLWidget(self, *args, **kwargs)
        
        # call original init AFTER we created the widget
        BaseFigure.__init__(self)
    
    def _SetCurrent(self):
        """ make this scene the current context """
        if self._widget:
            self._widget.make_current()
        
        
    def _SwapBuffers(self):
        """ Swap the memory and screen buffer such that
        what we rendered appears on the screen """
        self._widget.swap_buffers()

    def _SetTitle(self, title):
        """ Set the title of the figure... """
        window = self._widget
        if hasattr(window,'label'):
            title = title.replace('Figure', 'fl_Figure')
            window.label(title)
    
    def _SetPosition(self, x, y, w, h):
        """ Set the position of the widget. """
        # select widget to resize. If it 
        widget = self._widget       
        # apply
        widget.position(x,y)
        widget.size(w, h)

    def _GetPosition(self):
        """ Get the position of the widget. """
        # select widget to resize. If it 
        widget = self._widget        
        # get and return        
        return widget.x(), widget.y(), widget.w(), widget.h()
    
    def _RedrawGui(self):
        self._widget.redraw()
    
    def _ProcessGuiEvents(self):
        fltk.Fl.wait(0) 
    
    def _Close(self, widget=None):
        if widget is None:
            widget = self._widget
        if widget:
            widget.OnClose()        
    

def newFigure():
    """ Create a window with a figure widget.
    """
    # Make sure the is a GUI application instance
    app._GetUnderlyingApp()
    
    # Create figure
    figure = Figure(560, 420, "Figure")    
    figure._widget.size_range(100,100,0,0,0,0)
    figure._widget.show() # Show AFTER canvas is added    
    
    # Make OpenGl Initialize and return
    # Also call draw(), otherwise it will not really draw and crash on Linux
    figure.DrawNow()
    figure._widget.draw()
    return figure




class App(events.App):
    """ Application class to wrap the fltk application in a simple class
    with a simple interface.     
    """
    
    def _GetUnderlyingApp(self):
        return fltk.Fl
    
    def ProcessEvents(self):
        app = self._GetUnderlyingApp()
        app.wait(0) 
    
    def Run(self):
        app = self._GetUnderlyingApp()
        app.run()

app = App()
