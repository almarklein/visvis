// the texture
uniform sampler2D texture; 

void main()
{
    gl_FragColor = texture2D(texture, vec2(gl_TexCoord[0]));
    if (gl_FragColor[0] > 0.5)            
    {
        gl_FragColor *= 1.0;
    }
    else
    {
        gl_FragColor *= 0.2;
    }
}