#!/usr/bin/env python
""" This example illustrates how to create an isosurface from a volume
and display it. This code relies on scikit-image.
"""

import visvis as vv

vol = vv.volread('stent')  # a standard visvis volume
mesh = vv.isosurface(vol)  # returns a visvis BaseMesh object

vv.figure(1)
vv.clf()
vv.volshow2(vol)
m = vv.mesh(mesh)
m.faceColor = (0, 1, 1)


vv.title('Isosurface')
app = vv.use()
app.Run()
