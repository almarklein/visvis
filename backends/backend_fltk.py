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
This backend is VERY unstable if multiple figures are used...
We recommend using the QT4 or WX backend.

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
    _list = []
    
    def __init__(self, figure, *args, **kwargs):     
        fltk.Fl_Gl_Window.__init__(self, *args, **kwargs)        
        self.figure = figure
        
        # to determine resizing
        self._size = (0,0)
        
        # callback when closed
        self.callback(self.OnClose)
        
        # keep visvis up to date
        fltk.Fl.add_timeout(0.05,self.OnTimerFire)
        
        # add to list to prevent crashing
        #GLWidget._list.append(list)
        
    
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
            if w != self._size[0] or h !=self._size[1]:
                self._size = w, h
                self.OnResize(None)                
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
    
    def draw(self):
        # do the draw commands a short while from now        
        self.figure.Draw() 
    
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
        """ evaluates the keycode of wx, and transform to visvis key.
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
    
    
    def OnResize(self, event):        
        self.figure._OnResize()     
    
    def OnClose(self, event=None):    
        ev = self.figure.eventClose
        ev.Clear()
        ev.Fire()                
        self.figure.Destroy()
        self.hide()
        # I don't know how to destroy ...
        # I hope that the fact that the figure.OnDestroy() removes 
        # the widget's reference is enough...        
        self.figure._widget = None
    
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
        self._widget.make_current()
        #pass
        
        
    def _SwapBuffers(self):
        """ Swap the memory and screen buffer such that
        what we rendered appears on the screen """
        self._widget.swap_buffers()

    def _SetTitle(self, title):
        """ Set the title of the figure... """
        window = self._widget
        if hasattr(window,'label'):
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

    def _ProcessEvents(self):
        app = fltk.Fl.wait(0) 
    
    def _Close(self):
        self._widget.OnClose()
    

def newFigure():
    """ Create a window with a figure widget.
    """
    figure = Figure(560, 420, "Figure")    
    figure._widget.size_range(100,100,0,0,0,0)    
    figure._widget.show() # Show AFTER canvas is added
    return figure


class App:
    """ Application instance of fltk app, with a visvis API. """
    def __init__(self):
        pass
    def Run(self):
        fltk.Fl.run()


# # make fltk call the visvis update function ...
# # fltk.Fl is fltk's global static class (not instance)
# import types
# def wait_to_call_visvis(cls, *args):
#     processEvents()
#     return fltk.Fl.wait_original(*args)
# def run_visvis(*args):
#     while fltk.Fl.wait() > 0:
#         pass
#     return 0
# fltk.Fl.wait_original = fltk._fltk.Fl_wait
# fltk.Fl.wait = types.MethodType(wait_to_call_visvis, fltk.Fl)
# # update the run function, because it calls an internal (not
# # overloaded) wait function. Only do this if run was not overloaded
# # already (for example to hijack fltk)!
# if fltk.Fl.run.func_name == 'run':
#     fltk.Fl.run = types.MethodType(run_visvis, fltk.Fl)
# 