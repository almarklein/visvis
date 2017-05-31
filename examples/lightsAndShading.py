#!/usr/bin/env python
""" This example illustrate different ways to shade mesh objects and
shows an example with lighting. Two light sources are created and
the diffuse reflection of the objects is varied.
"""

import visvis as vv
vv.figure()

# Define shadings to apply, and numbef of steps for diffuse reflection
shading = [ ('plain', None), ('flat', None), ('smooth', None),
            ('smooth', 'plain'), (None, 'smooth')]
ndiffuse = 4


# Init two lights (you should thus see two specular spots)
# Please experiment with the values below to see the effect!

# light0 is always on, and is attached to the camera shining straight ahead
a = vv.gca()
a.light0.ambient = 0.2 # 0.2 is default for light 0
a.light0.diffuse = 1.0 # 1.0 is default

# The other lights are off by default and are positioned at the origin
light1 = a.lights[1]
light1.On()
light1.ambient = 0.0 # 0.0 is default for other lights
light1.color = (1,0,0) # this light is red


# Create spheres
for i in range(len(shading)):
    for j in range(ndiffuse):
        s = vv.solidSphere((i,j,0), (0.3, 0.3, 0.3))
        s.faceShading, s.edgeShading = shading[i]
        s.faceColor = (0.8,0.8,1.0)
        s.edgeColor = (0.8,0.8,1.0)
        s.diffuse = float(j)/ndiffuse

# Set settings for axes
a = vv.gca()
a.axis.xTicks = [str(s) for s in shading]
a.axis.xLabel = 'face- and edgeshading'
a.axis.yTicks = [str(float(j)/ndiffuse) for j in range(ndiffuse)]
a.axis.yLabel = 'diffuse reflection'

# Set back bg
a.bgcolor = 'k'
a.axis.axisColor = 'w'

# Enter mainloop
app = vv.use()
app.Run()
