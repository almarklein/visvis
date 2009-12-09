""" Set the zlabel of the given or current axes. """

import visvis as vv

def zlabel(text, axes=None):
    """ zlabel(text, axes=None)
    Set the zlabel of the given or current axes. 
    Note: you can also use "axes.zLabel = text".
    """
    if axes is None:
        axes = vv.gca()
    axes.zLabel = text

if __name__=='__main__':
    
    a = vv.gca()
    vv.plot([1,2,3],[1,3,2],[3,1,2])
    a.cameraType = '3d'
    
    vv.xlabel('label x')
    vv.ylabel('label y')
    zlabel('label test')