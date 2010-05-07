import visvis as vv

def grid(*args, **kwargs):
    """ grid(..., axes=None)
    
    Create a wireframe parametric surfaces. 
    
    Can be called using several ways:
     * grid(z) - create a grid mesh the given image with z coordinates.
     * grid(z, c) - also supply a texture image to map.
     * grid(x, y, z) - give x, y and z coordinates.
     * grid(x, y, z, c) - also supply a texture image to map.
    
    Note: this function is know in Matlab as mesh(), but to avoid confusion
    with the vv.Mesh class, it is called grid() in visvis.
    
    See also surf.
    """
    
    m = vv.surf(*args, **kwargs)
    m.faceShading = None
    m.edgeShading = 'smooth'
    m.edgeColor = 'w'
    return m

if __name__ == '__main__':
    vv.figure()
    a = vv.cla()
    m = grid(vv.peaks())
    m.colormap = vv.CM_HOT
    
    # show 
    a.daspectAuto = False
    a.cameraType = '3d'
    a.SetLimits()