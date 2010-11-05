/* Fragment shader for Maximum Intensity Projection (MIP) rendering.
 * This shader uses a texture with texture coordinates that
 * were obtained in an earlier render pass. It is not used anymore
 * because it does not work on laptop with ATI card, and because the
 * obtaining of the backcoords image produces a lot of overhead. 
 *
 * This file is part of Visvis.
 * Copyright 2009 Almar Klein
 */

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
    
    // limit (or only a partial volume will be shown)
    if (n>256)    
        n = 256;
    
    // calculate ray
    vec3 ray = totalray / float(n);
    
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
