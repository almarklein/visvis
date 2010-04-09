""" Plot 1, 2 or 3 dimensional data. """
#   This file is part of VISVIS.
#    
#   VISVIS is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as 
#   published by the Free Software Foundation, either version 3 of 
#   the License, or (at your option) any later version.
# 
#   VISVIS is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
# 
#   You should have received a copy of the GNU Lesser General Public 
#   License along with this program.  If not, see 
#   <http://www.gnu.org/licenses/>.
#
#   Copyright (C) 2010 Almar Klein
from visvis.points import Point, Pointset
import numpy as np
from visvis.line import PolarLine
import visvis as vv
from visvis.misc import Range

def makeArray(data):
    if isinstance(data,np.ndarray):
        return data
    else:
        # create numpy array
        try:
            l = len(data)
            a = np.empty((l,1))
            for i in range(len(data)):
                a[i] = data[i]                
            return a
        except TypeError:
            raise Exception("Cannot plot %s" % data.__class__.__name__)


def polarplot(data1, data2=None,  inRadians = False,
            lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k', 
            alpha=1, setlimits=True, axes=None, **kwargs):
    """ plot(data1, data2=None, inRadians = False, 
            lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k', 
            alpha=1, setlimits=True, axes=None):
    
    Polar Plot 1, 2 or 3 dimensional data:
      * plot([1,4,2]) plots a 1D signal, with the values plotted 
        along the theta-axis every degree
      * plot([10,11,12],[1,4,2]) also supplies theta coordinates in degrees
        or in radians if inRadians = True

      
    The longer names for the line properties can also be used:
      * lineWidth: lw
      * lineColor: lc
      * lineStyle: ls
      * markerWidth: mw
      * markerColor: mc
      * markerStyle: ms
      * markerEdgeWidth: mew
      * markerEdgeColor: mec
    
    If setlimits is False, plots the new data without resetting
    the displayed range.
    
    polarplot uses PolarAxis2D
    PolarAxis2D draws a polar grid, and modifies PolarLine objects 
    to properly plot onto the polar grid.  PolarAxis2D has some 
    specialized methods unique to it for adjusting the polar plot.
    Access these via vv.gca().axis.
    These include:
        SetLimits(thetaRange, radialRange): 
        thetaRange, radialRange = GetLimits():

        angularRefPos: Get and Set methods for the relative screen 
        angle of the 0 degree polar reference.  Default is 0 degs 
        which corresponds to the positive x-axis (y =0)
        
        isCW: Get and Set methods for the sense of rotation CCW or 
        CW. This method takes/returns a bool (True if the default CW).

        Drag mouse up/down to translate radial axis
        Drag mouse left/right to rotate angular ref position
        Drag mouse + shift key up/down to rescale radial axis (min R fixed)
    
    """

    # create a dict from the properties and combine with kwargs
    tmp     = { 'lineWidth':lw,         'lineColor':lc,     'lineStyle':ls,
                'markerWidth':mw,       'markerColor':mc,   'markerStyle':ms,
                'markerEdgeWidth':mew,  'markerEdgeColor':mec}
    for i in tmp:
        if not i in kwargs:
            kwargs[i] = tmp[i]
    
    
    ##  create the data
    
    if isinstance(data1,Pointset):
        pp = data1
    elif isinstance(data1,Point):
        pp = Pointset(data1.ndim)
        pp.Append(data1)
    else:   
        
        if data1 is None:
            raise Exception("The first argument cannot be None!")
        data1 = makeArray(data1)
        
        
        if data2 is None:
            # R data is given, thetadata must be a range starting from 0 degrees
            data2 = data1
            data1 = np.arange(0,data2.shape[0])
        else:
            data2 = makeArray(data2)
        
        # check dimensions
        L = data1.size
        if L != data2.size:
            raise("Array dimensions do not match! %i vs %i " % 
                    (data1.size, data2.size))
        
        # build points
        data1 = data1.reshape((data1.size,1))
        data2 = data2.reshape((data2.size,1))
        
        
    if not inRadians:
        data1 = np.pi*data1/180.0
    
    ## create the line
    if axes is None:
        axes = vv.gca() 
    axes.cameraType = '2d'

    axes.daspectAuto = False
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
    
    ## done...
    if setlimits:
        axes.axis.SetLimits()

    axes.axis.Draw()
    
    # The following is a trick to get the polar plot to center.
    # Never found out why it initial draws too high, but this works
    vv.gcf().position.w = vv.gcf().position.w + 1
    vv.gcf().position.w = vv.gcf().position.w - 1

    return l
    
