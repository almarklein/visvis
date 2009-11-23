// the textures
uniform sampler3D texture; 
uniform sampler2D backCoords;

// viewport so we can translate the coordinates...
uniform vec4 viewport;

// the dimensions of the data, to determine stepsize (nx, ny, nz)
uniform vec3 shape;

// for window level and window width
uniform vec2 scaleBias;

// ratio to tune the number of steps
uniform float stepRatio;

// threshold
uniform float th;


void main()
{    
    
    // get current pixel location
    vec3 edgeLoc1 = vec3(gl_TexCoord[0]);
    
    // get normalized screenpos
    vec2 screenpos = vec2( (gl_FragCoord.x-viewport[0])/viewport[2], 
                           (gl_FragCoord.y-viewport[1])/viewport[3] );
    
    // get texture coordinate of back face
    vec3 edgeLoc2 = texture2D( backCoords, screenpos ).rgb;
    
    // get vector pointing from front to back (total ray)
    vec3 totalray = edgeLoc2 - edgeLoc1;
    
    // uncomment to visualize underlying texture...
    //gl_FragColor = vec4(edgeLoc2.x, edgeLoc2.y, 0.5, 1.0);
    //return;
    
    // Calculate amount of steps required
    // The method is surprisingly simple. If you'd do pytagoras, you would
    // want to reduce the stepsize for rays that are not straigh (the less
    // straight the smaller the steps). By simpy adding the values instead,
    // a very suitable amount of steps results.
    float nf = ( abs(shape[0]*totalray[0]) + abs(shape[1]*totalray[1]) 
                + abs(shape[2]*totalray[2]) );
    int n = int( nf * stepRatio );
    
    // calculate ray
    vec3 ray = totalray / float(n);
    
    // calculate step
    vec3 step = 1.0 / shape;
    // calculate light direction
    //vec3 L = vec3(1.0,2.0,1.0);
    vec3 L = gl_LightSource[0].position.xyz - gl_FragCoord.xyz;
    L = normalize(L);
    // no ideas what this is...
    vec3 V = vec3(0.0,2.0,-1.0);
    V = normalize(V);
    
    
    // init value
    float maxval = 0.0;
    
    // loop!
    for (int i=0; i<n; i++)
    {
        // calculate location        
        vec3 loc = edgeLoc1 + float(i) * ray;
        
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
                vec3 E = normalize(ray);
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


