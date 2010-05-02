import visvis as vv
import numpy as np
from visvis.points import Point, Pointset

import OpenGL.GL as gl


# todo: rename to box, or remove completely as the cylinder can make it too!
def solidCube(position=None, scale=None, axes=None):
    """ solidCube(position=Point(0,0,0), scale=Point(0,0,0), axes=None)
    
    Creates a solid cube (or box if you scale it). The position and scale
    may also be 3-element tuples. The position defines the center position
    of the cube.
    """
    
    # Check position and scale
    if isinstance(position, tuple):
        position = Point(position)
    if isinstance(scale, tuple):
        scale = Point(scale)
    
    # Create vertices of a cube
    pp = Pointset(3)
    # Bottom
    pp.Append(-0.5,-0.5,-0.5)
    pp.Append(+0.5,-0.5,-0.5)
    pp.Append(+0.5,+0.5,-0.5)
    pp.Append(-0.5,+0.5,-0.5)
    # Top
    pp.Append(-0.5,-0.5,+0.5)
    pp.Append(-0.5,+0.5,+0.5)
    pp.Append(+0.5,+0.5,+0.5)
    pp.Append(+0.5,-0.5,+0.5)
    
    # Init vertices and normals
    vertices = Pointset(3)
    normals = Pointset(3)
    
    # Create vertices
    for i in [0,1,2,3]: # Top
        vertices.Append(pp[i]); normals.Append(0,0,-1)
    for i in [4,5,6,7]: # Bottom
        vertices.Append(pp[i]); normals.Append(0,0,+1)
    for i in [3,2,6,5]: # Front
        vertices.Append(pp[i]); normals.Append(0,+1,0)
    for i in [0,4,7,1]: # Back
        vertices.Append(pp[i]); normals.Append(0,-1,0)
    for i in [0,3,5,4]: # Left
        vertices.Append(pp[i]); normals.Append(-1,0,0)
    for i in [1,7,6,2]: # Right
        vertices.Append(pp[i]); normals.Append(+1,0,0)
    
    # Create axes
    if axes is None:
        axes = vv.gca()
    
    # Create mesh
    m = vv.Mesh(axes,vertices, normals, type=gl.GL_QUADS)
    
    # Scale and translate
    if position is not None:
        tt = vv.Transform_Translate(position.x, position.y, position.z)    
        m.transformations.append(tt)
    if scale is not None:
        ts = vv.Transform_Scale(scale.x, scale.y, scale.z)
        m.transformations.append(ts)
    
    # Done
    return m


if __name__ == '__main__':
    a = vv.gca()
    a.daspectAuto = 0
    a.cameraType = '3d'
    m2 = solidCube((1,2,1) )
    m1 = solidCube((3,1,1), (2,2,1))
    a.SetLimits((0,5), (0,5), (0,5))
    