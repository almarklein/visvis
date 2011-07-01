# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np
import OpenGL.GL as gl


def boxplot(data, width=0.75, axesAdjust=True, axes=None):
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create boxes and boxplot object
    boxes = [BoxPlotBox(d) for d in data]
    bp = BoxPlot(axes, *boxes)
    
    # Adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = True
        axes.cameraType = '2d'
        axes.SetLimits()
    
    # Done
    axes.Draw()
    return bp


class BoxPlotBox(object):
    """ BoxPlotBox
    
    Represents a block in a boxplot. Used for storing information
    such as position of box and whiskers etc.
    
    """
    def __init__(self, data):
        
        # Store data, make numpy array and sort
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        self._data = data.ravel()
        self._data.sort()
        
        # Init width
        self._width = 0.75
        
        # Init style
        self._style = 'minmax'
        
        # Init line style
        self._lc = (0,0,0)
        self._lw = 1
        
        # Calculate now
        self.calculate()
    
    
    def SetWidth(self, w):
        self._width = w
        self.calculate()
    
    
    def SetStyle(self, style):
        
        # Lowercase and check
        style = style.lower()
        if style not in ['default', 'minmax', 'std', 'violin']:
            raise ValueError('Invalid style')
        
        # Set
        self._style = style
        self.calculate()
    
    
    def _percentile(self, data, per):
        #data = sorted(data) # done in __init__
        i = (len(data)-1) * float(per)
        i = int(round(i))
        return data[i]
    
    
    def calculate(self):
        """ calculate()
        
        Calculate the stats, and storing them such that they can
        be drawn easily. 
        
        """
        
        # Get data
        data = self._data
        
        # Get min, max and range
        self._dmin, self._dmax = data.min(), data.max()
        self._drange = self._dmax - self._dmin
        
        # Get mean and std
        self._mean = data.mean()
        self._std = data.std()
        
        # Get percentages
        self._p25 = self._percentile(data, 0.25) 
        self._p50 = self._percentile(data, 0.50) 
        self._p75 = self._percentile(data, 0.75)
        self._IQR = self._p75 - self._p25
        
        # Calculate more?
        if self._style == 'violin':
            self.calculate_violin()
        elif self._style == 'default':
            self.calculate_outliers()
    
    
    def calculate_outliers(self):
        
        data = self._data
        
        # todo:  enable setting border
        
        # Get indices of points beyond whiskers
        w1 = self._p25 - self._IQR * 1.5
        w2 = self._p75 + self._IQR * 1.5
        I1, = np.where(data < w1)
        I2, = np.where(data > w2)
        
        # Get points for whiskers
        if I1:
            self._wmin = data[ I2[-1]+1 ]
        else:
            self._wmin = data[0]
        if I2:
            self._wmax = data[ I1[0]-1 ]
        else:
            self._wmax = data[-1]
        
        # Get outlier points
        Iall = np.concatenate([I1, I2])
        self._outliers = data[ Iall ]
    
    
    def calculate_violin(self):
        
        # Get data and a few other things
        data, drange, IQR = self._data, self._drange, self._IQR
        
        # Get number of bins according to Freedman–Diaconis rule
        bin_size = 2 * IQR * len(data)**(-1.0/3)
        nbins = drange / bin_size
        nbins = min(int(nbins), 128)
        
        # Get histogram
        if np.__version__ < '1.3':
            values, edges = np.histogram(data, nbins, new=True)
        else:
            values, edges = np.histogram(data, nbins)
        
        # The bins are the left bin edges, let's get the centers
        centers = np.empty(values.size, np.float32)
        for i in range(len(values)):
            centers[i] = (edges[i] + edges[i+1]) * 0.5
        
        # Normalize values
        values = values * (0.5 * self._width / values.max())
        
        # Create array with locations
        n = values.size
        points = np.zeros((n*2+1,3), np.float32)
        points[:n,0] = values
        points[:n,1] = centers
        points[n:2*n,0] = -np.flipud(values)
        points[n:2*n,1] = np.flipud(centers)
        points[2*n,0] = values[0]
        points[2*n,1] = centers[0]
        #
        self._points = points
    
    
    def Draw(self, x_offset):
        
        # Prepare color and line width
        clr = self._lc
        gl.glColor3f(clr[0], clr[1], clr[2])
        gl.glLineWidth(self._lw)
        
        # Set line smoothing?
        if self._lw == int(self._lw):
            gl.glDisable(gl.GL_LINE_SMOOTH)
        else:
            gl.glEnable(gl.GL_LINE_SMOOTH)
        
        # Draw
        if self._style == 'violin':
            self.DrawViolin(x_offset)
        elif self._style in ['default', 'minmax', 'std']:
            self.DrawBox(x_offset)
        else:
            raise RuntimeError("Invalid style")
        
        # Reset
        gl.glDisable(gl.GL_LINE_SMOOTH)
    
    
    def DrawBox(self, x_offset):
        
        # Get data
        p25, p50, p75 = self._p25, self._p50, self._p75
        
        # Determine whisker position
        if self._style == 'minmax':
            wmin, wmax = self._dmin, self._dmax
        elif self._style == 'std':
            wmin, wmax = self._mean - self._std, self._mean + self._std
        
        # Relative width
        w1 = self._width * 0.5
        w2 = self._width * 0.125
        
        # Draw box
        gl.glBegin(gl.GL_LINE_LOOP)
        gl.glVertex2f(x_offset-w1, p25)
        gl.glVertex2f(x_offset+w1, p25)
        gl.glVertex2f(x_offset+w1, p75)
        gl.glVertex2f(x_offset-w1, p75)
        gl.glEnd()
        
        # Draw mean, wisker lines, and wiskers
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(x_offset-w1, p50)
        gl.glVertex2f(x_offset+w1, p50)
        #
        gl.glVertex2f(x_offset, p25)
        gl.glVertex2f(x_offset, wmin)
        gl.glVertex2f(x_offset, p75)
        gl.glVertex2f(x_offset, wmax)
        #
        gl.glVertex2f(x_offset-w2, wmin)
        gl.glVertex2f(x_offset+w2, wmin)
        gl.glVertex2f(x_offset-w2, wmax)
        gl.glVertex2f(x_offset+w2, wmax)
        gl.glEnd()
        
    
    def DrawViolin(self, x_offset):
        
        # Get data
        points, p25, p50, p75 = self._points, self._p25, self._p50, self._p75
        
        # Translate points
        points = points.copy()
        points[:,0] += x_offset
        
        # Draw outer lines
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(points)
        gl.glDrawArrays(gl.GL_LINE_STRIP, 0, points.shape[0])
        gl.glFlush()
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        
        # Draw mean p25, p50 and p75
        w2 = self._width * 0.25
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(x_offset-w2, p50)
        gl.glVertex2f(x_offset+w2, p50)
        gl.glVertex2f(x_offset, p25)
        gl.glVertex2f(x_offset, p75)
        gl.glEnd()
    

class BoxPlot(vv.Wobject):
    """
    
    """
    def __init__(self, parent, *boxes):
        vv.Wobject.__init__(self, parent)
        self._boxes = boxes
    
    
    def OnDraw(self):
        
        # Draw all boxes
        for i in range(len(self._boxes)):
            self._boxes[i].Draw(i)
    
    
    def _GetLimits(self):
        
        # xlim and zlim are easy
        x1, x2 = -0.5, len(self._boxes)-0.5
        z1, z2 = 0, 0
        
        # ylim is harder
        y1, y2 = 9999999999999, -99999999999999999
        for box in self._boxes:
            y1 = min(y1, box._dmin)
            y2 = max(y2, box._dmax)
        if not self._boxes:
            y1, y2 = 0,1
        
        # Done
        return vv.Wobject._GetLimits(self, x1, x2, y1, y2, z1, z2)
    
    
    @vv.misc.PropWithDraw
    def lineColor():
        """ Get/Set the line color of the boxes. 
        """
        def fget(self):
            return self._boxes[0]._lc
        def fset(self, value):
            lc = vv.misc.getColor(value, 'setting line color')
            for box in self._boxes:
                box._lc = lc
    
    @vv.misc.PropWithDraw
    def lineWidth():
        """ Get/Set the line width of the boxes. 
        """
        def fget(self):
            return self._boxes[0]._lw
        def fset(self, value):
            for box in self._boxes:
                box._lw = float(value)
    
    
    @vv.misc.PropWithDraw
    def whiskerStyle():
        """ Get/Set the style of the whiskers. 
        """
        def fget(self):
            return self._boxes[0]._style
        def fset(self, value):
            for box in self._boxes:
                box.SetStyle(value)


if __name__ == '__main__':
    
    vv.clf()
    a = vv.gca()
    d1 = np.random.normal(0, 4, (100,100))
    d2 = np.random.normal(2, 3, (20,))
    d3 = np.random.uniform(-1, 3, (100,))
    d4 = [1,2,1,2.0, 8, 2, 3, 1, 2, 2, 3, 2, 2.1]
    
    b = boxplot((d1,d2,d3, d4))
    
   