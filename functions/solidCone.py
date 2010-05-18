# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv
import numpy as np
from visvis.points import Point, Pointset

import OpenGL.GL as gl

def solidCone(translation=None, scaling=None, direction=None, rotation=None,
                N=16, M=16, axesAdjust=True, axes=None):
    """ solidCone(translation=None, scaling=None, direction=None, rotation=None,
                    N=16, M=16, axesAdjust=True, axes=None)
    
    Creates a solid cone with quad faces and its base at the origin.
    Returns an OrientableMesh instance.
    
    N is the number of subdivisions around its axis. M is the
    number of subdivisions along its axis. If N or M is smaller than 8, 
    flat shading is used instead of smooth shading. With N=4, a pyramid
    is obtained.
    """
    
    # Note that the number of vertices around the axis is N+1. This
    # would not be necessary per see, but it helps create a nice closed
    # texture when it is mapped. There are N number of faces though.
    # Similarly, to obtain M faces along the axis, we need M+1
    # vertices.
    
    # Quick access
    pi2 = np.pi*2
    cos = np.cos
    sin = np.sin
    sl = N+1
    
    # Precalculate z component of the normal
    zn = 1.0
    
    # Calculate vertices, normals and texcords
    vertices = Pointset(3)
    normals = Pointset(3)
    texcords = Pointset(2)
    # Cone
    for m in range(M+1):
        z = 1.0 - float(m)/M # between 0 and 1
        v = float(m)/M
        #
        for n in range(N+1):
            b = pi2 * float(n) / N
            u = float(n) / (N)
            x = cos(b) * (1.0-z)
            y = sin(b) * (1.0-z)
            vertices.Append(x,y,z)
            normals.Append(x,y,zn)
            texcords.Append(u,v)
    # Bottom
    for m in range(2):
        for n in range(N+1):
            b = pi2 * float(n) / N
            u = float(n) / (N)
            x = cos(b) * (1-m)
            y = sin(b) * (1-m)
            vertices.Append(x,y,0)
            normals.Append(0,0,-1)
            texcords.Append(u,1)
    
    # Calculate indices
    indices = []
    for j in range(M):
        for i in range(N):
            indices.extend([j*sl+i, j*sl+i+1, (j+1)*sl+i+1, (j+1)*sl+i])
    j = M + 1
    for i in range(N):
        indices.extend([j*sl+i, j*sl+i+1, (j+1)*sl+i+1, (j+1)*sl+i])
    
    # Make indices a numpy array
    indices = np.array(indices, dtype=np.uint32)
    
    
    ## Visualization
    
    # Create axes 
    if axes is None:
        axes = vv.gca()
    
    # Create mesh
    m = vv.OrientableMesh(axes, vertices, normals, faces=indices, 
        texcords=texcords, verticesPerFace=4)
    #
    if translation is not None:
        m.translation = translation
    if scaling is not None:
        m.scaling = scaling
    if direction is not None:
        m.direction = direction
    if rotation is not None:
        m.rotation = rotation
    
    # Set flat shading?
    if N<8 or M<8:
        m.faceShading = 'flat'
    
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
    m = solidCone(N=8)
    im = vv.imread('lena.png')
    m.SetTexture(im)    
    m._normals = None
    m.Draw()
