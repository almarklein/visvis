import visvis as vv
import numpy as np
from visvis.points import Point, Pointset

import OpenGL.GL as gl

def solidCylinder(translation=None, scale=None, slices=16, stacks=16, axes=None):
    """ solidCylinder(translation=None, scale=None, slices=16, stacks=16, axes=None)
    
    Creates a cylinder object. Position is a 3-element tuple or a Point instance.
    Scale is a scalar, 3-element tuple or Point instance.
    
    Slices is the number of subdivisions around its axis. Stacks is the
    number of subdivisions along its axis.
    
    If slices <= 8, the edges are modeled as genuine edges. So with faces=4,
    a box can be obtained. If slices>8, the normals vary smoothly
    over the faces which makes the object look rounder.
    """
    
    # Note that the number of vertices around the axis is slices+1. This
    # would not be necessary per see, but it helps create a nice closed
    # texture when it is mapped. There are slices number of faces though.
    # Similarly, to obtain stacks faces along the axis, we need stacks+1
    # vertices.
    
    # Check position
    if isinstance(translation, tuple):
        translation = Point(translation)
    
    # Check scale
    if isinstance(scale, tuple):
        scale = Point(scale)
    elif isinstance(scale, (float, int)):
        scale = Point(scale, scale, scale)
    
    # Quick access
    pi2 = np.pi*2
    cos = np.cos
    sin = np.sin
    sl = slices+1
    
    # Calculate vertices, normals and texcords
    vertices = Pointset(3)
    normals = Pointset(3)
    texcords = Pointset(2)
    # Round part
    for stack in range(stacks+1):
        z = 1.0 - float(stack)/stacks # between 0 and 1
        v = float(stack)/stacks
        #
        for slice in range(slices+1):
            b = pi2 * float(slice) / slices
            u = float(slice) / (slices)
            x = cos(b)
            y = sin(b)
            vertices.Append(x,y,z)
            normals.Append(x,y,0)
            texcords.Append(u,v)
    # Top
    for stack in range(2):
        for slice in range(slices+1):
            b = pi2 * float(slice) / slices
            u = float(slice) / (slices)
            x = cos(b) * stack # todo: check welke frontfacing!
            y = sin(b) * stack
            vertices.Append(x,y,1)
            normals.Append(0,0,1)
            texcords.Append(u,0)
    # Bottom
    for stack in range(2):
        for slice in range(slices+1):
            b = pi2 * float(slice) / slices
            u = float(slice) / (slices)
            x = cos(b) * (1-stack)
            y = sin(b) * (1-stack)
            vertices.Append(x,y,0)
            normals.Append(0,0,-1)
            texcords.Append(u,1)
    
    # Normalize normals
    normals = normals.Normalize()
    
    # Calculate indices
    indices = []
    for j in range(stacks):
        for i in range(slices):
            indices.extend([j*sl+i, j*sl+i+1, (j+1)*sl+i+1, (j+1)*sl+i])
    j = stacks+1
    for i in range(slices):
        indices.extend([j*sl+i, j*sl+i+1, (j+1)*sl+i+1, (j+1)*sl+i])
    j = stacks+3
    for i in range(slices):
        indices.extend([j*sl+i, j*sl+i+1, (j+1)*sl+i+1, (j+1)*sl+i])
    
    # Make indices a numpy array
    indices = np.array(indices, dtype=np.uint32)
    
    # Make edges appear as edges, for pyramids for example
    if slices <= 8:
        newVertices = Pointset(3)
        newNormals = Pointset(3)
        newTexcords = Pointset(2)
        for i in range(0,len(indices),4):
            ii = indices[i:i+4]
            # Obtain average normal
            tmp = Point(0,0,0)
            for j in range(4):
                tmp += normals[ii[j]]
            tmp = tmp.Normalize()
            # Unroll vertices and texcords, set new normals
            for j in range(4):
                newVertices.Append( vertices[ii[j]] )
                newNormals.Append( tmp )
                newTexcords.Append( texcords[ii[j]] )
        # Apply
        vertices = newVertices
        normals = newNormals
        texcords = newTexcords
        indices = None
    
    # Create axes 
    if axes is None:
        axes = vv.gca()
    
    # Create mesh
    m = vv.Mesh(axes, vertices, normals, indices, 
        texcords=texcords, type=gl.GL_QUADS)
    
    # Scale and translate
    if translation is not None:
        tt = vv.Transform_Translate(translation.x, translation.y, translation.z)    
        m.transformations.append(tt)
    if scale is not None:
        ts = vv.Transform_Scale(scale.x, scale.y, scale.z)
        m.transformations.append(ts)
    
    # Done
    return m


if __name__ == '__main__':
    import visvis as vv
    a = vv.cla()
    a.daspectAuto = False
    a.cameraType = '3d'
    a.SetLimits((-2,2),(-2,2),(-2,2))
    
    # Create sphere
    m = solidCylinder(slices=6)
    m2 = solidCylinder(translation=(0,0,0.1), scale=(0.5,0.5,2.5))
    im = vv.imread('lena.png')
    m2.SetTexture(im)    
    m.Draw()
    
#     data = np.linspace(0,1,m._vertices.shape[0])
#     m.SetTexcords(data.astype(np.float32))