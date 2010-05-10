# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv

def grid(*args, **kwargs):
    """ grid(..., axesAdjust=True, axes=None)
    
    Create a wireframe parametric surfaces. 
    
    Can be called using several ways:
     * grid(z) - create a grid mesh the given image with z coordinates.
     * grid(z, c) - also supply a texture image to map.
     * grid(x, y, z) - give x, y and z coordinates.
     * grid(x, y, z, c) - also supply a texture image to map.
    
    Note: this function is know in Matlab as mesh(), but to avoid confusion
    with the vv.Mesh class, it is called grid() in visvis.
    
    If axesAdjust==True, this function will call axes.SetLimits(), and set
    the camera type to 3D. If daspectAuto has not been set yet, it is set 
    to False.
    
    Also see surf()
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
