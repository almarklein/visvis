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

""" The QT4 backend.


"""

# NOTICE: OpenGl some problems on Ubuntu (probably due gnome).
# The drawing of the frame and background seems sometimes be done
# seperate from the opengl drawings. This means that sometimes the
# OpenGl stuff is drawn while the frame is not, which results in stuff
# hangin in "mid-air". Or while dragging the whole window, the frame
# is drawn, but in it is either rubish (qt) or gray bg (wx). When the
# frame is not visible, it is still there (you can still resize etc.)
# This is a known bug of the X Server: 
# https://wiki.ubuntu.com/RedirectedDirectRendering
# A solution while the bug is not fixed is to set the visual effects off 
# in System > Preferences > Appearance.
# Also note tha wx seems the less affected backend (there is a small fix
# by redrawing on a Activate event which helps a lot)

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

# todo: get qt4 backend working in IPython
# Works on vista PC with Python 2.5.2

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
        
#         # implement timer
#         self._timer = QtCore.QTimer(self)
#         self._timer.setInterval(10)  # a bit arbitrary...
#         self._timer.setSingleShot(True)
#         self.connect(self._timer, QtCore.SIGNAL('timeout()'), self.timerUpdate)
#         self._timer.start()
#         self._CreateTimer()

        # Create low level timer
        self._timer = QtCore.QBasicTimer()
        self._timer.start(10,self)
    
#     def _CreateTimer(self):
#         self._timer = QtCore.QTimer(self)
#         self._timer.setInterval(1)  # a bit arbitrary...
#         self._timer.setSingleShot(True)
#         self.connect(self._timer, QtCore.SIGNAL('timeout()'), self.timerUpdate)
#         self._timer.start()
    
    
    def timerEvent(self, event):       
        
        # Process visvis events
        events.processVisvisEvents()
        # todo: remove timerUpdate below
    
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
        if self.figure:
            # update position
            point = event.pos()
            self.figure._mousepos = ( point.x(), point.y() )
            # fire event        
            self.figure._GenerateMouseEvent('motion', event.x(), event.y())
    
    def keyPressEvent(self, event):
        ev = self.figure.eventKeyDown        
        key = self._ProcessKey(event)
        text = str(event.text())
        ev.Set(key, text)
        ev.Fire() 
    
    def keyReleaseEvent(self, event):
        ev = self.figure.eventKeyUp
        key = self._ProcessKey(event)
        text = str(event.text())
        ev.Set(key, text)
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
        if self.figure:            
            ev = self.figure.eventEnter
            ev.Set(0,0,0)
            ev.Fire()
    
    def leaveEvent(self, event):
        if self.figure:
            ev = self.figure.eventLeave
            ev.Set(0,0,0)
            ev.Fire()
    
#     def resizeEvent(self, event):
#         """ QT event when the widget is resized.
#         """        
#         self.figure._OnResize()
    
    def closeEvent(self, event):
        if self.figure:
            self.figure.Destroy()
        event.accept()

    def focusInEvent (self, event):
        if self.figure:
            BaseFigure._currentNr = self.figure.nr
    
    
    def initializeGL(self):
        pass # no need
    
    def resizeGL(self, w, h):
        # This does not work if we implement resizeEvent
        self.figure._OnResize()
    
    def paintEvent(self,event):
        # Use this rather than paintGL, because the latter also swaps buffers,
        # while visvis already does that.
        # We could use self.setAutoBufferSwap(False), but it seems not to help.
        self.figure.OnDraw()
    
# This is to help draw the frame (see bug above), but I guess one should
# simply disable it's visual effects
#     def moveEvent(self, event):
#         self.update()
#         
#     def showEvent(self, event):
#         # This is to make the frame being drawn on Ubuntu
#         w, h = self.width(), self.height()
#         self.resize(w-1,h)
#         self.resize(w,h)
    
    def timerUpdate(self):
        """ Enable timers in visvis.
        """        
        events.processVisvisEvents()        
        self._timer.start(10)


class Figure(BaseFigure):
    """ This is the Qt4 implementation of the figure class.
    
    A Figure represents the OpenGl context and is the root
    of the visualization tree; a Figure Wibject does not have a parent.
    
    A Figure can be created with the function vv.figure() or vv.gcf().
    """
    
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
            title = title.replace('Figure', 'qt_Figure')
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
    
    def _RedrawGui(self):
        if self._widget:
            self._widget.update()
    
    def _ProcessGuiEvents(self):
        app = QtGui.QApplication.instance()
        app.flush()
        app.processEvents()
    
    def _Close(self, widget):
        if widget is None:
            widget = self._widget
        if widget:
            widget.close()


def newFigure():
    """ function that produces a new Figure object, the widget
    in a window. """
    # Make sure the app works
    app._GetUnderlyingApp()
    
    # Create figure
    fig = Figure(None)
    fig._widget.show() # In Gnome better to show before resize
    fig._widget.resize(560,420)
    
    # Let OpenGl initialize and return
    fig.DrawNow() 
    return fig


class App(events.App):
    """ Application class to wrap the QtGui.QApplication instance
    in a simple class with a simple interface.     
    """
    
    def _GetUnderlyingApp(self):
        app = QtGui.QApplication.instance()
        if not app:
            # No application instance has been made, so we have to 
            # make it. This means we also have to prevent from getting
            # deleted. We do this by storing it as qApp.
            QtGui.qApp = app = QtGui.QApplication([])
        return app
    
    def ProcessEvents(self):
        app = self._GetUnderlyingApp()
        app.flush()
        app.processEvents()
    
    def Run(self):
        app = self._GetUnderlyingApp()
        app.exec_()

app = App()
