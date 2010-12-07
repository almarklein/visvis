# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import numpy as np

def unwindFaces(mesh):
    """ unwindFaces(mesh)
    
    Unwinds the faces to make new versions of the vertices, normals,
    color and texCords, which are usually larger. The new arrays 
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
    
    # Unwind color
    if mesh._colors is not None:
        # Get ref and allocate new array
        colors = mesh._colors
        newColors = np.zeros((N,3), dtype='float32')
        for i in range(N):
            newColors[i,:] = colors[faces[i]]
        # Store
        mesh._colors = newColors
    
    # Unwind texcords
    if mesh._texcords is not None:
        # Get ref and allocate new array
        texcords = mesh._texcords
        if mesh._texcords.ndim==1:
            newTexcords = np.zeros((N,), dtype='float32')
            for i in range(N):
                newTexcords[i] = texcords[faces[i]]
        else:                    
            verticesPerFace = mesh._texcords.shape[1]
            newTexcords = np.zeros((N,verticesPerFace), dtype='float32')
            for i in range(N):
                newTexcords[i,:] = texcords[faces[i]]
        # Store
        mesh._texcords = newTexcords
    
    # Remove reference to faces
    mesh._faces = None
