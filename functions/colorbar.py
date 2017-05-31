# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
 
def colorbar(axes=None):
    """ colorbar(axes=None)
    
    Attach a colorbar to the given axes (or the current axes if
    not given). The reference to the colorbar instance is returned.
    Also see the vv.ColormapEditor wibject.
    
    """
    
    if axes is None:
        axes = vv.gca()
    
    return vv.Colorbar(axes)


if __name__ == '__main__':
    # Create and show grayscale image, using a colormap
    im = vv.imread('astronaut.png')[:,:,0]
    t = vv.imshow(im)
    t.colormap = vv.CM_COPPER
    # Show how the values map to colors
    vv.colorbar()
