# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
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
