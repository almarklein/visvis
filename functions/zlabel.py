# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def zlabel(text, axes=None):
    """ zlabel(text, axes=None)
    
    Set the zlabel of the given or current axes. 
    Note: you can also use "axes.axis.zLabel = text".
    
    """
    if axes is None:
        axes = vv.gca()
    axes.axis.zLabel = text

if __name__=='__main__':
    
    a = vv.gca()
    vv.plot([1,2,3],[1,3,2],[3,1,2])
    a.cameraType = '3d'
    
    vv.xlabel('label x')
    vv.ylabel('label y')
    zlabel('label test')
