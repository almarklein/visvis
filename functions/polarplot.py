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


def polarplot(data1, data2=None, data3=None, 
            lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k', 
            alpha=1, setlimits=True, axes=None, **kwargs):
    """ plot(data1, data2=None, data3=None, 
            lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k', 
            alpha=1, setlimits=True, axes=None):
    
    Plot 1, 2 or 3 dimensional data:
      * plot([1,4,2]) plots a 1D signal, with the values plotted 
        along the y-axis
      * plot([10,11,12],[1,4,2]) also supplies x coordinates
      * plot([10,11,12],[1,4,2],[8,8,8]) also supplies z coordinates
      
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
        
        d3 = data3
        if data3 is None:
            data3 = 0.1*np.ones(data1.shape)
        else:
            data3 = makeArray(data3)
        
        if data2 is None:
            if d3 is not None:
                tmp = "third argument in plot() ignored, as second not given."
                print "Warning: " + tmp
            # y data is given, xdata must be a range starting from 1
            data2 = data1
            data1 = np.arange(1,data2.shape[0]+1)
            data3 = 0.1*np.ones(data2.shape)
        else:
            data2 = makeArray(data2)
        
        # check dimensions
        L = data1.size
        if L != data2.size or L != data3.size:
            raise("Array dimensions do not match! %i vs %i vs %i" % 
                    (data1.size, data2.size, data3.size))
        
        # build points
        data1 = data1.reshape((data1.size,1))
        data2 = data2.reshape((data2.size,1))
        data3 = data3.reshape((data3.size,1))
        
        tmp = data1, data2, data3
        pp = Pointset( np.concatenate(tmp, 1) )
        #pp.points = np.empty((L,3))
        #pp.points[:,0] = data1.ravel()
        #pp.points[:,1] = data2.ravel()
        #pp.points[:,2] = data3.ravel()
        
        
    
    ## create the line
    if axes is None:
        axes = vv.gca() 
    axes.cameraType = '2d'
    #axes._CorrectPositionForLabels()
    axes.daspectAuto = False
    axes.axisType = 'polar'

    l = PolarLine(axes, np.pi*data1/180.0, data2)
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
        axes.SetLimits()
    axes.Draw()
    return l
    