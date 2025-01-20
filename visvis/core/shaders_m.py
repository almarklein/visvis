# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module shaders_m

Contains the source for various shaders for the Mesh wobject,
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


## Mesh base vertex

SH_MV_BASE = ShaderCodePart('base', 'mesh-vertex-default',
"""
    // Uniforms
    //--uniforms--
    
    // Varyings
    varying vec3 normal, vVertex;
    varying vec4 vColor;
    //--varyings--
    
    void main()
    {
        // Get position
        vec4 vertex = vec4(gl_Vertex);
        
        // Calculate vertex in eye coordinates
        vVertex = vec3(gl_ModelViewMatrix * vertex);
        
        // Calculate projected position
        gl_Position = gl_ModelViewProjectionMatrix * vertex;
        
        // Calculate nornal
        normal = gl_NormalMatrix * gl_Normal;
        
        // Store texture coordinate (also a default thing).
        gl_TexCoord[0].xyz = gl_MultiTexCoord0.xyz;
        
        // Set the vertex color
        vColor = gl_Color;
        
        // Below comes code if light is calculated in vertex shader
        // (Gouraud and flat shading)
        //--light--
    }
""")


## Mesh base fragment

SH_MF_BASE = ShaderCodePart('base', 'mesh-fragment-default',
"""
    // Uniforms
    // --uniforms--
    
    // Varyings
    varying vec3 normal, vVertex;
    varying vec4 vColor;
    // --varyings--
    
    void main (void)
    {
        // Define colors
        vec4 albeido = vec4(1.0, 1.0, 1.0, 1.0);
        vec4 final_color;
        
        // Calculate light
        // --light--
        
        // Set albeido (i.e. base color)
        // --albeido--
        
        // Set final_color (including lighting)
        // --final-color--
        
        // Set fragment color using final_color, alpha using the albeido
        gl_FragColor.rgb = final_color.rgb;
        gl_FragColor.a = albeido.a;
    }
""")

## LIGHT / SHADING

_SH_LIGHT = """
    >>// Define colors
    // Define colors (tag exists only in fragment shader)
    vec4 ambient_color, diffuse_color, specular_color;
    
    >>--light--
    
    // Init colors
    ambient_color = vec4(0.0, 0.0, 0.0, 0.0);
    diffuse_color = vec4(0.0, 0.0, 0.0, 0.0);
    specular_color = vec4(0.0, 0.0, 0.0, 0.0);
    
    // Init vectors
    vec3 N = normalize(normal);
    vec3 V = vec3(0.0, 0.0, 1.0); //view (eye) direction (in eye coords; is easy)
    vec3 L;
    
    // Flip normal so it points towards viewer
    float Nselect = float(dot(N,V) > 0.0);
    N = (2.0*Nselect - 1.0) * N;  // ==  Nselect * N - (1.0-Nselect)*N;
    
    int nlights = 1;
    for (int i=0; i<nlights; i++)
    {
        // Get light position
        vec4 lightPos = gl_LightSource[i].position;
        
        // Is this thing on?
        float lightEnabled = float( length(lightPos) > 0.0 );
        
        // Get light direction (make sure to prevent zero devision)
        // Also take into account if its a directional light
        L = lightPos.xyz - lightPos.w*vVertex;
        L = normalize(L + (1.0-lightEnabled));
        
        // Calculate lighting properties (blinn-phong light model)
        float lambertTerm = clamp( dot(N,L), 0.0, 1.0 );
        vec3 H = normalize(L+V); // Halfway vector
        float specularTerm = pow( max(dot(H,N),0.0), gl_FrontMaterial.shininess);
        
        // Below is Phong reflection (for reference)
        //vec3 R = -reflect(L,N);
        //float specularTerm = pow( max(dot(R, V), 0.0), gl_FrontMaterial.shininess );
        
        // Calculate masks
        float mask1 = lightEnabled;
        float mask2 = lightEnabled * float(lambertTerm>0.0);
        
        // Calculate colors
        ambient_color += (mask1 * gl_LightSource[i].ambient * gl_FrontMaterial.ambient);
        diffuse_color += (mask2 * gl_LightSource[i].diffuse *
                          gl_FrontMaterial.diffuse * lambertTerm);
        specular_color += (mask2 * gl_LightSource[i].specular *
                           gl_FrontMaterial.specular * specularTerm);
    }
"""

## Mesh shading plain

SH_MV_SHADING_PLAIN = ShaderCodePart('shading', 'plain',
"""
    >>--light--
    // No lighting calculations
""")
SH_MF_SHADING_PLAIN = ShaderCodePart('shading', 'plain',
"""
    >>--light--
    // No lighting calculations
    >>--final-color--
    final_color = albeido = vColor; // Plain shading -> only use vertex color
""")

## Mesh shading gouraud

SH_MV_SHADING_GOURAUD = ShaderCodePart('shading', 'gouraud',
    _SH_LIGHT + """\n
    >>--varyings--
    varying vec4 ambient_color, diffuse_color, specular_color; // to fragment
    //--varyings--
""")
SH_MF_SHADING_GOURAUD = ShaderCodePart('shading', 'gouraud',
"""
    >>--varyings--
    varying vec4 ambient_color, diffuse_color, specular_color; // from vertex
    //--varyings--
    
    >>--light--
    // Light calculations done in vertex shader
    
    >>--final-color--
    final_color = albeido * ( ambient_color + diffuse_color) + specular_color;
""")

## Mesh shading smooth (aka phong-shading)

SH_MV_SHADING_SMOOTH = ShaderCodePart('shading', 'smooth',
"""
    >>--light--
    // Lighting calculations performed in fragment shader
""")
SH_MF_SHADING_SMOOTH = ShaderCodePart('shading', 'smooth',
    _SH_LIGHT + """\n
    >>--final-color--
    final_color = albeido * ( ambient_color + diffuse_color) + specular_color;
""")

## Mesh shading toon (aka cel-shading)
# Toon shading is a type of shading that produces a cartoonish look.
# The number of colors is reduced (thats what done here) and
# a dark edge is drawn around the objects (done in OnDraw() method
# of the Mesh class.
# The colours are reduced in a way that does not use if-statements.
# There is also a simple form of anti-aliasing.

SH_MV_SHADING_TOON = ShaderCodePart('shading', 'toon',
    SH_MV_SHADING_SMOOTH.rawCode)
SH_MF_SHADING_TOON = ShaderCodePart('shading', 'toon',
    _SH_LIGHT + """\n
    >>--final-color--
    
    // Discretisize diffuse part
    float nLimits = (5.0) - 1.001; // Number in brachets is number of levels
    vec4 C1, C2, C3;
    float W = 0.25 * fwidth(length(diffuse_color.rgb));
    C1 = vec4(ivec4((diffuse_color-W)*nLimits+0.5)) / nLimits;
    C2 = vec4(ivec4((diffuse_color  )*nLimits+0.5)) / nLimits;
    C3 = vec4(ivec4((diffuse_color+W)*nLimits+0.5)) / nLimits;
    diffuse_color = 0.3333 * (C1 + C2 + C3);
    
    // Discretisize specular part. Ensure we always have some reflection ...
    nLimits = (2.0) / length(gl_FrontMaterial.specular.rgb) -1.001;
    W = 0.5 * fwidth(length(specular_color.rgb));
    C1 = vec4(ivec4((specular_color-W)*nLimits+0.5)) / nLimits;
    C2 = vec4(ivec4((specular_color  )*nLimits+0.5)) / nLimits;
    C3 = vec4(ivec4((specular_color+W)*nLimits+0.5)) / nLimits;
    specular_color = 0.333 * (C1 + C2 + C3);
    
    // Compose final color
    final_color = albeido * ( ambient_color + diffuse_color) + specular_color;
""")

## Let there be light (but how many?)

_NLIGHTS = """
    >>int nlights = 1;
    int nlights = %i;
    >>varying vec3 lightDirs[1];
    varying vec3 lightDirs[%i];
"""

SH_NLIGHTS_2 = ShaderCodePart('nlights', '2', _NLIGHTS % (2,2))
SH_NLIGHTS_3 = ShaderCodePart('nlights', '3', _NLIGHTS % (3,3))
SH_NLIGHTS_4 = ShaderCodePart('nlights', '4', _NLIGHTS % (4,4))
SH_NLIGHTS_5 = ShaderCodePart('nlights', '5', _NLIGHTS % (5,5))
SH_NLIGHTS_6 = ShaderCodePart('nlights', '6', _NLIGHTS % (6,6))
SH_NLIGHTS_7 = ShaderCodePart('nlights', '7', _NLIGHTS % (7,7))
SH_NLIGHTS_8 = ShaderCodePart('nlights', '8', _NLIGHTS % (8,8))

# Make one light extra lightweight
# (I know at least one occurance where it meant the difference between
# success and failure for the iso volume renderer).
SH_NLIGHTS_1 = ShaderCodePart('nlights', '1',
"""
    >>for (int i=0; i<nlights; i++)
    int i = 0;
""")

SH_NLIGHTS_0 = ShaderCodePart('nlights', '0',
"""
    >>int nlights = 1;
    int nlights = 0;
    >>varying vec3 lightDirs[1];
    // no lightDirs
    >>lightDirs[i] =
    // Removed Assignment to lightDirs
""")


## ALBEIDO
# Different ways to determine the albeido of the mesh. The material
# always has influence, but the ambient+diffuse term can be multiplied
# with another color before the specular reflection is added. This
# can be a colormap, texture, RGB or RGBA value.

SH_MF_ALBEIDO_UNIT = ShaderCodePart('albeido', 'unit',
"""
    >>--albeido--
    // Albeido stays unit, but takes alpha from vColor
    albeido.a = vColor.a;
""")
SH_MF_ALBEIDO_LUT1 = ShaderCodePart('albeido', '1D LUT',
"""
    >>--uniforms--
    uniform sampler1D colormap;
    // --uniforms--
        
    >>--albeido--
    albeido = texture1D( colormap, gl_TexCoord[0].x);
    albeido.a *= vColor.a;
""")
SH_MF_ALBEIDO_LUT2 = ShaderCodePart('albeido', '2D LUT',
"""
    >>--uniforms--
    uniform sampler2D texture;
    // --uniforms--
    
    >>--albeido--
    albeido = texture2D( texture, gl_TexCoord[0].xy);
    albeido.a *= vColor.a;
""")
SH_MF_ALBEIDO_RGB = ShaderCodePart('albeido', 'RGB', # No transparency possible here
"""
    >>--albeido--
    albeido = vec4(vColor.rgb, 1.0);
""")
SH_MF_ALBEIDO_RGBA = ShaderCodePart('albeido', 'RGBA',
"""
    >>--albeido--
    albeido = vColor.rgba;
""")
