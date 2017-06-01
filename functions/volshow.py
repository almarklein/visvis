# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def volshow(*args, **kwargs):
    """ volshow(vol, clim=None, cm=CM_GRAY, axesAdjust=True, axes=None)
    
    Display a 3D image (a volume).
    
    This is a convenience function that calls either volshow3() or
    volshow2(). If the current system supports it (OpenGL version >= 2.0),
    displays a 3D  rendering (volshow3). Otherwise shows three slices
    that can be moved interactively (volshow2).
    
    Parameters
    ----------
    vol : numpy array
        The 3D image to visualize. Can be grayscale, RGB, or RGBA.
        If the volume is an anisotropic array (vv.Aaray), the appropriate
        scale and translate transformations are applied.
    clim : 2-element tuple
        The color limits to scale the intensities of the image. If not given,
        the im.min() and im.max() are used (neglecting nan and inf).
    cm : Colormap
        Set the colormap to apply in case the volume is grayscale.
    axesAdjust : bool
        If axesAdjust==True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet, it is
        set to False.
    axes : Axes instance
        Display the image in this axes, or the current axes if not given.
    
    Any other keyword arguments are passed to either volshow2() or volshow3().
    
    """
    
    # Make sure that a figure exists
    vv.gcf()
    
    # Test and run
    if vv.settings.volshowPreference==3 and vv.misc.getOpenGlCapable(2.0):
        return vv.volshow3(*args, **kwargs)
    else:
        return vv.volshow2(*args, **kwargs)


if __name__ == "__main__":
    vol = vv.aVolume()
    t = vv.volshow(vol)
