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

""" The QT4 backend.

$Author$
$Date$
$Rev$

"""

from visvis import BaseFigure, events, constants

from PyQt4 import QtCore, QtGui, QtOpenGL

KEYMAP = {  QtCore.Qt.Key_Shift: constants.KEY_SHIFT, 
            QtCore.Qt.Key_Alt: constants.KEY_ALT,
            QtCore.Qt.Key_Control: constants.KEY_CONTROL,
            QtCore.Qt.Key_Left: constants.KEY_LEFT,
            QtCore.Qt.Key_Up: constants.KEY_UP,
            QtCore.Qt.Key_Right: constants.KEY_RIGHT,
            QtCore.Qt.Key_Down: constants.KEY_DOWN,
            QtCore.Qt.Key_PageUp: constants.KEY_PAGEUP,
            QtCore.Qt.Key_PageDown: constants.KEY_PAGEDOWN,
            QtCore.Qt.Key_Enter: constants.KEY_ENTER,
            QtCore.Qt.Key_Return: constants.KEY_ENTER,
            QtCore.Qt.Key_Escape: constants.KEY_ESCAPE,
            }

class GLWidget(QtOpenGL.QGLWidget):
    """ An OpenGL widget inheriting from PyQt4.QtOpenGL.QGLWidget
    to pass events in the right way to the wrapping Figure class.
    """
    
    def __init__(self, figure, parent, *args):
        QtOpenGL.QGLWidget.__init__(self, parent, *args)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose) # keep cleaned up
        self.figure = figure
        # Note that the default QGLFormat has double buffering enabled.
        
        # enable mouse tracking so mousemove events are always fired.        
        self.setMouseTracking(True)
        
        # enable getting keyboard focus
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus() # make the widget have focus...
        
        # implement timer
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(10)  # a bit arbitrary...
        self._timer.setSingleShot(True)
        self.connect(self._timer, QtCore.SIGNAL('timeout()'), self.timerUpdate)
        self._timer.start()
    
    
    def mousePressEvent(self, event):
        but = 0
        if event.button() == QtCore.Qt.LeftButton:
            but = 1
        elif event.button() == QtCore.Qt.RightButton:
            but = 2
        self.figure._GenerateMouseEvent('down', event.x(), event.y(), but)
    
    def mouseReleaseEvent(self, event):
        but = 0
        if event.button() == QtCore.Qt.LeftButton:
            but = 1
        elif event.button() == QtCore.Qt.RightButton:
            but = 2
        self.figure._GenerateMouseEvent('up', event.x(), event.y(), but)
    
    def mouseDoubleClickEvent(self, event):
        but = 0
        if event.button() == QtCore.Qt.LeftButton:
            but = 1
        elif event.button() == QtCore.Qt.RightButton:
            but = 2
        self.figure._GenerateMouseEvent('double', event.x(), event.y(), but)
    
    def mouseMoveEvent(self, event):
        # update position
        point = event.pos()
        self.figure._mousepos = ( point.x(), point.y() )
        # fire event        
        self.figure._GenerateMouseEvent('motion', event.x(), event.y())
    
    def keyPressEvent(self, event):
        ev = self.figure.eventKeyDown
        ev.Clear()
        ev.key = self._ProcessKey(event)
        ev.text = str(event.text())
        ev.Fire() 
    
    def keyReleaseEvent(self, event):
        ev = self.figure.eventKeyUp
        ev.Clear()
        ev.key = self._ProcessKey(event)
        ev.text = str(event.text())
        ev.Fire()
    
    def _ProcessKey(self,event):
        """ evaluates the keycode of wx, and transform to visvis key.
        """
        key = event.key()
        # special cases for shift control and alt -> map to 17 18 19
        
        if key in KEYMAP:
            return KEYMAP[key]
        else:
            return key
    
    def enterEvent(self, event):
        ev = self.figure.eventEnter
        ev.Clear()
        ev.Fire()   
    
    def leaveEvent(self, event):
        ev = self.figure.eventLeave
        ev.Clear()
        ev.Fire() 
        
    def resizeEvent(self, event):
        """ QT event when the widget is resized.
        """
        self.figure._OnResize()
    
    def closeEvent(self, event):
        ev = self.figure.eventClose
        ev.Clear()
        ev.Fire()
        self.figure.Destroy() # destroy figure
        event.accept()

    def focusInEvent (self, event):
        BaseFigure._currentNr = self.figure.nr

    def paintGl(self):        
        pass # do nothing, let the paintEvent handler call the Draw()        
    
    def paintEvent (self,event):
        """ QT event when window is requested to paint itself.
        """
        self.figure.Draw()
        
    def timerUpdate(self):
        """ Enable timers in visvis.
        """        
        events.processVisvisEvents()        
        self._timer.start(10)


class Figure(BaseFigure):
    
    def __init__(self, parent, *args, **kwargs):
        
        # keep same documentation
        self.__doc__ = BaseFigure.__doc__
        
        # create widget
        self._widget = GLWidget(self, parent, *args, **kwargs)
        
        # call original init AFTER we created the widget
        BaseFigure.__init__(self)
    
    def _SetCurrent(self):
        """ Make this scene the current OpenGL context. 
        """
        if not self._destroyed:
            self._widget.makeCurrent()
        
    def _SwapBuffers(self):
        """ Swap the memory and screen buffer such that
        what we rendered appears on the screen """
        if not self._destroyed:
            self._widget.swapBuffers()
        
    def _SetTitle(self, title):
        """ Set the title of the figure. Note that this
        does not have to work if the Figure is uses as
        a widget in an application.
        """
        if not self._destroyed:
            self._widget.setWindowTitle(title)

    def _SetPosition(self, x, y, w, h):
        """ Set the position of the widget. """
        if not self._destroyed:
            self._widget.setGeometry(x, y, w, h)
    
    def _GetPosition(self):
        """ Get the position of the widget. """        
        if not self._destroyed:
            tmp = self._widget.geometry()
            return tmp.left(), tmp.top(), tmp.width(), tmp.height()
    
    def _ProcessEvents(self):
        app = QtGui.qApp
        app.processEvents()
    
    def _Close(self):
        if self._widget:
            self._widget.close()


def newFigure():
    """ function that produces a new Figure object, the widget
    in a window. """
    fig = Figure(None)
    fig._widget.resize(560,420)    
    #fig._widget.resize(560,720) # to tecognize qt windows
    fig._widget.show()
    return fig
  
import weakref
class App:
    """ Application instance of QT4 app, with a visvis API. """
    def __init__(self):
        app =  QtGui.QApplication([])
    def Run(self):
        QtGui.qApp.exec_()

