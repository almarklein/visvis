# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

from visvis.core import BaseFigure
import visvis as vv

def gcf():
    """ gcf()
    
    Get the current figure. 
    
    """
    
    if not BaseFigure._figures:
        # no figure yet
        return vv.figure()    
    
    nr = BaseFigure._currentNr    
    if not nr in BaseFigure._figures:
        # erroneous nr
        nr = BaseFigure._figures.keys()[0]
        BaseFigure._currentNr = nr
    
    return BaseFigure._figures[nr]
