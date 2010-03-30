import visvis as vv

def volshow(vol, clim=None, axes=None, renderStyle='mip', cm=None):
    """ volshow(vol, clim=None, axes=None, renderStyle='mip', cm=CM_GRAY)
    
    Display a 3D image (a volume) and returns the Texture3D object.
    
    The default renderStyle is MIP. If the volume is an Anisotropic Array
    (points.Aaray), the appropriate scale and translate transformations
    are applied.
    """
    
    # get axes
    if axes is None:
        axes = vv.gca()
    
    # create texture
    t = vv.Texture3D(axes, vol, renderStyle)
    
    # set clim
    if isinstance(clim,list):
        clim = tuple(clim)
    if isinstance(clim, tuple):
        t.SetClim(clim)
    
    # set colormap
    if cm is not None:
        t.colormap = cm
    
    # set axes
    axes.daspectAuto = False
    axes.SetLimits()
    
    # set camera
    axes.cameraType = '3d'
    
    # done
    axes.Draw()
    return t


if __name__ == "__main__":
    import numpy as np
    vol = np.zeros((128,128,128), dtype=np.uint8)
    vol[40:-20,10:-5,:] = 50
    vol[30:50,:,40:70] += 100
    volshow(vol)
    