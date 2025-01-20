# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def movieShow(images, clim=None, duration=0.1, axesAdjust=True, axes=None):
    """ movieShow(images, duration=0.1)
    
    Show the images in the given list as a movie.
    
    Parameters
    ----------
    images : list
        The 2D images (can be color images) that the movie consists of.
    clim : (min, max)
        The color limits to apply. See imshow.
    duration : scalar
        The duration (in seconds) of each frame. The real duration can
        differ from the given duration, depending on the performance of
        your system.
    axesAdjust : bool
        If axesAdjust==True, this function will call axes.SetLimits(), set
        the camera type to 2D, and make axes.daspect[1] negative (i.e. flip
        the y-axis). If daspectAuto has not been set yet, it is set to False.
    axes : Axes instance
        Display the image in this axes, or the current axes if not given.
    
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


if __name__ == '__main__':
    ims = vv.movieRead('newtonscradle.gif')
    vv.movieShow(ims)
