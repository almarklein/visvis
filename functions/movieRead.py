# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import os
import visvis as vv

# Try importing imageio
imageio = None

try:
    import imageio
except ImportError:
    pass


def movieRead(filename, *args, **kwargs):
    """ Proxy for imageio.mimread()
    """
    
    if imageio is None:
        raise RuntimeError("visvis.movieRead requires the imageio package.")
    
    if not os.path.isfile(filename):
        # try loadingpil from the resource dir
        path = vv.misc.getResourceDir()
        filename2 = os.path.join(path, filename)
        if os.path.isfile(filename2):
            filename = filename2
    
    return imageio.mimread(filename, *args, **kwargs)


if __name__ == '__main__':
    ims = vv.movieRead('newtonscradle.gif')
    vv.movieShow(ims)
