import visvis as vv
 
def colorbar(axes=None):
    """ colorbar(axes=None)
    Attach a colorbar to the given axes (or the current axes if 
    not given). The reference to the colorbar instance is returned.
    Also see the vv.ColormapEditor wibject.
    """
    
    if axes is None:
        axes = vv.gca()
    
    return vv.cm.Colorbar(axes)