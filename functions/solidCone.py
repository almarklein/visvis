# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv
import numpy as np
from visvis.points import Point, Pointset

import OpenGL.GL as gl

def solidCone(translation=None, scale=None, N=32, M=32,
                axesAdjust=True, axes=None):
    """ solidCone(translation=None, scale=None, N=20, M=20,
                    axesAdjust=True, axes=None)
    
    Creates a solid cone. Position is a 3-element tuple or a Point instance.
    Scale is a scalar, 3-element tuple or Point instance.
    
    N is the number of subdivisions around its axis. M is the
    number of subdivisions along its axis.
    
    If N <= 8, the edges are modeled as genuine edges. So with faces=4,
    a pyramid can be obtained. If N>8, the normals vary smoothly
    over the faces which makes the object look rounder.
    """
    
    # Note that the number of vertices around the axis is N+1. This
    # would not be necessary per see, but it helps create a nice closed
    # texture when it is mapped. There are N number of faces though.
    # Similarly, to obtain M faces along the axis, we need M+1
    # vertices.
    
    # Check position
    if isinstance(translation, tuple):
        translation = Point(translation)
    
    # Check scale
    if isinstance(scale, tuple):
        scale = Point(scale)
    elif isinstance(scale, (float, int)):
        scale = Point(scale, scale, scale)
    
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
    
    # Make edges appear as edges, for pyramids for example
    if N <= 8:
        newVertices = Pointset(3)
        newNormals = Pointset(3)
        newTexcords = Pointset(2)
        for i in range(0,len(indices),4):
            ii = indices[i:i+4]
            # Obtain average normal
            tmp = Point(0,0,0)
            for j in range(4):
                tmp += normals[ii[j]]
            tmp = tmp.Normalize()
            # Unroll vertices and texcords, set new normals
            for j in range(4):
                newVertices.Append( vertices[ii[j]] )
                newNormals.Append( tmp )
                newTexcords.Append( texcords[ii[j]] )
        # Apply
        vertices = newVertices
        normals = newNormals
        texcords = newTexcords
        indices = None
    
    
    ## Visualization
    
    # Create axes 
    if axes is None:
        axes = vv.gca()
    
    # Create mesh
    m = vv.Mesh(axes, vertices, normals, faces=indices, 
        texcords=texcords, verticesPerFace=4)
    
    # Scale and translate
    if translation is not None:
        tt = vv.Transform_Translate(translation.x, translation.y, translation.z)    
        m.transformations.append(tt)
    if scale is not None:
        ts = vv.Transform_Scale(scale.x, scale.y, scale.z)
        m.transformations.append(ts)
    
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
    m = solidCone(N=4)
    im = vv.imread('lena.png')
    m.SetTexture(im)    
