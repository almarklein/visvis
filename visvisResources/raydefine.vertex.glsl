// the textures
//uniform sampler3D texture; // not used
uniform sampler2D backCoords;

// viewport so we can translate the coordinates...
uniform vec4 viewport;

// the dimensions of the data, to determine stepsize (nx, ny, nz)
uniform vec3 shape;

// ratio to tune the number of steps
uniform float stepRatio;

// varyings to pass to fragment shader
//varying vec3 totalray;
//varying float nsteps;
varying vec3 edgeLoc1;
varying vec3 edgeLoc2;

void main()
{    
    
    // get current pixel location
    //vec3 edgeLoc1 = vec3(1.0,1.0,1.0); //vec3(gl_TexCoord[0]);
    
    // make position right (because we overload the default vertex shader)
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    edgeLoc1 = gl_MultiTexCoord0.xyz;
    //gl_TexCoord[0].xyz = gl_MultiTexCoord0.xyz;
    
    // get normalized screenpos
    //vec2 fragCord = gl_FragCoord.xy;//vec2(0.1,0.1); // gl_FragCoord TODO
    //vec2 screenpos = vec2( (fragCord[0]-viewport[0])/viewport[2], 
    //                       (fragCord[1]-viewport[1])/viewport[3] );
    vec2 screenpos = (gl_Position.xy+1.0)/2.0;
    //vec2 screenpos = ((gl_ModelViewProjectionMatrix * gl_Vertex).xy+1.0)/2.0;
    
    // get texture coordinate of back face
    edgeLoc2 = texture2D( backCoords, screenpos.xy ).rgb;
    
    
}
