/*    
 *    GLSL Fragment shader to create window-level window-width
 *    functionality. Also reduces aliasing by smoothing the data
 *    in a small neighbourhood. The kernel to do this is created
 *    in the application.
 *    
 *    Almar Klein, University of Twente
 *    may 2008
 */

// the texture
uniform sampler2D texture; 

// the parameters (need to be set from the application)

// for window level and window width
uniform vec2 scaleBias;

void main()
{      
    
    // get centre location
    vec2 pos= vec2(gl_TexCoord[0]);
    gl_FragColor = texture2D(texture, pos);
    
    // apply window-level window-width    
    gl_FragColor = ( gl_FragColor + scaleBias[1] ) * scaleBias[0];
    gl_FragColor.a = 1.0;
}
