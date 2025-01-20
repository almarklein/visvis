# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def close(fig):
    """ close(fig)
    
    Close a figure.
    
    fig can be a Figure object or an integer representing the id of the
    figure to close. Note that for the first case, you migh also call
    fig.Destroy().
    
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

if __name__ == '__main__':
    import time
    # Create figure
    fig = vv.figure(1)
    vv.processEvents(); vv.processEvents()
    time.sleep(1.0)
    # Close it
    vv.close(1) # Note: you can also pus the fig object
