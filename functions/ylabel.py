import visvis as vv

def ylabel(text, axes=None):
    """ ylabel(text, axes=None)
    Set the ylabel of the given or current axes. 
    Note: you can also use "axes.yLabel = text".
    """
    if axes is None:
        axes = vv.gca()
    axes.yLabel = text

if __name__=='__main__':
    vv.gca()
    ylabel('label test')