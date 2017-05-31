# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np
import OpenGL.GL as gl

from visvis.processing.statistics import StatData
from visvis.core.misc import basestring


# todo: enable notch in boxplot

def boxplot(data1, data2=None, width=0.75, whiskers=1.5, axesAdjust=True, axes=None):
    """ boxplot(*args, width=0.75, whiskers=1.5, axesAdjust=True, axes=None)
    
    Create a box and whisker plot and returns a BoxPlot wobject that can
    be used to change the appearance of the boxes (such as color).
    
    If whiskers=='violin' creates a violin plot, which displays the
    kernel density estimate (kde) of each data.
    
    Usage
    -----
      * boxplot(data, ...) creates boxplots for the given list of data
      * boxplot(X, data, ...) also supply x-coordinates for each data
    
    Arguments
    ---------
    X : iterable (optional)
        Specify x position of the boxes.
    data : list
        List of data, where each data is a sequence (something that can be
        passed to numpy.array()).
    width : scalar
        The width of the boxes.
    whiskers : scalar or string
        How to draw the whiskers. If a scalar is given, it defines the
        length of the whiskers as a function of the IQR. In this case any
        points lying beyond the whiskers are drawn as outliers.
        If 'minmax', the whiskers simply extend to the maximal data range.
        If 'std', the whiskers indicate the mean +/- the standard deviation.
        If 'violin', a violin plot is drawn, which shows the probability
        density function completely.
    axesAdjust : bool
        If True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet,
        it is set to False.
    axes : Axes instance
        Display the bars in the given axes, or the current axes if not given.
    
    """
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Pre check
    if data2 is None:
        data_list = data1
    else:
        data_list = data2
    if not isinstance(data_list, (tuple,list)):
        raise ValueError('Data should be given as a list.')
    #
    if data2 is None:
        xx = list(range(len(data_list)))
    else:
        xx = [float(x) for x in data1]
        if len(data_list) != len(xx):
            raise ValueError('Positions do not match length of data.')
    
    # Remove data where x position is invalid
    # At the same time sort data by x position
    validIndices, = np.where(np.isfinite(xx))
    validIndices = sorted(validIndices, key=lambda i:xx[i])
    xx = [xx[i] for i in validIndices]
    data_list = [data_list[i] for i in validIndices]
    
    # Create boxes and boxplot object
    boxes = [BoxPlotBox(d, width, whiskers) for d in data_list]
    bp = BoxPlot(axes, xx, boxes)
    
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
    def __init__(self, data, width, whiskers):
        
        # Get stats of data
        self._stats = StatData(data)
        
        # Init width
        self._width = width
        
        # Init whisker style
        self._whiskers = whiskers
        
        # Init line style
        self._lc = (0,0,0)
        self._lw = 1
        
        # Calculate now
        self.calculate()
    
    
    def SetWidth(self, w):
        self._width = w
        self.calculate()
    
    
    def SetWhiskers(self, whiskers):
        
        # Lowercase and check
        
        if isinstance(whiskers, basestring):
            whiskers = whiskers.lower()
            if whiskers == 'default':
                whiskers = 1.5
            elif whiskers not in ['minmax', 'std', 'violin']:
                raise ValueError('Invalid whiskers style')
        elif isinstance(whiskers, (float, int)):
            whiskers = float(whiskers)
        else:
            raise ValueError('Invalid whiskers style')
        
        # Set
        self._whiskers = whiskers
        self.calculate()
    
    
    def calculate(self):
        """ calculate()
        
        Calculate the stats, and storing them such that they can
        be drawn easily.
        
        """
        
        # Init limts
        self._limits = vv.Range(self._stats.dmin, self._stats.dmax)
        
        # Calculate more?
        if isinstance(self._whiskers, float):
            self.calculate_outliers()
        elif self._whiskers == 'violin':
            self.calculate_violin()
        else:
            pass # we have all the info we need
    
    
    def calculate_outliers(self):
        
        # Get stats and data
        stats = self._stats
        data = stats._data
        
        # Set border
        whiskerWidth = 1.5
        if isinstance(self._whiskers, float):
            whiskerWidth = self._whiskers
        
        # Get indices of points beyond whiskers
        w1 = stats.Q1 - stats.IQR * whiskerWidth
        w2 = stats.Q3 + stats.IQR * whiskerWidth
        I1, = np.where(data < w1)
        I2, = np.where(data > w2)
        
        # Get points for whiskers
        if I1.size:
            self._wmin = data[ I1[-1]+1 ]
        else:
            self._wmin = data[0]
        if I2.size:
            self._wmax = data[ I2[0]-1 ]
        else:
            self._wmax = data[-1]
        
        # Get outlier points
        Iall = np.concatenate([I1, I2])
        self._outliers = data[ Iall ]
    
    
    def calculate_violin(self):
        
        # Get stats
        stats = self._stats
        
        # Get kernel density estimate
        nbins = stats.best_number_of_bins(8, 128)
        centers, values = stats.kde(nbins)
        
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
        
        # Update limits
        self._limits = vv.Range(centers[0], centers[-1])
    
    
    def Draw(self, x_offset):
        
        # Prepare color and line width
        clr = self._lc
        gl.glColor3f(clr[0], clr[1], clr[2])
        gl.glLineWidth(self._lw)
        
        # Set line smoothing
        if self._lw == int(self._lw):
            gl.glDisable(gl.GL_LINE_SMOOTH)
        else:
            gl.glEnable(gl.GL_LINE_SMOOTH)
        
        # Draw
        if self._whiskers == 'violin':
            self.DrawViolin(x_offset)
        else:
            self.DrawBox(x_offset)
        
        # Reset
        gl.glEnable(gl.GL_LINE_SMOOTH)
    
    
    def DrawBox(self, x_offset):
        
        # Get data
        stats = self._stats
        
        # Determine whisker position
        if isinstance(self._whiskers, float):
            wmin, wmax = self._wmin, self._wmax
        elif self._whiskers == 'minmax':
            wmin, wmax = stats.dmin, stats.dmax
        elif self._whiskers == 'std':
            wmin, wmax = stats.mean - stats.std, stats.mean + stats.std
        
        
        # Relative width
        w1 = self._width * 0.5
        w2 = self._width * 0.125
        
        # Draw box
        gl.glBegin(gl.GL_LINE_LOOP)
        gl.glVertex2f(x_offset-w1, stats.Q1)
        gl.glVertex2f(x_offset+w1, stats.Q1)
        gl.glVertex2f(x_offset+w1, stats.Q3)
        gl.glVertex2f(x_offset-w1, stats.Q3)
        gl.glEnd()
        
        # Draw mean, wisker lines, and wiskers
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(x_offset-w1, stats.Q2)
        gl.glVertex2f(x_offset+w1, stats.Q2)
        #
        gl.glVertex2f(x_offset, stats.Q1)
        gl.glVertex2f(x_offset, wmin)
        gl.glVertex2f(x_offset, stats.Q3)
        gl.glVertex2f(x_offset, wmax)
        #
        gl.glVertex2f(x_offset-w2, wmin)
        gl.glVertex2f(x_offset+w2, wmin)
        gl.glVertex2f(x_offset-w2, wmax)
        gl.glVertex2f(x_offset+w2, wmax)
        gl.glEnd()
        
        # Draw outliers?
        if isinstance(self._whiskers, float):
            # Group outliers
            outliers = []
            for p in self._outliers:
                if outliers and outliers[0][-1] == p:
                    outliers[0].append(p)
                else:
                    outliers.append([p])
            # Draw outliers
            w3 = self._width * 0.125*0.5
            gl.glPointSize(5)
            gl.glEnable(gl.GL_POINT_SMOOTH)
            gl.glBegin(gl.GL_POINTS)
            for outlierGroup in outliers:
                offset = - (len(outlierGroup)-1) * w3 * 0.5
                offset = max(offset, -w1)
                for i in range(len(outlierGroup)):
                    p = outlierGroup[i]
                    gl.glVertex2f(x_offset+offset+w3*i, p)
            gl.glEnd()
    
    
    def DrawViolin(self, x_offset):
        
        # Get stats
        stats = self._stats
        
        # Smooth lines
        gl.glEnable(gl.GL_LINE_SMOOTH)
        
        # Translate points
        points = self._points.copy()
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
        gl.glVertex2f(x_offset-w2, stats.Q2)
        gl.glVertex2f(x_offset+w2, stats.Q2)
        gl.glVertex2f(x_offset, stats.Q1)
        gl.glVertex2f(x_offset, stats.Q3)
        gl.glEnd()
    

class BoxPlot(vv.Wobject):
    """
    
    """
    def __init__(self, parent, xx, boxes):
        vv.Wobject.__init__(self, parent)
        self._xx = xx
        self._boxes = boxes
    
    
    def OnDraw(self):
        
        # Draw all boxes
        for i in range(len(self._boxes)):
            self._boxes[i].Draw(self._xx[i])
    
    
    def _GetLimits(self):
        
        # xlim and zlim are easy
        #x1, x2 = 0.5, len(self._boxes)-0.5
        x1 = self._xx[0] - self._boxes[0]._width * 1.05
        x2 = self._xx[-1] + self._boxes[-1]._width * 1.05
        z1, z2 = 0, 0.2
        
        # ylim is harder
        y1, y2 = 9999999999999, -99999999999999999
        for box in self._boxes:
            y1 = min(y1, box._stats.dmin)
            y2 = max(y2, box._stats.dmax)
        if not self._boxes:
            y1, y2 = 0,1
        
        # Done
        return vv.Wobject._GetLimits(self, x1, x2, y1, y2, z1, z2)
    
    
    @vv.misc.PropWithDraw
    def lc():
        """ Get/Set the line color of the boxes.
        """
        def fget(self):
            return self._boxes[0]._lc
        def fset(self, value):
            lc = vv.misc.getColor(value, 'setting line color')
            for box in self._boxes:
                box._lc = lc
        return locals()
    
    @vv.misc.PropWithDraw
    def lw():
        """ Get/Set the line width of the boxes.
        """
        def fget(self):
            return self._boxes[0]._lw
        def fset(self, value):
            for box in self._boxes:
                box._lw = float(value)
        return locals()
    
    
    @vv.misc.PropWithDraw
    def whiskers():
        """ Get/Set the style of the whiskers.
        """
        def fget(self):
            return self._boxes[0]._whiskers
        def fset(self, value):
            for box in self._boxes:
                box.SetWhiskers(value)
        return locals()


if __name__ == '__main__':
    # Create data
    d1 = np.random.normal(1, 4, (1000,1000))
    d2 = np.random.normal(2, 3, (20,))
    d3 = np.random.uniform(-1, 3, (100,))
    d4 = [1,2,1,2.0, 8, 2, 3, 1, 2, 2, 3, 2, 2.1, 8, 8, 8, 8, 8,  1.2, 1.3, 0, 0, 1.5, 2]
    # Show boxplot
    b = vv.boxplot((d1,d2,d3, d4), width=0.8, whiskers='violin')
