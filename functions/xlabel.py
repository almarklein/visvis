""" Set the xlabel of the given or current axes. """

import visvis as vv

def xlabel(text, axes=None):
    """ xlabel(text, axes=None)
    Set the xlabel of the given or current axes. 
    Note: you can also use "axes.xLabel = text".
    """
    if axes is None:
        axes = vv.gca()
    axes.xLabel = text

if __name__=='__main__':
    vv.gca()
    xlabel('label test')