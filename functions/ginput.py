# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
from visvis.utils.pypoints import Pointset
import time

class GinputHelper(object):
    """ GinputHelper()
    
    Helper class for ginput function.
    Keeps track of things.
    
    """
    
    def __init__(self):
        self.axes = None
        self.pp = None
        self.N = 0
    
    def Start(self, axes, pp, N):
        self.Unregister()
        
        if axes:
            
            # Store pointset and axes
            self.axes = axes
            self.pp = pp
            self.N = N
            
            # Register with axes
            self.axes.eventMouseDown.Bind(self.OnMouseDown)
            self.axes.eventDoubleClick.Bind(self.OnDoubleClick)
            self.axes.eventKeyDown.Bind(self.OnKeyDown)
        
    
    def Unregister(self):
        
        if self.axes:
            # Unregister axes
            self.axes.eventMouseDown.Unbind(self.OnMouseDown)
            self.axes.eventDoubleClick.Unbind(self.OnDoubleClick)
            self.axes.eventKeyDown.Unbind(self.OnKeyDown)
        
        # Remove references
        self.axes = None
        self.pp = None
        self.N = 0
    
    def OnMouseDown(self, event):
        
        # Add point
        if self.pp is not None:
            self.pp.append(event.x2d, event.y2d, 0.1)
        
        # Draw
        if self.axes:
            fig = self.axes.GetFigure()
            if fig:
                fig.DrawNow()
        
        # Is this the last point?
        if self.pp is not None and self.N and len(self.pp)==self.N:
            self.Unregister()
        
        # Accept event
        return True
    
    def OnDoubleClick(self, event):
        self.Unregister()
    
    def OnKeyDown(self, event):
        if event.key == vv.KEY_ENTER:
            self.Unregister()
            


ginputHelper = GinputHelper()


def ginput(N=0, axes=None, ms='+', **kwargs):
    """ ginput(N=0, axes=None, ms='+', **kwargs)
    
    Graphical input: select N number of points with the mouse.
    Returns a 2D pointset.
    
    Parameters
    ----------
    N : int
        The maximum number of points to capture. If N=0, will keep capturing
        until the user stops it. The capturing always stops when enter is
        pressed or the mouse is double clicked. In the latter case a final
        point is added.
    axes : Axes instance
        The axes to capture the points in, or the current axes if not given.
    ms : markerStyle
        The marker style to use for the points. See plot.
    
    Any other keyword arguments are passed to plot to show the selected
    points and the lines between them.
    
    """
    
    # Get axes
    if not axes:
        axes = vv.gca()
    
    # Get figure
    fig = axes.GetFigure()
    if not fig:
        return
    
    # Init pointset, helper, and line object
    line = vv.plot(Pointset(2), axes=axes, ms=ms, **kwargs)
    pp = line._points
    ginputHelper.Start(axes, pp, N)
    
    # Enter a loop
    while ginputHelper.axes:
        fig._ProcessGuiEvents()
        time.sleep(0.1)
    
    # Remove line object and return points
    pp = Pointset(pp[:,:2])
    line.Destroy()
    return pp


if __name__ == '__main__':
    vv.cla()
    vv.title('Selec three points.')
    print(vv.ginput(3))
