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
      * grid(z) - create a grid mesh using the given image with z coordinates.
      * grid(z, c) - also supply a texture image to map.
      * grid(x, y, z) - give x, y and z coordinates.
      * grid(x, y, z, c) - also supply a texture image to map.
    
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
