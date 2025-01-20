# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np

def imshow(im, clim=None, aa=2, interpolate=False, cm=None,
            axesAdjust=True, axes=None):
    """ imshow(im, clim=None, aa=2, interpolate=False, cm=CM_GRAY,
                axesAdjust=True, axes=None)
    
    Display a 2D image and returns the Texture2D object.
    
    If the image is an anisotropic array (vv.Aaray), the appropriate
    scale and translate transformations are applied.
    
    Parameters
    ----------
    im : numpy array
        The image to visualize. Can be grayscale, RGB, or RGBA.
    clim : 2-element tuple
        The color limits to scale the intensities of the image. If not given,
        the im.min() and im.max() are used (neglecting nan and inf).
    aa : 0, 1, 2 or 3
        Anti aliasing. 0 means no anti-aliasing. The highee the number, the
        better quality the anti-aliasing is (Requires a GLSL compatible
        OpenGl implementation). Default 2.
    interpolation : bool
        Use no interpolation (i.e. nearest neighbour) or linear interpolation.
    cm : Colormap
        Set the colormap to apply in case the image is grayscale.
    axesAdjust : bool
        If axesAdjust==True, this function will call axes.SetLimits(), set
        the camera type to 2D, and make axes.daspect[1] negative (i.e. flip
        the y-axis). If daspectAuto has not been set yet, it is set to False.
    axes : Axes instance
        Display the image in this axes, or the current axes if not given.
    
    Notes
    -----
    New images are positioned on z=-0.1, such that lines and points are
    visible over the image. This z-pos of textures already in the axes
    are moved backwards if new images are displayed with imshow, such that
    the new image is displayed over the older ones.
    (the changed value is `Texture2D._trafo_trans.dz`)
    
    Visvis does not use the "hold on / hold off" system. So if updating
    an image, better use Texture2D.Refresh() or call Axes.Clear() first.
    
    """
    
    # get axes
    if axes is None:
        axes = vv.gca()
    
    # Check data
    if not isinstance(im, np.ndarray):
        raise ValueError('imshow expects an image as a numpy array.')
    elif im.size==0:
        raise ValueError('imshow cannot draw arrays with zero elements.')
    #
    if im.ndim==2 or im.ndim==3 and im.shape[-1] in [1,3,4]:
        pass
    else:
        raise ValueError('imshow expects a 2D image as a numpy array.')
    
    # determine texture offset, such that lines are always on top
    # of images, and new textures are on top of older images.
    texCount = 1
    texOffset = -0.1
    for item in reversed(axes._wobjects):
        if isinstance(item, vv.Texture2D):
            texCount += 1
            item._trafo_trans.dz = texCount * texOffset
    
    # create texture
    t = vv.Texture2D(axes, im)
    t._trafo_trans.dz = texOffset
    
    # set aa and interpolation
    t.aa = aa
    t.interpolate = interpolate
    
    # set clim
    if isinstance(clim,list):
        clim = tuple(clim)
    if isinstance(clim, tuple):
        t.SetClim(clim)
    
    # set colormap
    if cm is not None:
        t.colormap = cm
    
    # set axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = False
        axes.cameraType = '2d'
        da = axes.daspect
        axes.daspect = da[0], -abs(da[1]), da[2]
        axes.SetLimits()
    
    # return
    axes.Draw()
    return t



if __name__ == '__main__':
    im = vv.imread('astronaut.png')
    im = vv.Aarray(im[:,::4,:], (1,4,1)) # Keep every 4th pixel and make them wide
    # imshow knows about anisotropic arrays!
    t = vv.imshow(im)
