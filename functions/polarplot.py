# -*- coding: utf-8 -*-
# Copyright (C) 2012, Keith Smith
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.
#
# Thanks to Keith Smith for implementing the polar plot functionality.

import numpy as np
import visvis as vv

from visvis.utils.pypoints import Pointset, is_Point, is_Pointset
from visvis import PolarLine


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


def _SetLimitsAfterDraw(event):
    """ To be able to set the limits after the first draw. """
    # Set limits
    fig = event.owner
    for axis in fig.FindObjects(vv.axises.PolarAxis2D):
        limits = axis.GetLimits()
        axis.SetLimits(rangeTheta=limits[0], rangeR=limits[1])
    # Unsubscribe and redraw
    fig.eventAfterDraw.Unbind(_SetLimitsAfterDraw)
    fig.Draw()

    
def polarplot(data1, data2=None, inRadians=False,
            lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k',
            alpha=1, axesAdjust=True, axes=None, **kwargs):
    """ polarplot(*args, inRadians=False,
            lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k',
            alpha=1, axesAdjust=True, axes=None):
    
    Plot 2D polar data, using a polar axis to draw a polar grid.
    
    Usage
    -----
      * plot(Y, ...) plots a 1D polar signal.
      * plot(X, Y, ...) also supplies angular coordinates
      * plot(P, ...) plots using a Point or Pointset instance
    
    Keyword arguments
    -----------------
    (The longer names for the line properties can also be used)
    lw : scalar
        lineWidth. The width of the line. If zero, no line is drawn.
    mw : scalar
        markerWidth. The width of the marker. If zero, no marker is drawn.
    mew : scalar
        markerEdgeWidth. The width of the edge of the marker.
    lc : 3-element tuple or char
        lineColor. The color of the line. A tuple should represent the RGB
        values between 0 and 1. If a char is given it must be
        one of 'rgbmcywk', for reg, green, blue, magenta, cyan, yellow,
        white, black, respectively.
    mc : 3-element tuple or char
        markerColor. The color of the marker. See lineColor.
    mec : 3-element tuple or char
        markerEdgeColor. The color of the edge of the marker.
    ls : string
        lineStyle. The style of the line. (See below)
    ms : string
        markerStyle. The style of the marker. (See below)
    axesAdjust : bool
        If axesAdjust==True, this function will call axes.SetLimits(), and set
        the camera type to 2D.
    axes : Axes instance
        Display the image in this axes, or the current axes if not given.
    
    Line styles
    -----------
      * Solid line: '-'
      * Dotted line: ':'
      * Dashed line: '--'
      * Dash-dot line: '-.' or '.-'
      * A line that is drawn between each pair of points: '+'
      * No line: '' or None.
    
    Marker styles
    -------------
      * Plus: '+'
      * Cross: 'x'
      * Square: 's'
      * Diamond: 'd'
      * Triangle (pointing up, down, left, right): '^', 'v', '<', '>'
      * Pentagram star: 'p' or '*'
      * Hexgram: 'h'
      * Point/cirle: 'o' or '.'
      * No marker: '' or None
    
    Polar axis
    ----------
    This polar axis has a few specialized methods for adjusting the polar
    plot. Access these via vv.gca().axis.
      * SetLimits(thetaRange, radialRange)
      * thetaRange, radialRange = GetLimits()
      * angularRefPos: Get and Set methods for the relative screen
        angle of the 0 degree polar reference.  Default is 0 degs
        which corresponds to the positive x-axis (y =0)
      * isCW: Get and Set methods for the sense of rotation CCW or
        CW. This method takes/returns a bool (True if the default CW).
    
    Interaction
    -----------
      * Drag mouse up/down to translate radial axis.
      * Drag mouse left/right to rotate angular ref position.
      * Drag mouse + shift key up/down to rescale radial axis (min R fixed).
    
    """

    # create a dict from the properties and combine with kwargs
    tmp = {'lineWidth': lw, 'lineColor': lc, 'lineStyle': ls,
                'markerWidth': mw, 'markerColor': mc, 'markerStyle': ms,
                'markerEdgeWidth': mew, 'markerEdgeColor': mec}
    for i in tmp:
        if not i in kwargs:
            kwargs[i] = tmp[i]
    
    ##  create the data
    if is_Pointset(data1):
        pp = data1
    elif is_Point(data1):
        pp = Pointset(data1.ndim)
        pp.append(data1)
    else:

        if data1 is None:
            raise ValueError("The first argument cannot be None!")
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
            raise ValueError("Array dimensions do not match! %i vs %i " %
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
    fig = axes.GetFigure()
    
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
#     axes.axis.SetLimits()
    
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = True
        axes.cameraType = '2d'
        axes.SetLimits()
    
    # Subsribe after-draw event handler
    # (unsubscribe first in case we do multiple plots)
    fig.eventAfterDraw.Unbind(_SetLimitsAfterDraw)
    fig.eventAfterDraw.Bind(_SetLimitsAfterDraw)
    
    # Return
    axes.Draw()
    return l


if __name__ == '__main__':
    # Make data
    angs = 0.1 + np.linspace(-90, 90, 181)  # 0.1+ get rid of singularity
    angsRads = np.pi * angs / 180.0
    mag = 10 * np.log10(np.abs(np.sin(10 * angsRads) / angsRads)) + angsRads
    mag = mag - np.max(mag)
    # Show data
    vv.polarplot( angs, mag, lc='b')
    vv.polarplot(angs+20, mag, lc='r', lw=2)
    a = vv.gca() # Triggers an update required for polar plots
