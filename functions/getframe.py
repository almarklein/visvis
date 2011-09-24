# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import OpenGL.GL as gl
import numpy as np


def getframe(ob):
    """ getframe(object)
    
    Get a snapshot of the current figure or axes or axesContainer.
    It is retured as a numpy array (color image).
    Also see vv.screenshot().
    
    """
    
    # Get figure
    fig = ob.GetFigure()
    if not fig:
        raise ValueError('Object is not present in any alive figures.')
    
    # Select the figure
    fig._SetCurrent() # works on all backends

    # we read the pixels as shown on screen.
    gl.glReadBuffer(gl.GL_FRONT)
    
    # establish rectangle to sample
    if isinstance(ob, vv.BaseFigure):
        x,y,w,h = 0, 0, ob.position.w, ob.position.h
    elif isinstance(ob, vv.AxesContainer):
        x,y = ob.position.absTopLeft
        w,h = ob.position.size
        y = fig.position.h - (y+h)
    elif isinstance(ob, vv.Axes):
        x,y = ob.position.absTopLeft
        w,h = ob.position.size
        y = fig.position.h - (y+h)
        x+=1; y+=1; w-=1; h-=1;  # first pixel is the bounding box
    else:
        raise ValueError("The given object is not a figure nor an axes.")
    
    # read
    # use floats to prevent strides etc. uint8 caused crash on qt backend.
    im = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_FLOAT)
    
    # reshape, flip, and store
    im.shape = h,w,3
    im = np.flipud(im)
    
    # done
    return im
    


if __name__ == '__main__':
    import time
    
    f = vv.figure()
    a1 = vv.subplot(211)
    a2 = vv.subplot(212)
    
    vv.plot([2,3,4,2,4,3], axes=a1)
    
    for i in range(4):
        # draw and wait a bit
        f.DrawNow()
        time.sleep(1)
        # make snapshots
        im1 = getframe(f)
        im2 = getframe(a1)
        # clear and show snapshots
        a1.Clear()
        a2.Clear()
        vv.imshow(im1,axes=a1, clim=(0,1))
        vv.imshow(im2,axes=a2, clim=(0,1))
