#!/usr/bin/env python
import visvis as vv

# Create figure and make it wider than the default
fig = vv.figure()
fig.position.w = 700

# Create first axes
a1 = vv.subplot(121)

# Display an image
im = vv.imread('astronaut.png') # returns a numpy array
texture2d = vv.imshow(im)
texture2d.interpolate = True # if False the pixels are visible when zooming in

# Display two lines (values obtained via vv.ginput())
x = [182, 180, 161, 153, 191, 237, 293, 300, 272, 267, 254]
y = [145, 131, 112, 59, 29, 14, 48, 91, 136, 137, 172]
line1 = vv.plot(x, y, ms='.', mw=4, lw=2)
#
x = [507, 498, 483, 438, 364, 299, 278, 280]
y = [483, 452, 389, 349, 347, 393, 448, 508]
line2 = vv.plot(x, y, ms='s', mw=4, lw=2)

# The appearance of the line objects can be set in their
# constructor, or by using their properties
line1.lc, line1.mc = 'g', 'b'
line2.lc, line2.mc = 'y', 'r'

# Display a legend
a1.legend = "Astronaut's face", "Astronaut's helmet"


# Create second axes (with a black background)
a2 = vv.subplot(122)
a2.bgcolor = 'k'
a2.axis.axisColor = 'w'

# Display a texture
vol = vv.aVolume(2) # returns a test volume as a numpy array
texture3d = vv.volshow(vol)

# Display a mesh using one of the "solid" functions
mesh = vv.solidTeapot((32,32,80), scaling=(50,50,50))
mesh.faceColor = 0.4, 1, 0.4
mesh.specular = 'r'

# Set orthographic projection
a2.camera.fov = 45

# Create labels for the axis
a2.axis.xLabel = 'x-axis'
a2.axis.yLabel = 'y-axis'
a2.axis.zLabel = 'z-axis'

# Enter main loop
app = vv.use() # let visvis chose a backend for me
app.Run()
