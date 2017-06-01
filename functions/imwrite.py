# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

# Try importing imageio
imageio = None

try:
    import imageio
except ImportError:
    pass


def imwrite(filename, image, format=None):
    """ imwrite(filename, image, format=None)
    
    Write image (numpy array) to file, requires imageio.
    
    Parameters
    ----------
    filename : string
        The name of the file to store the screenshot to. If filename is None,
        the interpolated image is returned as a numpy array.
    image : numpy array
        The image to write.
    format : string
        The format for the image to be saved in. If not given, the
        format is deduced from the filename.
    
    Notes
    -----
      * For floating point images, 0 is considered black and 1 is white.
      * For integer types, 0 is considered black and 255 is white.
    
    """
    
    if imageio is None:
        raise RuntimeError("visvis.imwrite requires the imageio package.")
    
    imageio.imwrite(filename, image, format)


if __name__ == '__main__':
    im = vv.imread('astronaut.png')
    vv.imwrite('astronaut_new.jpg', im)
