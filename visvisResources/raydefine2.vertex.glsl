// viewport so we can translate the coordinates...
uniform vec4 viewport;

// the dimensions and data aspect of the data, to determine stepsize
uniform vec3 shape;
uniform vec3 daspect;

// ratio to tune the number of steps
uniform float stepRatio;

// varyings to pass to fragment shader
varying vec3 ray;

void main()
{    
    
    // first of all, set position right
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    
    // store texture coordinate
    gl_TexCoord[0].xyz = gl_MultiTexCoord0.xyz;
    
    // get current projection matrix
    mat4 M = gl_ProjectionMatrix;
    
    // calculate ray direction, eventually, the ray will point in the view
    // direction expressed in texture coordinates.
    vec4 p1 = vec4(0.0, 0.0, 0.0, 1.0) * M;
    vec4 p2 = vec4(0.0, 0.0, 1.0, 1.0) * M;
    vec3 p11 = vec3(p1[0], p1[1], p1[2]) / p1[3];
    vec3 p22 = vec3(p2[0], p2[1], p2[2]) / p2[3];
    ray = p22-p11;
    
    // normalize ray to unit length
    ray = normalize(ray);
    
    // correct ray for data size and daspect
    // correct for aspect twice as we probably have to correct the other
    // way than the projection matrix does...
    ray = ray / shape / daspect / daspect;
    
    // scale ray to take smaller steps
    ray = ray * 0.58; // 1 over root of three = 0.577
    ray = ray / stepRatio;
    
}
