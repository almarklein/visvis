# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein
#
# The polar plot functionality was coded by 

from visvis.points import Point, Pointset
import numpy as np
from visvis.line import PolarLine
import visvis as vv
from visvis.misc import Range


def makeArray(data):
    if isinstance(data, np.ndarray):
        return data
    else:
        # create numpy array
        try:
            l = len(data)
            a = np.empty((l, 1))
            for i in range(len(data)):
                a[i] = data[i]
            return a
        except TypeError:
            raise Exception("Cannot plot %s" % data.__class__.__name__)


def polarplot(data1, data2=None,  inRadians=False,
            lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k',
            alpha=1, axesAdjust=True, axes=None, **kwargs):
    """ polarplot(data1, data2=None, inRadians=False,
            lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k',
            alpha=1, axesAdjust=True, axes=None):
    
    Plot 2D polar data. polarplot uses a polar axis to draw a polar grid, 
    and has some specialized methods for adjusting the polar plot.
    Access these via vv.gca().axis.
    These include:
        * SetLimits(thetaRange, radialRange):
        * thetaRange, radialRange = GetLimits():
        
        * angularRefPos: Get and Set methods for the relative screen
          angle of the 0 degree polar reference.  Default is 0 degs
          which corresponds to the positive x-axis (y =0)
        
        * isCW: Get and Set methods for the sense of rotation CCW or
          CW. This method takes/returns a bool (True if the default CW).

    Drag mouse up/down to translate radial axis.    
    Drag mouse left/right to rotate angular ref position.    
    Drag mouse + shift key up/down to rescale radial axis (min R fixed).
    
    If axesAdjust==True, this function will call axes.SetLimits() and set
    the camera type to 2D. If daspectAuto has not been set yet, it is set
    to True.

    

    """

    # create a dict from the properties and combine with kwargs
    tmp = {'lineWidth': lw, 'lineColor': lc, 'lineStyle': ls,
                'markerWidth': mw, 'markerColor': mc, 'markerStyle': ms,
                'markerEdgeWidth': mew, 'markerEdgeColor': mec}
    for i in tmp:
        if not i in kwargs:
            kwargs[i] = tmp[i]
    
    ##  create the data
    if isinstance(data1, Pointset):
        pp = data1
    elif isinstance(data1, Point):
        pp = Pointset(data1.ndim)
        pp.Append(data1)
    else:

        if data1 is None:
            raise Exception("The first argument cannot be None!")
        data1 = makeArray(data1)
        
        if data2 is None:
            # R data is given, thetadata must be
            # a range starting from 0 degrees
            data2 = data1
            data1 = np.arange(0, data2.shape[0])
        else:
            data2 = makeArray(data2)
        
        # check dimensions
        L = data1.size
        if L != data2.size:
            raise("Array dimensions do not match! %i vs %i " %
                    (data1.size, data2.size))
        
        # build points
        data1 = data1.reshape((data1.size, 1))
        data2 = data2.reshape((data2.size, 1))

    if not inRadians:
        data1 = np.pi * data1 / 180.0

    ## create the line
    if axes is None:
        axes = vv.gca()
    axes.axisType = 'polar'
    
    l = PolarLine(axes, data1, data2)
    l.lw = kwargs['lineWidth']
    l.lc = kwargs['lineColor']
    l.ls = kwargs['lineStyle']
    l.mw = kwargs['markerWidth']
    l.mc = kwargs['markerColor']
    l.ms = kwargs['markerStyle']
    l.mew = kwargs['markerEdgeWidth']
    l.mec = kwargs['markerEdgeColor']
    l.alpha = alpha

    ## almost done...
    
    # Init axis
    axes.axis.SetLimits( rangeTheta=0, rangeR=vv.Range(-40, 5))
    ra = axes.axis._radialRange
    axes.axis.SetLimits(rangeR=(ra.min, ra.min + ra.range*1.01))
    axes.axis.Draw()
    
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = True
        axes.cameraType = '2d'
        axes.SetLimits()
    
    # The following is a trick to get the polar plot to center.
    # Never found out why it initial draws too high, but this works
#     vv.gcf().position.w = vv.gcf().position.w + 1
#     vv.gcf().position.w = vv.gcf().position.w - 1
    
    # Return
    axes.Draw()
    return l


if __name__ == '__main__':
    # Make data
    import numpy as np
    angs = 0.1 + np.linspace(-90, 90, 181)  # 0.1+ get rid of singularity
    angsRads = np.pi * angs / 180.0
    mag = 10 * np.log10(np.abs(np.sin(10 * angsRads) / angsRads)) + angsRads
    mag = mag - np.max(mag)    
    # Show data
    vv.polarplot( angs, mag, lc='b')
    vv.polarplot(angs+20, mag, lc='r', lw=2)
    
    axes = vv.gca()
    