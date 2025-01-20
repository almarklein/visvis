# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import visvis.backends as backends
from visvis import BaseFigure


def figure(fig=None, clear=False):
    """ figure(fig=None, clear=False)

    Set the specified figure to be the current figure, creating it if
    necessary.  fig may be a Figure object, a figure number (a positive
    integer), or None.  Returns the specified or created figure.

    """

    # check if backends are loaded
    if not backends.currentBackend.name:
        backends.use()

    # get function to create new figure
    newFigure = backends.currentBackend.newFigure

    # fig can be a Figure instance
    if isinstance(fig, BaseFigure):
        if fig._destroyed:
            raise Exception("Figure has already been destroyed.")
        nr = fig.nr
    # ... or a positive integer
    elif fig is not None:
        # test nr
        try:
            nr = int(fig)
            if nr <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise Exception("Figure number should be an integer >=1")
    else:
        nr = None

    # does a figure with that number already exist?
    if nr and nr in BaseFigure._figures:
        # make current return that
        fig = BaseFigure._figures[nr]
        BaseFigure._currentNr = nr
        if clear:
            fig.Clear()
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


if __name__ == '__main__':
    fig = vv.figure()
