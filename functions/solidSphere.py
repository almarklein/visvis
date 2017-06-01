# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np
from visvis.utils.pypoints import Point, Pointset


# Alternative implementation bu subdeivinding a tetrahedon,
# but not as good for mapping textures.
def getSphere(ndiv=3, radius=1.0):
    # Example taken from the Red book, end of chaper 2.
    
    # Define constants
    X = 0.525731112119133606
    Z = 0.850650808352039932
    
    # Creta vdata
    vdata = Pointset(3)
    app = vdata.append
    app(-X, 0.0, Z); app(X, 0.0, Z); app(-X, 0.0, -Z); app(X, 0.0, -Z)
    app(0.0, Z, X); app(0.0, Z, -X); app(0.0, -Z, X); app(0.0, -Z, -X)
    app(Z, X, 0.0); app(-Z, X, 0.0); app(Z, -X, 0.0); app(-Z, -X, 0.0)
    
    # Create faces
    tindices = [
        [0,4,1], [0,9,4], [9,5,4], [4,5,8], [4,8,1],
        [8,10,1], [8,3,10], [5,3,8], [5,2,3], [2,7,3],
        [7,10,3], [7,6,10], [7,11,6], [11,0,6], [0,1,6],
        [6,1,10], [9,0,11], [9,11,2], [9,2,5], [7,2,11] ]
    tindices = np.array(tindices, dtype=np.uint32)
    
    # Init vertex array
    vertices = Pointset(3)
    
    # Define function to recursively create vertices and normals
    def drawtri(a, b, c, div):
        if (div<=0):
            vertices.append(a)
            vertices.append(b)
            vertices.append(c)
        else:
            ab = Point(0,0,0)
            ac = Point(0,0,0)
            bc = Point(0,0,0)
            for i in range(3):
                ab[i]=(a[i]+b[i])/2.0
                ac[i]=(a[i]+c[i])/2.0
                bc[i]=(b[i]+c[i])/2.0
            ab = ab.normalize(); ac = ac.normalize(); bc = bc.normalize()
            drawtri(a, ab, ac, div-1)
            drawtri(b, bc, ab, div-1)
            drawtri(c, ac, bc, div-1)
            drawtri(ab, bc, ac, div-1)
    
    # Create vertices
    for i in range(20):
        drawtri(    vdata[int(tindices[i][0])],
                    vdata[int(tindices[i][1])],
                    vdata[int(tindices[i][2])],
                    ndiv )
    
    # Create normals and scale vertices
    normals = vertices.copy()
    vertices *= radius
    
    # Done
    return vertices, normals


# Alternative implementation bu subdeivinding a tetrahedon,
# but not as good for mapping textures.
# This version uses faces to reuse vertices.
def getSphereWithFaces(ndiv=3, radius=1.0):
    # Example taken from the Red book, end of chaper 2.
    
    # Define constants
    X = 0.525731112119133606
    Z = 0.850650808352039932
    
    # Creta vdata
    vdata = Pointset(3)
    app = vdata.append
    app(-X, 0.0, Z); app(X, 0.0, Z); app(-X, 0.0, -Z); app(X, 0.0, -Z)
    app(0.0, Z, X); app(0.0, Z, -X); app(0.0, -Z, X); app(0.0, -Z, -X)
    app(Z, X, 0.0); app(-Z, X, 0.0); app(Z, -X, 0.0); app(-Z, -X, 0.0)
    
    # Create faces
    tindices = [
        [0,4,1], [0,9,4], [9,5,4], [4,5,8], [4,8,1],
        [8,10,1], [8,3,10], [5,3,8], [5,2,3], [2,7,3],
        [7,10,3], [7,6,10], [7,11,6], [11,0,6], [0,1,6],
        [6,1,10], [9,0,11], [9,11,2], [9,2,5], [7,2,11] ]
    tindices = np.array(tindices, dtype=np.uint32)
    
    # Init vertex array with existing points, init faces as empty list
    vertices = vdata.copy()
    faces = []
    
    # Define function to recursively create vertices and normals
    def drawtri(ia, ib, ic, div):
        a, b, c = vertices[ia] , vertices[ib], vertices[ic]
        if (div<=0):
            # Store faces here
            faces.extend([ia, ib, ic])
        else:
            # Create new points
            ab = Point(0,0,0)
            ac = Point(0,0,0)
            bc = Point(0,0,0)
            for i in range(3):
                ab[i]=(a[i]+b[i])/2.0
                ac[i]=(a[i]+c[i])/2.0
                bc[i]=(b[i]+c[i])/2.0
            ab = ab.normalize(); ac = ac.normalize(); bc = bc.normalize()
            # Add new points
            i_offset = len(vertices)
            vertices.append(ab)
            vertices.append(ac)
            vertices.append(bc)
            iab, iac, ibc = i_offset+0, i_offset+1, i_offset+2
            #
            drawtri(ia, iab, iac, div-1)
            drawtri(ib, ibc, iab, div-1)
            drawtri(ic, iac, ibc, div-1)
            drawtri(iab, ibc, iac, div-1)
    
    # Create vertices
    for i in range(20):
        drawtri(    int(tindices[i][0]),
                    int(tindices[i][1]),
                    int(tindices[i][2]),
                    ndiv )
    
    # Create normals and scale vertices
    normals = vertices.copy()
    vertices *= radius
    
    # Create faces
    faces = np.array(faces, dtype='uint32')
    
    # Done
    return vertices, faces, normals


def solidSphere(translation=None, scaling=None, direction=None, rotation=None,
                N=16, M=16, axesAdjust=True, axes=None):
    """ solidSphere(translation=None, scaling=None, direction=None, rotation=None,
                    N=16, M=16, axesAdjust=True, axes=None)
    
    Creates a solid sphere with quad faces and centered at the origin.
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
    N : int
        The number of subdivisions around the Z axis (similar to lines
        of longitude). If smaller than 8, flat shading is used instead
        of smooth shading.
    M : int
        The number of subdivisions along the Z axis (similar to lines
        of latitude). If smaller than 8, flat shading is used instead
        of smooth shading.
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
    sl = N+1
    
    # Calculate vertices, normals and texcords
    vertices = Pointset(3)
    normals = Pointset(3)
    texcords = Pointset(2)
    # Cone
    for m in range(M+1):
        a = np.pi * float(m) / M
        z = cos(a)
        v = float(m)/M
        #
        for n in range(N+1):
            b = pi2 * float(n) / N
            u = float(n) / (N)
            x = cos(b) * sin(a)
            y = sin(b) * sin(a)
            vertices.append(x,y,z)
            normals.append(x,y,z)
            texcords.append(u,v)
    
    # Calculate indices
    indices = []
    for j in range(M):
        for i in range(N):
            #indices.extend([j*sl+i, j*sl+i+1, (j+1)*sl+i+1, (j+1)*sl+i])
            indices.extend([(j+1)*sl+i, (j+1)*sl+i+1, j*sl+i+1, j*sl+i])
    
    # Make indices a numpy array
    indices = np.array(indices, dtype=np.uint32)
    
    
    ## Visualize
    
    # Create axes
    if axes is None:
        axes = vv.gca()
    
    # Create mesh
    m = vv.OrientableMesh(axes, vertices, indices, normals, texcords, 4)
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
    m = vv.solidSphere(scaling=(1,1,1.5), direction=(1,1,3))
    m.SetTexture( vv.imread('astronaut.png') )
