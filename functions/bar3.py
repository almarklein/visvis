# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv


class Bars3D(vv.Wobject):
    """ Bars3D(parent)
    
    The Bars3D class represents a bar chart. It has a few methods to
    change the appearance of the bars.
    
    This class is a container for a series of Mesh objects created using 
    solidBox.
    
    """
    
    @vv.misc.Property
    def ambient():
        """ Get/Set the ambient reflectance of the bars. 
        The getter returns the ambient reflectance of the first bar, 
        or None if there are no bars.
        """
        def fget(self):
            if self._children:
                return self._children[0].ambient
            else:
                return None
        def fset(self, value):
            for child in self.children:
                child.ambient = value
    
    @vv.misc.Property
    def diffuse():
        """ Get/Set the diffuse reflectance of the bars. 
        The getter returns the diffuse reflectance of the first bar, 
        or None if there are no bars.
        """
        def fget(self):
            if self._children:                
                return self._children[0].diffuse
            else:
                return None
        def fset(self, value):
            for child in self.children:
                child.diffuse = value
    
    @vv.misc.Property
    def specular():
        """ Get/Set the specular reflectance of the bars. 
        The getter returns the specular reflectance of the first bar, 
        or None if there are no bars.
        """
        def fget(self):
            if self._children:                
                return self._children[0].specular
            else:
                return None
        def fset(self, value):
            for child in self.children:
                child.specular = value
    
    @vv.misc.Property
    def color():
        """ Get/Set the color of the bars. The getter returns the color
        of the first bar, or None if there are no bars.
        """
        def fget(self):
            if self._children:                
                return self._children[0].faceColor
            else:
                return None
        def fset(self, value):
            for child in self.children:
                child.faceColor = value
    
    @vv.misc.Property
    def colors():
        """ Get/Set the colors of all bars at once. The number of colors
        should match the number of bars. """
        def fget(self):
            if self._children:                
                return [child.faceColor for child in self.children 
                                    if hasattr(child, 'faceColor')]
            else:
                return None
        def fset(self, value):
            for child, color in zip(self.children, value):
                child.faceColor = color
    


def bar3(data1, data2=None, data3=None, width=0.75, axesAdjust=True, axes=None):    
    """ bar3(*args, width=0.75, axesAdjust=True, axes=None)
    
    Create a 3D bar chart and returns a Bars3D instance that can be
    used to change the appearance of the bars (such as lighting properties
    and color).
    
    bar3(H, ...) creates bars of specified height.
    bar3(X, H, ...) also supply their x-coordinates
    bar3(X, Y, H, ...) supply both x- and y-coordinates
    
    If axesAdjust==True, this function will call axes.SetLimits(), set
    the camera type to 2D when plotting 2D data and to 3D when plotting
    3D data. If daspectAuto has not been set yet, it is set to True.
    """
    
    # Pre check
    if data1 is not None:
        try:
            if not hasattr(data1, '__len__'):
                raise ValueError
            data1 = [float(val) for val in data1]
        except Exception:
            raise ValueError('bar3 needs a sequence of numbers.')
    if data2 is not None:
        try:
            if not hasattr(data2, '__len__'):
                raise ValueError
            data2 = [float(val) for val in data2]
        except Exception:
            raise ValueError('bar3 needs a sequence of numbers.')
    if data3 is not None:
        try:
            if not hasattr(data3, '__len__'):
                raise ValueError
            data3 = [float(val) for val in data3]
        except Exception:
            raise ValueError('bar3 needs a sequence of numbers.')
    
    # Parse input
    if data2 is None and data3 is None:
        # Only height given
        hh = data1
        xx = range(len(hh))
        yy = [0] * len(hh)
    elif data3 is None:
        # Height and x given
        xx = data1
        hh = data2
        yy = [0] * len(hh)
    else:
        # All three given
        xx = data1
        yy = data2
        hh = data3
    
    # Check
    if len(hh) != len(xx) or len(hh) != len(yy):
        raise ValueError('Given arrays for bar3 must be of equal length.')
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create Bars instance
    bars = Bars3D(axes)
    
    # Create boxes    
    for x,y,h in zip(xx,yy, hh):
        pos = (x,y,h/2.0)
        scale = (width,width,h)
        m = vv.solidBox(pos, scale, axesAdjust=False, axes=bars)
        m.specular = 0
    
   # Adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = False
        axes.cameraType = '3d'
        axes.SetLimits()
    
    # Done
    axes.Draw()
    return bars
    
    
    
if __name__ == '__main__':
    vv. figure()    
    b = bar3([1,2,3,2,4,3], width=0.5) 
    a = vv.gca()
    a.axis.showGrid = 1
    a.axis.xTicks = ['Januari', 'Februari', 'March', 'April', 'May', 'June']
    b.colors = 'rgbcmy'
    
    