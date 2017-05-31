#!/usr/bin/env python

import numpy as np
import visvis as vv

# Read image and crop
astro = vv.imread('astronaut.png').astype(np.float32)
astro = astro[100:-100,100:-100, :]

# Smooth a bit
im = astro.copy()
im[1:,:,:] = astro[:-1,:,:]
im[:-1,:,:] += astro[1:,:,:]
im[:,:-1,:] += astro[:,1:,:]
im[:,1:,:] += astro[:,:-1,:]
im /= 4

# Prepare figure
vv.figure()

# Without color, with colormap
a1 = vv.subplot(121)
m1 = vv.surf(im[:,:,0])
m1.colormap = vv.CM_HOT
vv.title('With colormap')

# With color
a2 = vv.subplot(122)
m2 = vv.surf(im[:,:,0], im)
vv.title('With original texture')

# Flip y-axis, otherwise the image is upside down
a1.daspect = 1,-1,1
a2.daspect = 1,-1,1

# Enter mainloop
app=vv.use()
app.Run()
