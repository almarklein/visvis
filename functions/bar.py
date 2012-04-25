# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np
import OpenGL.GL as gl


def bar(data1, data2=None, width=0.75, axesAdjust=True, axes=None):    
    """ bar(*args, width=0.75, axesAdjust=True, axes=None)
    
    Create a bar chart and returns a Bars2D instance that can be
    used to change the appearance of the bars (such as color).
    
    Usage
    -----
      * bar(H, ...) creates bars of specified height.
      * bar(X, H, ...) also supply their x-coordinates
    
    Keyword arguments
    -----------------
    width : scalar
        The width of the bars.
    axesAdjust : bool
        If True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet, 
        it is set to False.
    axes : Axes instance
        Display the bars in the given axes, or the current axes if not given.
    
    """
    
    # Pre check
    if True:
        try:
            if not hasattr(data1, '__len__'):
                raise ValueError
            data1 = [float(val) for val in data1]
        except Exception:
            raise ValueError('bar needs a sequence of numbers.')
    if data2 is not None:
        try:
            if not hasattr(data2, '__len__'):
                raise ValueError
            data2 = [float(val) for val in data2]
        except Exception:
            raise ValueError('bar needs a sequence of numbers.')
    
    # Parse input
    if data2 is None:
        # Only height given
        hh = data1
        xx = list(range(len(hh)))
    else:
        # All three given
        xx = data1
        hh = data2
    
    # Check
    if len(hh) != len(xx):
        raise ValueError('Given arrays for bar must be of equal length.')
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create Bars instance
    bars = Bars2D(axes, xx, hh, width)
    
    # Adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = True
        axes.cameraType = '2d'
        axes.SetLimits()
    
    # Done
    axes.Draw()
    return bars
    


class Bars2D(vv.Wobject):
    """ Bars2D(parent)
    
    The Bars2D class represents a bar chart. It has a few methods to
    change the appearance of the bars.
    
    This wobject is created by the function vv.bar().
    
    """
    def __init__(self, parent, xx, hh, width):
        vv.Wobject.__init__(self, parent)
        
        # Store data
        self._xx = xx
        self._hh = hh
        
        # Init width
        self._width = width
        
        # Init line style
        self._colors = [(0,0,1) for i in hh]
        self._lc = (0,0,0)
        self._lw = 1
    
    
    def _GetLimits(self):
        
        # Get limits
        w = 0.5 * self._width
        x1, x2 = min(self._xx) - w, max(self._xx) + w
        y1, y2 = 0, max(self._hh)
        z1, z2 = 0, 0
        
        # Done
        return vv.Wobject._GetLimits(self, x1, x2, y1, y2, z1, z2)
    
    
    def OnDraw(self):
        
        # Prepare
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_LINE_SMOOTH)
        
        w = self._width * 0.5
        z = 0.1
        
        for x, h, c in zip(self._xx, self._hh, self._colors):
            
            # Define rectangle
            vertices = np.array([   (x-w, 0, z), (x-w, h, z),
                                    (x+w, h, z), (x+w, 0, z) ]).astype('float32')
            
            gl.glVertexPointerf(vertices)
            
            # Draw bg
            gl.glColor3f(c[0], c[1], c[2])
            gl.glDrawArrays(gl.GL_QUADS, 0, vertices.shape[0])
            
            # Draw outer lines            
            vertices[:,2] += 0.1
            clr = self._lc
            gl.glColor3f(clr[0], clr[1], clr[2])
            gl.glLineWidth(self._lw)
            gl.glDrawArrays(gl.GL_LINE_LOOP, 0, vertices.shape[0])
        
        
        # Wrap up
        gl.glFlush()
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        
    
    
    @vv.misc.PropWithDraw
    def lc():
        """ Get/Set the line color of the bars. 
        """
        def fget(self):
            return self._lc
        def fset(self, value):
            self._lc = vv.misc.getColor(value, 'setting line color')            
        return locals()
    
    @vv.misc.PropWithDraw
    def lw():
        """ Get/Set the line width of the bars. 
        """
        def fget(self):
            return self._lw
        def fset(self, value):
            self._lw = float(value)
        return locals()
    
    
    @vv.misc.PropWithDraw
    def color():
        """ Get/Set the color of the bars. The getter returns the color
        of the first bar, or None if there are no bars.
        """
        def fget(self):
            if self._colors:                
                return self._colors[0]
            else:
                return None
        def fset(self, value):
            c = vv.misc.getColor(value)
            self._colors = [c for h in self._hh]
        return locals()
    
    @vv.misc.PropWithDraw
    def colors():
        """ Get/Set the colors of all bars at once. The number of colors
        should match the number of bars. """
        def fget(self):
            return [c for c in self._colors]
        def fset(self, value):
            if len(value) != len(self._colors):
                raise ValueError('Number of colors should match number of bars.')
            getColor = vv.misc.getColor
            self._colors = [getColor(c) for c in value]
        return locals()


if __name__ == '__main__':
    
    vv.figure(1); vv.clf()
    a = vv.gca()
    b = bar([1,2,1,5])
    