# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv
import numpy as np
from visvis.pypoints import Point, Pointset

import OpenGL.GL as gl


def solidBox(translation=None, scaling=None, direction=None, rotation=None,
                axesAdjust=True, axes=None):
    """ solidBox(translation=None, scaling=None, direction=None, rotation=None,
                    axesAdjust=True, axes=None)
    
    Creates a solid cube (or box if you scale it) centered at the 
    origin. Returns an OrientableMesh.
    """
    
    # Create vertices of a cube
    pp = Pointset(3)
    # Bottom
    pp.Append(-0.5,-0.5,-0.5)
    pp.Append(+0.5,-0.5,-0.5)
    pp.Append(+0.5,+0.5,-0.5)
    pp.Append(-0.5,+0.5,-0.5)
    # Top
    pp.Append(-0.5,-0.5,+0.5)
    pp.Append(-0.5,+0.5,+0.5)
    pp.Append(+0.5,+0.5,+0.5)
    pp.Append(+0.5,-0.5,+0.5)
    
    # Init vertices and normals
    vertices = Pointset(3)
    normals = Pointset(3)
    
    # Create vertices
    for i in [0,1,2,3]: # Top
        vertices.Append(pp[i]); normals.Append(0,0,-1)
    for i in [4,5,6,7]: # Bottom
        vertices.Append(pp[i]); normals.Append(0,0,+1)
    for i in [3,2,6,5]: # Front
        vertices.Append(pp[i]); normals.Append(0,+1,0)
    for i in [0,4,7,1]: # Back
        vertices.Append(pp[i]); normals.Append(0,-1,0)
    for i in [0,3,5,4]: # Left
        vertices.Append(pp[i]); normals.Append(-1,0,0)
    for i in [1,7,6,2]: # Right
        vertices.Append(pp[i]); normals.Append(+1,0,0)
    
    
    ## Visualize
    
    # Create axes
    if axes is None:
        axes = vv.gca()
    
    # Create mesh and set orientation
    m = vv.OrientableMesh(axes,vertices, normals, verticesPerFace=4)
    #
    if translation is not None:
        m.translation = translation
    if scaling is not None:
        m.scaling = scaling
    if direction is not None:
        m.direction = direction
    if rotation is not None:
        m.rotation = rotation
    
    # Adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = False
        axes.cameraType = '3d'
        axes.SetLimits()
    
    # Done
    axes.Draw()
    return m


if __name__ == '__main__':
    vv.figure()
    a = vv.gca()
    m1 = solidBox((3,1,1), (2,2,1), rotation=-20)
    m2 = solidBox((1,1,0), (1,1,1.5), direction=(1,0.4,0.2))
