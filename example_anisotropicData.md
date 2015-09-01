# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_anisotropicData.png](http://wiki.visvis.googlecode.com/hg/images/examples/example_anisotropicData.png)

```
#!/usr/bin/env python
import visvis as vv
from visvis import Aarray
app = vv.use()

# Let's say we have lena, but only the even pixels in the y dimension.
# So each pixel should have twice the size in the y direction.
im = vv.imread('lena.png')
im = im[::2,:,:]

# Init a figure with two axes
vv.figure()
a1 = vv.subplot(121); vv.title('pixel units')
a2 = vv.subplot(122); vv.title('real-world units')

# Method 1: scale the whole scene
# Use this if you want the axis to depict pixel units.
t1 = vv.imshow(im, axes=a1)
a1.daspect = 1,-2 # daspect works x,y,z, the y-axis is flipped for images

# Method 2: use the Aarray class to scale the image
# You could use this is you know the physical dimensions of a pixel,
# to have the axis depict, for example, mm.
im2 = Aarray(im,(2,1,1))  # sampling is given in y,x,color order
t2 = vv.imshow(im2, axes=a2)

app.Run()

```