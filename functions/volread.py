# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
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
    
    # Try loading our base volume(s)
    if filename == 'stent':
        path = vv.misc.getResourceDir()
        filename2 = os.path.join(path, 'stent_vol.ssdf')
        if os.path.isfile(filename2):
            filename = filename2
            s = vv.ssdf.load(filename)
            return s.vol.astype('int16') * s.colorscale
    
    # Use imageio (can also load from http, etc)
    if imageio is None:
        raise RuntimeError("visvis.volread needs the imageio package to read arbitrary files.")
    return imageio.volread(filename)


if __name__ == '__main__':
    vol = vv.volread('stent')
    t = vv.volshow(vol)
    t.renderStyle = 'mip' # maximum intensity projection (is the default)
