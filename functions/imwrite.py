""" Write an image to disk (requires PIL). """

import numpy as np

try:
    import PIL.Image
except ImportError:
    PIL = None

def imwrite(filename, image):
    """ imwrite(filename, image)
    Write image to disk, requires PIL. 
    For floating point images, 0 is considered black and 1 is white.
    For integer types, 0 is considered black and 255 is white.
    """
    
    if PIL is None:
        raise RuntimeError("visvis.imwrite requires the PIL package.")
    
    # check image
    if len(image.shape) == 2:
        pass # grayscale
    elif len(image.shape) == 3:
        if image.shape[2] == 3:
            pass # RGB
        else:
            raise ValueError("Cannot write image: To many values in third dim.")
    else:
        raise ValueError("Cannot write image: Invalid number of dimensions.")
    
    # check type -> convert
    if image.dtype.name == 'uint8':
        pass # ok
    elif image.dtype.name in ['float32', 'float64']:
        image = (image*255).astype(np.uint8)
    else:
        image = image.astype(np.uint8)
    
    # write image
    pim = PIL.Image.fromarray(image)
    pim.save(filename)
    
    