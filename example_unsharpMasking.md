# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_unsharpMasking.gif](http://wiki.visvis.googlecode.com/hg/images/examples/example_unsharpMasking.gif)

```
#!/usr/bin/env python
""" This example shows hoe the GLSL program for a 2D texture 
can be modified to achieve all kinds of graphic effects.
In this example we will demonstrate sharpening an image using
unsharp masking.
"""

import visvis as vv
import numpy as np

# First define our part of the shading code
# The '>>' Denote what piece of code we want to replace.  
# There is a pre-loop section, that is executed before the anti-aliasing
# loop. We use this to modify the aliasing kernel so it always does a fixed
# amount of smoothing.
# In the post-loop section we combine the subtracted image with the normal
# sampled image. Unsharp masking consists of subtracting the smoothed image
# from the original (thus removing low frequency components), and then adding
# the result with a certain factor to the original.
#
# Note that the aa kernel is symetric; kernel[0] is the center pixel, and
# kernel[1] through kernel[3] is the tail on all ends.
SH_2F_SHARPEN = vv.shaders.ShaderCodePart('sharpen','unsharp masking',
"""
    >>--uniforms--
    uniform float amount;
    // --uniforms--
    
    >>--pre-loop--
    sze = 3; // Use full kernel (otherwise it wont work if t.aa == 0)
    kernel = vec4(1.0, 0.9, 0.6, 0.3); // approximate Gauss of sigma 2
    float kernel_norm = kernel[0] + (kernel[1] + kernel[2] + kernel[3])*2.0;
    kernel /= kernel_norm;
    // --pre-loop--
    
    >>--post-loop--
    float th = 0.05;
    vec4 normalColor = texture2D(texture, pos);
    // Element-wise mask on blurred image (color1), using a threshold    
    float mask = float(length(color1.rgb)-length(color2.rgb)>th);
    normalColor.rgb += mask * amount * (normalColor.rgb -color1.rgb);
    color1 = normalColor;
    // --post-loop--    
""")

# Read image
im = vv.imread('lena.png')

# Show two times, the second will be sharpened
vv.subplot(121); t1 = vv.imshow(im)
vv.subplot(122); t2 = vv.imshow(im)

# Share cameras and turn off anti-aliasing for proper comparison
t1.parent.camera = t2.parent.camera
t1.aa = 0

# Insert our part in the fragment shader program
t2.shader.fragment.AddOrReplace(SH_2F_SHARPEN, after='base')
if False: # Execute this line to turn it off:
    t2.shader.fragment.RemovePart('sharpen')

# Make a slider to set the amount
def sliderCallback(event):
    t2.shader.SetStaticUniform('amount', slider.value)
    t2.Draw()
slider = vv.Slider(t2.parent, (0.0, 1.5))
slider.position = 0.05, 10, 0.9, 40
slider.eventSliding.Bind(sliderCallback)
sliderCallback(None) # init uniform

# In case there are bugs in the code, it might be helpfull to see the code
# t2.fragmentShader.ShowCode() # Shows the whole code
t2.shader.fragment.ShowCode('sharpen') # Shows only our bit, with line numbers

# Run app
app = vv.use()
app.Run()

```