""" 
This example illustrate embedding a visvis figure in an application.
This examples uses wxPython, but the same constructions work for
pyQt or any other backend.
"""

from PyQt4 import QtGui, QtCore
import visvis as vv
vv.use('qt4')

class MainWindow(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        
        # Make a panel with a button
        self.panel = QtGui.QWidget(self)
        but = QtGui.QPushButton(self.panel)
        but.setText('Push me')
        
        # Make figure using "self" as a parent
        self.fig = vv.backends.backend_qt4.Figure(self)
        
        # Make sizer and embed stuff
        self.sizer = QtGui.QHBoxLayout(self)
        self.sizer.addWidget(self.panel, 1)
        self.sizer.addWidget(self.fig._widget, 2)
        
        # Make callback
        but.pressed.connect(self._Plot)
        
        # Apply sizers        
        self.setLayout(self.sizer)
    
    
    def _Plot(self):
        
        # Make sure our figure is the active one
        vv.figure(self.fig.nr)
        
        # Clear it
        vv.clf()
        
        # Plot
        vv.plot([1,2,3,1,6])
        vv.legend(['this is a line'])        
        self.fig.DrawNow()
    

# Create app and window
app = QtGui.QApplication([])    
m = MainWindow()
m.resize(560, 420)

# Show window and start loop
m.show()
app.exec_()
