# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017, Almar Klein
# This code is distributed under the terms of the (new) BSD License.

"""
This package provides two functions:
    * isocontour - for 2D images
    * isosurface - for 3D images

Visvis uses to implement this functionality itself using Cython. Visvis
was often used as a pure Python package though, so this functionality
was sort of hidden.

Therefore I've moved the marching cubes (isosurface) implementation
to scikit-image, and we now use that here.

"""

import visvis as vv
import numpy as np
from skimage.measure import find_contours, marching_cubes_lewiner


def isocontour(im, isovalue=None):
    """ isocontour(im, isovalue=None)
    
    Uses scikit-image to calculate the iso contours for the given 2D
    image. If isovalue is not given or None, a value between the min
    and max of the image is used.
    
    Returns a pointset in which each two subsequent points form a line
    piece. This van be best visualized using "vv.plot(result, ls='+')".
    
    """
    
    # Check image
    if not isinstance(im, np.ndarray) or (im.ndim != 2):
        raise ValueError('im should be a 2D numpy array.')
    
    # Get isovalue
    if isovalue is None:
        isovalue = 0.5 * (im.min() + im.max())
    isovalue = float(isovalue) # Will raise error if not float-like value given
    
    # Get the contours
    data = find_contours(im, isovalue)
    
    # Build the contour as we used to return it. It is less rich, but easier
    # to visualize.
    data2 = []
    for contour in data:
        n = contour.shape[0] * 2 - 2
        contour2 = np.empty((n, 2), np.float32)
        contour2[0::2] = contour[:-1]
        contour2[1::2] = contour[1:]
        data2.append(np.fliplr(contour2))
    
    # Return as pointset
    return vv.Pointset(np.row_stack(data2))


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
    
    # Check image
    if not isinstance(im, np.ndarray) or (im.ndim != 3):
        raise ValueError('vol should be a 3D numpy array.')
    
    # Get isovalue
    if isovalue is None:
        isovalue = 0.5 * (im.min() + im.max())
    isovalue = float(isovalue) # Will raise error if not float-like value given
    
    # Check steps
    step = int(step)
    if step < 1:
        raise ValueError('step must be at least one.')
    
    # Deal with Aarray
    if hasattr(im, 'sampling'):
        sampling = im.sampling[0], im.sampling[1], im.sampling[2]
    else:
        sampling = (1, 1, 1)
    
    # Call into skimage algorithm
    xx = marching_cubes_lewiner(im, isovalue,
                                spacing=sampling,
                                step_size=step,
                                use_classic=useClassic)
    vertices, faces, normals, values = xx
    
    # Transform the data to how Visvis likes it
    vertices = np.fliplr(vertices)
    
    # Check
    if not len(vertices):
        raise RuntimeError('No surface found at the given iso value.')
    
    # Done
    if useValues:
        return vv.BaseMesh(vertices, faces, normals, values)
    else:
        return vv.BaseMesh(vertices, faces, normals)
