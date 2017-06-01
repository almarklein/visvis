# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv


def isocontour(im, isovalue=None):
    """ isocontour(im, isovalue=None)
    
    Uses scikit-image to calculate the iso contours for the given 2D
    image. If isovalue is not given or None, a value between the min
    and max of the image is used.
    
    Returns a pointset in which each two subsequent points form a line
    piece. This van be best visualized using "vv.plot(result, ls='+')".
    
    """
    
    from visvis.utils.iso import isocontour as _isocontour
    
    return _isocontour(im, isovalue)


if __name__ == '__main__':
    vv.plot(isocontour(vv.imread('astronaut.png')[:,:,1]), ls='+', lw=3)
