#!/usr/bin/env python
""" 
This example illustrate embedding a visvis figure in an application.
This examples uses wxPython, but the same constructions work for
pyQt or any other backend.
"""

import wx
import visvis as vv

# Create a visvis app instance, which wraps a wx application object.
# This needs to be done *before* instantiating the main window. 
app = vv.use('wx')


class MainWindow(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        
        # Make a panel with a button
        self.panel = wx.Panel(self)
        but = wx.Button(self.panel, -1, 'Click me')
        
        # Make figure using "self" as a parent
        self.fig = vv.backends.backend_wx.Figure(self)
        
        # Make sizer and embed stuff
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.panel, 1, wx.EXPAND)
        self.sizer.Add(self.fig._widget, 2, wx.EXPAND)
        
        # Make callback
        but.Bind(wx.EVT_BUTTON, self._Plot)
        
        # Apply sizers        
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Layout()   
    
    
    def _Plot(self, event):
        
        # Make sure our figure is the active one
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
    
    # Create native app
    app.Create()
    # Create window
    m = MainWindow(None, -1, "Figure", size=(560, 420))
    m.Show()
    # Run main loop
    app.Run()

else:
    # The native way.
    
    # Create native app
    wxApp = wx.PySimpleApp()
    # Create window
    m = MainWindow(None, -1, "Figure", size=(560, 420))
    m.Show()
    # Run main loop
    wxApp.MainLoop()
