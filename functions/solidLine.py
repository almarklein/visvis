# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import numpy as np
import visvis as vv
from visvis.points import Point, Pointset
from visvis.processing import lineToMesh

def solidLine(pp, radius=1.0, N=16, axesAdjust=True, axes=None):
    """ solidLine(pp, radius=1.0, N=16, axesAdjust=True, axes=None)
    
    Creates a solid line in 3D space. pp can be a Pointset.
    Radius can also specify the radius for each point.
    """
    
    # Check first argument
    if isinstance(pp, Pointset):
        pass
    else:
        raise ValueError('solidLine() needs a Pointset or list of pointsets.')
    
    # Obtain mesh and make a visualization mesh
    baseMesh = lineToMesh(pp, radius, N)
    
    
    ## Visualize
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create mesh object
    m = vv.Mesh(axes, baseMesh)
    
    # Adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = False
        axes.cameraType = '3d'
        axes.SetLimits()
    
    # Return
    axes.Draw()
    return m
    
    
    
if __name__ == '__main__':    
    pp = Pointset(3)
    pp.Append(0,1,0)
    pp.Append(3,2,1)
    pp.Append(4,5,2)
    pp.Append(2,3,1)
    pp.Append(0,4,0)
#     pp.Append(0,1,0)
    vv.figure()
    m = solidLine(pp, [0.1, 0.2, 0.3, 0.03, 0.2], 8)
