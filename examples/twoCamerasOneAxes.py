#!/usr/bin/env python
""" This example demonstrates how one can use two of the same cameras
on the same axes.

The axes keeps a list of cameras, and only allows one camera of each type.
Therefore, in order to have two of the same cameras, we need to subclass it.

Note that in this example, there are actually 3 TwoDCamera's, as the original
is also still available (on index 2).
"""

import visvis as vv

class OurCamera1(vv.cameras.TwoDCamera):
    _NAMES = ('our1', 8)
    # a string name to be able to set cameraType
    # an int so it has an index, allowing changing the camera via a shortcut

class OurCamera2(vv.cameras.TwoDCamera):
    _NAMES = ('our2', 9)

# Draw an image
im = vv.imread('astronaut.png')
vv.imshow(im)
vv.title('Press ALT+8 for cam1 and ALT+9 for cam2')

# Get axes
a = vv.gca()

# Add cameras and select the first
a.camera = OurCamera1()
a.camera = OurCamera2()
a.cameraType = 'our1' # We can do this because we set the _NAMES attribute

# Increase zoom
a.camera.zoom *= 2

# Enter mainloop
app = vv.use()
app.Run()
