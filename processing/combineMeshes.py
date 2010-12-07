# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import numpy as np
from visvis.polygonalModeling import BaseMesh

def combineMeshes(meshes):
    """ combineMeshes(meshes)
    
    Given a list of mesh objects, produces a combined mesh.
    
    """
    
    # Check mesh simularity
    vpf = 0
    hasNormals = True
    hasFaces = True
    hasColors = True
    hasTexcords = True
    #
    for mesh in meshes:
        if vpf == 0:
            # First mesh: init
            hasFaces = (mesh._faces is not None)
            vpf = mesh._verticesPerFace
        else:
            # Compare with first
            if mesh._verticesPerFace != vpf:
                raise ValueError('Cannot combine meshes with different verticesPerFace.')
            if (mesh._faces is not None) != hasFaces:
                raise ValueError('Cannot combine meshes with and without face data.')
        if True:
            # Compare always
            hasNormals = hasNormals and (mesh._normals is not None)
            hasColors = hasColors and (mesh._colors is not None)
            hasTexcords = hasTexcords and (mesh._texcords is not None)            
    
    # Combine vertices
    vertices = np.concatenate( [m._vertices for m in meshes] )
    
    # Combine faces
    faces = None
    if hasNormals:
        facesList = []
        startIndex = 0
        for mesh in meshes:            
            facesList.append( mesh._faces + startIndex )
            startIndex += mesh._vertices.shape[0]
        faces = np.concatenate( facesList )
    
    # Combine normals
    normals = None
    if hasNormals:
        normals = np.concatenate( [m._normals for m in meshes] )
    
    # Combine colors
    colors = None
    if hasColors:
        colors = np.concatenate( [m._colors for m in meshes] )
    
    # Combine texcords
    texcords = None
    if hasTexcords:
        texcords = np.concatenate( [m._texcords for m in meshes] )
    
    # Done
    return BaseMesh(vertices, normals, faces, colors, texcords, vpf)
