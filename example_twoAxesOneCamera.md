# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_twoAxesOneCamera.gif](http://wiki.visvis.googlecode.com/hg/images/examples/example_twoAxesOneCamera.gif)

```
#!/usr/bin/env python

""" This example shows how to use the same camera for multiple axes, 
which can be helpful if for example the axes show a different view 
on the same data.
"""

import visvis as vv
app = vv.use()

# Read lena
im1 = vv.imread('lena.png')

# Our second image is a thresholded image
im2 = im1 > 100

# Create figure with two axes
vv.figure()
a1 = vv.subplot(121)
a2 = vv.subplot(122)

# Create new camera and attach
cam = vv.cameras.TwoDCamera()
a1.camera = a2.camera = cam

# Draw images
vv.imshow(im1, axes=a1)
vv.imshow(im2, axes=a2)

app.Run()

```