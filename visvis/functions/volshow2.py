# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np

def volshow2(vol, clim=None, renderStyle=None, cm=None,
            axesAdjust=True, axes=None):
    """ volshow2(vol, clim=None, renderStyle=None, cm=CM_GRAY,
            axesAdjust=True, axes=None)
    
    Display a 3D image (a volume) using three slice textures that can be
    moved interactively. Returns a SliceTextureProxy instance that "wraps"
    the three SliceTexture instances.
    
    Parameters
    ----------
    vol : numpy array
        The 3D image to visualize. Can be grayscale, RGB, or RGBA.
        If the volume is an anisotropic array (vv.Aaray), the appropriate
        scale and translate transformations are applied.
    clim : 2-element tuple
        The color limits to scale the intensities of the image. If not given,
        the im.min() and im.max() are used (neglecting nan and inf).
    renderStyle : not used
        This parameter is included for compatibility with volshow3. Its
        value is ignored.
    cm : Colormap
        Set the colormap to apply in case the volume is grayscale.
    axesAdjust : bool
        If axesAdjust==True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet, it is
        set to False.
    axes : Axes instance
        Display the image in this axes, or the current axes if not given.
    
    """
    
    # get axes
    if axes is None:
        axes = vv.gca()
    
     # Check data
    if not isinstance(vol, np.ndarray):
        raise ValueError('volshow expects an image as a numpy array.')
    elif vol.size==0:
        raise ValueError('volshow cannot draw arrays with zero elements.')
    #
    if vol.ndim==3 or vol.ndim==4 and vol.shape[-1] in [1,3,4]:
        pass
    else:
        raise ValueError('volshow expects a 3D image as a numpy array.')
    
    # Get centre
    centre = [int(s/2) for s in vol.shape]
    
    # create textures
    proxy = vv.SliceTextureProxy(axes)
    for i in range(3):
        vv.SliceTexture(proxy, vol, i, centre[i])
    
    # set clim
    if isinstance(clim,list):
        clim = tuple(clim)
    if isinstance(clim, tuple):
        proxy.SetClim(clim)
    
    # set colormap
    if cm is not None:
        proxy.colormap = cm
    
    # adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = False
        axes.cameraType = '3d'
        axes.SetLimits()
    
    # done
    axes.Draw()
    return proxy


if __name__ == "__main__":
    vol = vv.aVolume()
    t = vv.volshow2(vol)
