# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import numpy as np
import visvis as vv
from visvis.utils.pypoints import Point, Pointset
from visvis.wobjects.polygonalModeling import BaseMesh

def getSpanVectors(normal, c, d):
    """ getSpanVectors(normal, prevA, prevB) -> (a,b)
    
    Given a normal, return two orthogonal vectors which are both orthogonal
    to the normal. The vectors are calculated so they match as much as possible
    the previous vectors.
    
    """
    
    # Calculate a from previous b
    a1 = d.cross(normal)
    
    if a1.norm() < 0.001:
        # The normal and  d point in same or reverse direction
        # -> Calculate b from previous a
        b1 = c.cross(normal)
        a1 = b1.cross(normal)
    
    # Consider the opposite direction
    a2 = -1 * a1
    if c.distance(a1) > c.distance(a2):
        a1 = a2
    
    # Ok, calculate b
    b1 = a1.cross(normal)
        
#     # Consider the opposite (don't: this would make backfacing faces)
#     b2 = -1 * b1
#     if d.distance(b1) > d.distance(b2):
#         b1 = b2

    # Done
    return a1.normalize(), b1.normalize()


def getCircle(angles_cos, angles_sin, a, b):
    """ getCircle(angles_cos, angles_sin, a, b) -> circle_cords
    
    Creates a circle of points around the origin,
    the circle is spanned by the vectors a and b.
    
    """
    X = np.empty((len(angles_cos),3),dtype=np.float32)
    X[:,0] = angles_cos * a.x + angles_sin * b.x
    X[:,1] = angles_cos * a.y + angles_sin * b.y
    X[:,2] = angles_cos * a.z + angles_sin * b.z
    
    return Pointset(X)


def lineToMesh(pp, radius, vertex_num, values=None):
    """ lineToMesh(pp, radius, vertex_num, values=None)
    
    From a line, create a mesh that represents the line as a tube with
    given diameter. Returns a BaseMesh instance.
    
    Parameters
    ----------
    pp : 3D Pointset
        The points along the line. If the first and last point are the same,
        the mesh-line is closed.
    radius : scalar
        The radius of the tube that is created. Radius can also be a
        sequence of values (containing a radius for each point).
    vertex_num : int
        The number of vertices to create along the circumference of the tube.
    values : list or numpy array (optional)
        A value per point. Can be Nx1, Nx2, Nx3 or Nx4. A list of scalars
        can also be given. The values are propagated to the mesh vertices
        and supplied as input to the Mesh constructor. This allows for example
        to define the color for the tube.
    
    """
    
    # we need this quite a bit
    pi = np.pi
    
    # process radius
    if hasattr(radius, '__len__'):
        if len(radius) != len(pp):
            raise ValueError('Len of radii much match len of points.')
        else:
            radius = np.array(radius, dtype=np.float32)
    else:
        radius = radius*np.ones((len(pp),), dtype=np.float32)
    
    # calculate vertex points for 2D circle
    angles = np.arange(0, pi*2-0.0001, pi*2/vertex_num)
    angle_cos = np.cos(angles)
    angle_sin = np.sin(angles)
    vertex_num2 = len(angles) # just to be sure
    
    # calculate distance between two line pieces (for smooth cylinders)
    dists = pp[1:].distance(pp[:-1])
    bufdist = min( radius.max(), dists.min()/2.2)
    
    # check if line is closed
    lclosed = np.all(pp[0]==pp[-1])
    
    # calculate normal vectors on each line point
    normals = pp[:-1].subtract( pp[1:] ).copy()
    if lclosed:
        normals.append( pp[0]-pp[1] )
    else:
        normals.append( pp[-2]-pp[-1] )
    normals = -1 * normals.normalize()
    
    # create list to store vertices
    vertices = Pointset(3)
    surfaceNormals = Pointset(3)
    
    # And a list for the values
    if values is None:
        vvalues = None
    elif isinstance(values, list):
        if len(values) != len(pp):
            raise ValueError('There must be as many values as points.')
        vvalues = Pointset(1)
    elif isinstance(values, np.ndarray):
        if values.ndim != 2:
            raise ValueError('Values must be Nx1, Nx2, Nx3 or Nx4.')
        if values.shape[0] != len(pp):
            raise ValueError('There must be as many values as points.')
        vvalues = Pointset(values.shape[1])
    elif vv.utils.pypoints.is_Pointset(values):
        if values.ndim > 4:
            raise ValueError('Can specify one to four values per point.')
        if len(values) != len(pp):
            raise ValueError('There must be as many values as points.')
        vvalues = Pointset(values.ndim)
    else:
        raise ValueError('Invalid value for values.')
    
    # Number of triangelized cylinder elements added to plot the 3D line
    n_cylinders = 0
    
    # Init a and b
    a, b = Point(0,0,1), Point(0,1,0)
    
    # Calculate the 3D circle coordinates of the first circle/cylinder
    a,b = getSpanVectors(normals[0], a, b)
    circm = getCircle(angle_cos, angle_sin, a, b)
    
    # If not a closed line, add half sphere made with 5 cylinders at line start
    if not lclosed:
        for j in range(5,0,-1):
            # Translate the circle on it's position on the line
            r = (1-(j/5.0)**2)**0.5
            circmp = float(r*radius[0])*circm + (pp[0]-(j/5.0)*bufdist*normals[0])
            # Calc normals
            circmn = ( pp[0].subtract(circmp) ).normalize()
            # Store the vertex list
            vertices.extend( circmp )
            surfaceNormals.extend( -1*circmn )
            if vvalues is not None:
                for iv in range(vertex_num2):
                    vvalues.append(values[0])
            n_cylinders += 1
    
    # Loop through all line pieces
    for i in range(len(pp)-1):
        
        ## Create main cylinder between two line points
        # which consists of two connected circles.
        
        # get normal and point
        normal1 = normals[i]
        point1 = pp[i]
        
        # calculate the 3D circle coordinates
        a,b = getSpanVectors(normal1, a, b)
        circm = getCircle(angle_cos, angle_sin, a, b)
        
        # Translate the circle, and store
        circmp = float(radius[i])*circm + (point1+bufdist*normal1)
        vertices.extend( circmp )
        surfaceNormals.extend( circm )
        if vvalues is not None:
            for iv in range(vertex_num2):
                vvalues.append(values[i])
        n_cylinders += 1
        
        # calc second normal and line
        normal2 = normals[i+1]
        point2 = pp[i+1]
        
        # Translate the circle, and store
        circmp = float(radius[i+1])*circm + (point2-bufdist*normal1)
        vertices.extend( circmp )
        surfaceNormals.extend( circm )
        if vvalues is not None:
            for iv in range(vertex_num2):
                vvalues.append(values[i+1])
        n_cylinders += 1
        
        
        ## Create in between circle to smoothly connect line pieces
        
        if not lclosed and i == len(pp)-2:
            break
        
        # get normal and point
        normal12 = (normal1 + normal2).normalize()
        tmp = (point2+bufdist*normal2) + (point2-bufdist*normal1)
        point12 = 0.5858*point2 + 0.4142*(0.5*tmp)
        
        # Calculate the 3D circle coordinates
        a,b = getSpanVectors(normal12, a, b)
        circm = getCircle(angle_cos, angle_sin, a, b)
        
        # Translate the circle, and store
        circmp = float(radius[i+1])*circm + point12
        vertices.extend( circmp )
        surfaceNormals.extend( circm )
        if vvalues is not None:
            for iv in range(vertex_num2):
                vvalues.append( 0.5*(values[i]+values[i+1]) )
        n_cylinders += 1
    
    
    # If not a closed line, add half sphere made with 5 cylinders at line start
    # Otherwise add the starting circle to the line end.
    if not lclosed:
        for j in range(0,6):
            # Translate the circle on it's position on the line
            r = (1-(j/5.0)**2)**0.5
            circmp = float(r*radius[-1])*circm + (pp[-1]+(j/5.0)*bufdist*normals[-1])
            # Calc normals
            circmn = ( pp[-1].subtract(circmp) ).normalize()
            # Store the vertex list
            vertices.extend( circmp )
            surfaceNormals.extend( -1*circmn )
            if vvalues is not None:
                for iv in range(vertex_num2):
                    vvalues.append(values[-1])
            n_cylinders += 1
    else:
        # get normal and point
        normal1 = normals[-1]
        point1 = pp[-1]
        
        # calculate the 3D circle coordinates
        a,b = getSpanVectors(normal1, a, b)
        circm = getCircle(angle_cos, angle_sin, a, b)
        
        # Translate the circle, and store
        circmp = float(radius[0])*circm + (point1+bufdist*normal1)
        vertices.extend( circmp )
        surfaceNormals.extend( circm )
        if vvalues is not None:
            for iv in range(vertex_num2):
                vvalues.append(values[-1])
        n_cylinders += 1
    
    
    # almost done, determine quad faces ...
    
    # define single faces
    #firstFace = [0, 1, vertex_num+1, vertex_num]
    #lastFace = [vertex_num-1, 0, vertex_num, 2*vertex_num-1]
    firstFace = [vertex_num, vertex_num+1, 1, 0]
    lastFace = [2*vertex_num-1, vertex_num, 0, vertex_num-1]
    
    # define single round
    oneRound = []
    for i in range(vertex_num-1):
        oneRound.extend( [val+i for val in firstFace] )
    oneRound.extend(lastFace)
    oneRound = np.array(oneRound, dtype=np.uint32)
    
    # calculate face data
    parts = []
    for i in range(n_cylinders-1):
        parts.append(oneRound+i*vertex_num)
    faces = np.concatenate(parts)
    faces.shape = faces.shape[0]//4, 4
    
    # Done!
    return BaseMesh(vertices, faces, surfaceNormals, vvalues)
