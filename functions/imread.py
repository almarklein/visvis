# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np
import os

# Try importing imageio or PIL
imageio = None
PIL = None
#
try:
    import imageio
except ImportError:
    try:
        import PIL.Image
    except ImportError:
        pass



def imread(filename):
    """ imread(filename) 
    
    Read image from a file, requires PIL. 
    
    """
    
    if imageio is None and PIL is None:
        raise RuntimeError("visvis.imread requires the imageio or PIL package.")
    
    if not os.path.isfile(filename):
        # try loadingpil from the resource dir
        path = vv.misc.getResourceDir()
        filename2 = os.path.join(path, filename)
        if os.path.isfile(filename2):
            filename = filename2
        else:
            raise IOError("Image '%s' does not exist." % filename)
    
    if imageio:
        # Get image as a numpy array
        a = imageio.imread(filename)
    
    elif PIL:
        # Get Pil image and convert if we need to
        im = PIL.Image.open(filename)
        if im.mode == 'P':
            im = im.convert()
        # Make numpy array
        a = np.asarray(im)
        if len(a.shape)==0:
            raise MemoryError("Too little memory to convert PIL image to array")
        # cleanup
        del im
    
    return a
