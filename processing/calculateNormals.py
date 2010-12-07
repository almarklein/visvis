# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import numpy as np
import time

##
v = np.array([10,11,12,20,21,22,30,31,32,40,41,42,50,51,52,60,61,62])
v.shape = 6,3
N = v.shape[0]
faces = np.arange(N); faces.shape = len(v)/3,3


def calculateNormals(mesh):
    """ calculateNormals(mesh)
    
    Calculate the normal data from the vertices.
    Handles triangular and quad faces.
    
    """
    t0 = time.time()
    
    # Get vertices as np array
    vertices = mesh._vertices
    if vertices is None:
        return
    
    # Init normal array
    N = vertices.shape[0]
    normals = np.zeros((N,3), dtype='float32')
    defaultNormal = np.array([1,0,0], dtype='float32')
    
    # Get faces array
    faces = mesh._GetFaces()
    Nfaces, vpf = faces.shape
    Nfaces = faces.size / vpf
    
    # Apply    
    
    # Select lists of vertices. v1,v2,v3 are lists of vertices
    # corresponding to the first, second, third vertices of the faces.
    # They are Nfaces times 3/4
    
    if vpf == 3:
        # Get vertex per faces index (for all faces)
        v1 = vertices[faces[:,0]]
        v2 = vertices[faces[:,1]]
        v3 = vertices[faces[:,2]]
        
        # Calculate normals
        _vectorsToNormals(v2-v1, v2-v3, faces, normals)
        
    elif vpf == 4:
        # Get vertex per faces index (for all faces)
        v1 = vertices[faces[:,0]]
        v2 = vertices[faces[:,1]]
        v3 = vertices[faces[:,2]]
        v4 = vertices[faces[:,3]]
        # Calculate normals using all possible sets of 3 vertices.
        # (order found by simply testing)
        _vectorsToNormals(v2-v1, v2-v3, faces, normals)
        _vectorsToNormals(v2-v4, v2-v3, faces, normals)
        _vectorsToNormals(v1-v3, v4-v3, faces, normals)
        _vectorsToNormals(v2-v1, v1-v4, faces, normals)
    
    # Normalize the normals
    lengths = normals[:,0]**2 + normals[:,1]**2 + normals[:,2]**2
    lengths = lengths**0.5
    normals[:,0] /= lengths
    normals[:,1] /= lengths
    normals[:,2] /= lengths
    
    # Correct NANs
    I, = np.where(lengths==0)
    normals[I,0] = 0
    normals[I,1] = 0
    normals[I,2] = 1
    
#     print np.isnan(normals).sum(), 'nans'
#     print 'calculated normals in ', time.time()-t0
    
    # Store normals (need to flip sign)
    mesh._normals = normals


def _vectorsToNormals(a, b, faces, normals):
    
    # The normal is orthogonal to both vectors. Use cross product
    normalsPerFace = np.zeros((faces.shape[0],3), dtype='float32')
    normalsPerFace[:,0] = a[:,1]*b[:,2] - a[:,2]*b[:,1]
    normalsPerFace[:,1] = a[:,2]*b[:,0] - a[:,0]*b[:,2]
    normalsPerFace[:,2] = a[:,0]*b[:,1] - a[:,1]*b[:,0]
    
    # The normals can be distributed over the normals per vertex
    normals[faces[:,0]] += normalsPerFace
    normals[faces[:,1]] += normalsPerFace
    normals[faces[:,2]] += normalsPerFace
    
    

def calculateNormals_old(mesh):
    """ calculateNormals(mesh)
    
    Calculate the normal data from the vertices.
    Handles triangular and quad faces.
    
    """
    t0 = time.time()
    
    # Get vertices as np array
    vertices = mesh._vertices
    if vertices is None:
        return
    
    # Init normal array
    N = vertices.shape[0]        
    normals = np.zeros((N,3), dtype='float32')
    defaultNormal = np.array([1,0,0], dtype='float32')
    
    # For all faces, calculate normals, and add to normals
    # If quads, we neglect the 4th vertex, which should be save, as it
    # should be in the same plane.
    for ii in mesh._IterFaces():
        v1 = vertices[ii[0],:]
        v2 = vertices[ii[1],:]
        v3 = vertices[ii[2],:]
        # Calculate normal
        tmp = np.cross(v1-v2,v2-v3)
        if np.isnan(tmp).sum():
            tmp = defaultNormal
        # Insert normals
        normals[ii[0],:] += tmp
        normals[ii[1],:] += tmp
        normals[ii[2],:] += tmp
    
    # Normalize normals
    for i in range(N):
        tmp = normals[i,:]
        tmp = tmp / ( (tmp**2).sum()**0.5 )
        if np.isnan(tmp).sum():
            tmp = defaultNormal
        normals[i,:] = -tmp
    print 'calculated normals in ', time.time()-t0
    
    # Store normals
    mesh._normals = normals
    