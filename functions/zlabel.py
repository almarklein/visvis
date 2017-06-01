# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def zlabel(text, axes=None):
    """ zlabel(text, axes=None)
    
    Set the zlabel of an axes.
    Note that you can also use "axes.axis.zLabel = text".
    
    Parameters
    ----------
    text : string
        The text to display.
    axes : Axes instance
        Display the image in this axes, or the current axes if not given.
    
    """
    if axes is None:
        axes = vv.gca()
    axes.axis.zLabel = text

if __name__=='__main__':
    # Create a 3D plot
    a = vv.gca()
    vv.plot([1,2,3],[1,3,2],[3,1,2])
    a.cameraType = '3d'
    # Set labels for all 3 dimensions
    vv.xlabel('label x')
    vv.ylabel('label y')
    vv.zlabel('label z')
