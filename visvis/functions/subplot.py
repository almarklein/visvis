# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
from visvis import Axes, AxesContainer



def getcenter(f, a):
    """ Get the center (in relative coords) of the axes)."""
    pos = a.position.Copy()
    # make relative
    relative = pos._GetFractionals()
    for i in range(4):
        if not relative[i]:
            pos[i] = pos[i] / f.position[i%2+2]
        if pos[i]<0:
            pos[i] = 1.0 - pos[i]
    return pos.x + pos.w/2.0, pos.y + pos.h/2.0


def laysin(cols, rows, c):
    """ Given the center and the amount of rows and columns,
    return in which bin the axes is in.
    """
    dx, dy = 1.0/cols, 1.0/rows
    x, y = int(c[0]/dx), int(c[1]/dy)
    return x + y*cols
    

def subplot(*args):
    """ subplot(ncols, nrows, nr)
    
    Create or return axes in current figure. Note that subplot(322) is the
    same as subplot(3,2,2).
    
    Parameters
    ----------
    ncols : int
        The number of columns to devide the figure in.
    nrows : int
        The number of rows to devide the figure in.
    nr : int
        The subfigure number on the grid specified by ncols and nrows.
        Should be at least one. subplot(221) is the top left. subplot(222)
        is the top right.
    
    Notes
    -----
    It is checked whether (the center of) an axes is present at the
    specified grid location. If so, that axes is returned. Otherwise
    a new axes is created at that location.
    
    """
    
    # parse input
    if len(args)==1:
        tmp = args[0]
        if tmp>999 or tmp<111:
            raise ValueError("Invalid cols/rows/nr specified.")
        rows = tmp // 100
        tmp  = tmp % 100
        cols = tmp // 10
        tmp  = tmp % 10
        nr   = tmp
    elif len(args)==3:
        rows, cols, nr = args
    else:
        raise ValueError("Invalid number of cols/rows/nr specified.")
    
    # check if ok
    if nr<=0 or cols<=0 or rows<=0:
        raise ValueError("Invalid cols/rows/nr: all bust be >0.")
    if nr > cols*rows:
        raise ValueError("Invalid nr: there are not so many positions.")
        
    # init
    f = vv.gcf()
    nr = nr-1
    
    # check if an axes is there
    for a in f._children:
        if isinstance(a, AxesContainer):
            n = laysin( cols, rows, getcenter(f, a) )
            if n == nr:
                # make current and return
                a = a.GetAxes()
                f.currentAxes = a
                return a
    
    # create axes in container
    a = Axes(f)
    c = a.parent
    
    # calculate relative coordinates
    dx, dy = 1.0/cols, 1.0/rows
    y = int( nr / cols )
    x = int( nr % cols )
    
    # apply positions
    c.position = dx*x, dy*y, dx, dy
    a.position = 10, 10, -20, -20
    
    # done
    return a
    
    

if __name__ == "__main__":
    f = vv.figure()
    # Get axes on 2x2 grid
    a1 = vv.subplot(221)
    a2 = vv.subplot(221)
    a3 = vv.subplot(224)
    # Get axes on 3x3 grid
    a4 = vv.subplot(331) # (center is inside 221)
    a5 = vv.subplot(333)
    # Check
    print(a1 is a2, a1 is a4)
