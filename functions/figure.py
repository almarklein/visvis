# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis.backends as backends
from visvis.core import BaseFigure


def figure(nr=None):
    """ figure(nr=None)
    Create a new figure or return the figure with the asociated nr. 
    """
    
    # check if backends are loaded
    if not backends.currentBackend.name:
        backends.use()
    
    # get function to create new figure
    newFigure = backends.currentBackend.newFigure
    
    # nr given?
    if nr is not None:
        # test nr
        try:
            nr = int(nr)
            assert nr > 0
        except (ValueError, AssertionError):
            raise Exception("Figure nr should be an integer >=1")
    
    # does a figure with that number already exist?
    if nr and BaseFigure._figures.has_key(nr):        
        # make current return that
        fig = BaseFigure._figures[nr]
        BaseFigure._currentNr = nr
        return fig
    else:
        if nr:
            # prepare spot, if no nr given, a spot is chosen in the
            # constructor of BaseFigure...
            BaseFigure._figures[nr] = None
        # create new figure and return
        fig = newFigure()
        fig.title = '' #_SetTitle("Figure " + str(fig.nr))
        return fig
