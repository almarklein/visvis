# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import numpy as np


class BarDescription:
    def __init__(self, sze):
        self.i = int(np.random.uniform(0,sze))
        self.j = int(np.random.uniform(0,sze))
        self.k1 = int(np.random.uniform(0,sze/3))
        self.k2 = int(np.random.uniform(0,sze/3))
        self.w1 = int(np.random.uniform(1,10))
        self.w2 = int(np.random.uniform(1,10))
        self.value = np.random.uniform(0,1)


def aVolume(N=5, size=64):
    """ aVolume(N=5, size=64)
    
    Creates a volume (3D image) with random bars.
    The returned numpy array has values between 0 and 1.
    Intended for quick illustration and test purposes.
    
    Parameters
    ----------
    N : int
        The number of bars for each dimension.
    size : int
        The size of the volume (for each dimension).
    
    """
    
    # Create volume
    vol = np.zeros((size,size,size), dtype=np.float32)

    # Make bars
    for iter in range(N):
        # x
        b = BarDescription(size)
        vol[ b.i-b.w1:b.i+b.w1, b.j-b.w2:b.j+b.w2, b.k1:-b.k2 ] += b.value
        # y
        b = BarDescription(size)
        vol[ b.i-b.w1:b.i+b.w1, b.k1:-b.k2, b.j-b.w2:b.j+b.w2 ] += b.value
        # z
        b = BarDescription(size)
        vol[ b.k1:-b.k2, b.i-b.w1:b.i+b.w1, b.j-b.w2:b.j+b.w2 ] += b.value

    # Clip and return
    vol[vol>1.0]=1.0
    return vol


if __name__ == '__main__':
    vol = vv.aVolume()
    t = vv.volshow(vol)
    t.renderStyle = 'mip' # maximum intensity projection (is the default)
