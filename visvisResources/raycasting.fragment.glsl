/* Fragment shader for raycasting rendering.
 * The ray is cast through the volume and at each position we determine
 * color and alpha via the colormap. The result is added to the total
 * color. This is the most generic render style, which can produce the
 * most beautifull images. 
 *
 * This file is part of Visvis.
 * Copyright 2009 Almar Klein
 */

// the 3D texture and colormap texture.
uniform sampler3D texture;
uniform sampler1D colormap;

// for window level and window width
uniform vec2 scaleBias;
uniform float stepRatio;

// varying calculated by vertex shader
varying vec3 ray;


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

vec4 getRayAndSteps(vec3 edgeLoc)
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
    
    // determine amount of steps and correct ray
    vec4 result;
    float n = ceil(smallest);
    result.xyz = ray * (smallest/n);
    result[3] = n;
    
    // done
    return result;
}


void main()
{    
    
    // Get current pixel location.
    vec3 edgeLoc = vec3(gl_TexCoord[0]);
    
    // Get ray and steps.
    vec4 tmp4 = getRayAndSteps(edgeLoc);
    vec3 ray2 = tmp4.xyz;
    int n = int(tmp4[3]);
    
    // make floats for scale and bias
    float sb_scale = scaleBias[0];
    float sb_bias = scaleBias[1];
    
    // calculate normalization factor
    float alphaFactor = 1.0/stepRatio;
    
    // init value
    gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
    
    // loop!
    for (int i=0; i<n; i++)
    {
        // calculate location        
        vec3 loc = edgeLoc + float(i) * ray2;
        
        // sample value and get RGBA
        float val = texture3D( texture, loc ).r;
        vec4 color = texture1D( colormap, (val+sb_bias)*sb_scale );
        
        // update value
        //gl_FragColor = gl_FragColor * gl_FragColor.a + color * color.a;
        float a1 = gl_FragColor.a;
        float a = color.a / (gl_FragColor.a + color.a + 0.0001);        
        gl_FragColor = gl_FragColor * (1.0-a) + color * a;
        gl_FragColor.a = a1 + color.a * alphaFactor;
        //gl_FragColor += val * vec4(1.0, 1.0, 1.0, 0.0 );
        //if (gl_FragColor.a >=1.0)
        //    break;
        
    }
    
    // discard fragment if small alpha
    if (gl_FragColor.a < 0.1)
        discard;
    
    // Apply a depth? No, does only really make sence for the iso renderer.
    
}
