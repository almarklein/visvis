# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np
from visvis.utils.pypoints import Point, Pointset


def solidRing(translation=None, scaling=None, direction=None, rotation=None,
                thickness=0.25, N=16, M=16, axesAdjust=True, axes=None):
    """ solidRing(translation=None, scaling=None, direction=None, rotation=None,
                thickness=0.25, N=16, M=16, axesAdjust=True, axes=None)
    
    Creates a solid ring with quad faces oriented at the origin.
    Returns an OrientableMesh instance.
    
    Parameters
    ----------
    Note that translation, scaling, and direction can also be given
    using a Point instance.
    translation : (dx, dy, dz), optional
        The translation in world units of the created world object.
    scaling: (sx, sy, sz), optional
        The scaling in world units of the created world object.
    direction: (nx, ny, nz), optional
        Normal vector that indicates the direction of the created world object.
    rotation: scalar, optional
        The anle (in degrees) to rotate the created world object around its
        direction vector.
    thickness : scalar
        The tickness of the ring, represented as a fraction of the radius.
    N : int
        The number of subdivisions around its axis. If smaller
        than 8, flat shading is used instead of smooth shading.
    M : int
        The number of subdivisions along its axis. If smaller
        than 8, flat shading is used instead of smooth shading.
    axesAdjust : bool
        If True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet,
        it is set to False.
    axes : Axes instance
        Display the bars in the given axes, or the current axes if not given.
    
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
    sl = M+1
    
    # Determine where the stitch is, depending on M
    if M<=8:
        rotOffset = 0.5/M
    else:
        rotOffset = 0.0
    
    # Calculate vertices, normals and texcords
    vertices = Pointset(3)
    normals = Pointset(3)
    texcords = Pointset(2)
    # Cone
    for n in range(N+1):
        v = float(n)/N
        a = pi2 * v
        # Obtain outer and center position of "tube"
        po = Point(sin(a), cos(a), 0)
        pc = po * (1.0-0.5*thickness)
        # Create two vectors that span the the circle orthogonal to the tube
        p1 = (pc-po)
        p2 = Point(0, 0, 0.5*thickness)
        # Sample around tube
        for m in range(M+1):
            u = float(m) / (M)
            b = pi2 * (u+rotOffset)
            dp = cos(b) * p1 + sin(b) * p2
            vertices.append(pc+dp)
            normals.append(dp.normalize())
            texcords.append(v,u)
    
    # Calculate indices
    indices = []
    for j in range(N):
        for i in range(M):
            #indices.extend([j*sl+i, j*sl+i+1, (j+1)*sl+i+1, (j+1)*sl+i])
            indices.extend([(j+1)*sl+i, (j+1)*sl+i+1, j*sl+i+1, j*sl+i])
    
    # Make indices a numpy array
    indices = np.array(indices, dtype=np.uint32)
    
    
    ## Visualize
    
    # Create axes
    if axes is None:
        axes = vv.gca()
    
    # Create mesh
    m = vv.OrientableMesh(axes, vertices, indices, normals, values=texcords,
            verticesPerFace=4)
    #
    if translation is not None:
        m.translation = translation
    if scaling is not None:
        m.scaling = scaling
    if direction is not None:
        m.direction = direction
    if rotation is not None:
        m.rotation = rotation
    
    # If necessary, use flat shading
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
    m1 = vv.solidRing((0,0,1), N=64, M=4, thickness=0.5)
    m2 = vv.solidRing((0,0,2), N=64, thickness=0.25)
    m1.SetTexture( vv.imread('astronaut.png') )
