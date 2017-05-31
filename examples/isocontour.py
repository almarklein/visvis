#!/usr/bin/env python
""" This example illustrates how to create an isocontour from an image
and display it over the contour. The contour consists of a pointset
in which each 2 subsequent points describe a linepiece.

This code relies on scikit-image. For a possibly more useful representation
of the contour, see skimage.measure.find_contours.
"""

import visvis as vv

im = vv.imread('imageio:chelsea.png')[:,:,1]
pp = vv.isocontour(im)

vv.figure(1)
vv.clf()
vv.imshow(im)
vv.plot(pp, ls='+', lw=2)

vv.title('Isocontour')
app = vv.use()
app.Run()
