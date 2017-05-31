#!/usr/bin/env python

import visvis as vv
app = vv.use()

# Get green channel of lena image
im = vv.imread('astronaut.png')[:,:,1]

# Make 4 subplots with different colormaps
cmaps = [vv.CM_GRAY, vv.CM_JET, vv.CM_SUMMER, vv.CM_HOT]
for i in range(4):
    a = vv.subplot(2,2,i+1)
    t = vv.imshow(im, clim=(0,255))
    a.axis.visible = 0
    t.colormap = cmaps[i]
    vv.colorbar()

app.Run()
