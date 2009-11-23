""" Read an image from disk (requires PIL). """

import numpy as np

try:
    import PIL.Image
except ImportError:
    PIL = None

def imread(filename):
    """ imread(filename) 
    Read image from disk, requires PIL. """
    
    if PIL is None:
        raise RuntimeError("visvis.imread requires the PIL package.")
    
    im = PIL.Image.open(filename)
    a = np.asarray(im)
    if len(a.shape)==0:
        raise MemoryError("Too little memory to convert PIL image to array")
    
    del im
    return a
    