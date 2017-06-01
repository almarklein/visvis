#!/usr/bin/env python
"""
This example illustrates the use of the Aarray class.
Particularly how the class is aware of slicing and adapts
the origin and sampling accordingly. Visvis uses the sampling
and origin of the Aarray instances to draw the image at the
correct scale and position.
"""

import visvis as vv
from visvis import Aarray
app = vv.use()

# Load image and make Aarray
im = vv.imread('astronaut.png')
im = Aarray(im)

# Cut in four pieces, but also change resolution using different step sizes
im1 = im[:300,:300]
im2 = im[300:,:300:7]
im3 = im[:300:5,300:]
im4 = im[300::4,300::4]

# Get an axes
a = vv.gca()

# Show all images
tt = []
for im in [im1, im2, im3, im4]:
    tt.append(vv.imshow(im))

# Note that some parts seem to stick out. This is because visvis
# renders data such that the pixel center is at the spefied position;
# larger pixels thus stick out more.

# Enter mainloop
app.Run()
