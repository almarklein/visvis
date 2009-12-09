/* Fragment shader for Maximum Intensity Projection (MIP) rendering.
 * The ray is cast through the volume and we keep track of the 
 * smalest value. This is the fastest rendermethod available.
 *
 * This file is part of Visvis.
 * Copyright 2009 Almar Klein
 */

// the 3D texture and colormap texture.
uniform sampler3D texture;
uniform sampler1D colormap;

// for window level and window width
uniform vec2 scaleBias;

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
    
    // Init. Remember that we made sure that the total range of the data is 
    // mapped between 0 and 1 (also for signed data types).
    float maxval = 0.0;
    
    // Cast ray. For some reason the inner loop is not iterated the whole
    // way for large datasets. Thus this ugly hack. If you know how to do
    // it better, please let me know!
    int i=0;
    while (i<n)
    {
        for (i=i; i<n; i++)
        {
            // Calculate location.
            vec3 loc = edgeLoc + float(i) * ray2;
            
            
            // Sample value (avoid if statements).
            float val = texture3D( texture, loc )[0];        
            float r = float(val>maxval);
            maxval = (1.0-r)*maxval + r*val;
            
            // Sample value (with if statements).
            //float val = texture3D( texture, loc )[0];
            //if (val>maxval)            
            //    maxval = val;
        }
    }
    
    // Finaly, apply window-level window-width.
    maxval = ( maxval + scaleBias[1] ) * scaleBias[0];    
    //gl_FragColor = vec4(maxval, maxval, maxval, 1.0);
    
    // Apply colormap.
    gl_FragColor = texture1D( colormap, maxval );
    
    // Apply a depth?
    //gl_FragDepth = 2.0
}
