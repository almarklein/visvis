# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np
import os

try:
    import PIL.Image
except ImportError:
    PIL = None

# todo: I'm not sure about the status of FreeImage.
try:
    import FreeImage
except ImportError:
    FreeImage = None


def imread(filename):
    """ imread(filename) 
    
    Read image from a file, requires PIL. 
    
    """
    
    if PIL is None and FreeImage is None:
        raise RuntimeError("visvis.imread requires the PIL package.")
    
    if not os.path.isfile(filename):
        # try loadingpil from the resource dir
        path = vv.misc.getResourceDir()
        filename2 = os.path.join(path, filename)
        if os.path.isfile(filename2):
            filename = filename2
        else:
            raise IOError("Image '%s' does not exist." % filename)
    
    if PIL:
        # Get Pil image and convert if we need to
        im = PIL.Image.open(filename)
        if im.mode == 'P':
            im = im.convert()
        
        # Make numpy array
        a = np.asarray(im)
        if len(a.shape)==0:
            raise MemoryError("Too little memory to convert PIL image to array")
        
        del im
    
    elif FreeImage:
        # Get image as a numpy array
        im = FreeImage.read(filename)
        
        # Reshape, because FreeImage uses fortran indices, arg!
        if im.ndim == 2:
            a = im.T.copy()
        else:
            s = im.shape[1:] + (im.ndim,)
            a = np.zeros(s, im.dtype)
            for i in range(im.ndim):
                a[:,:,i] = im[i,:,:].T
        
        del im
    
    return a
