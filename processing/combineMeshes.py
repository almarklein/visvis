# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import numpy as np
from visvis.wobjects.polygonalModeling import BaseMesh

def combineMeshes(meshes):
    """ combineMeshes(meshes)
    
    Given a list of mesh objects, produces a combined mesh.
    
    """
    if not meshes:
        raise ValueError('No meshes or empty meshes given')
    
    # Check mesh simularity
    vpf = 0
    hasNormals = True
    hasFaces = True
    hasValues = True
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
            hasValues = hasValues and (mesh._values is not None)
    
    # Combine vertices
    vertices = np.concatenate( [m._vertices for m in meshes] )
    
    # Combine faces
    faces = None
    if hasFaces:
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
    
    # Combine values
    values = None
    if hasValues:
        values = np.concatenate( [m._values for m in meshes] )
    
    # Done
    return BaseMesh(vertices, faces, normals, values, vpf)
