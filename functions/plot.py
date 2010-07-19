# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

from visvis.points import Point, Pointset
import numpy as np

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


def plot(data1, data2=None, data3=None, 
            lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k', 
            alpha=1, axesAdjust=True, axes=None, **kwargs):
    """ plot(*args, lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k', 
            alpha=1, axesAdjust=True, axes=None):
    
    Plot 1, 2 or 3 dimensional data and return the Line object:
      * plot(Y, ...) plots a 1D signal, with the values plotted along the y-axis
      * plot(X, Y, ...) also supplies x coordinates
      * plot(X, Y, Z, ...) also supplies z coordinates
      * plot(P, ...) plots using a Point or Pointset instance
      
    The longer names for the line properties can also be used:
      * lineWidth: lw
      * lineColor: lc
      * lineStyle: ls
      * markerWidth: mw
      * markerColor: mc
      * markerStyle: ms
      * markerEdgeWidth: mew
      * markerEdgeColor: mec
    
    If axesAdjust==True, this function will call axes.SetLimits(), set
    the camera type to 2D when plotting 2D data and to 3D when plotting
    3D data. If daspectAuto has not been set yet, it is set to True.
    """
    
    # create a dict from the properties and combine with kwargs
    tmp     = { 'lineWidth':lw,         'lineColor':lc,     'lineStyle':ls,
                'markerWidth':mw,       'markerColor':mc,   'markerStyle':ms,
                'markerEdgeWidth':mew,  'markerEdgeColor':mec}
    for i in tmp:
        if not i in kwargs:
            kwargs[i] = tmp[i]
    
    
    # init dimension variable
    camDim = 0
    
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
            camDim = 2
        else:
            camDim = 3
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
            raise Exception("Array dimensions do not match! %i vs %i vs %i" % 
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
    
    # Process camdim for given points or pointsets
    if not camDim:
        camDim = pp.ndim
        
    
    ## create the line
    if axes is None:
        axes = vv.gca()    
    l = vv.Line(axes, pp)
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
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = True
        axes.cameraType = str(camDim)+'d'
        axes.SetLimits()
    
    axes.Draw()
    return l


if __name__ == '__main__':
    vv.figure()
    vv.subplot(311)
    vv.plot([3,4,5],[7,5,4])
    vv.subplot(312)
    vv.plot([1,3,1,4,1,5,1,6,1,7,6,5,4,3,2,1])
    vv.subplot(313)
    vv.plot([3,4,5],[7,5,4], [1,2,3])
