from pyzolib import pyximport

import numpy as np
import visvis as vv

pyximport.install()
from . import marchingsquares_
pyximport.install()
from . import marchingcubes_

# Map cell-index to zero or more edge indices
# This first element specifies the number of edge-pairs in the list
# 1 | 2
# ------   -> to see below
# 8 | 4
CELLTOEDGE = np.array(  [
                        [0, 0, 0, 0, 0], # Case 0: nothing 
                        [1, 0, 3, 0, 0], # Case 1
                        [1, 0, 1, 0, 0], # Case 2
                        [1, 1, 3, 0, 0], # Case 3 
                        
                        [1, 1, 2, 0, 0], # Case 4 
                        [2, 0, 1, 2, 3], # Case 5 > ambiguous
                        [1, 0, 2, 0, 0], # Case 6
                        [1, 2, 3, 0, 0], # Case 7
                        
                        [1, 2, 3, 0, 0], # Case 8
                        [1, 0, 2, 0, 0], # Case 9
                        [2, 0, 3, 1, 2], # Case 10 > ambiguous
                        [1, 1, 2, 0, 0], # Case 11
                        
                        [1, 1, 3, 0, 0], # Case 12
                        [1, 0, 1, 0, 0], # Case 13
                        [1, 0, 3, 0, 0], # Case 14
                        [0, 0, 0, 0, 0], # Case 15
                        ], 'int32')
                        
# Map an edge-index to two relaive pixel positions. The ege index 
# represents a point that lies somewhere in between these pixels.
# Linear interpolation should be used to determine where it is exactly.
#   0
# 3   1   ->  0x
#   2         xx
EDGETORELATIVEPOSX = np.array([ [0,1],[1,1],[1,0],[0,0] ], 'int32')
EDGETORELATIVEPOSY = np.array([ [0,0],[0,1],[1,1],[1,0] ], 'int32')
# EDGETORELATIVEPOSX = np.array([ [-1,+1],[+1,+1],[+1,-1],[-1,-1] ], 'int32')
# EDGETORELATIVEPOSY = np.array([ [-1,-1],[-1,+1],[+1,+1],[+1,-1] ], 'int32')


def isocontour(im, isovalue=None):
    """ isocontour(im, isovalue=None) -> pointset
    
    Calculate the iso contours for the given 2D image. If isovalue
    is not given or None, a value between the min and max of the image
    is used. 
    
    Returns a pointset in which each two subsequent points form a line 
    piece. This van be best visualized using "vv.plot(result, ls='+')".
    
    """
    
    # Check image
    if not isinstance(im, np.ndarray) or (im.ndim != 2):
        raise ValueError('Image should be a 2D numpy array.')
    
    # Make sure its 32 bit float
    # todo: also allow bool and uint8 ?
    if im.dtype != np.float32:
        im = im.astype('float32')
    
    # Get isovalue
    if isovalue is None:
        isovalue = 0.5 * (im.min() + im.max())
    isovalue = float(isovalue) # Will raise error if not float-like value given
    
    # Do the magic!
    data = marchingsquares_.marching_squares(im, isovalue, 
                    CELLTOEDGE, EDGETORELATIVEPOSX, EDGETORELATIVEPOSY)
    
    # todo: include functionality to group line pieces that belong to the same contour.
    
    # Return as pointset
    return vv.Pointset(data)
    