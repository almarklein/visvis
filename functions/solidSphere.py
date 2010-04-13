import visvis as vv
import numpy as np
from visvis.points import Pointset

import OpenGL.GL as gl


def solidSphere(radius=1.0, slices=20, stacks=20):
    """ solidSphere(radius, slices, stacks)
    Creates a solid sphere with quad faces. Slices is the number of
    subdivisions around the Z axis (similar to lines of longitude). 
    Stacks is the number of subdivisions along the Z axis (similar to 
    lines of latitude). 
    """
    
    # Quick access
    pi2 = np.pi*2
    cos = np.cos
    sin = np.sin
    st = stacks
    
    # Obtain vertices
    vertices = Pointset(3)
    for slice in range(slices+1):
        a = np.pi * float(slice) / slices 
        z = cos(a)
        
        for stack in range(stacks):
            b = pi2 * float(stack) / stacks            
            x = cos(b) * sin(a)
            y = sin(b) * sin(a)
            vertices.Append(x,y,z)
    
    # Calc normals and scale
    vertices = vertices.Normalize()
    normals = vertices.Copy()
    vertices = vertices * radius
    
    # Calculate indices
    indices = []
    for j in range(slices):
        for i in range(0,stacks-1):
            indices.extend([j*st+i, j*st+i+1, (j+1)*st+i+1, (j+1)*st+i])
        i = stacks-1
        indices.extend([j*st+i, j*st+0, (j+1)*st+0, (j+1)*st+i])
    j = slices-1
    if False: # last row
        for i in range(0,stacks-1):
            indices.extend([j*st+i, j*st+i+1, 0*st+i+1, 0*st+i])
        i = stacks-1
        indices.extend([j*st+i, j*st+0, 0*st+0, 0*st+i])
    
    # Make indices a numpy array
    indices = np.array(indices, dtype=np.uint32)
    
    # Create texture coordinates
    texcords = Pointset(2)
    for slice in range(slices+1):
        y = float(slice) / slices 
        for stack in range(stacks):
            x = float(stack) / (stacks-1)
            texcords.Append(x,y)
    
    # Create axes and return Patch object
    a = vv.gca()
    p = vv.polygon.Patch(a, vertices, normals, indices, type=gl.GL_QUADS)
    p._texcords = texcords
    return p


if __name__ == '__main__':
    import visvis as vv
    a = vv.cla()
    a.daspectAuto = False
    a.cameraType = '3d'
    a.SetLimits((-2,2),(-2,2),(-2,2))
    #p = vv.polygon.getCube(a)
    p = solidSphere(2)
    p.Draw()