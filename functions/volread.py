# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np
import os


# Try importing imageio
imageio = None
try:
    import imageio
except ImportError:
    pass


def volread(filename):
    """ volread(filename) 
    
    Read volume from a file. If filename is 'stent', read a dedicated
    test dataset. For reading any other kind of volume, the imageio
    package is required.
    
    """
    
    if filename == 'stent':
        # Get full filename
        path = vv.misc.getResourceDir()
        filename2 = os.path.join(path, 'stent_vol.ssdf')
        if os.path.isfile(filename2):
            filename = filename2
        else:
            raise IOError("File '%s' does not exist." % filename)
        # Load
        s = vv.ssdf.load(filename)
        return s.vol.astype('int16') * s.colorscale
    
    elif imageio is not None:
        return imageio.volread(filename)
        
    else:
        raise RuntimeError("visvis.volread needs the imageio package to read arbitrary files.")
        


if __name__ == '__main__':
    vol = vv.volread('stent')
    t = vv.volshow(vol)
    t.renderStyle = 'mip' # maximum intensity projection (is the default) 
