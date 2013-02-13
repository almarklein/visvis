# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np
import os


def volread(filename):
    """ volread(filename) 
    
    Read volume from a file. Currently this only reads a dedicated
    dataset. In the future this will use imageio and support various
    volumetric formats.
    
    """
    
    if filename != 'stent':
        raise ValueError('Only "stent" is supported as an argument to volread for now.')
    
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
    

if __name__ == '__main__':
    vol = vv.volread('stent')
    t = vv.volshow(vol)
    t.renderStyle = 'mip' # maximum intensity projection (is the default) 
