# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_embeddingInQt4.png](http://wiki.visvis.googlecode.com/hg/images/examples/example_embeddingInQt4.png)

```
#!/usr/bin/env python
""" 
This example illustrates embedding a visvis figure in a Qt application.
This example works for the pyqt4 and pyside backends.
"""

try:
    from PySide import QtGui, QtCore
    backend = 'pyside'
except ImportError:
    from PyQt4 import QtGui, QtCore
    backend = 'pyqt4'

import visvis as vv

# Create a visvis app instance, which wraps a qt4 application object.
# This needs to be done *before* instantiating the main window. 
app = vv.use(backend)

class MainWindow(QtGui.QWidget):
    def __init__(self, *args):
        QtGui.QWidget.__init__(self, *args)
        
        # Make a panel with a button
        self.panel = QtGui.QWidget(self)
        but = QtGui.QPushButton(self.panel)
        but.setText('Push me')
        
        # Make figure using "self" as a parent
        Figure = app.GetFigureClass()
        self.fig = Figure(self)
        
        # Make sizer and embed stuff
        self.sizer = QtGui.QHBoxLayout(self)
        self.sizer.addWidget(self.panel, 1)
        self.sizer.addWidget(self.fig._widget, 2)
        
        # Make callback
        but.pressed.connect(self._Plot)
        
        # Apply sizers        
        self.setLayout(self.sizer)
        
        # Finish
        self.resize(560, 420)
        self.setWindowTitle('Embedding in Qt (%s)' % backend)
        self.show()
    
    
    def _Plot(self):
        
        # Make sure our figure is the active one. 
        # If only one figure, this is not necessary.
        #vv.figure(self.fig.nr)
        
        # Clear it
        vv.clf()
        
        # Plot
        vv.plot([1,2,3,1,6])
        vv.legend(['this is a line'])        
        #self.fig.DrawNow()
    

# Two ways to create the application and start the main loop
if True:
    # The visvis way. Will run in interactive mode when used in IEP or IPython.
    app.Create()
    m = MainWindow()
    app.Run()

else:
    # The native way.
    qtApp = QtGui.QApplication([''])    
    m = MainWindow()
    qtApp.exec_()

```