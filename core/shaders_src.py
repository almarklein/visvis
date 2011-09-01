""" Module shaders_src

Contains the source for various shaders, divided in different parts.

The names consists of different parts, seperated by underscores:
  * SH: just to indicate its a shader
  * 2F, 3F, MF, 2V, 3V, MV: the kind of program, 2D/3D texture or mesh,
    vertex or fragment shader. May be left out for generic parts (such as color)
  * part name: can be BASE, STYLE, or anything else really.
  * part name type: Optional. Some parts have alternatives, 
    such as the STYLE part for 3D rendering techniques. 

"""

## Color
# These are used by many shaders to be able to deal with scalar or RGB data.
# color1-to-val is used by volume renderes to test thresholds etc.
# color1-to-color2 is used to convert the color sampled from the texture to
# a color to be displayed on screen.

# This one is not really usefull, but included for completeness
SH_COLOR_SCALARNOCMAP = """

    >>uniforms>>
    uniform vec2 scaleBias;
    <<uniforms<<
    
    >>pre-loop>>
    float _colorval;
    
    >>color1-to-val>>
    val = color1.r;
    
    >>color1-to-color2>>
    _colorval = ( color1.r + scaleBias[1] ) * scaleBias[0];
    color2 = vec4(_colorval, _colorval, _colorval, 1.0);
    
    """

SH_COLOR_SCALAR = """
    
    >>uniforms>>
    uniform sampler1D colormap;
    uniform vec2 scaleBias;
    <<uniforms<<
    
    >>color1-to-val>>
    val = color1.r;
    
    >>color1-to-color2>>
    color2 = texture1D( colormap, (color1.r + scaleBias[1]) * scaleBias[0]);
    
    """

SH_COLOR_RGB = """

    >>uniforms>>
    uniform vec2 scaleBias;
    <<uniforms<<
    
    >>color1-to-val>>
    val = max(color1.r, max(color1.g, color1.b));
    
    >>color1-to-color2>>
    color2 = ( color1 + scaleBias[1] ) * scaleBias[0];
    
    """

## 2D fragment
# Shows 2D texture and does anti-aliasing when image is zoomed out.

SH_2F_BASE = """

// Uniforms obtained from OpenGL
uniform sampler2D texture; // The 3D texture
uniform vec2 shape; // And its shape (as in OpenGl)
uniform vec2 extent; // Extent of the data in world coordinates
uniform vec4 aakernel; // The smoothing kernel for anti-aliasing
<<uniforms<<

// Varyings obtained from vertex shader
<<varyings<<

void main()
{    
    // Get centre location
    vec2 pos = gl_TexCoord[0].xy;
    
    // Init value
    vec4 color1 = vec4(0.0, 0.0, 0.0, 0.0); 
    vec4 color2; // to set color later
    
    // Init kernel and number of steps
    vec4 kernel = aakernel;
    <<aa-steps<<
    
    // Init step size in tex coords
    float dx = 1.0/shape.x;
    float dy = 1.0/shape.y;
    
    // Allow more stuff
    <<pre-loop<<
    
    // Convolve
    for (int y=-sze; y<sze+1; y++)
    {
        for (int x=-sze; x<sze+1; x++)
        {   
            float k = kernel[abs(x)] * kernel[abs(y)];
            vec2 dpos = vec2(float(x)*dx, float(y)*dy);
            <<in-loop<<
        }
    }
    
    // Allow more stuff
    <<post-loop<<
    
    // Determine final color
    <<color1-to-color2<<
    gl_FragColor = color2;
    
}
"""

# Simply samples the color from the texture
SH_2F_STYLE_NORMAL = """
    >>in-loop>>
    color1 += texture2D(texture, pos+dpos) * k;
"""

# This cannot be done with a uniform, because on some systems it wont code
# with loops of which the length is undefined.
_SH_2F_AASTEPS = """
>>aa-steps>>
int sze = %i;
"""
SH_2F_AASTEPS_0 = _SH_2F_AASTEPS % 0
SH_2F_AASTEPS_1 = _SH_2F_AASTEPS % 1
SH_2F_AASTEPS_2 = _SH_2F_AASTEPS % 2
SH_2F_AASTEPS_3 = _SH_2F_AASTEPS % 3


## 3D vertex base
# The vertex shader only has one part

SH_3V_BASE = """
    // Uniforms obtained from OpenGL
    uniform vec3 shape; // The dimensions of the data
    uniform float stepRatio; // Ratio to tune the number of steps
    
    // Varyings to pass to fragment shader
    varying vec3 ray; // The direction to cast the rays in
    varying vec3 L; // The 0th light source direction
    varying vec3 V; // The View direction
    varying vec4 vertexPosition; // The vertex position in world coordinates
    
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
        L = (gl_LightSource[0].position * gl_ModelViewMatrix).xyz;
        if (gl_LightSource[0].position[3]==1.0)
            L -= gl_Vertex.xyz;
        L = normalize(L);
        
        // Calculate view direction
        V = (vec4(0.0, 0.0, 1.0, 1.0) * gl_ModelViewMatrix).xyz;
        V = normalize(V);
        
        // Calculate ray. Not perfect in projective view, 
        // but quite acceptable
        
        // Get location of vertex in device coordinates
        vec4 refPos1 = gl_Position;
        refPos1 *= refPos1.w; // Not sure why, but this does the trick
        // Calculate point right behind it
        vec4 refPos2 = refPos1 + vec4(0.0, 0.0, 1.0, 0.0);
        // Project back to world coordinates to calculate ray direction
        vec4 p1 = gl_ModelViewProjectionMatrixInverse * refPos1 ;
        vec4 p2 = gl_ModelViewProjectionMatrixInverse * refPos2 ;
        ray = (p2.xyz/p2.w) - (p1.xyz/p1.w);
        
        // Normalize ray to unit length.    
        ray = normalize(ray);
        
        // Make the ray represent the length of a single voxel.
        ray = ray / shape;
        ray = ray * 0.58; // 1 over root of three = 0.577
        
        // Scale ray to take smaller steps.
        ray = ray / stepRatio;
        
    }

"""

# todo: remove this old version in a few commits
_SH_3V_BASE = """
    // Uniforms obtained from OpenGL
    uniform vec3 shape; // The dimensions of the data
    uniform float stepRatio; // Ratio to tune the number of steps
    
    // Varyings to pass to fragment shader
    varying vec3 ray; // The direction to cast the rays in
    varying vec3 L; // The 0th light source direction
    varying vec3 V; // The View direction
    varying vec4 vertexPosition; // The vertex position in world coordinates
    
    void main()
    {    
        
        // First of all, set position.
        // (We need to do this because this shader replaces the original shader.)
        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        
        // Store position of vertex too, so the fragment shader can calculate
        // the depth
        vertexPosition = gl_Vertex.xyzw;
        
        // Store texture coordinate (also a default thing).
        gl_TexCoord[0].xyz = gl_MultiTexCoord0.xyz;
        
        // Calculate light direction
        L = (gl_LightSource[0].position * gl_ModelViewMatrix).xyz;
        if (gl_LightSource[0].position[3]==1.0)
            L -= gl_Vertex.xyz;
        L = normalize(L);
        
        // Calculate view direction
        V = (vec4(0.0, 0.0, 1.0, 1.0) * gl_ModelViewMatrix).xyz;
        V = normalize(V);
        
        // Calculate the scaling of the modelview matrix so we can correct
        // for axes.daspect and scale transforms of the wobject (in case
        // of anisotropic data).
        // We go from world coordinates to eye coordinates.
        vec4 p0 = gl_ModelViewMatrix * vec4(0.0,0.0,0.0,1.0);
        vec4 px = gl_ModelViewMatrix * vec4(1.0,0.0,0.0,1.0);
        vec4 py = gl_ModelViewMatrix * vec4(0.0,1.0,0.0,1.0);
        vec4 pz = gl_ModelViewMatrix * vec4(0.0,0.0,1.0,1.0);
        float sx = length(p0.xyz - px.xyz);
        float sy = length(p0.xyz - py.xyz);
        float sz = length(p0.xyz - pz.xyz);
        
        // Create a (diagonal) matrix to correct for the scaling
        mat4 Ms = mat4(0.0);
        Ms[0][0] = 1.0/(sx*sx);
        Ms[1][1] = 1.0/(sy*sy);
        Ms[2][2] = 1.0/(sz*sz);
        Ms[3][3] = 1.0;
        
        // Calculate ray direction. By correcting for the scaling, the ray is
        // expressed in textute coordinates.
        // We go from eye coordinates to world/texture coordinates.
        vec4 p1 = vec4(0.0, 0.0, 0.0, 1.0) * gl_ModelViewProjectionMatrix * Ms;
        vec4 p2 = vec4(0.0, 0.0, 1.0, 1.0) * gl_ModelViewProjectionMatrix * Ms;
        ray = (p2.xyz/p2[3]) - (p1.xyz/p1[3]);
        
        // Normalize ray to unit length.    
        ray = normalize(ray);
        
        // Make the ray represent the length of a single voxel.
        ray = ray / shape;
        ray = ray * 0.58; // 1 over root of three = 0.577
        
        // Scale ray to take smaller steps.
        ray = ray / stepRatio;
        
    }

"""
## 3D fragment base
# Base for volume rendering
# The 3D fragment shader needs calcsteps, and a type

SH_3F_BASE = """

    // Uniforms obtained from OpenGL
    uniform sampler3D texture; // The 3D texture
    uniform vec3 shape; // And its shape (as in OpenGl)
    uniform vec3 extent; // extent of the data in world coordinates
    <<uniforms<<
    
    // Varyings received from fragment shader
    varying vec3 ray; // One unit step in texture coordinates
    varying vec4 vertexPosition;  // Vertex position in world coordinates
    <<varyings<<
    
    // ----- Functions follow below -----
    
    <<functions<<
    
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
        <<pre-loop<<
        
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
                
                // Insert more loop stuff here
                <<in-loop<<
            }
        }
        
        // Insert finalization code here
        <<post-loop<<
        
        
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
    
"""

## 3D fragment calcsteps
# Calculates the amount of steps that the volume rendering should take

SH_3F_CALCSTEPS = """

>>functions>>
<<functions<<

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

"""

## 3D fragment STYLE MIP
# Casts a ray all the way through. Displays the highest encountered
# intensity.

SH_3F_STYLE_MIP = """
    
    >>pre-loop>>
    
    // Remember that we made sure that the total range of the data is 
    // mapped between 0 and 1 (also for signed data types).
    // We track best color because resampling is inconsistent for some reason
    float val; // to store the current value
    float maxval = -99999.0; // The maximum encountered value
    float maxi = 0.0;  // Where the maximum value was encountered
    vec4 maxcolor; // The color found at the maximum value 
    vec4 color1; // What we sample from the texture
    vec4 color2; // What should be displayed
    <<pre-loop<<
    
    >>in-loop>>
    
    // Sample color and make value
    color1 = texture3D( texture, loc );
    <<color1-to-val<<
    // Bookkeeping (avoid if statements)
    float r = float(val>maxval);
    maxval = (1.0-r)*maxval + r*val;
    maxi = (1.0-r)*maxi + r*float(i);
    maxcolor = (1.0-r)*maxcolor + r*color1;
    <<in-loop<<
    
    >>post-loop>>
    
    // Set depth
    iter_depth = int(maxi);
    
    // Resample color and make display-color
    //color1 = texture3D( texture, edgeLoc + float(maxi)*ray );
    color1 = maxcolor;
    <<color1-to-color2<<
    gl_FragColor = color2;
    <<post-loop<<
    
"""

## 3D fragment STYLE PMIP
# todo: names....
# Pseudo mip. This looks a bit like MIP, and like MIP, it does usually show
# structures of interest without having to fiddle with the alpha channel.
# A ray is cast through the volume and each voxel contributes to the final
# color. The contribution saturates linearly, so things in the back have
# small contributions.

SH_3F_STYLE_PMIP = """
    
    >>uniforms>>
    uniform float stepRatio;
    <<uniforms<<
    
    >>pre-loop>>
    vec4 color1; // what we sample from the texture
    vec4 color2; // what should be displayed
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    float alpha = 0.0; // total contribution
    float val;
    <<pre-loop<<
    
    >>in-loop>>
    
    // Sample color and make display color
    color1 = texture3D( texture, loc );
    <<color1-to-color2<<
    <<color1-to-val<<
    
    // Update value  by adding contribution of this voxel
    // Put bias in denominator so the first voxels dont contribute too much
    float color2_alpha = val*val*val*val + 0.00001;
    float a = color2_alpha / ( color2_alpha + alpha + 1.0); 
    a /= stepRatio;
    color3.rgba += color2.rgba*a;
    alpha += a; // alpha counts total color contribution.
    <<in-loop<<
    
    >>post-loop>>
    
    // Set depth at zero
    iter_depth = 0;
    
    // Set color
    color3.rgba /= alpha;
    color3.a = min(1.0, color3.a);
    gl_FragColor = color3;
    <<post-loop<<
    
"""

## SH_3D fragment STYLE RAY
# Casts a ray all the way through. All voxels contribute (using their alpha
# value), untill the alpha is saturated.
SH_3F_STYLE_RAY = """
    
    >>uniforms>>
    uniform float stepRatio;
    <<uniforms<<
    
    >>pre-loop>>
    vec4 color1; // what we sample from the texture
    vec4 color2; // what should be displayed
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    <<pre-loop<<
    
    >>in-loop>>
    
    // Sample color and make display color
    color1 = texture3D( texture, loc );
    <<color1-to-color2<<
    
    // Update value  by adding contribution of this voxel
    // Put bias in denominator so the first voxels dont contribute too much
    //float a = color2.a / ( color2.a + color3.a + 1.0); 
    //a /= stepRatio;
    float a = color2.a * max(0.0, 1.0-color3.a) / stepRatio;
    color3.rgb += color2.rgb*a;
    color3.a += a; // color3.a counts total color contribution.
    <<in-loop<<
    
    >>post-loop>>
    
    // Set depth at zero
    iter_depth = 0;
    
    // Set color
    color3.rgb /= color3.a;
    color3.a = min(1.0, color3.a);
    gl_FragColor = color3;
    <<post-loop<<
    
"""
## SH_3D fragment STYLE RAY2
# Same as ray, but has some artificial shadow effects. Really not that usefull,
# because the normal ray renderer also has these effects, although a bit less.
SH_3F_STYLE_RAY2 = """
    
    >>uniforms>>
    uniform float stepRatio;
    <<uniforms<<
    
    >>pre-loop>>
    vec4 color1; // what we sample from the texture
    vec4 color2; // what should be displayed
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    vec3 step = 1.5 / shape;
    <<pre-loop<<
    
    >>in-loop>>
    
    // Sample color and make display color
    color1 = texture3D( texture, loc );
    vec4 color0 = color1;
    
    // Look in neighborhood
    color2 = color1;
    color1 = texture3D( texture, loc+vec3(-step[0],0.0,0.0) );
    color2 = max(color1, color2);
    color1 = texture3D( texture, loc+vec3(step[0],0.0,0.0) );
    color2 = max(color1, color2);    
    color1 = texture3D( texture, loc+vec3(0.0,-step[1],0.0) );
    color2 = max(color1, color2);    
    color1 = texture3D( texture, loc+vec3(0.0,step[1],0.0) );
    color2 = max(color1, color2);
    color1 = texture3D( texture, loc+vec3(0.0,0.0,-step[2]) );
    color2 = max(color1, color2);
    color1 = texture3D( texture, loc+vec3(0.0,0.0,step[2]) );
    color2 = max(color1, color2);
    
    // Calculate color strengths
    float colorStrength0 = length(color0.rgb);
    float colorStrength2 = length(color2.rgb);
    
    // Calculate display color and reduce according to difference
    color1 = color2 * (colorStrength0/(colorStrength2+0.01));
    <<color1-to-color2<<
    color2.rgb *= max(0.5, 1.0-(colorStrength2-colorStrength0));
    
    // Update value  by adding contribution of this voxel
    // Put bias in denominator so the first voxels dont contribute too much
    float a = color2.a * max(0.0, 1.0-color3.a) / stepRatio;
    color3.rgb += color2.rgb*a;
    color3.a += a; // color3.a counts total color contribution.
    <<in-loop<<
    
    >>post-loop>>
    
    // Set depth at zero
    iter_depth = 0;
    
    // Set color
    color3.rgb /= color3.a;
    color3.a = min(1.0, color3.a);
    gl_FragColor = color3;
    <<post-loop<<
    
"""
## 3D fragment STYLE ISO
# Needs Color part and litvoxel part
SH_3F_STYLE_ISO = """

    >>uniforms>>
    uniform float th; // isosurface treshold
    uniform float stepRatio;
    uniform int maxIsoSamples;
    <<uniforms<<
    
    >>pre-loop>>
    vec3 step = 1.5 / shape; // Step the size of one voxel
    float val; // the value  to determine if voxel is above threshold
    vec4 color1; // temp color
    vec4 color2; // temp color
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    float iter_depth_f = 0.0; // to set the depth
    int nsamples = 0;
    <<pre-loop<<
    
    >>in-loop>>
    
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
        iter_depth_f =  float(i);
        
        // Break
        nsamples += 1;
        if (nsamples>maxIsoSamples)
        {
            i = n;
            break;
        }
    }
    <<in-loop<<
    
    >>post-loop>>
    
    // Set depth
    iter_depth = int(iter_depth_f);
    
    // Set color
    color3.rgb /= color3.a;
    color3.a = float(iter_depth_f>0.0);
    gl_FragColor = color3;
    <<post-loop<<
    
"""

## 3D fragment_STYLE ISORAY
# Needs Color part and litvoxel part
# Casts a ray all the way through and calculates lighting at each step
# All contributions are combined untill alpha value saturates.
SH_3F_STYLE_ISORAY = """

    >>uniforms>>
    uniform float stepRatio;
    <<uniforms<<
    
    >>pre-loop>>
    vec3 step = 1.5 / shape; // Step the size of one voxel
    float val; // the value  to determine if voxel is above threshold
    vec4 color1; // temp color
    vec4 color2; // temp color
    vec4 color3 = vec4(0.0, 0.0, 0.0, 0.0); // init color
    float iter_depth_f = 0.0; // to set the depth
    <<pre-loop<<
    
    >>in-loop>>
    
    // Sample color and make display color
    color1 = texture3D( texture, loc );

    // Set color
    color2 = calculateColor(color1, loc, step);
    
    // Update value by adding contribution of this voxel
    float a = color2.a * max(0.0, 1.0-color3.a) / stepRatio;
    //float a = color2.a / ( color2.a + color3.a + 0.00001); 
    color3.rgb += color2.rgb*a;
    color3.a += a; // color3.a counts total color contribution.
    
    // Set depth
    iter_depth_f =  float(iter_depth==0.0) * float(color3.a>0) * float(i);
    <<in-loop<<
    
    >>post-loop>>
    
    // Set depth
    iter_depth = int(iter_depth_f);
    
    color3.rgb /= color3.a;
    color3.a = min(1.0, color3.a);
    gl_FragColor = color3;
    <<post-loop<<
    
"""

## 3D fragment_LITVOXEL (for ISO and ISORAY styles)
SH_3F_LITVOXEL = """
    >>uniforms>>
    // lighting
    uniform vec4 ambient;
    uniform vec4 diffuse;
    uniform vec4 specular;
    uniform float shininess;
    <<uniforms<<
    
    >>varyings>>
    varying vec3 L; // light direction
    varying vec3 V; // view direction
    <<varyings<<
    
    
    >>functions>>
    <<functions<<
    
    float colorToVal(vec4 color1)
    {
        //return color1.r;
        float val;
        <<color1-to-val<<
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
        
        // Init total color and strengt variable
        vec4 totalColor;
        float str;
        
        // Apply ambient and diffuse light
        totalColor = ambient * gl_LightSource[0].ambient;
        str = clamp(dot(L,N),0.0,1.0);
        totalColor += str * diffuse * gl_LightSource[0].diffuse;
        
        // Apply color of the texture
        color1 = betterColor;
        <<color1-to-color2<<
        totalColor *= color2;
        
        // Apply specular color
        vec3 H = normalize(L+V);
        str = pow( max(dot(H,N),0.0), shininess);
        totalColor += str * specular * gl_LightSource[0].specular;
        
        totalColor.a = color2.a * gm;
        return totalColor;
    }
    
"""


