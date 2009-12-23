/* Vertex shader to calculate the ray to cast through the volume data.
 * The result is passed to the fragment shader using a varying.
 *
 * This file is part of Visvis.
 * Copyright 2009 Almar Klein
 */

// the dimensions of the data, to determine stepsize
uniform vec3 shape;

// ratio to tune the number of steps
uniform float stepRatio;

// varyings to pass to fragment shader
varying vec3 ray;

void main()
{    
    
    // First of all, set position.
    // (We need to do this because this shader replaces the original shader.)
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
    
    // Store texture coordinate (also a default thing).
    gl_TexCoord[0].xyz = gl_MultiTexCoord0.xyz;
    
    // Get projection matrix for the texture. It is the projection matrix,
    // but with the modelview stuff undone. This makes that it automatically
    // deals with anisotropic data and changes in Axes.daspect.
    mat4 M = gl_ProjectionMatrix * gl_ModelViewMatrixInverse;
    
    // Calculate ray direction, eventually, the ray will point in the view
    // direction expressed in texture coordinates.
    vec4 p1 = vec4(0.0, 0.0, 0.0, 1.0) * M;
    vec4 p2 = vec4(0.0, 0.0, 1.0, 1.0) * M;
    vec3 p11 = vec3(p1[0], p1[1], p1[2]) / p1[3];
    vec3 p22 = vec3(p2[0], p2[1], p2[2]) / p2[3];
    ray = p22-p11;
    
    // Normalize ray to unit length.    
    ray = normalize(ray);
    
    // Make the ray represent the length of a single voxel.
    ray = ray / shape;
    ray = ray * 0.58; // 1 over root of three = 0.577
    
    // Scale ray to take smaller steps.
    ray = ray / stepRatio;
    
}
