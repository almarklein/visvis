# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module shaders_3

Contains the source for various shaders for the Texture3D wobject,
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


## 3D vertex base
# The vertex shader only has one part

SH_3V_BASE = ShaderCodePart('base', '3D-vertex-default',
"""
    // Uniforms obtained from OpenGL
    uniform vec3 shape; // The dimensions of the data
    uniform float stepRatio; // Ratio to tune the number of steps
    // --uniforms--
    
    // Varyings to pass to fragment shader
    varying vec3 ray; // The direction to cast the rays in
    varying vec3 lightDirs[1]; // The light source directions
    varying vec3 V; // The View direction
    varying vec4 vertexPosition; // The vertex position in world coordinates
    // --varyings--
    
    void main()
    {
        
        // First of all, set projected position.
        // (We need to do this because this shader replaces the original shader.)
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        
        // Store position of vertex too, so the fragment shader can calculate
        // the depth
        vertexPosition = gl_Vertex.xyzw;
        
        // Store texture coordinate (also a default thing).
        gl_TexCoord[0].xyz = gl_MultiTexCoord0.xyz;
        
        // Calculate light direction
        int nlights = 1;
        for (int i=0; i<nlights; i++)
        {
            vec4 lightPos = gl_LightSource[i].position;
            vec3 L = (lightPos * gl_ModelViewMatrix).xyz;
            if (lightPos.w==1.0)
                L -= gl_Vertex.xyz;
            float lightEnabled = float( length(lightPos) > 0.0 );
            lightDirs[i] = lightEnabled * L;
        }
        
        // Calculate view direction
        V = (vec4(0.0, 0.0, 1.0, 1.0) * gl_ModelViewMatrix).xyz;
        V = normalize(V);
        
        // Calculate ray. In projective view the result is ok at the vertices
        // but in between there can be all kind of non-linear bending of the
        // rays. To solve this, one should use a denser grid of vertex-texture
        // pairs. In textures.py, this is done by partitioning the quads.
        
        // Get location of vertex in device coordinates
        float w = max(1.0, gl_Position.w);
        vec4 refPos1 = gl_Position * gl_Position.w;
        // Calculate point right behind it. Distance depends on w-value
        // to prevent wobly artifacts at low field of views.
        float zdist = max(1.0, gl_Position.w/10.0);
        vec4 refPos2 = refPos1 + vec4(0.0, 0.0, zdist, 0.0);
        // Project back to world coordinates to calculate ray direction
        // Note: gl_ModelViewProjectionMatrixInverse does not work on Mac OSX
        vec4 p1 = gl_ModelViewMatrixInverse * gl_ProjectionMatrixInverse * refPos1;
        vec4 p2 = gl_ModelViewMatrixInverse * gl_ProjectionMatrixInverse * refPos2;
        
        ray = (p2.xyz/p2.w) - (p1.xyz/p1.w);
        
        // Normalize ray to unit length.
        ray = normalize(ray);
        
        // Make the ray represent the length of a single voxel.
        ray = ray / shape;
        ray = ray * 0.58; // 1 over root of three = 0.577
        
        // Scale ray to take smaller steps.
        ray = ray / stepRatio;
    
    }

""")


## 3D fragment base
# Base for volume rendering
# The 3D fragment shader needs calcsteps, and a type

SH_3F_BASE = ShaderCodePart('base', '3D-fragment-default',
"""
    // 3D_FRAGMENT_SHADER (used to recognize that this is a renderStyle)
    
    // Uniforms obtained from OpenGL
    uniform sampler3D texture; // The 3D texture
    uniform vec3 shape; // And its shape (as in OpenGl)
    uniform vec3 extent; // extent of the data in world coordinates
    // --uniforms--
    
    // Varyings received from fragment shader
    varying vec3 ray; // One unit step in texture coordinates
    varying vec4 vertexPosition;  // Vertex position in world coordinates
    // --varyings--
    
    // ----- Functions follow below -----
    // --functions--
    // ----- End of functions -----
    
    void main()
    {
        
        // Get current pixel location.
        vec3 edgeLoc = vec3(gl_TexCoord[0]);
        // Get number of steps
        int n = calculateSteps(edgeLoc);
        // Init iter where the depth should be
        int iter_depth = 0;
        
        // Insert more initialization here
        // --pre-loop--
        
        // Cast ray. For some reason the inner loop is not iterated the whole
        // way for large datasets. Thus this ugly hack. If you know how to do
        // it better, please let me know!
        int i=0;
        while (i<n)
        {
            for (i=i; i<n; i++)
            {
                // Calculate location.
                vec3 loc = edgeLoc + float(i) * ray;
                
                // --in-loop--
            }
        }
        
        // Insert finalization code here
        // --post-loop--
        
        
        // Discard fragment if small alpha
        if (gl_FragColor.a < 0.1)
            discard;
        
        // Set depth value
        //
        // Calculate end position in world coordinates
        vec4 position2 = vertexPosition;
        position2.xyz += ray*shape*float(iter_depth);
        // Project to device coordinates and set fragment depth
        vec4 iproj = gl_ModelViewProjectionMatrix * position2;
        iproj.z /= iproj.w;
        gl_FragDepth = (iproj.z+1.0)/2.0;
    }
    
""")


## 3D fragment calcsteps
# Calculates the amount of steps that the volume rendering should take

SH_3F_CALCSTEPS = ShaderCodePart('calcsteps', 'default',
"""
    >>--functions--
    // --functions--
    
    float d2P(vec3 p, vec3 d, vec4 P)
    {
        // calculate the distance of a point p to a plane P along direction d.
        // plane P is defined as ax + by + cz = d
        // line is defined as two points on that line
        
        // calculate nominator and denominator
        float nom = -( dot(P.rgb,p) - P.a );
        float denom =  dot(P.rgb,d);
        // determine what to return
        if (nom*denom<=0.0)
        return 9999999.0; // if negative, or ON the plane, return ~inf
        else
            return nom / denom; // return normally
    }
    
    int calculateSteps(vec3 edgeLoc)
    {
        // Given the start pos, returns a corrected version of the ray
        // and the number of steps combined in a vec4.
        
        // Check for all six planes how many rays fit from the start point.
        // Take the minimum value (not counting negative and 0).
        float smallest = 9999999.0;
        smallest = min(smallest, d2P(edgeLoc, ray, vec4(1.0, 0.0, 0.0, 0.0)));
        smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 1.0, 0.0, 0.0)));
        smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 0.0, 1.0, 0.0)));
        smallest = min(smallest, d2P(edgeLoc, ray, vec4(1.0, 0.0, 0.0, 1.0)));
        smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 1.0, 0.0, 1.0)));
        smallest = min(smallest, d2P(edgeLoc, ray, vec4(0.0, 0.0, 1.0, 1.0)));
        
        // round-off errors can cause the value to be very large.
        // an n of 100.000 is pretty save
        if (smallest > 9999.0)
            smallest = 0.0;
        
        // determine amount of steps
        return int( ceil(smallest) );
    }

""")


## 3D fragment STYLE MIP
# Casts a ray all the way through. Displays the highest encountered
# intensity; there is only one pixel that contributes to the final color.

SH_3F_STYLE_MIP = ShaderCodePart('renderstyle', 'mip',
"""
    >>--pre-loop--
    
    // Remember that we made sure that the total range of the data is
    // mapped between 0 and 1 (also for signed data types).
    // We track best color because resampling is inconsistent for some reason
    float val; // to store the current value
    float maxval = -99999.0; // The maximum encountered value
    float maxi = 0.0;  // Where the maximum value was encountered
    vec4 maxcolor; // The color found at the maximum value
    vec4 color1; // What we sample from the texture
    vec4 color2; // What should be displayed
    // --pre-loop--
    
    >>--in-loop--
    
    // Sample color and make value
    color1 = texture3D( texture, loc );
    --color1-to-val--
    // Bookkeeping (avoid if statements)
    float r = float(val>maxval);
    maxval = (1.0-r)*maxval + r*val;
    maxi = (1.0-r)*maxi + r*float(i);
    maxcolor = (1.0-r)*maxcolor + r*color1;
    // --in-loop--
    
    >>--post-loop--
    
    // Set depth
    iter_depth = int(maxi);
    
    // Resample color and make display-color
    //color1 = texture3D( texture, edgeLoc + float(maxi)*ray );
    color1 = maxcolor;
    // --color1-to-color2--
    gl_FragColor = color2;
    // --post-loop--
    
""")


## 3D fragment STYLE RAY
# Casts a ray all the way through. All voxels contribute (using their alpha
# value).

SH_3F_STYLE_RAY = ShaderCodePart('renderstyle', 'ray',
"""
    >>--uniforms--
    uniform float stepRatio;
    // --uniforms--
    
    >>--pre-loop--
    vec4 color1; // what we sample from the texture
    vec4 color2; // what should be displayed
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    // --pre-loop--
    
    >>--in-loop--
    
    // Sample color and make display color
    color1 = texture3D( texture, loc );
    // --color1-to-color2--
    
    // Update value  by adding contribution of this voxel
    float a = color2.a * max(0.0, 1.0-color3.a) / stepRatio;
    color3.rgb += color2.rgb*a;
    color3.a += a; // color3.a counts total color contribution.
    // --in-loop--
    
    >>--post-loop--
    
    // Set depth at zero
    iter_depth = 0;
    
    // Set color
    color3.rgb /= color3.a;
    color3.a = min(1.0, color3.a);
    gl_FragColor = color3;
    // --post-loop--
    
""")


## 3D fragment STYLE EDGERAY
# Same as ray, but the alpha is scaled with the gradient magnitude, which
# makes it easier to "quickly" visualize a volume without having to play
# with the alpha channel in the ColormapEditor.

SH_3F_STYLE_EDGERAY = ShaderCodePart('renderstyle', 'edgeray',
"""
    >>--uniforms--
    uniform float stepRatio;
    // --uniforms--
    
    >>--pre-loop--
    vec4 color1; // what we sample from the texture
    vec4 color2; // what should be displayed
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    vec3 step = 1.5 / shape;
    // --pre-loop--
    
    >>--in-loop--
    
    // Sample color and make display color
    color1 = texture3D( texture, loc );
    vec4 betterColor = color1;
    
    // Look in neighborhood
    // calculate normal vector from gradient
    vec3 N; // normal
    color1 = texture3D( texture, loc+vec3(-step[0],0.0,0.0) );
    color2 = texture3D( texture, loc+vec3(step[0],0.0,0.0) );
    N[0] = length(color1.rgb - color2.rgb);
    betterColor = max(max(color1, color2),betterColor);
    color1 = texture3D( texture, loc+vec3(0.0,-step[1],0.0) );
    color2 = texture3D( texture, loc+vec3(0.0,step[1],0.0) );
    N[1] = length(color1.rgb - color2.rgb);
    betterColor = max(max(color1, color2),betterColor);
    color1 = texture3D( texture, loc+vec3(0.0,0.0,-step[2]) );
    color2 = texture3D( texture, loc+vec3(0.0,0.0,step[2]) );
    N[2] = length(color1.rgb - color2.rgb);
    betterColor = max(max(color1, color2),betterColor);
    float gm = length(N); // gradient magnitude
    
    // Get "display" color
    color1 = betterColor;
    // --color1-to-color2--
    // threshold gm (this treshold can be crucial) and use to scale alpha
    gm = (gm-0.1);
    color2.a *= min(1.0, max(0.0, gm ));
    
    // Update value  by adding contribution of this voxel
    // Put bias in denominator so the first voxels dont contribute too much
    float a = color2.a * max(0.0, 1.0-color3.a) / stepRatio;
    color3.rgb += color2.rgb*a;
    color3.a += a; // color3.a counts total color contribution.
    // --in-loop--
    
    >>--post-loop--
    
    // Set depth at zero
    iter_depth = 0;
    
    // Set color
    color3.rgb /= color3.a;
    color3.a = min(1.0, color3.a);
    gl_FragColor = color3;
    // --post-loop--
    
""")


## 3D fragment STYLE ISO
# Needs Color part and litvoxel part.
# Traces a ray untill it meets a pre-defined threshold. At that location
# the lighting is calculated. When the threshold is passed X times (usually 3)
# the program exits. Final color thus corresponds to couple of voxels.

SH_3F_STYLE_ISO = ShaderCodePart('renderstyle', 'iso',
"""
    >>--uniforms--
    uniform float th; // isosurface treshold
    uniform float stepRatio;
    uniform int maxIsoSamples;
    // --uniforms--
    
    >>--pre-loop--
    vec3 step = 1.5 / shape; // Step the size of one voxel
    float val; // the value  to determine if voxel is above threshold
    vec4 color1; // temp color
    vec4 color2; // temp color
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    float iter_depth_f = 0.0; // to set the depth
    int nsamples = 0;
    // --pre-loop--
    
    >>--in-loop--
    
    // Sample color and make display color
    color1 = texture3D( texture, loc );
    val = colorToVal(color1);
    
    if (val > th)
    {
        // Set color
        color2 = calculateColor(color1, loc, step);
        
        // Update value by adding contribution of this voxel
        float a = color2.a * max(0.0, 1.0-color3.a) / stepRatio;
        //float a = color2.a / ( color2.a + color3.a + 0.00001);
        color3.rgb += color2.rgb*a;
        color3.a += a; // color3.a counts total color contribution.
        
        // Set depth
        iter_depth_f = iter_depth_f + float(iter_depth_f==0.0) * float(i);
        
        // Break
        nsamples += 1;
        if (nsamples>maxIsoSamples)
        {
            i = n;
            break;
        }
    }
    // --in-loop--
    
    >>--post-loop--
    
    // Set depth
    iter_depth = int(iter_depth_f);
    
    // Set color
    color3.rgb /= color3.a;
    color3.a = min(1.0, color3.a);
    if (iter_depth_f == 0.0) // discard fragment if we encountered nothing
        color3 = vec4(0.0, 0.0, 0.0, 0.0);
    gl_FragColor = color3;
    // --post-loop--
    
""")


## 3D fragment_STYLE LITRAY
# Needs Color part and litvoxel part
# Casts a ray all the way through and calculates lighting at each step
# All contributions are combined untill alpha value saturates.
# Most pretty and most demanding for the GPU.

SH_3F_STYLE_LITRAY = ShaderCodePart('renderstyle', 'litray',
"""
    >>--uniforms--
    uniform float stepRatio;
    // --uniforms--
    
    >>--pre-loop--
    vec3 step = 1.5 / shape; // Step the size of one voxel
    float val; // the value  to determine if voxel is above threshold
    vec4 color1; // temp color
    vec4 color2; // temp color
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    float iter_depth_f = 0.0; // to set the depth
    // --pre-loop--
    
    >>--in-loop--

    // Sample color and make display color
    color1 = texture3D( texture, loc );
    
    // Get color with lighting
    color2 = calculateColor(color1, loc, step);
    
    // Update value by adding contribution of this voxel
    float a = color2.a * max(0.0, 1.0-color3.a) / stepRatio;
    color3.rgb += color2.rgb*a;
    color3.a += a; // color3.a counts total color contribution.
    
    // Set depth
    iter_depth_f = iter_depth_f + float(iter_depth_f==0.0) * float(color3.a>0.5) * float(i);
    // --in-loop--
    
    >>--post-loop--
    
    // Set depth
    iter_depth = int(iter_depth_f);
    
    color3.rgb /= color3.a;
    color3.a = min(1.0, color3.a);
    gl_FragColor = color3;
    // --post-loop--
    
""")

## 3D fragment_LITVOXEL (for ISO and ISORAY styles)
# Calculates light using the binn-phong reflectance model
# Requires 'nlights' part (SH_NLIGHTS_X from shaders_m.py)

SH_3F_LITVOXEL = ShaderCodePart('litvoxel', 'default',
"""
    >>--uniforms--
    // lighting
    uniform vec4 ambient;
    uniform vec4 diffuse;
    uniform vec4 specular;
    uniform float shininess;
    // --uniforms--
    
    >>--varyings--
    varying vec3 lightDirs[1];
    varying vec3 V; // view direction
    // --varyings--
    
    
    >>--functions--
    // --functions--
    
    float colorToVal(vec4 color1)
    {
        //return color1.r;
        float val;
        // --color1-to-val--
        //val = color1.r;
        return val;
    }
    
    vec4 calculateColor(vec4 betterColor, vec3 loc, vec3 step)
    {
        // Calculate color by incorporating lighting
        vec4 color1;
        vec4 color2;
        
        // calculate normal vector from gradient
        vec3 N; // normal
        color1 = texture3D( texture, loc+vec3(-step[0],0.0,0.0) );
        color2 = texture3D( texture, loc+vec3(step[0],0.0,0.0) );
        N[0] = colorToVal(color1) - colorToVal(color2);
        betterColor = max(max(color1, color2),betterColor);
        color1 = texture3D( texture, loc+vec3(0.0,-step[1],0.0) );
        color2 = texture3D( texture, loc+vec3(0.0,step[1],0.0) );
        N[1] = colorToVal(color1) - colorToVal(color2);
        betterColor = max(max(color1, color2),betterColor);
        color1 = texture3D( texture, loc+vec3(0.0,0.0,-step[2]) );
        color2 = texture3D( texture, loc+vec3(0.0,0.0,step[2]) );
        N[2] = colorToVal(color1) - colorToVal(color2);
        betterColor = max(max(color1, color2),betterColor);
        float gm = length(N); // gradient magnitude
        N = normalize(N);
        
        // Flip normal so it points towards viewer
        float Nselect = float(dot(N,V) > 0.0);
        N = (2.0*Nselect - 1.0) * N;  // ==  Nselect * N - (1.0-Nselect)*N;
        
        // Get color of the texture (albeido)
        color1 = betterColor;
        // --color1-to-color2--
        
        // Init colors
        vec4 ambient_color = vec4(0.0, 0.0, 0.0, 0.0);
        vec4 diffuse_color = vec4(0.0, 0.0, 0.0, 0.0);
        vec4 specular_color = vec4(0.0, 0.0, 0.0, 0.0);
        vec4 final_color;
        
        int nlights = 1;
        for (int i=0; i<nlights; i++)
        {
            // Get light direction (make sure to prevent zero devision)
            vec3 L = lightDirs[i];
            float lightEnabled = float( length(L) > 0.0 );
            L = normalize(L+(1.0-lightEnabled));
            
            // Calculate lighting properties
            float lambertTerm = clamp( dot(N,L), 0.0, 1.0 );
            vec3 H = normalize(L+V); // Halfway vector
            float specularTerm = pow( max(dot(H,N),0.0), shininess);
            
            // Calculate mask
            float mask1 = lightEnabled;
            
            // Calculate colors
            ambient_color +=  mask1 * ambient * gl_LightSource[i].ambient;
            diffuse_color +=  mask1 * lambertTerm * diffuse * gl_LightSource[i].diffuse;
            specular_color += mask1 * specularTerm * specular * gl_LightSource[i].specular;
        }
        
        // Calculate final color by componing different components
        final_color = color2 * ( ambient_color + diffuse_color) + specular_color;
        final_color.a = color2.a;
        
        // Done
        return final_color;
    }
    
""")
