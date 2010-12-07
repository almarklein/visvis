# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv

def ylabel(text, axes=None):
    """ ylabel(text, axes=None)
    
    Set the ylabel of the given or current axes. 
    Note: you can also use "axes.axis.yLabel = text".
    
    """
    if axes is None:
        axes = vv.gca()
    axes.axis.yLabel = text

if __name__=='__main__':
    vv.figure()
    a = vv.gca()
    a.cameraType = '2d'    
    ylabel('label test')
