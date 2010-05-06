import visvis as vv
from visvis.points import Point, Pointset

import OpenGL.GL as gl

def surf(*args, **kwargs):
    """ surf(..., axes=None)
    
    Shaded surface plot. Can be called using several ways:
     * surf(z) - create a surface using the given image with z coordinates.
     * surf(z, c) - also supply a texture image to map.
     * surf(x, y, z) - give x, y and z coordinates.
     * surf(x, y, z, c) - also supply a texture image to map.
    
    """
    
    # Parse input
    if len(args) == 1:        
        z = args[0]
        y = range(z.shape[0])
        x = range(z.shape[1])        
        c = None
    elif len(args) == 2:
        z, c = args
        y = range(z.shape[0])
        x = range(z.shape[1])
    elif len(args) == 3:
        x, y, z = args
        c = None
    elif len(args) == 4:
        x, y, z, c = args
    else:
        raise ValueError('Invalid number of arguments for function surf().')
    
    # Parse kwargs
    axes = None
    if 'axes' in kwargs:
        axes = kwargs['axes']
    
    # todo: Check arguments
    
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create vertices
    vertices = Pointset(3)
    for j in range(len(y)):
        yy = y[j]
        for i in range(len(x)):
            xx = x[i]
            zz = z[j,i]
            vertices.Append(xx,yy,zz)
    
    # Create texcoords
    texcords, colors = None, None
    if c is not None:
        if c.ndim==3:
            texcords = None
            colors = c.reshape((c.shape[0]+c.shape[1], c.shape[2]))
        elif c.ndim==2:
            texcords = c.reshape((c.shape[0]+c.shape[1],))
            colors = None
        else:
            raise ValueError('Invalid color texture given.')
    
    # Create faces
    faces = []
    w = len(y)
    for j in range(len(y)-1):
        for i in range(len(x)-1):
            faces.extend([j + w*i, j+1+w*i, j+1+w*(i+1), j+w*(i+1)])
    
    # Create mesh
    m = vv.Mesh(axes, vertices, faces=faces, colors=colors, texcords=texcords, 
        type=gl.GL_QUADS)
    
    return m


if __name__ == "__main__":
    im = vv.imread('lena.png')
    surf(im[:,:,0])
    a = vv.gca()
    a.daspectAuto = False
    a.cameraType = '3d'
    