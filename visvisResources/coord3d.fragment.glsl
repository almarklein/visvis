/*
Code the texture coordinate in the RGB color components.
*/
uniform sampler3D texture; // is this necesary?

void main()
{
    // get current pixel location
    vec3 edgeLoc = vec3(gl_TexCoord[0]);
    gl_FragColor = vec4( edgeLoc[0], edgeLoc[1], edgeLoc[2], 1.0);
}