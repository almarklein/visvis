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


def imread(filename):
    """ imread(filename)
    
    Read image from file or http, requires imageio.
    
    """
    
    if imageio is None:
        raise RuntimeError("visvis.imread requires the imageio package.")
    
    if not os.path.isfile(filename) and '//' not in filename:
        # try loading from the resource dir
        path = vv.misc.getResourceDir()
        filename2 = os.path.join(path, filename)
        if os.path.isfile(filename2):
            filename = filename2
        else:
            pass  # imageio can read from http and more ...
    
    return imageio.imread(filename)


if __name__ == '__main__':
    im = vv.imread('astronaut.png')
    t = vv.imshow(im)
