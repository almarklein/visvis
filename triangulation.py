import visvis as vv
from visvis.points import Point, Pointset
import numpy as np

import OpenGL.GL as gl

def drawSphere(ndiv=3, radius=1.0):
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
    
    # Create indices
    tindices = [
        [0,4,1], [0,9,4], [9,5,4], [4,5,8], [4,8,1],    
        [8,10,1], [8,3,10], [5,3,8], [5,2,3], [2,7,3],    
        [7,10,3], [7,6,10], [7,11,6], [11,0,6], [0,1,6], 
        [6,1,10], [9,0,11], [9,11,2], [9,2,5], [7,2,11] ]
    tindices = np.array(tindices, dtype=np.uint32)
    
    # todo: make matrices and draw using vertex array
    def drawtri(a, b, c, div, r):
        if (div<=0):
            gl.glNormal3fv(a.data); gl.glVertex3f(a[0]*r, a[1]*r, a[2]*r);
            gl.glNormal3fv(b.data); gl.glVertex3f(b[0]*r, b[1]*r, b[2]*r);
            gl.glNormal3fv(c.data); gl.glVertex3f(c[0]*r, c[1]*r, c[2]*r);
        else:
            ab = Point(0,0,0)
            ac = Point(0,0,0)
            bc = Point(0,0,0)
            for i in range(3):
                ab[i]=(a[i]+b[i])/2.0;
                ac[i]=(a[i]+c[i])/2.0;
                bc[i]=(b[i]+c[i])/2.0;
            ab = ab.Normalize(); ac = ac.Normalize(); bc = bc.Normalize()
            drawtri(a, ab, ac, div-1, r)
            drawtri(b, bc, ab, div-1, r)
            drawtri(c, ac, bc, div-1, r)
            drawtri(ab, bc, ac, div-1, r)
        
    
    
    # Draw
    gl.glBegin(gl.GL_TRIANGLES)
    for i in range(20):
        drawtri(vdata[tindices[i][0]], vdata[tindices[i][1]], vdata[tindices[i][2]], ndiv, radius);
    gl.glEnd()
    

# todo: names ...
class Patch(vv.Wobject):
    def OnDraw(self):
        
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
        
        # Create quads (taken from Texture3D._CreateQuads)
        indices = [0,1,2,3, 4,5,6,7, 3,2,6,5, 0,4,7,1, 0,3,5,4,]# 1,7,6,2]
        indices = np.array(indices,dtype=np.uint8)
        
        # Create normals
        # Note that this is true for the discrete case
        nn = Pointset(3)
        for p in pp:
            nn.Append(1*p.Normalize())
        
        # Prepare for drawing
        gl.glEnable(gl.GL_NORMALIZE)  # gl.GL_RESCALE_NORMAL
#         gl.glEnableClientState(gl.GL_VERTEX_ARRAY)        
#         gl.glVertexPointerf(pp.data)
#         gl.glNormalPointerf(nn.data)
        gl.glFrontFace(gl.GL_CW)
        
        
        white_light = np.array([1.0,1.0,1.0,1.0], dtype=np.float32)
        lmodel_amb = np.array([0.1, 0.1, 0.1, 1.0], dtype=np.float32)
        mat_shin = np.array([51], dtype=np.float32)
        
        # Prepare material
#         gl.glColor(1,0,0)
        gl.glMaterial(gl.GL_FRONT, gl.GL_AMBIENT, (0,0,1,1))
        gl.glMaterial(gl.GL_FRONT, gl.GL_DIFFUSE, (1,0,0,1))
        gl.glMaterial(gl.GL_FRONT, gl.GL_SPECULAR, (0,0.3,1,1))
#         gl.glMaterial(gl.GL_BACK, gl.GL_EMISSION, (0,0.8,0,1))
        gl.glMaterial(gl.GL_FRONT, gl.GL_SHININESS, 40)
        
        # Prepare lights
        gl.glShadeModel(gl.GL_SMOOTH)
#         gl.glShadeModel(gl.GL_FLAT)
#         gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, (0.1,0.1,1,0))
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, white_light)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, white_light)
        gl.glLightModelfv(gl.GL_LIGHT_MODEL_AMBIENT, lmodel_amb)
        # Apply the line below if mapping textures
#         gl.glLightModelfv(gl.GL_LIGHT_MODEL_COLOR_CONTROL, gl.GL_SEPARATE_SPECULAR_COLOR)
        gl.glLightModelfv(gl.GL_LIGHT_MODEL_TWO_SIDE, 1.0)
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        
        
        # Draw
        drawSphere(2)
#         gl.glDrawElements(gl.GL_QUADS, len(indices), gl.GL_UNSIGNED_BYTE, indices)
        gl.glFlush()
        
        # Clean up
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_LIGHTING)


if __name__ == '__main__':
    
    a = vv.cla()
    a.daspectAuto = False
    a.cameraType = '3d'
    a.SetLimits((-3,3),(-3,3),(-3,3))
    p = Patch(a)
    p.Draw()
    