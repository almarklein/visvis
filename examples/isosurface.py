#!/usr/bin/env python
""" This example illustrates how to create an isosurface from a volume
and display it. This code relies on scikit-image.
"""

import visvis as vv
from visvis.utils.iso import isosurface  # Note: this imports skimage

vol = vv.volread('stent')  # a standard visvis volume
mesh = isosurface(vol)  # returns a visvis BaseMesh object

vv.figure(1)
vv.clf()
vv.volshow2(vol)
m = vv.mesh(mesh)
m.faceColor = (0, 1, 1)
