// the textures
uniform sampler3D texture; 
uniform sampler1D backCoords;

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
    //vec2 screenpos = vec2( (gl_FragCoord.x-viewport[0])/viewport[2], 
    //                       (gl_FragCoord.y-viewport[1])/viewport[3] );
    //float screenpos = (gl_FragCoord.x-viewport[0]) + (gl_FragCoord.y-viewport[1])*viewport[2];
    //screenpos = screenpos / (viewport[2]*viewport[3]);
    float screenpos = (gl_FragCoord.x-viewport[0]) + (gl_FragCoord.y-viewport[1]);
    
    // get texture coordinate of back face
    vec3 edgeLoc2 = texture1D( backCoords, screenpos ).rgb;
    
    gl_FragColor = vec4(edgeLoc2,1.0);
    
    
}
