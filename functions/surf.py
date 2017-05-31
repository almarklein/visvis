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
        If axesAdjust==True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet,
        it is set to False.
    axes : Axes instance
        Display the image in this axes, or the current axes if not given.
    
    Also see grid()
    
    """
    
    def checkZ(z):
        if z.ndim != 2:
            raise ValueError('Z must be a 2D array.')
    
    # Parse input
    if len(args) == 1:
        z = np.asanyarray(args[0])
        checkZ(z)
        y = np.arange(z.shape[0])
        x = np.arange(z.shape[1])
        c = None
    elif len(args) == 2:
        z, c = map(np.asanyarray, args)
        checkZ(z)
        y = np.arange(z.shape[0])
        x = np.arange(z.shape[1])
    elif len(args) == 3:
        x, y, z = map(np.asanyarray, args)
        checkZ(z)
        c = None
    elif len(args) == 4:
        x, y, z, c = map(np.asanyarray, args)
        checkZ(z)
    else:
        raise ValueError('Invalid number of arguments.  Must pass 1-4 arguments.')
    
    
    # Parse kwargs
    axes = None
    if 'axes' in kwargs:
        axes = kwargs['axes']
    axesAdjust = True
    if 'axesAdjust' in kwargs:
        axesAdjust = kwargs['axesAdjust']
    
    
    # Set y vertices
    if y.shape == (z.shape[0],):
        y = y.reshape(z.shape[0], 1).repeat(z.shape[1], axis=1)
    elif y.shape != z.shape:
        raise ValueError('Y must have same shape as Z, or be 1D with length of rows of Z.')
    
    # Set x vertices
    if x.shape == (z.shape[1],):
        x = x.reshape(1, z.shape[1]).repeat(z.shape[0], axis=0)
    elif x.shape != z.shape:
        raise ValueError('X must have same shape as Z, or be 1D with length of columns of Z.')
    
    # Set vertices
    vertices = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    
    
    # Create texcoords
    if c is None or c.shape == z.shape:
        # No texture -> colormap on the z value
        # Grayscale texture -> color mapping
        texcoords = (c if c is not None else z).ravel()
    
    elif c.ndim == 3:
        # color texture -> use texture mapping
        U, V = np.meshgrid(np.linspace(0,1,z.shape[1]), np.linspace(0,1,z.shape[0]))
        texcoords = np.column_stack((U.ravel(), V.ravel()))
    
    else:
        raise ValueError('C must have same shape as Z, or be 3D array.')
    
    # Create faces
    w = z.shape[1]
    i = np.arange(z.shape[0]-1)
    faces = np.row_stack(
        np.column_stack((j + w*i, j+1 + w*i, j+1 + w*(i+1), j + w*(i+1)))
        for j in range(w-1))
    
    
    ## Visualize
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create mesh
    m = vv.Mesh(axes, vertices, faces, values=texcoords, verticesPerFace=4)
    
    # Should we apply a texture?
    if c is not None and c.ndim==3:
        m.SetTexture(c)
    else:
        m.clim = m.clim  # trigger correct limits
    
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
    im0 = vv.imread('astronaut.png').astype(np.float32)
    im = im0.copy()
    im[1:,:,:] = im0[:-1,:,:]
    im[:-1,:,:] += im0[1:,:,:]
    im[:,:-1,:] += im0[:,1:,:]
    im[:,1:,:] += im0[:,:-1,:]
    im /= 4
    # Surf
    m = vv.surf(im[:,:,0], im)
