#!/usr/bin/env python
""" This example shows hoe the GLSL program for a 2D texture
can be modified to achieve all kinds of graphic effects.
In this example we will demonstrate showing the edges of an image.
Also see the unsharpMasking example.
"""

import visvis as vv

# First define our part of the shading code
# The '>>' Denote what piece of code we want to replace. We replace the
# standard texture lookup for one that samples the derivatives, and use them
# to calculate the gradient magnitude.
#
# Note that in contrast to the unsharp masking example, this example leaves
# the anti-aliasing in place, so we can zoom out without the edges flickering.
SH_2F_EDGE = vv.shaders.ShaderCodePart('edge', 'gradient magnitude',
"""
    >>color1 += texture2D(texture, pos+dpos) * k;
    vec2 dposx = vec2(dx, 0.0);
    vec2 dposy = vec2(0.0, dy);
    vec4 gradx = texture2D(texture, pos+dpos+dposx) - texture2D(texture, pos+dpos-dposx);
    vec4 grady = texture2D(texture, pos+dpos+dposy) - texture2D(texture, pos+dpos-dposy);
    vec4 tmpColor = gradx*gradx + grady*grady;
    tmpColor = sqrt(tmpColor);
    tmpColor.a = texture2D(texture, pos+dpos).a;
    color1 += tmpColor * k;
""")

# Read image
im = vv.imread('astronaut.png')

# Show two times, the second will be sharpened
t = vv.imshow(im)

# Insert our part in the fragment shader program
t.shader.fragment.AddPart(SH_2F_EDGE)
if False: # Use this line to switch back:
    t.shader.fragment.RemovePart(SH_2F_EDGE)

# In case there are bugs in the code, it might be helpfull to see the code
# t.shader.fragment.ShowCode() # Shows the whole code
t.shader.fragment.ShowCode('edge') # Shows only our bit, with line numbers

# Run app
app = vv.use()
app.Run()
