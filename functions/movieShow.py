# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def movieShow(images, clim=None, duration=0.1, axesAdjust=True, axes=None):
    """ movieShow(images, duration=0.1)
    
    Show the images in the given list as a movie. 
    The actual duration can differ from the given duration, depending
    on the performance of your system.
    
    """
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create container
    m = vv.MotionDataContainer(axes, duration*1000)
    
    # Create images and put in container
    for im in images:
        t = vv.imshow(im, clim=clim, axesAdjust=axesAdjust, axes=axes)
        t.parent = m
    
    # Return container object
    return m
