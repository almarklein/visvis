# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein

"""
This package provides two functions:
    * isocontour - for 2D images
    * isosurface - for 3D images

""" 

import numpy as np
import visvis as vv

import sys
import base64
PY3 = sys.version_info[0] == 3
if PY3:
    base64decode = base64.decodebytes
else:
    base64decode = base64.decodestring

from pyzolib import pyximport
pyximport.install()
from . import marchingsquares_
pyximport.install()
from . import marchingcubes_

from . import mcluts



# Map cell-index to zero or more edge indices
# This first element specifies the number of edge-pairs in the list
# 1 | 2
# ------   -> to see below
# 8 | 4
CONTOUR_CASES = np.array(  [
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
                        ], 'int8')
                        
# Map an edge-index to two relative pixel positions. The ege index 
# represents a point that lies somewhere in between these pixels.
# Linear interpolation should be used to determine where it is exactly.
#   0
# 3   1   ->  0x
#   2         xx
# These arrays are used in both isocontour and isosurface algorithm
EDGETORELATIVEPOSX = np.array([ [0,1],[1,1],[1,0],[0,0], [0,1],[1,1],[1,0],[0,0], [0,0],[1,1],[1,1],[0,0] ], 'int8')
EDGETORELATIVEPOSY = np.array([ [0,0],[0,1],[1,1],[1,0], [0,0],[0,1],[1,1],[1,0], [0,0],[0,0],[1,1],[1,1] ], 'int8')
EDGETORELATIVEPOSZ = np.array([ [0,0],[0,0],[0,0],[0,0], [1,1],[1,1],[1,1],[1,1], [0,1],[0,1],[0,1],[0,1] ], 'int8')


def isocontour(im, isovalue=None):
    """ isocontour(im, isovalue=None)
    
    Calculate the iso contours for the given 2D image. If isovalue
    is not given or None, a value between the min and max of the image
    is used. 
    
    Returns a pointset in which each two subsequent points form a line 
    piece. This van be best visualized using "vv.plot(result, ls='+')".
    
    """
    
    # Check image
    if not isinstance(im, np.ndarray) or (im.ndim != 2):
        raise ValueError('im should be a 2D numpy array.')
    
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
                    CONTOUR_CASES, EDGETORELATIVEPOSX, EDGETORELATIVEPOSY)
    
    # Return as pointset
    return vv.Pointset(data)



def isosurface(im, isovalue=None, step=1, useclassic=False, usevalues=False):
    """ isosurface(vol, isovalue=None, step=1, useclassic=False, usevalues=False)
    
    Calculate the isosurface for the given 3D image. 
    Returns a vv.BaseMesh object.
    
    Parameters
    ----------
    vol : 3D numpy array
        The volume for which to calculate the isosurface.
    isovalue : float
        The value at which the surface should be created. If not given or None, 
        the average of the min and max of vol is used.
    step : int
        The stepsize for stepping through the volume. Larger steps yield
        faster but coarser results. The result shall always be topologically
        correct though.
    useClassic : bool
        If True, uses the classic marching cubes by Lorensen (1987) is used.
        This algorithm has many ambiguities and is not guaranteed to produce
        a topologically correct result.
    useValues : bool
        If True, the returned BaseMesh object will also have a value for
        each vertex, which is relates to the maximum value in a local region
        near the isosurface. In some situations this allows discerning
        sharp edges from smooth ones.
    
    
    Notes about the algorithm
    -------------------------
    
    This is an implementation of:
        
        Efficient implementation of Marching Cubes' cases with topological guarantees.
        Thomas Lewiner, Helio Lopes, Antonio Wilson Vieira and Geovan Tavares.
        Journal of Graphics Tools 8(2): pp. 1-15 (december 2003)
    
    The algorithm is an improved version of Chernyaev's Marching Cubes 33
    algorithm, originally written in C++. It is an efficient algorithm
    that relies on heavy use of lookup tables to handle the many different 
    cases. This keeps the algorithm relatively easy. The current algorithm
    is a port of Lewiner's algorithm in Cython.
    
    Although a lot of care was taken to reduce the risk of introducing errors
    during the porting process, this code should be taken as is and in no
    event shall any of its authors be liable for any damage (see also the
    visvis license).
    
    """ 
    
    # Check image
    if not isinstance(im, np.ndarray) or (im.ndim != 3):
        raise ValueError('vol should be a 3D numpy array.')
    
    # Make sure its 32 bit float
    if im.dtype != np.float32:
        im = im.astype('float32')
        
    # Get isovalue
    if isovalue is None:
        isovalue = 0.5 * (im.min() + im.max())
    isovalue = float(isovalue) # Will raise error if not float-like value given
    
    # Check steps
    step = int(step)
    if step < 1:
        raise ValueError('step must be at least one.')
    
    # Remaining args
    useclassic = bool(useclassic)
    usevalues = bool(usevalues)
    
    # Get LutProvider class (reuse if possible) 
    L = _getMCLuts()
    
    # Apply algorithm
    vertices, faces , normals, values = marchingcubes_.marching_cubes(im, isovalue, L, step, useclassic)
    
    # Done
    if usevalues:
        return vv.BaseMesh(vertices, faces, normals, values)
    else:
        return vv.BaseMesh(vertices, faces, normals)



def _toArray(args):
    shape, text = args
    byts = base64decode(text.encode('utf-8'))
    ar = np.frombuffer(byts, dtype='int8')
    ar.shape = shape
    return ar

def _getMCLuts():
    """ Kind of lazy obtaining of the luts.
    """ 
    if not hasattr(mcluts, 'THE_LUTS'):
        
        mcluts.THE_LUTS = marchingcubes_.LutProvider(
                EDGETORELATIVEPOSX, EDGETORELATIVEPOSY, EDGETORELATIVEPOSZ, 
                
                _toArray(mcluts.CASESCLASSIC), _toArray(mcluts.CASES),
                
                _toArray(mcluts.TILING1), _toArray(mcluts.TILING2), _toArray(mcluts.TILING3_1), _toArray(mcluts.TILING3_2), 
                _toArray(mcluts.TILING4_1), _toArray(mcluts.TILING4_2), _toArray(mcluts.TILING5), _toArray(mcluts.TILING6_1_1),
                _toArray(mcluts.TILING6_1_2), _toArray(mcluts.TILING6_2), _toArray(mcluts.TILING7_1), 
                _toArray(mcluts.TILING7_2), _toArray(mcluts.TILING7_3), _toArray(mcluts.TILING7_4_1), 
                _toArray(mcluts.TILING7_4_2), _toArray(mcluts.TILING8), _toArray(mcluts.TILING9), 
                _toArray(mcluts.TILING10_1_1), _toArray(mcluts.TILING10_1_1_), _toArray(mcluts.TILING10_1_2), 
                _toArray(mcluts.TILING10_2), _toArray(mcluts.TILING10_2_), _toArray(mcluts.TILING11), 
                _toArray(mcluts.TILING12_1_1), _toArray(mcluts.TILING12_1_1_), _toArray(mcluts.TILING12_1_2), 
                _toArray(mcluts.TILING12_2), _toArray(mcluts.TILING12_2_), _toArray(mcluts.TILING13_1), 
                _toArray(mcluts.TILING13_1_), _toArray(mcluts.TILING13_2), _toArray(mcluts.TILING13_2_), 
                _toArray(mcluts.TILING13_3), _toArray(mcluts.TILING13_3_), _toArray(mcluts.TILING13_4), 
                _toArray(mcluts.TILING13_5_1), _toArray(mcluts.TILING13_5_2), _toArray(mcluts.TILING14),
                
                _toArray(mcluts.TEST3), _toArray(mcluts.TEST4), _toArray(mcluts.TEST6), 
                _toArray(mcluts.TEST7), _toArray(mcluts.TEST10), _toArray(mcluts.TEST12), 
                _toArray(mcluts.TEST13), _toArray(mcluts.SUBCONFIG13),
                )
    
    return mcluts.THE_LUTS

