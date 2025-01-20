# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def grid(*args, **kwargs):
    """ grid(*args, axesAdjust=True, axes=None)
    
    Create a wireframe parametric surface.
    
    Usage
    -----
      * grid(Z) - create a grid mesh using the given image with z coordinates.
      * grid(Z, C) - also supply a texture image to map.
      * grid(X, Y, Z) - give x, y and z coordinates.
      * grid(X, Y, Z, C) - also supply a texture image to map.
    
    Parameters
    ----------
    Z : A MxN 2D array
    X : A length N 1D array, or a MxN 2D array
    Y : A length M 1D array, or a MxN 2D array
    C : A MxN 2D array, or a AxBx3 3D array
        If 2D, C specifies a colormap index for each vertex of Z.  If
        3D, C gives a RGB image to be mapped over Z.  In this case, the
        sizes of C and Z need not match.
    
    Keyword arguments
    -----------------
    axesAdjust : bool
        If True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet,
        it is set to False.
    axes : Axes instance
        Display the bars in the given axes, or the current axes if not given.
    
    Notes
    -----
      * This function should not be confused with the axis grid, see the
        Axis.showGrid property.
      * This function is know in Matlab as mesh(), but to avoid confusion
        with the vv.Mesh class, it is called grid() in visvis.
    
    Also see surf() and the solid*() methods.
    
    """
    
    m = vv.surf(*args, **kwargs)
    m.faceShading = None
    m.edgeShading = 'smooth'
    m.edgeColor = 'w'
    return m

if __name__ == '__main__':
    vv.figure()
    m = vv.grid(vv.peaks())
    m.colormap = vv.CM_HOT
