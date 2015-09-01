# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_transparantTextures.png](http://wiki.visvis.googlecode.com/hg/images/examples/example_transparantTextures.png)

```
#!/usr/bin/env python

""" This example illustrates using transparant textures. This can be used,
for example to overlay a segmentation result over an original image.

Note that the alpha value is always asumed between 0 and 1, so a
transparant texture should always be of float type.
"""

import visvis as vv
import numpy as np
app = vv.use()

# Lena is our original image
vv.clf()
im = vv.imread('lena.png')

# Find the regions where there's relatively much blue
mask = (im[:,:,0] < 200) & (im[:,:,2]>0.7*im[:,:,0])

# Create an RGBA texture and fill in the found region in blue
mask2 = np.zeros(mask.shape+(4,), dtype=np.float32)
mask2[:,:,2] = mask
mask2[:,:,3] = mask * 0.5

# Add a black, green, red, and yellow region in the corner
mask2[100:200,:200,0] = 1.0
mask2[:200,100:200,1] = 1.0
mask2[:200,:200,3] = 0.5
  
# Show image and mask
t1=vv.imshow(im)
t2=vv.imshow(mask2)

app.Run()

```