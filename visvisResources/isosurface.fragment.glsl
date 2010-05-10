/* Fragment shader for isosurface rendering.
 * The ray is cast through the volume until it encounters a user-defined
 * threshold. At that point, the surface normals are calculated to 
 * produce some lighting effects.
 *
 * Currently this renderer is merely a proof of concept; it doesn't look
 * very nice. I haven't read the chapter on lighting in my OpenGl book 
 * yet. Will work on this in the future.
 *
 * This file is part of Visvis.
 * Copyright 2009 Almar Klein
 */

// idea: use the upper or lower value of clim as the threshold?

// the 3D texture and 1D colormap
uniform sampler3D texture;
uniform sampler1D colormap;

// the dimensions of the data, to determine stepsize
uniform vec3 shape;

// varying calculated by vertex shader
varying vec3 ray;
varying vec3 L; // light direction
varying vec3 V; // view direction

// threshold
uniform float th;


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
    
    // round-off errors can cause the value to be very large.
    // an n of 100.000 is pretty save
    if (smallest > 9999.0)
        smallest = 1.0;
    
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
    
    // calculate step
    vec3 step = 1.0 / shape;
    
    
    // loop!
    int i=0;
    while (i<n)
    {
        for (i=i; i<n; i++)
        {
            
            // calculate location        
            vec3 loc = edgeLoc + float(i) * ray2;
            
            // sample value (avoid if statements)
            float val = texture3D( texture, loc )[0];        
            
            if (val > th)
            {
                // calculate normal vector from gradient
                vec4 color1; 
                vec4 color2;
                float betterVal;
                vec3 N; // normal
                color1 = texture3D( texture, loc+vec3(-step[0],0.0,0.0) );
                color2 = texture3D( texture, loc+vec3(step[0],0.0,0.0) );
                N[0] = color1[1] - color2[1];
                betterVal = max(color1.r, color2.r);
                color1 = texture3D( texture, loc+vec3(0.0,-step[1],0.0) );
                color2 = texture3D( texture, loc+vec3(0.0,step[1],0.0) );
                N[1] = color1[1] - color2[1];
                betterVal = max(max(color1.r, color2.r),betterVal);
                color1 = texture3D( texture, loc+vec3(0.0,0.0,-step[2]) );
                color2 = texture3D( texture, loc+vec3(0.0,0.0,step[2]) );
                N[2] = color1[1] - color2[1]; 
                betterVal = max(max(color1.r, color2.r),betterVal);
                N = normalize(N);
                
                // Init reflectanve colors. Maybe make them properties later.
                vec4 ambientRefl = vec4(0.7,0.7,0.7,1.0);
                vec4 diffuseRefl = vec4(0.7,0.7,0.7,1.0);
                vec4 specularRefl = vec4(0.3,0.3,0.3,1.0);
                float shininess = 50.0;
                
                // Init strengt variable
                float str;
                
                // Apply ambient and diffuse light
                gl_FragColor = ambientRefl * gl_LightSource[0].ambient;
                str = clamp(dot(L,N),0.0,1.0);
                gl_FragColor += str * diffuseRefl * gl_LightSource[0].diffuse;
                
                // Apply colormap
                gl_FragColor *= texture1D( colormap, betterVal);
                
                // Apply specular color
                vec3 H = normalize(L+V);
                str = pow( max(dot(H,N),0.0), shininess);
                gl_FragColor += str * specularRefl * gl_LightSource[0].specular;
                
                return;
            }
        
        }
    }
    discard;
    // apply a depth?
    //gl_FragDepth = 2.0
}


