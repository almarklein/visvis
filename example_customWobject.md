# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_customWobject.png](http://wiki.visvis.googlecode.com/hg/images/examples/example_customWobject.png)

```
#!/usr/bin/env python
import visvis as vv
import OpenGL.GL as gl


class CustomWobject(vv.Wobject):
    """ Example Custom wobject.   
    This example is not optimal, it is just to illustrate how Wobject 
    can be subclassed.
    """
    
    def __init__(self, parent):
        vv.Wobject.__init__(self, parent)
    
    def _drawTraingles(self, how, color):
        a = 0, 0, 0
        b = 1, 0, 0
        c = 1, 1, 0
        d = 1, 1, 1
        
        gl.glColor(*color)
        gl.glBegin(how)
        gl.glVertex(*a);  gl.glVertex(*b); gl.glVertex(*c)
        gl.glVertex(*a);  gl.glVertex(*c); gl.glVertex(*d)
        gl.glVertex(*b);  gl.glVertex(*c); gl.glVertex(*d)
        gl.glVertex(*a);  gl.glVertex(*d); gl.glVertex(*b)
        gl.glEnd()
    
    def _GetLimits(self):
        """ Tell the axes how big this object is.
        """ 
        # Get limits
        x1, x2 = 0, 1
        y1, y2 = 0, 1
        z1, z2 = 0, 1
        # Return
        return vv.Wobject._GetLimits(self, x1, x2, y1, y2, z1, z2)
    
    def OnDraw(self):
        """ To draw the object.
        """ 
        self._drawTraingles(gl.GL_TRIANGLES, (0.2, 0.8, 0.4))
        gl.glLineWidth(3)
        self._drawTraingles(gl.GL_LINE_LOOP, (0,0,0))
    
    def OnDrawShape(self, clr):
        """ To draw the shape of the object.
        Only necessary if you want to be able to "pick" this object
        """
        self._drawTraingles(gl.GL_TRIANGLES, clr)
    
    def OnDrawScreen(self):
        """ If the object also needs to draw in screen coordinates.
        Text needs this for instance.
        """
        pass
    
    def OnDestroyGl(self):
        """ To clean up any OpenGl resources such as textures or shaders.
        """
        pass
    
    def OnDestroy(self):
        """ To clean up any other resources.
        """
        pass
    

# Create an instance of this class and set axes limits
a = vv.cla()
c = CustomWobject(a)
a.SetLimits()

# Enter main loop
app = vv.use() # let visvis chose a backend for me
app.Run()

```