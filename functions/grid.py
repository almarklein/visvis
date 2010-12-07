# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def grid(*args, **kwargs):
    """ grid(..., axesAdjust=True, axes=None)
    
    Create a wireframe parametric surface. (Not to be confused with 
    the axis grid, see the Axis.showGrid property.)
    
    Can be called using several ways:
     * grid(z) - create a grid mesh using the given image with z coordinates.
     * grid(z, c) - also supply a texture image to map.
     * grid(x, y, z) - give x, y and z coordinates.
     * grid(x, y, z, c) - also supply a texture image to map.
    
    Note: this function is know in Matlab as mesh(), but to avoid confusion
    with the vv.Mesh class, it is called grid() in visvis.
    
    If axesAdjust==True, this function will call axes.SetLimits(), and set
    the camera type to 3D. If daspectAuto has not been set yet, it is set 
    to False.
    
    Also see surf() and the solid*() methods.
    
    """
    
    m = vv.surf(*args, **kwargs)
    m.faceShading = None
    m.edgeShading = 'smooth'
    m.edgeColor = 'w'
    return m

if __name__ == '__main__':
    vv.figure()
    m = grid(vv.peaks())
    m.colormap = vv.CM_HOT    
