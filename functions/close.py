# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def close(fig):
    """ close(fig)
    
    fig can be a Figure object or an integer representing the id of the
    figure to close. Note that for the first case, you migh also call
    fig.Destroy()
    
    """
    
    if isinstance(fig, int):
        figDict = vv.BaseFigure._figures
        if fig in figDict:
            figDict[fig].Destroy()
        else:
            raise ValueError('A figure whith that id does not exist: '+str(fig))
    elif isinstance(fig, vv.BaseFigure):
        fig.Destroy()
    else:
        raise ValueError('Invalid argument for vv.functions.close')
