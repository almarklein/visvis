import visvis as vv
from visvis.wobjects.polygonalModeling import checkDimsOfArray
import numpy as np

def mesh(vertices, faces=None, normals=None, values=None, colormap=None, 
         texture=None, verticesPerFace=3, axesAdjust=True, axes=None):
    """ mesh(vertices, faces=None, normals=None, values=None, colormap=None,
    texture=None, verticesPerFace=3, axesAdjust=True, axes=None)
    *** WARNING: This signature is preliminary and will likely change! ***
    
    Display a mesh of polygons, either triangles or quads.
    
    Parameters
    ----------
    vertices : Nx3 array
        The positions of the vertices in 3D space.
    faces : array or list of indices
        The faces given in terms of the vertex indices.  Should be 1D, in
        which case the indices are grouped into groups of verticesPerFace,
        or Mx3 or Mx4, in which case verticesPerFace is ignored.
    normals : Nx3
        A list of vectors specifying the vertex normals.
    values : N, Nx2, Nx3, or Nx4 array
        Sets the color of each vertex, using values from a colormap (1D),
        colors from a texture (Nx2), RGB values (Nx3), or RGBA value (Nx4).
    colormap : a Colormap
        If values is 1D, the vertex colors are set from this colormap.
    texture : a Texture
        If values is Nx2, the vertex colors are set from this texture.
    verticesPerFace : 3 or 4
        Whether the faces are triangle or quads, if not specified in faces.
    axesAdjust : bool
        Whether to adjust the view after the mesh is drawn.
    axes : Axes instance
        The axes into which the mesh will be added.  If None, the current
        axes will be used.
    """
    
    if axes is None:
        axes = vv.gca()
    
    # Check that vertices is (converted to) a Nx3 array; otherwise user
    # will see odd behavior from Mesh
    try:
        vertices = checkDimsOfArray(vertices, 3)
    except ValueError:
        raise ValueError('vertices must be Nx3 array.')
    
    # Set the method for coloring
    texcoords = None
    colors = None
    try:
        values = checkDimsOfArray(values, 0, 2, 3, 4)
    except ValueError:
        raise ValueError('values must be 1D, Nx2, Nx3, or Nx4 array.')
    if values.shape[0] != vertices.shape[0]:
        raise ValueError('First dimension of values must be same length as vertices.')
    if values.ndim == 1 or values.shape[1] == 2:
        texcoords = values
    elif values.shape[1] in (3,4):
        colors = values
    
    m = vv.Mesh(axes, vertices, normals, faces, colors, texcoords, verticesPerFace)
    if colormap is not None and values.ndim == 1:
        m.colormap = colormap
    elif texture is not None and values.ndim == 2 and values.shape[1] == 2:
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
