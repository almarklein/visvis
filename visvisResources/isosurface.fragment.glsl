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

// the 3D texture
uniform sampler3D texture;

// the dimensions of the data, to determine stepsize
uniform vec3 shape;

// varying calculated by vertex shader
varying vec3 ray;

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
    // calculate light direction
    //vec3 L = vec3(1.0,2.0,1.0);
    vec3 L = gl_LightSource[0].position.xyz - gl_FragCoord.xyz;
    L = normalize(L);
    // no ideas what this is...
    vec3 V = vec3(0.0,2.0,-1.0);
    V = normalize(V);
    
    
    
    // loop!
    for (int i=0; i<n; i++)
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
            vec3 N; // normal
            color1 = texture3D( texture, loc+vec3(-step[0],0.0,0.0) );
            color2 = texture3D( texture, loc+vec3(step[0],0.0,0.0) );
            N[0] = color1[1] - color2[1];
            color1 = texture3D( texture, loc+vec3(0.0,-step[1],0.0) );
            color2 = texture3D( texture, loc+vec3(0.0,step[1],0.0) );
            N[1] = color1[1] - color2[1];
            color1 = texture3D( texture, loc+vec3(0.0,0.0,-step[2]) );
            color2 = texture3D( texture, loc+vec3(0.0,0.0,step[2]) );
            N[2] = color1[1] - color2[1];            
            N = normalize(N);
            
            
            // calculate lambertian
            float lambert = dot(N,L);
            
            // default color
            gl_FragColor = vec4(0.0, 0.0, 1.0, 1.0);
            
            if (lambert > 0.0)
            {
                // self-shadow
                gl_FragColor += gl_LightSource[0].diffuse * 
                    gl_FrontMaterial.diffuse * lambert;
                /*
                // specular does not really work yet
                vec3 E = normalize(ray2);
                vec3 R = reflect(-L, N);
                float specular = pow( max(dot(R, E), 0.0), 
                    gl_FrontMaterial.shininess );
                gl_FragColor += 0.01*gl_LightSource[0].specular * 
                    gl_FrontMaterial.specular *  specular;   
                */
            }
            return;
            
            /*
            // DJ solution
            float Id = dot(N,L);
            vec3 R = 2.0 * dot(N, L) * N - L;
            float Is = max(pow(dot(R,V),3.0),0.0);
            
            gl_FragColor[0] = min(0.7+Id+Is,1.0);
            gl_FragColor[1] = min(Is,1.0);
            gl_FragColor[2] = min(Is,1.0);
            return;
            */
        
        }
    }
    discard;
    // apply a depth?
    //gl_FragDepth = 2.0
}


