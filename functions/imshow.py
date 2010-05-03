import visvis as vv

def imshow(im, clim=None, axes=None, aa=1, interpolate=False, cm=None):
    """ imshow(im, clim, axes, aa, interpolate=False, cm=CM_GRAY)
    
    Display a 2D image and returns the Texture2D object. 
    
    If the image is an anisotropic array (vv.points.Aaray), the appropriate         scale and translate transformations are applied. The daspect of the axes
    is changed such that the y axes is negative.
    
    The aa and interpolate parameters can be used to specify anti aliasing
    and (linear) interpolation, respectively.
    
    New images are positioned on z=-0.1, such that lines and points are
    visible over the image. This z-pos of textures already in the axes
    are moved backwards if new images are displayed with imshow, such that 
    the new image is displayed over the older ones.
    (the set value is Texture2D._trafo_trans.dz)
    
    Visvis does not use the "hold on / hold off" system. So if updating 
    an image, better use Texture2D.Refresh() or do Axes.Clear() first.
    """
    
    # get axes
    if axes is None:
        axes = vv.gca()
    
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
    axes.daspectAuto = False    
    axes.SetLimits()
    da = axes.daspect
    axes.daspect = da[0], -abs(da[1]), da[2]
    
    # return
    axes.Draw()
    return t
    
if __name__ == "__main__":
    import numpy as np
    from visvis.points import Aarray
    
    im = np.zeros((100,100), dtype=np.float32)
    im[40:-20,10:-5] = 0.4
    im[30:50,40:70] = 0.4
    im2 = Aarray(im,sampling=(0.5,1), origin=(0,105))
    im2[:] += 0.1
    im2[0,0] = 0
    imshow(im)
    imshow(im2)
    
