# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv

def xlabel(text, axes=None):
    """ xlabel(text, axes=None)
    Set the xlabel of the given or current axes. 
    Note: you can also use "axes.axis.xLabel = text".
    """
    if axes is None:
        axes = vv.gca()
    axes.axis.xLabel = text

if __name__=='__main__':
    vv.figure()
    a = vv.gca()
    a.cameraType = '2d'    
    xlabel('label test')
