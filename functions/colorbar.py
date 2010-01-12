""" Attach a colorbar to the given axes. """

import visvis as vv

def colorbar(axes=None, editor=False):
    """ colorbar(axes=None, editor=False)
    Attach a colorbar to the given axes (or the current axes if 
    not given). If 'editor' is True, will create a colormap editor
    instead of a colorbar.
    The reference to the colorbar or colormapEditor instance is returned.
    """
    
    if axes is None:
        axes = vv.gca()
    
    if editor:
        return vv.cm.ColormapEditor(axes)
    else:
        return vv.cm.Colorbar(axes)