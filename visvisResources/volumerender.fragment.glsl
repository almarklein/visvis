/* Fragment shader for 3D texture rendering.
 * This is a generic shader in which simple code can be inserted
 * to make different volume renderers in a simple way.
 *
 * This file is part of Visvis.
 * Copyright 2011 Almar Klein
 */
 
// The 3D texture, and its shape
uniform sampler3D texture;
uniform vec3 shape;

// Ray vector, calculated by vertex shader
varying vec3 ray;

// Vertex position in world coordinates
varying vec4 vertexPosition; 

// More uniforms are inserted here
<<uniforms<<

// Functions can be inserted here
<<functions<<


void main()
{    
    
    // Get current pixel location.
    vec3 edgeLoc = vec3(gl_TexCoord[0]);
    
    // Get number of steps
    int n = calculateSteps(edgeLoc);
    
    // Init iter where the depth should be
    int iter_depth = 0;
    
    
    // Insert more initialization here
    <<pre-loop<<
    
    // Cast ray. For some reason the inner loop is not iterated the whole
    // way for large datasets. Thus this ugly hack. If you know how to do
    // it better, please let me know!
    int i=0;
    while (i<n)
    {
        for (i=i; i<n; i++)
        {
            // Calculate location.
            vec3 loc = edgeLoc + float(i) * ray;
            
            // Insert more loop stuff here
            <<in-loop<<
        }
    }
    
    
    // Insert finalization code here
    <<post-loop<<
    
    
    // Discard fragment if small alpha
    if (gl_FragColor.a < 0.1)
        discard;
    
    // Set depth value
    //
    // Calculate end position in world coordinates
    vec4 position2 = vertexPosition;
    position2.xyz += ray*shape*float(iter_depth);
    // Project to device coordinates and set fragment depth
    vec4 iproj = gl_ModelViewProjectionMatrix * position2;
    iproj.z /= iproj.w;
    gl_FragDepth = (iproj.z+1.0)/2.0;
    
}
