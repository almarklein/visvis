# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import numpy as np
from visvis.processing.unwindFaces import unwindFaces

def calculateFlatNormals(mesh):
    """ calculateFlatNormals(mesh)
    
    Calculate a variant of the normals that is more suited for
    flat shading. This is done by setting the first normal for each
    face (the one used when flat shading is used) to the average
    of all normals of that face. This can in some cases lead to
    wrong results if a vertex is the first vertex of more than one
    face.
    
    """
    
    # If we want flat shading, we should not use faces
    unwindFaces(mesh)
    
    # Get normals
    normals = mesh._normals
    if normals is None:
        return
    
    # Allocate new array
    N = normals.shape[0]
    flatNormals = np.zeros((N,3), dtype='float32')
    
    # obtain faces array
    faces = mesh._GetFaces()
    
    # For each face add the contribution of each others vertices.
    vpf = mesh._verticesPerFace
    for i in range(vpf):
        I = faces[:,i]
        for j in range(vpf):
            J = faces[:,j]
            flatNormals[J] += normals[I]
    
    # Normalize
    flatNormals /= vpf
    
    # Old bit
#     # Sum all normals belonging to one face
#     verticesPerFace = float(mesh._verticesPerFace)
#     a, b = set(), list()
#     for ii in mesh._IterFaces():
#         i0 = ii[-1]
#         a.add(i0)
#         b.append(i0)
#         for i in ii:
#             flatNormals[i0,:] += normals[i,:] / verticesPerFace
#     print(len(a), len(b))
    
    
    # Store
    mesh._flatNormals = flatNormals
