# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

from visvis import BaseFigure
import visvis as vv

def gcf():
    """ gcf()
    
    Get the current figure. If there is no figure yet, figure() is
    called to create one. To make a figure current,
    use Figure.MakeCurrent().
    
    See also gca()
    
    """
    
    if not BaseFigure._figures:
        # no figure yet
        return vv.figure()
    
    nr = BaseFigure._currentNr
    if not nr in BaseFigure._figures:
        # erroneous nr
        nr = list(BaseFigure._figures.keys())[0]
        BaseFigure._currentNr = nr
    
    return BaseFigure._figures[nr]

if __name__ == '__main__':
    fig = vv.gcf()
