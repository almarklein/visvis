# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_embeddingInWx.png](http://wiki.visvis.googlecode.com/hg/images/examples/example_embeddingInWx.png)

```
#!/usr/bin/env python
""" 
This example illustrates embedding a visvis figure in a wx application.
"""

import wx
import visvis as vv

# Create a visvis app instance, which wraps a wx application object.
# This needs to be done *before* instantiating the main window. 
app = vv.use('wx')


class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Embedding in WX", size=(560, 420))
        
        # Make a panel with a button
        self.panel = wx.Panel(self)
        but = wx.Button(self.panel, -1, 'Click me')
        
        # Make figure using "self" as a parent
        Figure = app.GetFigureClass()
        self.fig = Figure(self)
        
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
        
        # Finish
        self.Show()
    
    
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
    app.Create()
    m = MainWindow()
    app.Run()

else:
    # The native way.
    wxApp = wx.App()    
    m = MainWindow()
    wxApp.MainLoop()

```