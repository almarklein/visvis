# -*- coding: utf-8 -*-
# Copyright (C) 2012, Robert Schroll
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
from visvis.wobjects.polygonalModeling import checkDimsOfArray


def mesh(vertices, faces=None, normals=None, values=None, verticesPerFace=3,
        colormap=None, clim=None, texture=None, axesAdjust=True, axes=None):
    """ mesh(vertices, faces=None, normals=None, values=None, verticesPerFace=3,
        colormap=None, clim=None, texture=None, axesAdjust=True, axes=None)
    
    Display a mesh of polygons, either triangles or quads.
    
    Parameters
    ----------
    vertices : Nx3 array
        The positions of the vertices in 3D space.
    faces : array or list of indices
        The faces given in terms of the vertex indices.  Should be 1D, in
        which case the indices are grouped into groups of verticesPerFace,
        or Mx3 or Mx4, in which case verticesPerFace is ignored.
        The front of the face is defined using the right-hand-rule.
    normals : Nx3
        A list of vectors specifying the vertex normals.
    values : N, Nx2, Nx3, or Nx4 array
        Sets the color of each vertex, using values from a colormap (1D),
        colors from a texture (Nx2), RGB values (Nx3), or RGBA value (Nx4).
    verticesPerFace : 3 or 4
        Whether the faces are triangle or quads, if not specified in faces.
    colormap : a Colormap
        If values is 1D, the vertex colors are set from this colormap.
    clim : 2 element array
        If values is 1D, sets the values to be mapped to the limits of the
        colormap.  If None, the min and max of values are used.
    texture : a Texture
        If values is Nx2, the vertex colors are set from this texture.
    axesAdjust : bool
        Whether to adjust the view after the mesh is drawn.
    axes : Axes instance
        The axes into which the mesh will be added.  If None, the current
        axes will be used.
    
    """
    
    if axes is None:
        axes = vv.gca()
    
    # Accept basemesh instances
    if isinstance(vertices, vv.BaseMesh):
        other = vertices
        vertices = other._vertices
        faces = other._faces
        normals = other._normals
        values = other._values
        verticesPerFace = other._verticesPerFace
    
    # Check that vertices is (converted to) a Nx3 array; otherwise user
    # will see odd behavior from Mesh
    if not isinstance(vertices, vv.BaseMesh):
        try:
            vertices = checkDimsOfArray(vertices, 3)
        except ValueError:
            raise ValueError("Vertices should represent an array of 3D vertices.")
    
    # Set the method for coloring
    if values is not None:
        try:
            values = checkDimsOfArray(values, 0, 1, 2, 3, 4)
            # Returned values is always a 2D numpy array
        except ValueError:
            raise ValueError('values must be 1D, Nx2, Nx3, or Nx4 array.')
        if values.shape[0] != vertices.shape[0]:
            raise ValueError('First dimension of values must be same length as vertices.')
    
    # Instantiate Mesh
    m = vv.Mesh(axes, vertices, faces, normals, values, verticesPerFace)
    
    # Set colormap or texture
    if values is not None and values.shape[1] == 1:
        if colormap is not None:
            m.colormap = colormap
        if clim is not None and len(clim) == 2:
            m.clim = clim
        else:
            m.clim = values.min(), values.max()
    elif texture is not None and values is not None and values.shape[1] == 2:
        m.SetTexture(texture)
    
    # Adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = False
        axes.cameraType = '3d'
        axes.SetLimits()
    
    # Return
    axes.Draw()
    return m


if __name__ == '__main__':
    # Create BaseMesh object (has no visualization props)
    bm = vv.meshRead('teapot.ssdf')
    # Show it, returning a Mesh object (which does have visualization props)
    m = vv.mesh(bm)
