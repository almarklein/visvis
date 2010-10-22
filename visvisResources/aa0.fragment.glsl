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
uniform vec2 scaleBias;
uniform int applyColormap;

void main()
{      
    
    // get centre location
    vec2 pos= vec2(gl_TexCoord[0]);
    gl_FragColor = texture2D(texture, pos);
    
    // apply window-level window-width
    gl_FragColor.rgb = ( gl_FragColor.rgb + scaleBias[1] ) * scaleBias[0];
    
    // apply colormap
    if (applyColormap == 1)    
        gl_FragColor = texture1D( colormap, gl_FragColor.r );        
    
}
