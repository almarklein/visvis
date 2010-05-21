# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv

class Bars3D(vv.Wobject):
    
    pass


def bar3(data1, data2=None, width=0.75, axesAdjust=True, axes=None):    
    """ bar3()
    Create a 3D bar chart.
    """
    
    # Parse input
    yy = data1
    xx = range(len(yy))
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create Bars instance
    bars = Bars3D(axes)
    
    # Create boxes    
    for x,y in zip(xx,yy):
        vv.solidBox((x,0,0), (width,width,y), axesAdjust=False, axes=bars)
    
    # Set limits
    axes.SetLimits()#(0,len(xx)), (-1,1),(0,max(yy)))
    
    return bars
    
    
    
if __name__ == '__main__':
    bar3([1,2,3,2,4,3,5], width=0.75) 
    