
// the texture
uniform sampler3D texture;
uniform sampler2D backCords;
uniform sampler1D colormap;

// the dimensions and data aspect of the data, to determine stepsize
uniform vec3 shape;
uniform vec3 daspect;

// for window level and window width
uniform vec2 scaleBias;

// the parameters (need to be set from the application)
uniform float fast;


float distanceToPlane(vec3 p, vec3 d, vec4 P)
{
    // calculate the distance of a point p to a plane P along direction d.
    // plane P is defined as ax + by + cz = d    
    // line is defined as two points on that line
        
    // calculate nominator and denominator
    float nom = -( dot(P.rgb,p) - P[3] );
    float denom =  dot(P.rgb,d);
    // return zero if either is zero
    float tmp = nom*denom;
    if (tmp==0.0)
        return 0.0;
    else
        return nom / denom;
}

void main()
{    
    /*
    // Only process frontfacing fragments.
    // My laptop's ATI X1300 cannot do gl_FrontFacing in hardware mode...
    // We'll discard fragments based on the ray direction below.
    // I may sometime uncomment this code on my PC with nvidia card for debug.
    if (!gl_FrontFacing)
    {
        gl_FragColor = vec4(0.8, 0.0, 0.0, 1.0);
        return;
    } 
    */
    
    // get current pixel location
    vec3 edgeLoc = vec3(gl_TexCoord[0]);
    
    // get current projection matrix
    mat4 M = gl_ProjectionMatrix;
    
    // calculate ray direction, eventually, the ray will point in the view
    // direction expressed in texture coordinates.
    vec4 p1 = vec4(0.0, 0.0, 0.0, 1.0) * M;
    vec4 p2 = vec4(0.0, 0.0, 1.0, 1.0) * M;
    vec3 p11 = vec3(p1[0], p1[1], p1[2]) / p1[3];
    vec3 p22 = vec3(p2[0], p2[1], p2[2]) / p2[3];
    vec3 ray = p22-p11;
    
    // normalize ray to unit length
    ray = normalize(ray);
    
    /* When only drawing frontfacing, this is not required
    // If I would take one step, am I still inside my volume?
    // If not, discard this fragment
    vec3 oneStep = edgeLoc + 0.0001*ray;
    bool stop = false;
    if (oneStep.x < 0.0 || oneStep.y < 0.0 || oneStep.z < 0.0)
        stop = true;
    if (oneStep.x > 1.0 || oneStep.y > 1.0 || oneStep.z > 1.0 )
        stop = true;
    if (stop)
    {
        //gl_FragColor = vec4(1.0,0.0,0.0,1.0);
        //return;
        discard;
    }
    */
    
    // correct ray for data size and daspect
    // correct for aspect twice as we probably have to correct the other
    // way than the projection matrix does...
    ray = ray / shape / daspect / daspect;
    
    // scale ray to take smaller steps
    if (fast==0.0)
        ray = ray * 0.58; // 1 over root of three = 0.577
    else
        ray = ray * 2.0;
    
    // intersection with the six planes
    vec3 t1;
    t1.x = distanceToPlane(edgeLoc, ray, vec4(1.0, 0.0, 0.0, 0.0)); //x=0
    t1.y = distanceToPlane(edgeLoc, ray, vec4(0.0, 1.0, 0.0, 0.0)); //y=0
    t1.z = distanceToPlane(edgeLoc, ray, vec4(0.0, 0.0, 1.0, 0.0)); //z=0
    vec3 t2;
    t2.x = distanceToPlane(edgeLoc, ray, vec4(1.0, 0.0, 0.0, 1.0)); //x=1
    t2.y = distanceToPlane(edgeLoc, ray, vec4(0.0, 1.0, 0.0, 1.0)); //y=1    
    t2.z = distanceToPlane(edgeLoc, ray, vec4(0.0, 0.0, 1.0, 1.0)); //z=1
    // find smallest distance that is positive
    float smallest = 9999999.0;
    for (int i=0; i<3; i++)
    {
        if (t1[i] > 0.0 && t1[i] < smallest)
            smallest = t1[i];
        if (t2[i] > 0.0 && t2[i] < smallest)
            smallest = t2[i];
    }
    // define amount of steps to take
    int n = int(smallest*1.0)-1;
    
    // init. remember that we made sure that the total range of the data is 
    // mapped between 0 and 1 (also for signed data types).
    float maxval = 0.0;
    
    // cast ray. For some reason the inner loop is not iterated the whole
    // way for large datasets. This hack solves the problem...
    int i=0;
    while (i<n)
    {
        for (i=i; i<n; i++)
        {
            // calculate location        
            vec3 loc = edgeLoc + float(i) * ray;
            
            
            // sample value (avoid if statements)
            float val = texture3D( texture, loc )[0];        
            float r = float(val>maxval);
            maxval = (1.0-r)*maxval + r*val;
            
            /*
            // sample value (with if statements)
            float val = texture3D( texture, loc )[0];
            if (val>maxval)            
                maxval = val;
            */
        }
        // apply now, I think the algorithm sometimes prematurely 
        // exists
        gl_FragColor = vec4(maxval,maxval,maxval,1.0);   
    }
    
    // finaly, apply window-level window-width
    maxval = ( maxval + scaleBias[1] ) * scaleBias[0];    
    //gl_FragColor = vec4(maxval, maxval, maxval, 1.0);
    
    // apply colormap
    gl_FragColor = texture1D( colormap, maxval );
    
    
    // apply a depth?
    //gl_FragDepth = 2.0
}
