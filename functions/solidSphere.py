import visvis as vv
import numpy as np
from visvis.points import Point, Pointset

import OpenGL.GL as gl

# Alternative implementation bu subdeivinding a tetrahedon,
# but not as good for mapping textures.
def getSphere(ndiv=3, radius=1.0):
    # Example taken from the Red book, end of chaper 2.
    
    # Define constants
    X = 0.525731112119133606 
    Z = 0.850650808352039932
    
    # Creta vdata
    vdata = Pointset(3)
    app = vdata.Append
    app(-X, 0.0, Z); app(X, 0.0, Z); app(-X, 0.0, -Z); app(X, 0.0, -Z)
    app(0.0, Z, X); app(0.0, Z, -X); app(0.0, -Z, X); app(0.0, -Z, -X)
    app(Z, X, 0.0); app(-Z, X, 0.0); app(Z, -X, 0.0); app(-Z, -X, 0.0)
    
    # Create faces
    tindices = [
        [0,4,1], [0,9,4], [9,5,4], [4,5,8], [4,8,1],    
        [8,10,1], [8,3,10], [5,3,8], [5,2,3], [2,7,3],    
        [7,10,3], [7,6,10], [7,11,6], [11,0,6], [0,1,6], 
        [6,1,10], [9,0,11], [9,11,2], [9,2,5], [7,2,11] ]
    tindices = np.array(tindices, dtype=np.uint32)
    
    # Init vertex array
    vertices = Pointset(3)
    
    # Define function to recursively create vertices and normals
    def drawtri(a, b, c, div):
        if (div<=0):
            vertices.Append(a)
            vertices.Append(b)
            vertices.Append(c)
        else:
            ab = Point(0,0,0)
            ac = Point(0,0,0)
            bc = Point(0,0,0)
            for i in range(3):
                ab[i]=(a[i]+b[i])/2.0;
                ac[i]=(a[i]+c[i])/2.0;
                bc[i]=(b[i]+c[i])/2.0;
            ab = ab.Normalize(); ac = ac.Normalize(); bc = bc.Normalize()
            drawtri(a, ab, ac, div-1)
            drawtri(b, bc, ab, div-1)
            drawtri(c, ac, bc, div-1)
            drawtri(ab, bc, ac, div-1)
    
    # Create vertices
    for i in range(20):
        drawtri(    vdata[tindices[i][0]], 
                    vdata[tindices[i][1]], 
                    vdata[tindices[i][2]], 
                    ndiv )
    
    # Create normals and scale vertices
    normals = vertices.Copy()
    vertices *= radius
    
    # Done
    return vertices, normals

# todo: rename to elipsoid?
def solidSphere(radius=1.0, translation=None, slices=16, stacks=16, axes=None):
    """ solidSphere(radius=1.0, translation=None, slices=16, stacks=16, axes=None)
    
    Creates a solid sphere with quad faces. Slices is the number of
    subdivisions around the Z axis (similar to lines of longitude). 
    Stacks is the number of subdivisions along the Z axis (similar to 
    lines of latitude). 
    """
    
    # Note that the number of vertices around the axis is slices+1. This
    # would not be necessary per see, but it helps create a nice closed
    # texture when it is mapped. There are slices number of faces though.
    # Similarly, to obtain stacks faces along the axis, we need stacks+1
    # vertices.
    
    # Check position
    if isinstance(translation, tuple):
        translation = Point(translation)
    
    
    # Quick access
    pi2 = np.pi*2
    cos = np.cos
    sin = np.sin
    sl = slices+1
    
    # Calculate vertices, normals and texcords
    vertices = Pointset(3)
    normals = Pointset(3)
    texcords = Pointset(2)
    # Cone
    for stack in range(stacks+1):
        a = np.pi * float(stack) / stacks
        z = cos(a)
        v = float(stack)/stacks
        #
        for slice in range(slices+1):
            b = pi2 * float(slice) / slices
            u = float(slice) / (slices)
            x = cos(b) * sin(a)
            y = sin(b) * sin(a)
            vertices.Append(x,y,z)
            normals.Append(x,y,z)
            texcords.Append(u,v)
    
    # Calculate indices
    indices = []
    for j in range(stacks):
        for i in range(slices):
            indices.extend([j*sl+i, j*sl+i+1, (j+1)*sl+i+1, (j+1)*sl+i])
    
    # Make indices a numpy array
    indices = np.array(indices, dtype=np.uint32)
    
    
    # Create axes 
    if axes is None:
        axes = vv.gca()
    
    # Create mesh
    m = vv.Mesh(axes, vertices, normals, indices, 
        texcords=texcords, verticesPerFace=4)
    
    # Scale and translate
    if translation is not None:
        tt = vv.Transform_Translate(translation.x, translation.y, translation.z)    
        m.transformations.append(tt)
    
    # Done
    return m


if __name__ == '__main__':
    import visvis as vv
    a = vv.cla()
    a.daspectAuto = False
    a.cameraType = '3d'
    a.SetLimits((-2,2),(-2,2),(-2,2))
    
    # Create sphere
    m = solidSphere(3,(1,1,1))
    im = vv.imread('lena.png')
    m.SetTexture(im)    
    m.Draw()
    
#     data = np.linspace(0,1,m._vertices.shape[0])
#     m.SetTexcords(data.astype(np.float32))