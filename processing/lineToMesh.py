# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import numpy as np
from visvis.points import Point, Pointset
from visvis.polygonalModeling import BaseMesh

def getSpanVectors(normal, c, d):
    """ getSpanVectors(normal, prevA, prevB) -> (a,b)
    Given a normal, return two orthogonal vectors which are both orthogonal
    to the normal. The vectors are calculated so they match as much as possible
    the previous vectors.
    These vectors will be used to span the circle.
    """
    
    # init random vector
    # A normal vector only defines two rotations not the in plane rotation.
    # Thus a (random) vector is needed which is not orthogonal with 
    # the normal vector.
    randomv = Point(0.57745, 0.5774, 0.57735)
    randomv2 = Point(0,0,1)
    
    # Calculate a from previous b
    a1 = d.Cross(normal)
    if a1.Norm() < 0.001:
        a1 = d
    else:
        a2 = -1 * a1
        if c.Distance(a1) > c.Distance(a2):
            a1 = a2
    
    # Make sure the vector is not Nan or Inf
    if a1.x*0!=0:
        a1 = randomv.Cross(normal)
    if a1.x*0!=0:
        a1 = randomv2.Cross(normal)
    
    # Calculate b
    b = a1.Cross(normal)
    if a1.x*0!=0:
        print  normal, c, d
    # Done
    return a1.Normalize(), b.Normalize()


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


def lineToMesh(pp, radius, vertex_num):
    """ lineToMesh(pp, radius, vertex_num)
    
    From a line, create a mesh that represents the line as a tube with 
    given diameter. vertex_num is the number of vertices to create
    along the circumference of the tube. Returns a BaseMesh instance.
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
    angle_cos  = np.cos(angles)
    angle_sin = np.sin(angles)
    
    # calculate distance between two line pieces (for smooth cylinders)
    dists = pp[1:].Distance(pp[:-1])
    bufdist = min( radius.max(), dists.min()/2.2)
    
    # check if line is closed
    lclosed = (pp[0]==pp[-1])
    
    # calculate normal vectors on each line point    
    normals = pp[1:] - pp[:-1]
    if lclosed:        
        normals.Append( pp[0]-pp[1] )
    else:        
        normals.Append( pp[-2]-pp[-1] )
    normals = -1 * normals.Normalize()
    
    # create list to store vertices
    vertices = Pointset(3)
    surfaceNormals = Pointset(3)
    
    # Number of triangelized cylinder elements added to plot the 3D line
    n_cylinders = 0
    
    # Init a and b
    a, b = Point(0,0,1), Point(0,1,0)
    
    # Calculate the 3D circle coordinates of the first circle/cylinder
    a,b = getSpanVectors(normals[0], a, b)
    circm = getCircle(angle_cos, angle_sin, a, b);
    
    # If not a closed line, add half sphere made with 5 cylinders at line start     
    if not lclosed:
        for j in range(5,0,-1):
            # Translate the circle on it's position on the line
            r = (1-(j/5.0)**2)**0.5
            circmp = float(r*radius[0])*circm + (pp[0]-(j/5.0)*bufdist*normals[0])
            # Calc normals
            circmn = ( circmp - pp[0]).Normalize() 
            # Store the vertex list            
            vertices.Extend( circmp )
            surfaceNormals.Extend( -1*circmn )
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
        vertices.Extend( circmp )
        surfaceNormals.Extend( circm )
        n_cylinders += 1
        
        # calc second normal and line
        normal2 = normals[i+1]
        point2 = pp[i+1]
        
        # Translate the circle, and store
        circmp = float(radius[i+1])*circm + (point2-bufdist*normal1)
        vertices.Extend( circmp )
        surfaceNormals.Extend( circm )
        n_cylinders += 1
        
        
        ## Create in between circle to smoothly connect line pieces
        
        if not lclosed and i == len(pp)-2:
            break
        
        # get normal and point
        normal12 = (normal1 + normal2).Normalize()
        tmp = (point2+bufdist*normal2) + (point2-bufdist*normal1)
        point12 = 0.5858*point2 + 0.4142*(0.5*tmp)
        
        # Calculate the 3D circle coordinates
        a,b = getSpanVectors(normal12, a, b)
        circm = getCircle(angle_cos, angle_sin, a, b);
        
        # Translate the circle, and store
        circmp = float(radius[i+1])*circm + point12
        vertices.Extend( circmp )
        surfaceNormals.Extend( circm )
        n_cylinders += 1
    
    
    # If not a closed line, add half sphere made with 5 cylinders at line start
    # Otherwise add the starting circle to the line end.
    if not lclosed:
        for j in range(0,6):
            # Translate the circle on it's position on the line
            r = (1-(j/5.0)**2)**0.5
            circmp = float(r*radius[-1])*circm + (pp[-1]+(j/5.0)*bufdist*normals[-1])
            # Calc normals
            circmn = ( circmp - pp[-1]).Normalize()            
            # Store the vertex list
            vertices.Extend( circmp )
            surfaceNormals.Extend( -1*circmn )
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
        vertices.Extend( circmp )
        surfaceNormals.Extend( circm )
        n_cylinders += 1
    
    
    # almost done, determine quad faces ...
    
    # define single faces
    firstFace = [0, 1, vertex_num+1, vertex_num]    
    lastFace = [vertex_num-1, 0, vertex_num, 2*vertex_num-1]
    
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
    faces.shape = faces.shape[0]/4, 4
    
    # Done!
    return BaseMesh(vertices, surfaceNormals, faces)
