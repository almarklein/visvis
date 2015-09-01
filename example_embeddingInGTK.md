# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_embeddingInGTK.png](http://wiki.visvis.googlecode.com/hg/images/examples/example_embeddingInGTK.png)

```
#!/usr/bin/env python
"""
This example illustrates embedding a visvis figure in a GTK application.
"""

import gtk
import visvis as vv

app = vv.use('gtk')

class MainWindow(gtk.Window):
    
    def __init__(self, size=(560, 420)):
        gtk.Window.__init__(self)
        
        # Create boxes and button
        hbox = gtk.HBox()
        self.add(hbox)
        vbox = gtk.VBox()
        hbox.pack_start(vbox, False, False, 0)
        button = gtk.Button('Click me')
        vbox.pack_start(button, False, False, 0)
        
        # Cteate visvis figure
        Figure = app.GetFigureClass()
        self.figure = Figure()
        hbox.pack_start(self.figure._widget, True, True, 0)
        
        # Connect signals
        button.connect('clicked', self._Plot)
        self.connect('delete_event', gtk.main_quit)
        
        # Finish
        self.set_size_request(*size)
        self.set_title("Embedding in GTK")
        self.show_all()
    
    
    def _Plot(self, *args):
        vv.figure(self.figure.nr)
        vv.clf()
        vv.plot([1,2,3,1,6])
        vv.legend(['this is a line'])


# Two ways to create the application and start the main loop
if True:
    # The visvis way. Will run in interactive mode when used in IEP or IPython.
    app.Create()
    m = MainWindow()
    app.Run()
else:
    # The native way
    m = MainWindow()
    gtk.main()

```