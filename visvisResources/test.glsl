// the textures
uniform sampler3D texture; 
//uniform sampler2D backCoords; // not used

// ratio to tune the number of steps
uniform float stepRatio;

// the dimensions of the data, to determine stepsize (nx, ny, nz)
uniform vec3 shape;

// for window level and window width
uniform vec2 scaleBias;

// varyings received from vertex shader
//varying vec3 totalray;
//varying float nsteps;
varying vec3 edgeLoc1;
varying vec3 edgeLoc2;

void main()
{ 
    //vec3 totalray=vec3(1.0, 1.0, 1.0);
    //float nsteps = 100.0;
    
    // get current pixel location
    //vec3 edgeLoc1 = vec3(gl_TexCoord[0]);
    
    // get vector pointing from front to back (total ray)
    vec3 totalray = edgeLoc2 - edgeLoc1;
    
    // Calculate amount of steps required
    // The method is surprisingly simple. If you'd do pytagoras, you would
    // want to reduce the stepsize for rays that are not straigh (the less
    // straight the smaller the steps). By simpy adding the values instead,
    // a very suitable amount of steps results.
    float nf = ( abs(shape[0]*totalray[0]) + abs(shape[1]*totalray[1]) 
                + abs(shape[2]*totalray[2]) );
    int n = int(nf * stepRatio);
    
    // limit (or only a partial volume will be shown)
    if (n>256)    
        n = 256;
    
    // calculate ray
    vec3 ray = totalray / float(n); // todo: replace with nsteps
    
    // init value
    float maxval = 0.0;
    
    // loop!
    for (int i=0; i<n; i++)
    {
        // calculate location        
        vec3 loc = edgeLoc1 + float(i) * ray;
        
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
    
    // finaly, apply window-level window-width
    gl_FragColor = vec4(maxval,maxval,maxval,1.0);
    gl_FragColor = ( gl_FragColor + scaleBias[1] ) * scaleBias[0];    
    
    
}
