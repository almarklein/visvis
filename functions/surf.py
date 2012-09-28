# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import numpy as np
import visvis as vv


def surf(*args, **kwargs):
    """ surf(..., axesAdjust=True, axes=None)
    
    Shaded surface plot. 
    
    Usage
    -----
      * surf(Z) - create a surface using the given image with z coordinates.
      * surf(Z, C) - also supply a texture image to map.
      * surf(X, Y, Z) - give x, y and z coordinates.
      * surf(X, Y, Z, C) - also supply a texture image to map.
    
    If C is a 2D image, it should match the dimensions of z. If it is an Nx3
    array it specifies the color for each vertex.
    
    Keyword arguments
    -----------------
    axesAdjust : bool
        If axesAdjust==True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet,
        it is set to False.
    axes : Axes instance
        Display the image in this axes, or the current axes if not given.
    
    Also see grid()
    
    """
    
    def checkZ(z):
        if z.ndim != 2:
            raise ValueError('Surf() requires Z to be 2D.')
    
    # Parse input
    if len(args) == 1:
        z = args[0]
        checkZ(z)
        y = np.arange(z.shape[0])
        x = np.arange(z.shape[1])        
        c = None
    elif len(args) == 2:
        z, c = args
        checkZ(z)
        y = np.arange(z.shape[0])
        x = np.arange(z.shape[1])
    elif len(args) == 3:
        x, y, z = args
        checkZ(z)
        c = None
    elif len(args) == 4:
        x, y, z, c = args
        checkZ(z)
    else:
        raise ValueError('Invalid number of arguments for function surf().')
    
    
    # Parse kwargs
    axes = None
    if 'axes' in kwargs:
        axes = kwargs['axes']
    axesAdjust = True
    if 'axesAdjust' in kwargs:
        axesAdjust = kwargs['axesAdjust']
    
    
    # Init vertices
    vertices = np.zeros( (z.shape[0] * z.shape[1], 3), dtype=np.float32  )
    
    # Set y vertices
    if y.shape == (z.shape[0],):
        jump = z.shape[1]
        for i in range(z.shape[1]):
            vertices[i::jump,1] = y
    elif y.shape == z.shape:
        vertices[:,1] = y.ravel()
    else:
        raise ValueError('Y does not match the dimensions of Z.')
    
    # Set x vertices
    if x.shape == (z.shape[1],):
        start, jump = 0, z.shape[1]
        for i in range(z.shape[0]):
            vertices[start:start+jump,0] = x
            start += jump
    elif x.shape == z.shape:
        vertices[:,0] = x.ravel()
    else:
        raise ValueError('X does not match the dimensions of Z.')
    
    # Set z vertices
    vertices[:,2] = z.ravel()
    
    
    # Create texcoords
    if c is None or c.shape == z.shape:
        # No texture -> colormap on the z value
        # Grayscale texture -> color mapping        
        texcords = (c if c is not None else z).ravel()
        
        # Correct for min-max
        mi, ma = texcords.min(), texcords.max()
        texcords = (texcords-mi) / (ma-mi)
    
    elif c.ndim == 3:
        # color texture -> use texture mapping
        
        texcords = np.zeros( (vertices.shape[0],2), dtype=np.float32  )
        # y coordinates
        v = np.linspace(0,1,z.shape[0])
        jump = z.shape[1]
        for i in range(z.shape[1]):
            texcords[i::jump,1] = v
        # x coordinates
        u = np.linspace(0,1,z.shape[1])
        start = 0
        for i in range(z.shape[0]):
            texcords[start:start+jump,0] = u
            start += jump
    
    else:
        raise ValueError('C does not match the dimensions of Z.')
    
    # Create faces
    faces = []
    w = z.shape[1]
    for j in range(z.shape[1]-1):
        for i in range(z.shape[0]-1):
            faces.extend([j + w*i, j+1+w*i, j+1+w*(i+1), j+w*(i+1)])
    
    
    ## Visualize
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create mesh
    m = vv.Mesh(axes, vertices, faces, values=texcords, verticesPerFace=4)
    
    # Should we apply a texture?
    if c is not None and c.ndim==3:
        m.SetTexture(c)
    
    # Adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = False
        axes.cameraType = '3d'
        axes.SetLimits()
    
    # Return
    axes.Draw()
    return m


if __name__ == "__main__":
    # Read image and smooth a bit
    lena = vv.imread('lena.png').astype(np.float32)
    im = lena.copy()
    im[1:,:,:] = lena[:-1,:,:]
    im[:-1,:,:] += lena[1:,:,:]
    im[:,:-1,:] += lena[:,1:,:]
    im[:,1:,:] += lena[:,:-1,:]
    im /= 4
    # Surf
    m = vv.surf(im[:,:,0], im)
    
