#   This file is part of VISVIS.
#    
#   VISVIS is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as 
#   published by the Free Software Foundation, either version 3 of 
#   the License, or (at your option) any later version.
# 
#   VISVIS is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
# 
#   You should have received a copy of the GNU Lesser General Public 
#   License along with this program.  If not, see 
#   <http://www.gnu.org/licenses/>.
#
#   Copyright (C) 2009 Almar Klein

""" Module misc

Various things are defined here, that did not fit nicely in any
other module.

$Author$
$Date$
$Rev$

"""

import sys, os


class OpenGLError(Exception):
    pass


def Property(function):
    """ A property decorator which allows to define fget, fset and fdel
    inside the function.
    Note that the class to which this is applied must inherit from object!
    Code from George Sakkis: http://code.activestate.com/recipes/410698/
    """
    keys = 'fget', 'fset', 'fdel'
    func_locals = {'doc':function.__doc__}
    def probeFunc(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict((k,locals.get(k)) for k in keys))
            sys.settrace(None)
        return probeFunc
    sys.settrace(probeFunc)
    function()
    return property(**func_locals)

    
class Range(object):
    """ Indicates a range ( a minimum and a maximum )
    Range(0,1)
    Range((3,4)) # also works with tuples and lists
    If max max is set smaller than min, the min and max are flipped.    
    """
    def __init__(self, min=0, max=1):
        self.Set(min,max)
    
    def Set(self, min=0, max=1):
        """ Set the values of min and max with one call. 
        Same signature as constructor.
        """
        if isinstance(min, (tuple,list)):
            min, max = min[0], min[1]            
        self._min = float(min)
        self._max = float(max)
        self._Check()
    
    @property
    def range(self):        
        return self._max - self._min
    
    @Property # visvis.Property
    def min():
        """ Get/Set the minimum value of the range. """
        def fget(self):
            return self._min
        def fset(self,value):
            self._min = float(value)
            self._Check()
    
    @Property # visvis.Property
    def max():
        """ Get/Set the maximum value of the range. """
        def fget(self):
            return self._max
        def fset(self,value):
            self._max = float(value)
            self._Check()
    
    def _Check(self):
        """ Flip min and max if order is wrong. """
        if self._min > self._max:
            self._max, self._min = self._min, self._max
    
    def Copy(self):
        return Range(self.min, self.max)
        
    def __repr__(self):
        return "<Range %1.2f to %1.2f>" % (self.min, self.max)


class Position(object):
    """ Indicates a position: left, top, width, height.
    
    It also provides short (x, y, w, h) properties to get/set 
    them and allows setting via indexing. Additionally the properties
    x2, right, y2 and bottom are also provided, which simply calculate
    x+w and y+h respectively. Use these only on a Position instance with 
    all absolute values (can be obtained using InPixels()).
    
    Create using Position(x,y,w,h), or Position(pos), where pos 
    is a 4 element list or tuple, or another Position.
    
    Each element can be either:
    - The integer pixel value in screen coordinates.
    - The relative (floating point) value between 0.0 and 1.0.
    - The value may be negative, in which case the difference from the 
      parent's full width/height is taken. So (-200, 50, 150,-100), with
      a parent's w/h of (500,500) is equal to ( 300, 50, 150, 400), thus
      allowing aligning to the right edge, and easier centering. Negative
      values may also be used with relative values.
    
    Remarks:
    - relative/absoulte/negative values may be mixed.
    - x and y are considered relative on <-1, 1> 
    - w and h are considered relative on [-1, 1]    
    - the value 0 can always be considered absolute    
    """
    
    def __init__(self, *pos):
        
        # initial check
        if len(pos)==0:
            raise ValueError("A position consists of 4 values!")
        if len(pos)==1:
            pos= pos[0]
        
        # special case, another position!
        if isinstance(pos, Position):
            self._x, self._y = pos._x, pos._y
            self._w, self._h = pos._w, pos._h
            self._owner = None
            #self._owner = pos._owner (I don't think we want this!)
            return
        
        # check length
        if not hasattr(pos,'__len__') or len(pos)!=4:
            raise ValueError("A position consists of 4 values!")
        
        # set
        self._x = pos[0]
        self._y = pos[1]
        self._w = pos[2]
        self._h = pos[3]
        
        # init owner, 
        # the wibject sets this in the f_set part of the position property
        self._owner = None
        
        # make sure non-relative items are int
        self._GetRelative()
    
    
    def Copy(self):
        """ Make a copy. Otherwise you'll point to the same object! """
        return Position(self)
    
    
    def _Changed(self):
        """ Notify owner. """
        # an owner is almost always a wibject, which has an event
        # for when this happens ...
        # note to also fire the events for the children!
        if self._owner:           
            if hasattr(self._owner,'eventPosition'):
                self._owner.eventPosition.Fire()                
            for child in self._owner._children:
                if hasattr(child,'position'):
                    child.position._Changed()
    
    
    def _GetRelative(self):
        """ Get a list which items are considered relative.         
        Also int()'s the items which are not.
        """
        # init
        relative = [0,0,0,0]        
        # test
        for i in range(2):
            if self[i] > -1 and self[i] < 1 and self[i]!=0:
                relative[i] = 1
            else:
                # make sure its int
                if i==0:  self._x = int(self._x)
                else:  self._y = int(self._y)
        for i in range(2,4):            
            if self[i] >= -1 and self[i] <= 1 and self[i]!=0:
                relative[i] = 1
            else:
                # make sure its int
                if i==2:  self._w = int(self._w)
                else:  self._h = int(self._h)
                
        # return
        return relative
    
    
    def AsTuple(self):
        """ Return the postion as a tuple of four values. """ 
        return (self._x, self._y, self._w, self._h)
    
    
    def InPixels(self, w_h=None):
        """ Return the position in screen coordinates as a Position. 
        If all coordinates are already absolute, return self.Copy().
        If w_h is given, this is used as the parent's width/height.
        If not, the parent's position is obtained. 
        """
        
        # test if this is easy
        relatives = self._GetRelative()
        negatives = [int(self[i]<0) for i in range(4)]
        if max(relatives)==0 and max(negatives)==0:
            return self.Copy()
        
        
        # test if we can calculate
        if not self._owner or not hasattr(self._owner,'parent'):
            raise Exception("Can only calculate the position in pixels"+
                            " if the position instance is owned by a wibject!")
        # if owner is a figure, it can have negative numbers yes...
        if hasattr(self._owner, '_SwapBuffers'):
            return self.Copy()
        # else, the owner must have a parent...
        if self._owner.parent is None:
            print self._owner
            raise Exception("Can only calculate the position in pixels"+
                            " if the owner has a parent!")
        
        # get width/height of parent
        tmp = self._owner.parent.position.InPixels()
        whwh = (tmp.w, tmp.h, tmp.w, tmp.h)
        
        # calculate!
        pos = self.Copy()
        for i in range(4):
            if relatives[i]:
                pos[i] = pos[i]*whwh[i]
            if negatives[i]:
                pos[i] = whwh[i] + pos[i]
            # make sure it's int (even if user supplied floats > 1)
            pos[i] = int(pos[i]) 
        
        # done
        return pos
    
    
    def __getitem__(self,index):
        if not isinstance(index,int):
            raise IndexError("Position only accepts single indices!")        
        if index==0: return self._x
        elif index==1: return self._y
        elif index==2: return self._w
        elif index==3: return self._h
        else:
            raise IndexError("Position only accepts indices 0,1,2,3!")
    
    def __setitem__(self,index, value):
        if not isinstance(index,int):
            raise IndexError("Position only accepts single indices!")
        if index==0: self._x = value
        elif index==1: self._y = value
        elif index==2: self._w = value
        elif index==3: self._h = value
        else:
            raise IndexError("Position only accepts indices 0,1,2,3!")
        self._Changed()


    def __repr__(self):
        return "<Position %1.2f, %1.2f,  %1.2f, %1.2f>" % (
            self.x, self.y, self.w, self.h)
    
    ## Short named properties
    
    @Property
    def x():
        def fget(self):
            return self._x
        def fset(self,value):
            self._x = value
            self._Changed()
    
    @Property
    def y():
        def fget(self):
            return self._y
        def fset(self,value):
            self._y = value
            self._Changed()
    
    @Property
    def w():
        def fget(self):
            return self._w
        def fset(self,value):
            self._w = value
            self._Changed()
    
    @Property
    def h():
        def fget(self):
            return self._h
        def fset(self,value):
            self._h = value
            self._Changed()
    
    @property
    def x2(self):
        return self._x + self._w
    
    @property
    def y2(self):
        return self._y + self._h
    
    ## Long names properties
    
    @Property
    def left():
        def fget(self):
            return self._x
        def fset(self,value):
            self._x = value
            self._Changed()
    
    @Property
    def top():
        def fget(self):
            return self._y
        def fset(self,value):
            self._y = value
            self._Changed()
    
    @Property
    def width():
        def fget(self):
            return self._w
        def fset(self,value):
            self._w = value
            self._Changed()
    
    @Property
    def height():
        def fget(self):
            return self._h
        def fset(self,value):
            self._h = value
            self._Changed()

    @property
    def right(self):
        return self._x + self._w
    
    @property
    def bottom(self):
        return self._y + self._h
    


## Transform classes for wobjects

class Transform_Base(object):
    """ Base transform object. 
    Inherited by classes for translation, scale and rotation.
    """
    pass
    
class Transform_Translate(Transform_Base):
    """ Translates the wobject. """
    def __init__(self, dx=0.0, dy=0.0, dz=0.0):
        self.dx = dx
        self.dy = dy
        self.dz = dz
    
class Transform_Scale(Transform_Base):
    """ Scales the wobject. """
    def __init__(self, sx=1.0, sy=1.0, sz=1.0):
        self.sx = sx
        self.sy = sy
        self.sz = sz

class Transform_Rotate(Transform_Base):
    """ Rotates the wobject. 
    Angle is in degrees. Use angleInRadians to specify the angle 
    in radians, which is then converted in degrees. """
    def __init__(self, angle=0.0, ax=0, ay=0, az=1, angleInRadians=None):
        if angleInRadians is not None:
            angle = angleInRadians * 180 / np.pi 
        self.angle = angle
        self.ax = ax
        self.ay = ay
        self.az = az

## Colour stuff

colours = { 'k':(0,0,0), 'w':(1,1,1), 'r':(1,0,0), 'g':(0,1,0), 'b':(0,0,1),
            'c':(0,1,1), 'y':(1,1,0), 'm':(1,0,1) }

def getColor(value, descr='getColor'):
    """ Make sure a value is a color. """
    tmp = ""
    if not value:
        value = None
    elif isinstance(value, (str, unicode)):
        if value not in 'rgbycmkw':
            tmp = "string color must be one of 'rgbycmkw' !"
        else:
            value = colours[value]
    elif isinstance(value, (list, tuple)):
        if len(value) != 3:
            tmp = "tuple color must be length 3!"                
        value = tuple(value)
    else:
        tmp = "color must be a three element tuple or a character!"
    # error or ok?
    if tmp:
        raise ValueError("Error in %s: %s" % (descr, tmp) )        
    return value


## some functions 

def isFrozen():
    """ Find out whether this is a frozen application
    (using bbfreeze or py2exe) by finding out what was
    the executable name to start the application.
    """
    import os
    ex = os.path.split(sys.executable)[1]
    ex = os.path.splitext(ex)[0]
    if ex.lower() == 'python':
        return False
    else:
        return True


def getResourceDir():
    """ Get the directory to the resources. """
    if isFrozen():
        path =  os.path.abspath( os.path.dirname(sys.executable) )
    else:
        path = os.path.abspath( os.path.dirname(__file__) )
    return os.path.join(path, 'visvisResources')


