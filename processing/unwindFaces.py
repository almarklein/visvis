# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import numpy as np

def unwindFaces(mesh):
    """ unwindFaces(mesh)
    
    Unwinds the faces to make new versions of the vertices, normals,
    values, which are usually larger. The new arrays
    represent the same surface, but is described without a faces
    array.
    
    """
    
    # Make new vertices and normals if faces are used
    if mesh._faces is None:
        return
    
    # Get references and new size
    faces = mesh._faces
    N = faces.shape[0]
    
    # Unwind vertices
    if mesh._vertices is not None:
        # Get ref and allocate new array
        vertices = mesh._vertices
        newVertices = np.zeros((N,3), dtype='float32')
        # Unwind
        for i in range(N):
            newVertices[i,:] = vertices[faces[i]]
        # Store
        mesh._vertices = newVertices
    
    # Unwind normals
    if mesh._normals is not None:
        # Get ref and allocate new array
        normals = mesh._normals
        newNormals = np.zeros((N,3), dtype='float32')
        for i in range(N):
            newNormals[i,:] = normals[faces[i]]
        # Store
        mesh._normals = newNormals
        mesh._flatNormals = None
    
    # Unwind values
    if mesh._values is not None:
        # Get ref and allocate new array
        values = mesh._values
        M = values.shape[1]
        newValues = np.zeros((N,M), dtype='float32')
        for i in range(N):
            newValues[i,:] = values[faces[i]]
        # Store
        mesh._values = newValues
    
    # Remove reference to faces
    mesh._faces = None
