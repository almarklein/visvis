# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np
import OpenGL.GL as gl

# todo: make generic hist method that used kde if n < 10000 and 
# np.hist otherwise. Or based on auto-calculated nbins or something.

class StatData:
    def __init__(self, data):
        
        # Make numpy array, sort, make 1D, store
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        self._data = np.sort(data.ravel())
        
        # Calculate some stats
        self._mean = self._data.mean()
        self._std = self._data.std()
    
    def __repr__(self):
        return '<StatData object with %i elements>' % self.size
    
    def __str__(self):
        s = 'Summary of StatData object:\n'
        for key in ['size', 'dmin', 'dmax', 'drange', 'mean', 'std', 
                    'Q1', 'Q2', 'Q3', 'IQR']:
            value = str(getattr(self, key))
            line = key.rjust(10) + ' = ' + value + '\n'
            s += line
        return s
    
    @property
    def size(self):
        """ Get the number of elements in the data.
        """
        return self._data.size
    
    @property
    def drange(self):
        """ Get the range of the data (max-min).
        """
        return float(self._data[-1] - self._data[0])
    
    @property
    def dmin(self):
        """ Get the minimum of the data.
        """
        return self._data[0]
    
    @property
    def dmax(self):
        """ Get the max of the data.
        """
        return self._data[-1]
    
    @property
    def mean(self):
        """ Get the mean of the data.
        """
        return self._mean
    
    @property
    def std(self):
        """ Get the standard deviation of the data.
        """
        return self._std
    
    @property
    def Q1(self):
        """ Get first quartile of the data (i.e. the 25th percentile).
        """
        return self.percentile(0.25)
    
    @property
    def Q2(self):
        """ Get second quartile of the data (i.e. the 50th percentile).
        This is the median.
        """
        return self.percentile(0.50)
    
    @property
    def median(self):
        """ Get the median. This is the same as Q2.
        """
        return self.percentile(0.50)
    
    @property
    def Q3(self):
        """ Get second quartile of the data (i.e. the 50th percentile).
        """
        return self.percentile(0.75)
    
    @property
    def IQR(self):
        """ Get the inter-quartile range; the range where 50% of the
        data is.
        """
        return self.percentile(0.75) - self.percentile(0.25)
    
    
    def percentile(self, per, interpolate=True):
        """ percentile(per, interpolate=True)
        
        Given a percentage (as a number between 0 and 1)
        return the value corresponding to that percentile.
        
        By default, the value is linearly interpolated if it does not
        fall exactly on an existing value.
        """
        
        # Calculate float index
        data = self._data
        i = (data.size-1) * float(per)
        
        # Sample the value
        if interpolate:
            # http://en.wikipedia.org/wiki/Percentile
            ik = int(i)
            ir = i - ik
            if ik >= data.size-1:
                return data[ik]
            else:
                return data[ik] + ir*(data[ik+1] - data[ik])
        else:
            i = int(round(i))
            return data[i]
    
    
    def histogram_np(self, nbins=None, normed=True):
        
        if nbins is None:
            nbins = self.best_number_of_bins()
        
        # Get histogram        
        if np.__version__ < '1.3':
            values, edges = np.histogram(self._data, nbins, normed=normed, new=True)
        else:
            values, edges = np.histogram(self._data, nbins, normed=normed)
        
        # The bins are the left bin edges, let's get the centers
        centers = np.empty(values.size, np.float32)
        for i in range(len(values)):
            centers[i] = (edges[i] + edges[i+1]) * 0.5
        
        # Done
        return centers, values
    
    
    def histogram(self, nbins=None):
        
        if nbins is None:
            nbins = self.best_number_of_bins()
        
        return self._kernel_density_estimate(nbins, [1])
    
    
    def kde(self, nbins=None, kernel=None):
        
        best_nbins = self.best_number_of_bins()
        
        if nbins is None:
            nbins = 4 * best_nbins
        if kernel is None:
            kernel = float(nbins) / best_nbins
        
        return self._kernel_density_estimate(nbins, kernel)
    
    
    def best_number_of_bins(self, minbins=8, maxbins=256):
        """ calculate_number_of_bins(maxbins, minbins=8, maxbins=256)
        
        Calculates the best number of bins to make a histogram 
        of this data, according to Freedman–Diaconis rule.
        
        """ 
        # Get data
        data = self._data
        
        # Get number of bins according to Freedman–Diaconis rule
        bin_size = 2 * self.IQR * data.size**(-1.0/3)
        nbins = self.drange / bin_size
        nbins = max(minbins, min(maxbins, int(nbins)))
        
        # Done
        return nbins
    
    
    def _kernel_density_estimate(self, n, kernel):
        """ kernel density estimate(n, kernel)
        """
        
        # Get data
        data = self._data
        
        # Get some statistics
        dmin, dmax, drange = self.dmin, self.dmax, self.drange
        if not drange:
            # A single value, or all values the same
            eps = 0.5
            dmin, dmax, drange = dmin-eps, dmax+eps, 2*eps
        
        # Construct kernel
        if isinstance(kernel, float):
            sigma = kernel
            ktail = int(sigma*3)
            kn = ktail*2 + 1
            t = np.arange(-kn/2.0+0.5, kn/2.0, 1.0, dtype=np.float64)
            k = np.exp(- t**2 / (2*sigma**2) )
        else:
            k = np.array(kernel, dtype='float64').ravel()
            ktail = int( k.size/2 )
        
        
        
        # Get data "bins", these are the bin centers
        factor = drange / n
        nbins = n + ktail * 2 + 1
        bins = (np.arange(nbins) - ktail) * factor + dmin
        
        # Normalize kernel
        # todo: how to normalize?
        k /= k.sum() * data.size / nbins
        
        # Splat the kernels in!
        # kde represents the counts for each bin.
        # xxi represents the data, but scaled to the bin indices. The elements
        # in xxi are sorted (because data is), and if data.size >> nbins
        # there are many equal values in a row. We make use of that to make
        # the bin splatting very efficient.
        kde = np.zeros_like(bins)
        xx = (data-dmin) * (1.0/factor) # no +ktail here, no j-ktail at kernel index
        xxi = (xx+0.4999999).astype('int32') 
        #
        # Init binary search
        step = max(1, int(data.size/n))
        i0, i1, i2 = 0, 0, step
        val = xxi[i0]
        totalSplats = 0
        #
        i2 = min(i2, xxi.size-1)
        while i1<i2:
            if xxi[i2] > val:
                if xxi[i2-1] == val:
                    # === found it! 
                    # Splat kernel
                    nSplats = i2-i0
                    kde[val:val+k.size] += k * nSplats
                    totalSplats += nSplats
                    # Reset for next value
                    step = max(1, nSplats)
                    i0, i1, i2 = i2, i2, i2+step
                    val = xxi[i0]
                else:
                    # Too far
                    step = max(1, int(0.5*step))
                    i2 = i1 + step
            else:
                # Not far enough
                i1, i2 = i2, i2+step
            # Not beyond end!
            i2 = min(i2, xxi.size-1)
        # Wrap up
        if True:
            # Splat kernel
            nSplats = i2-i0+1
            kde[val:val+k.size] += k * nSplats
            totalSplats += nSplats
        
        # Check (should be equal)
        #print totalSplats, xxi.size
        
        if False:
            # Analog algoritm, better readable perhaps, but much slower:
            for x in data:
                i = (x-dmin) * (1.0/factor) + ktail
                i = int(round(i))
                for j in range(k.size):
                    kde[i+j-ktail] += k[j]
        
        # Done
        return bins, kde


def boxplot(data, width=0.75, style='default', axesAdjust=True, axes=None):
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create boxes and boxplot object
    boxes = [BoxPlotBox(d, width, style) for d in data]
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
    def __init__(self, data, width, style):
        
        # Get stats of data
        self._stats = StatData(data)
        
        # Init width
        self._width = width
        
        # Init style
        self._style = style
        
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
    
    
    def calculate(self):
        """ calculate()
        
        Calculate the stats, and storing them such that they can
        be drawn easily. 
        
        """
        
        # Init limts
        self._limits = self._stats.dmin, self._stats.dmax
        
        # Calculate more?
        if self._style == 'violin':
            self.calculate_violin()
        elif self._style == 'default':
            self.calculate_outliers()
        
    
    def calculate_outliers(self):
        
        # Get stats and data
        stats = self._stats
        data = stats._data
        
        # todo:  enable setting border
        
        # Get indices of points beyond whiskers
        w1 = stats.Q1 - stats.IQR * 1.5
        w2 = stats.Q3 + stats.IQR * 1.5
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
        
        # Get stats and data
        stats = self._stats
        data = stats._data
        
        centers, values = stats.kde()
        
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
        stats = self._stats
        
        # Determine whisker position
        if self._style == 'minmax':
            wmin, wmax = stats.dmin, stats.dmax
        elif self._style == 'std':
            wmin, wmax = stats.mean - stats.std, stats.mean + stats.std
        elif self._style == 'default':
            wmin, wmax = self._wmin, self._wmax
        
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
        if self._style == 'default':
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
                offset = - len(outlierGroup) * w3 * 0.5
                offset = max(offset, -w1)
                for i in range(len(outlierGroup)):
                    p = outlierGroup[i]
                    gl.glVertex2f(x_offset+offset+w3*i, p)
            gl.glEnd()
    
    
    def DrawViolin(self, x_offset):
        
        # Get stats
        stats = self._stats
        
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
            y1 = min(y1, box._limits.min)
            y2 = max(y2, box._limits.max)
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
    
    vv.figure(1); vv.clf()
    a = vv.gca()
    d1 = np.random.normal(1, 4, (1000,1000))
    d2 = np.random.normal(2, 3, (20,))
    d3 = np.random.uniform(-1, 3, (100,))
    d4 = [1,2,1,2.0, 8, 2, 3, 1, 2, 2, 3, 2, 2.1, 8, 8, 8, 8, 8,  1.2, 1.3, 0, 0, 1.5, 2]
    
    b = boxplot((d1,d2,d3, d4), 0.8, 'violin')
    ##
    dd = d4
    stat = StatData(dd)
    bins1, values1 = stat.histogram_np()
    bins2, values2 = stat.histogram()
    bins3, values3 = stat.kde(     )
    vv.figure(2); vv.clf()
    vv.plot(bins1, values1, lc='b', ms='.', mc='b', ls=':', mw=5)
    vv.plot(bins2, values2, lc='r', ms='.', mc='r')
    vv.plot(bins3, values3, lc='g', ms='.', mc='g')
    