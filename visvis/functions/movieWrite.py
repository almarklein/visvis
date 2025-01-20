# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

# Try importing imageio
iio = None

try:
    import imageio
    if hasattr(imageio, "v2"):
        iio = imageio.v2
    else:
        iio = imageio
except ImportError:
    pass


def movieWrite(filename, images, *args, **kwargs):
    """ Proxy for imageio.mimwrite()
    """

    if iio is None:
        raise RuntimeError("visvis.movieWrite requires the imageio package.")

    return iio.mimwrite(filename, images, *args, **kwargs)


if __name__ == '__main__':
    ims = vv.movieRead('newtonscradle.gif')
    vv.movieWrite('newtonscradle.swf', ims)
