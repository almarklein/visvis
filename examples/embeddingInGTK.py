#!/usr/bin/env python
"""Example of embedding a figure in a GTK application.  Based on the
embedding in WX example.
"""

import gtk
import visvis as vv

app = vv.use('gtk')

class MainWindow(gtk.Window):
    
    def __init__(self, size=(560, 420)):
        gtk.Window.__init__(self)
        
        hbox = gtk.HBox()
        self.add(hbox)
        vbox = gtk.VBox()
        hbox.pack_start(vbox, False, False, 0)
        button = gtk.Button('Click me')
        vbox.pack_start(button, False, False, 0)
        
        self.figure = vv.backends.backend_gtk.Figure()
        hbox.pack_start(self.figure._widget, True, True, 0)
        
        button.connect('clicked', self._Plot)
        self.connect('delete_event', gtk.main_quit)
        
        self.set_size_request(*size)
        self.show_all()
    
    def _Plot(self, *args):
        vv.figure(self.figure.nr)
        vv.clf()
        vv.plot([1,2,3,1,6])
        vv.legend(['this is a line'])
        self.figure.DrawNow()

# Two ways to create the application and start the main loop
if True:
    # The visvis way
    m = MainWindow()
    app.Run()
else:
    # The native way
    m = MainWindow()
    gtk.main()
