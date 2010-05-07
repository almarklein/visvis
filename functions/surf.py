import numpy as np
import visvis as vv
from visvis.points import Point, Pointset

import OpenGL.GL as gl
import time

def surf(*args, **kwargs):
    """ surf(..., axes=None)
    
    Shaded surface plot. Can be called using several ways:
     * surf(z) - create a surface using the given image with z coordinates.
     * surf(z, c) - also supply a texture image to map.
     * surf(x, y, z) - give x, y and z coordinates.
     * surf(x, y, z, c) - also supply a texture image to map.
    
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
    
    
    # Init vertices
    vertices = np.zeros( (len(x)*len(y), 3), dtype=np.float32  )
    
    # Set y vertices
    if len(y) == z.shape[0]:
        start, jump = 0, len(y)
        for i in range(z.shape[1]):
            vertices[start:start+jump,0] = y
            start += jump
    elif len(y) == z.shape[0]*z.shape[1]:
        vertices[:,0] = y
    else:
        raise ValueError('Y does not match the dimensions of Z.')
    
    # Set x vertices
    if len(x) == z.shape[1]:
        step = z.shape[0]
        for i in range(z.shape[0]):
            vertices[i::step,1] = x
    elif len(y) == z.shape[0]*z.shape[1]:
        vertices[:,1] = x
    else:
        raise ValueError('X does not match the dimensions of Z.')
    
    # Set z vertices
    vertices[:,2] = z.ravel()
    
    
    # Create texcoords
    if c is None or c.ndim==2:
        # Grayscale texture -> color mapping        
        # No texture -> colormap on the z value
        
        if c is None:
            texcords = z.reshape((z.shape[0]*z.shape[1],))
        else:
            texcords = c.reshape((c.shape[0]*c.shape[1],))
        
        # Correct for min-max
        mi, ma = texcords.min(), texcords.max()
        texcords = (texcords-mi) / (ma-mi)
    
    else:
        # color texture -> use texture mapping
        
        texcords = np.zeros( (vertices.shape[0],2), dtype=np.float32  )
        if True:
            v = np.linspace(0,1,z.shape[0])
            start, jump = 0, len(y)
            for i in range(z.shape[1]):
                texcords[start:start+jump,0] = v
                start += jump
        if True:
            u = np.linspace(0,1,z.shape[1])
            step = z.shape[0]
            for i in range(z.shape[0]):
                texcords[i::step,1] = u
    
    
    # Create faces
    faces = []
    w = len(y)
    for j in range(len(y)-1):
        for i in range(len(x)-1):
            faces.extend([j + w*i, j+1+w*i, j+1+w*(i+1), j+w*(i+1)])
    
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create mesh
    m = vv.Mesh(axes, vertices, faces=faces, texcords=texcords, 
        verticesPerFace=4)
    
    if c is not None and c.ndim==2:
        m.SetTexture(c)
        
    return m


if __name__ == "__main__":
    
    # Load part of lena image and smooth
    im = np.zeros((256,256,3), dtype=np.float32)
    lena = vv.imread('lena.png')
    for y in [-2,-1,0,1,2]:
        for x in [-2,-1,0,1,2]:
            im += lena[100+y:356+y, 100+x:356+x,:]
    im /= 9.0
    
    # show
    a = vv.cla()
    m = surf(im[:,:,0]/10, im[:,:,0])    
    a.daspectAuto = False
    a.cameraType = '3d'
    a.SetLimits()
    