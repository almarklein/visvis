# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module shaders_2

Contains the source for various shaders for the Texture2D wobject,
divided in different parts.

The names consists of different parts, seperated by underscores:
  * SH: just to indicate its a shader
  * 2F, 3F, MF, 2V, 3V, MV: the kind of program, 2D/3D texture or mesh,
    vertex or fragment shader. May be left out for some generic parts (such
    as color)
  * part name: can be BASE, STYLE, or anything else really.
  * part name type: Optional. Some parts have alternatives,
    such as the STYLE part for 3D rendering techniques. Or the SHADING
    part for meshes

"""
from visvis.core.shaders import ShaderCodePart


## Color
# These are used by many shaders to be able to deal with scalar or RGB data.
# color1-to-val is used by volume renderes to test thresholds etc.
# color1-to-color2 is used to convert the color sampled from the texture to
# a color to be displayed on screen.

# This one is not really usefull, but included for completeness
SH_COLOR_SCALARNOCMAP = ShaderCodePart('color', 'scalar-nocmap',
"""
    >>--uniforms--
    uniform vec2 scaleBias;
    // --uniforms--
    
    >>--color1-to-val--
    val = color1.r;
    
    >>--color1-to-color2--
    color2.rgb = ( color1.r + scaleBias[1] ) * scaleBias[0];
    color2.a = 1.0;
""")

SH_COLOR_SCALAR = ShaderCodePart('color', 'scalar',
"""
    >>--uniforms--
    uniform sampler1D colormap;
    uniform vec2 scaleBias;
    // --uniforms--
    
    >>--color1-to-val--
    val = color1.r;
    
    >>--color1-to-color2--
    color2 = texture1D( colormap, (color1.r + scaleBias[1]) * scaleBias[0]);
""")

SH_COLOR_RGB = ShaderCodePart('color', 'RGB',
"""
    >>--uniforms--
    uniform vec2 scaleBias;
    // --uniforms--
    
    >>--color1-to-val--
    val = length(color1.rgb);
    
    >>--color1-to-color2--
    color2 = ( color1 + scaleBias[1] ) * scaleBias[0];
""")


## 2D fragment base
# Shows 2D texture and does anti-aliasing when image is zoomed out.

SH_2F_BASE = ShaderCodePart('base', '2D-fragment-default',
"""
    // Uniforms obtained from OpenGL
    uniform sampler2D texture; // The 3D texture
    uniform vec2 shape; // And its shape (as in OpenGl)
    uniform vec2 extent; // Extent of the data in world coordinates
    uniform vec4 aakernel; // The smoothing kernel for anti-aliasing
    // --uniforms--
    
    // Varyings obtained from vertex shader
    // --varyings--
    
    void main()
    {
        // Get centre location
        vec2 pos = gl_TexCoord[0].xy;
        
        // Init value
        vec4 color1 = vec4(0.0, 0.0, 0.0, 0.0);
        vec4 color2; // to set color later
        
        // Init kernel and number of steps
        vec4 kernel = aakernel;
        int sze = 0; // Overwritten in aa-steps part
        
        // Init step size in tex coords
        float dx = 1.0/shape.x;
        float dy = 1.0/shape.y;
        
        // Allow more stuff
        // --pre-loop--
        
        // Convolve
        for (int y=-sze; y<sze+1; y++)
        {
            for (int x=-sze; x<sze+1; x++)
            {
                float k = kernel[int(abs(float(x)))] * kernel[int(abs(float(y)))];
                vec2 dpos = vec2(float(x)*dx, float(y)*dy);
                color1 += texture2D(texture, pos+dpos) * k;
            }
        }
        
        // Allow more stuff
        // --post-loop--
        
        // Determine final color
        // --color1-to-color2--
        gl_FragColor = color2;
        
    }

""")

# This cannot be done with a uniform, because on some systems it wont code
# with loops of which the length is undefined.
_SH_2F_AASTEPS = """
    >>int sze = 0;
    int sze = %i;
"""
SH_2F_AASTEPS_0 = ShaderCodePart('aa-steps', '0', _SH_2F_AASTEPS % 0)
SH_2F_AASTEPS_1 = ShaderCodePart('aa-steps', '1', _SH_2F_AASTEPS % 1)
SH_2F_AASTEPS_2 = ShaderCodePart('aa-steps', '2', _SH_2F_AASTEPS % 2)
SH_2F_AASTEPS_3 = ShaderCodePart('aa-steps', '3', _SH_2F_AASTEPS % 3)
