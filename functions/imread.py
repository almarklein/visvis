import visvis as vv
import numpy as np
import os

try:
    import PIL.Image
except ImportError:
    PIL = None

def imread(filename):
    """ imread(filename) 
    Read image from disk, requires PIL. 
    """
    
    if PIL is None:
        raise RuntimeError("visvis.imread requires the PIL package.")
    
    if not os.path.isfile(filename):
        # try loading from the resource dir
        path = vv.misc.getResourceDir()
        filename2 = os.path.join(path, filename)
        if os.path.isfile(filename2):
            filename = filename2
        else:
            raise IOError("Image '%s' does not exist." % filename)
    
    im = PIL.Image.open(filename)
    a = np.asarray(im)
    if len(a.shape)==0:
        raise MemoryError("Too little memory to convert PIL image to array")
    
    del im
    return a
    