/* Fragment shader to create window-level window-width
 * functionality. Also reduces aliasing by smoothing the data
 * in a small neighbourhood. The kernel to do this is created
 * in the application.
 *
 * This file is part of Visvis.
 * Copyright 2009 Almar Klein
 */

// the textures
uniform sampler2D texture; 
uniform sampler1D colormap; 

// the parameters (need to be set from the application)

// for window level and window width
uniform vec2 scaleBias;
uniform int applyColormap;
// the kernel
uniform vec4 kernel;
// stepsizes
uniform float dx;
uniform float dy;


void main()
{    
    // get centre location
    vec2 centre = vec2(gl_TexCoord[0]);
    
    // get value of the centre
    gl_FragColor = vec4(0.0,0.0,0.0,0.0);
    
    float szef = 1.0;
    
    // convolve
    for (float y=-szef; y<=szef; y+=1.0)
    {
        float sy = sign(y);
        for (float x=-szef; x<=szef; x+=1.0)
        {
            float sx = sign(x);            
            vec2 pos = centre + vec2(dx*x,dy*y);
            float k = kernel[ int(x*sx) ] * kernel[ int(y*sy) ];
            gl_FragColor += texture2D(texture, pos) * k;
        }
    }
    
    // finaly, apply window-level window-width    
    gl_FragColor = ( gl_FragColor + scaleBias[1] ) * scaleBias[0];
    gl_FragColor.a = 1.0;
    
    // apply colormap
    if (applyColormap == 1)    
        gl_FragColor = texture1D( colormap, gl_FragColor.r );   
    
}
