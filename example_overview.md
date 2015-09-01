# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_overview.gif](http://wiki.visvis.googlecode.com/hg/images/examples/example_overview.gif)

```
#!/usr/bin/env python
import visvis as vv

# Create figure and make it wider than the default
fig = vv.figure()
fig.position.w = 700


# Create first axes
a1 = vv.subplot(121)

# Display an image
im = vv.imread('lena.png') # returns a numpy array
texture2d = vv.imshow(im)
texture2d.interpolate = True # if False the pixels are visible when zooming in

# Display two lines (values obtained via vv.ginput())
x = [220, 258, 308, 336, 356, 341, 318, 311, 253, 225, 220]
y = [287, 247, 212, 201, 253, 318, 364, 385, 382, 358, 287]
line1 = vv.plot(x, y, ms='.', mw=4, lw=2)
#
x = [237, 284, 326, 352, 381, 175, 195, 217, 232, 237]
y = [385, 386, 394, 413, 507, 507, 476, 441, 399, 385]
line2 = vv.plot(x, y, ms='s', mw=4, lw=2)

# The appearance of the line objects can be set in their
# constructor, or by using their properties
line1.lc, line1.mc = 'g', 'b'
line2.lc, line2.mc = 'y', 'r'

# Display a legend
a1.legend = "Lena's face", "Lena's shoulder"


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

```

The structure of the objects in the figure is illustrated by the image below.
Note that the text objects for the axis and legend are also children of
the respective objects, but have been left out of the image for clarity. World
objects are shown in blue.

![http://wiki.visvis.googlecode.com/hg/images/graph_structure.png](http://wiki.visvis.googlecode.com/hg/images/graph_structure.png)
