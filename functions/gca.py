# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def gca():
    """ gca()
    
    Get the current axes in the current figure. If there is
    no axes, an Axes instance is created. To make an axes current,
    use Axes.MakeCurrent().
    
    See also gcf(), Figure.MakeCurrent(), Figure.currentAxes
    
    """
    f = vv.gcf()
    a = f.currentAxes
    if not a:
        # create axes
        a = vv.Axes(f)
        #a.position = 2, 2, -4, -4
        a.position = 10, 10, -20, -20
    return a
    
    
if __name__ == '__main__':
    a = vv.gca()
