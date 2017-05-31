#!/usr/bin/env python
""" This example shows all mesh objects that can be created out of the box.
It also shows the different techniques to apply color to the meshes using
plain color, colormaps and texture.

On the website, this example also demonstrates the fly camera to fly through
the mesh objects.

"""

import numpy as np
import visvis as vv
from visvis import Point, Pointset
vv.figure()
a = vv.gca()

# Define points for the line
pp = Pointset(3)
pp.append(0,0,0); pp.append(0,1,0); pp.append(1,2,0); pp.append(0,2,1)

# Create all solids
box = vv.solidBox((0,0,0))
sphere = vv.solidSphere((3,0,0))
cone = vv.solidCone((6,0,0))
pyramid = vv.solidCone((9,0,0), N=4) # a cone with 4 faces is a pyramid
cylinder = vv.solidCylinder((0,3,0),(1,1,2))
ring = vv.solidRing((3,3,0))
teapot = vv.solidTeapot((6,3,0))
line = vv.solidLine(pp+Point(9,3,0), radius = 0.2)

# Let's put a face on that cylinder
# This works because 2D texture coordinates are automatically generated for
# the sphere, cone, cylinder and ring.
im = vv.imread('astronaut.png')
cylinder.SetTexture(im)

# Make the ring green
ring.faceColor = 'g'

# Make the sphere dull
sphere.specular = 0
sphere.diffuse = 0.4

# Show lines in yellow pyramid
pyramid.faceColor = 'y'
pyramid.edgeShading = 'plain'

# Colormap example
N = cone._vertices.shape[0]
cone.SetValues( np.linspace(0,1,N) )
cone.colormap = vv.CM_JET

# Show title and enter main loop
vv.title('All mesh objects that can be created out of the box')
app = vv.use()
app.Run()
