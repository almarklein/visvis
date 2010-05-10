# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

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
