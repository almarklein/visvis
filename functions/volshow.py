# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv
import numpy as np

def volshow(vol, clim=None, renderStyle='mip', cm=None, 
            axesAdjust=True, axes=None):
    """ volshow(vol, clim=None, renderStyle='mip', cm=CM_GRAY, 
                axesAdjust=True, axes=None)
    
    Display a 3D image (a volume) and returns the Texture3D object.
    
    The default renderStyle is MIP. If the volume is an Anisotropic Array
    (points.Aaray), the appropriate scale and translate transformations
    are applied.
    
    If axesAdjust==True, this function will call axes.SetLimits(), and set
    the camera type to 3D. If daspectAuto has not been set yet, it is set 
    to False.
    """
    
    # get axes
    if axes is None:
        axes = vv.gca()
    
     # Check data
    if not isinstance(vol, np.ndarray):
        raise ValueError('volshow expects an image as a numpy array.')
    if vol.ndim==3 or vol.ndim==4 and vol.shape[-1] in [1,3,4]:
        pass
    else:
        raise ValueError('volshow expects a 3D image as a numpy array.')
    
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
    
    # adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = False
        axes.cameraType = '3d'
        axes.SetLimits()
    
    # done
    axes.Draw()
    return t


if __name__ == "__main__":
    import numpy as np
    vol = np.zeros((128,128,128), dtype=np.uint8)
    vol[40:-20,10:-5,:] = 50
    vol[30:50,:,40:70] += 100
    volshow(vol)
