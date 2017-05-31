# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv


def isosurface(im, isovalue=None, step=1, useClassic=False, useValues=False):
    """ isosurface(vol, isovalue=None, step=1, useClassic=False, useValues=False)
    
    Uses scikit-image to calculate the isosurface for the given 3D image.
    Returns a vv.BaseMesh object.
    
    Parameters
    ----------
    vol : 3D numpy array
        The volume for which to calculate the isosurface.
    isovalue : float
        The value at which the surface should be created. If not given or None,
        the average of the min and max of vol is used.
    step : int
        The stepsize for stepping through the volume. Larger steps yield
        faster but coarser results. The result shall always be topologically
        correct though.
    useClassic : bool
        If True, uses the classic marching cubes by Lorensen (1987) is used.
        This algorithm has many ambiguities and is not guaranteed to produce
        a topologically correct result.
    useValues : bool
        If True, the returned BaseMesh object will also have a value for
        each vertex, which is related to the maximum value in a local region
        near the isosurface.
    
    """
    
    from visvis.utils.iso import isosurface as _isosurface
    
    return _isosurface(im, isovalue, step, useClassic, useValues)


if __name__ == '__main__':
    vv.mesh(isosurface(vv.volread('stent')))
