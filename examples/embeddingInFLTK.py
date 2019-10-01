#!/usr/bin/env python
"""
This example illustrates embedding a visvis figure in an FLTK application.
"""

import fltk
import visvis as vv

# Create a visvis app instance, which wraps an fltk application object.
# This needs to be done *before* instantiating the main window.
app = vv.use('fltk')


class MainWindow(fltk.Fl_Window):
    def __init__(self):
        fltk.Fl_Window.__init__(self, 560, 420, "Embedding in FLTK")

        # Make a panel with a button
        but = fltk.Fl_Button(10,10,70,30, 'Click me')
        but.callback(self._Plot)

        # Make figure to draw stuff in
        Figure = app.GetFigureClass()
        self.fig = Figure(100,10,560-110,420-20, "")

        # Make box for resizing
        box = fltk.Fl_Box(fltk.FL_NO_BOX,100,50, 560-110,420-60,"")
        self.resizable(box)
        box.hide()

        # Finish
        self.end()
        self.show()
        self.fig._widget.show()


    def _Plot(self, event):

        # Make sure our figure is the active one
        # If only one figure, this is not necessary.
        #vv.figure(self.fig.nr)

        # Clear it
        vv.clf()

        # Plot
        vv.plot([1,2,3,1,6])
        vv.legend(['this is a line'])


# Two ways to create the application and start the main loop
if True:
    # The visvis way. Will run in interactive mode when used in IEP or IPython.
    app.Create()
    m = MainWindow()
    app.Run()

else:
    # The native way.
    m = MainWindow()
    fltk.Fl.run()
