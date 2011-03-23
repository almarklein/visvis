# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

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
    axesAdjust : bool
        If True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet, 
        it is set to False.
    axes : Axes instance
        Display the bars in the given axes, or the current axes if not given.
    
    """
    
    # Create vertices of a cube
    pp = Pointset(3)
    # Bottom
    pp.append(-0.5,-0.5,-0.5)
    pp.append(+0.5,-0.5,-0.5)
    pp.append(+0.5,+0.5,-0.5)
    pp.append(-0.5,+0.5,-0.5)
    # Top
    pp.append(-0.5,-0.5,+0.5)
    pp.append(-0.5,+0.5,+0.5)
    pp.append(+0.5,+0.5,+0.5)
    pp.append(+0.5,-0.5,+0.5)
    
    # Init vertices and normals
    vertices = Pointset(3)
    normals = Pointset(3)
    
    # Create vertices
    for i in [0,1,2,3]: # Top
        vertices.append(pp[i]); normals.append(0,0,-1)
    for i in [4,5,6,7]: # Bottom
        vertices.append(pp[i]); normals.append(0,0,+1)
    for i in [3,2,6,5]: # Front
        vertices.append(pp[i]); normals.append(0,+1,0)
    for i in [0,4,7,1]: # Back
        vertices.append(pp[i]); normals.append(0,-1,0)
    for i in [0,3,5,4]: # Left
        vertices.append(pp[i]); normals.append(-1,0,0)
    for i in [1,7,6,2]: # Right
        vertices.append(pp[i]); normals.append(+1,0,0)
    
    
    ## Visualize
    
    # Create axes
    if axes is None:
        axes = vv.gca()
    
    # Create mesh and set orientation
    m = vv.OrientableMesh(axes, vertices, normals, verticesPerFace=4)
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
