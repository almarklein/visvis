#!/usr/bin/env python
""" This example shows hoe the GLSL program for a 2D texture 
can be modified to achieve all kinds of graphic effects.
In this example we will demonstrate showing the edges of an image.
Also see the unsharpMasking example.
"""

import visvis as vv
import numpy as np

# First define our part of the shading code
# >>XXX>> denotes a code section; this section is inserted in shader code
# at the right spot. 
# 
# In this example we change the in-loop section, which is inserted in the
# convolution loop for anti-aliasing. The code part shown below will replace
# the default in-loop part. The default just samples the color from the 
# texture. We will sample the derivatives from the texture, and use them
# to calculate the gradient magnitude.
#
# Note that in contrast to the unsharp masking example, this example leaves
# the anti-aliasing in place, so we can zoom out without the edges flickering.
SH_2F_STYLE_EDGE = """
    >>in-loop>>
    vec2 dposx = vec2(dx, 0.0);
    vec2 dposy = vec2(0.0, dy);
    vec4 gradx = texture2D(texture, pos+dpos+dposx) - texture2D(texture, pos+dpos-dposx);
    vec4 grady = texture2D(texture, pos+dpos+dposy) - texture2D(texture, pos+dpos-dposy);
    vec4 tmpColor = gradx*gradx + grady*grady;
    tmpColor = sqrt(tmpColor);
    tmpColor.a = texture2D(texture, pos+dpos).a;
    color1 += tmpColor * k;
"""

# Read image
im = vv.imread('lena.png')

# Show two times, the second will be sharpened
t = vv.imshow(im)

# Insert our part in the fragment shader program
t.fragmentShader.ReplacePart('style', SH_2F_STYLE_EDGE)
if False: # Use this line to switch back:
    t.fragmentShader.ReplacePart('style', vv.shaders.SH_2F_STYLE_NORMAL)

# Run app
app = vv.use()
app.Run()
