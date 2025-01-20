# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv


class Bars3D(vv.Wobject):
    """ Bars3D(parent)
    
    The Bars3D class represents a bar chart. It has a few methods to
    change the appearance of the bars.
    
    This class is a container for a series of Mesh objects created using
    solidBox.
    
    This wobject is created by the function vv.bar3().
    
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
        return locals()
    
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
        return locals()
    
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
        return locals()
    
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
        return locals()
    
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
        return locals()



def bar3(data1, data2=None, data3=None, width=0.75, axesAdjust=True, axes=None):
    """ bar3(*args, width=0.75, axesAdjust=True, axes=None)
    
    Create a 3D bar chart and returns a Bars3D instance that can be
    used to change the appearance of the bars (such as lighting properties
    and color).
    
    Usage
    -----
      * bar3(H, ...) creates bars of specified height.
      * bar3(X, H, ...) also supply their x-coordinates
      * bar3(X, Y, H, ...) supply both x- and y-coordinates
    
    Keyword arguments
    -----------------
    width : scalar
        The width of the bars.
    axesAdjust : bool
        If True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet,
        it is set to False.
    axes : Axes instance
        Display the bars in the given axes, or the current axes if not given.
    
    """
    
    # Pre check
    if True:
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
        xx = list(range(len(hh)))
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
    a = vv.gca()
    b = vv.bar3([1,2,3,2,4,3], width=0.5)
    a.axis.showGrid = 1
    a.axis.xTicks = ['Januari', 'Februari', 'March', 'April', 'May', 'June']
    b.colors = 'rgbcmy'
