# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def ylabel(text, axes=None):
    """ ylabel(text, axes=None)
    
    Set the ylabel of an axes.
    Note that you can also use "axes.axis.yLabel = text".
    
    Parameters
    ----------
    text : string
        The text to display.
    axes : Axes instance
        Display the image in this axes, or the current axes if not given.
    
    """
    if axes is None:
        axes = vv.gca()
    axes.axis.yLabel = text

if __name__=='__main__':
    a = vv.gca()
    a.cameraType = '2d'
    vv.ylabel('label test')
