# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import numpy as np

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


def imwrite(filename, image, format=None):
    """ imwrite(filename, image, format=None)
    
    Write image (numpy array) to file, requires PIL. 
    
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
    
    if imageio is None and PIL is None:
        raise RuntimeError("visvis.imwrite requires the imageio or PIL package.")
    
    # check image
    if len(image.shape) == 2:
        pass # grayscale
    elif len(image.shape) == 3:
        if image.shape[2] == 3:
            pass # RGB
        else:
            raise ValueError("Cannot write image: Too many values in third dim.")
    else:
        raise ValueError("Cannot write image: Invalid number of dimensions.")
    
    # check type -> convert
    if image.dtype.name == 'uint8':
        pass # ok
    elif image.dtype.name in ['float32', 'float64']:
        image = image.copy()
        image[image<0] = 0
        image[image>1] = 1
        image = (image*255).astype(np.uint8)
    else:
        image = image.astype(np.uint8)
    
    # write image
    if imageio:
        imageio.imsave(filename, image, format)
    elif PIL:
        pim = PIL.Image.fromarray(image)
        pim.save(filename, format)
