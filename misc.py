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
import OpenGL.GL as gl

class OpenGLError(Exception):
    pass


# get opengl version
_glInfo = [None]*4

def getOpenGlInfo():
    """ getOpenGlInfo()
    Get information about the OpenGl version on this system. 
    Returned is a tuple (version, vendor, renderer, extensions) 
    Note that this function will return 4 Nones if the openGl 
    context is not set. 
    """
    if not _glInfo[0]:
        _glInfo[0] = gl.glGetString(gl.GL_VERSION)
        _glInfo[1] = gl.glGetString(gl.GL_VENDOR)
        _glInfo[2] = gl.glGetString(gl.GL_RENDERER)
        _glInfo[3] = gl.glGetString(gl.GL_EXTENSIONS)
    return tuple(_glInfo)

_glLimitations = {}
def getOpenGlCapable(version, what=None):
    """ getOpenGlCapable(version, what)
    Returns True if the OpenGl version on this system is equal or higher 
    than the one specified and False otherwise.
    If False, will display a message to inform the user, but only the first 
    time that this limitation occurs (identified by the second argument).
    """
    
    # obtain version of system
    curVersion = _glInfo[0]
    if not curVersion:
        curVersion, dum1, dum2, dum3 = getOpenGlInfo()
        if not curVersion:
            return False # OpenGl context not set, better safe than sory
    
    # make sure version is a string
    if isinstance(version, (int,float)):
        version = str(version)
    
    # test
    if curVersion >= version :
        return True
    else:
        # print message?
        if what and (what not in _glLimitations):
            _glLimitations[what] = True
            tmp = "Warning: the OpenGl version on this system is too low "
            tmp += "to support " + what + ". "
            tmp += "Try updating your drives or buy a new (nvidia) video card."
            print tmp
        return False


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
    """ Indicates a position: x, y, w, h.
    
    It provides short (x, y, w, h) properties to change the position
    and allows getting/setting via indexing. 
    
    Create using Position(x,y,w,h), or Position(pos), where pos 
    is a 4 element list or tuple, or another Position.
    
    Each element can be either:
    - The integer pixel value in screen coordinates.
    - The relative (floating point) value between 0.0 and 1.0.
    - The value may be negative. For the width and height the difference 
      from the parent's full width/height is taken. So (-200, 50, 150,-100), 
      with a parent's w/h of (500,500) is equal to ( -200, 50, 150, 400), thus
      allowing aligning to the right/bottom edge, and easier centering. 
      Negative values may also be used with relative values.
    
    Remarks:
    - relative/absoulte/negative values may be mixed.
    - x and y are considered relative on <-1, 1> 
    - w and h are considered relative on [-1, 1]    
    - the value 0 can always be considered absolute 
    
    The long named properties express the position in pixel coordinates.
    Internally a version in pixel coordinates is buffered, which is kept
    up to date. These long named (read-only) properties are:
    left, top, width, height, right, bottom, topLeft, bottomRight, size.
    (the latter three return two-element tuples)
    
    """
    
    def __init__(self, *pos):
        
        # initial check
        if len(pos)==1:
            pos= pos[0]
        
        # special case, another position!
        if isinstance(pos, Position):
            self._x, self._y = pos._x, pos._y
            self._w, self._h = pos._w, pos._h
            self._inpixels = pos._inpixels
            self._owner = None # don't copy the owner
            return
        
        # check length
        if not hasattr(pos,'__len__') or len(pos)!=4:
            raise ValueError("A position consists of 4 values!")
        
        # set
        self._x, self._y, self._w, self._h = pos[0], pos[1], pos[2], pos[3]
        
        # init position in pixels (as a tuple)
        self._inpixels = None
        
        # init owner, 
        # the wibject sets this in the f_set part of the position property
        self._owner = None
    
    
    
    def Copy(self):
        """ Copy()
        Make a copy. Otherwise you'll point to the same object! """
        return Position(self)
    
    
    def InPixels(self):
        """ InPixels()
        Return a copy, but in pixel coordinates. """
        p = Position(self.left, self.top, self.width, self.height)
        p._inpixels = self._inpixels
        return p
    
    
    def __repr__(self):
        return "<Position %1.2f, %1.2f,  %1.2f, %1.2f>" % (
            self.x, self.y, self.w, self.h)
    
    
    ## For keeping _inpixels up-to-date
    
    
    def SetOwner(self, object):
        """ _SetOwner(object)
        Set the owner of this position instance and call _Update().
        """
        if not hasattr(object, '_position'):
            # a bit ugly, but we cannot know the wibject class.
            raise ValueError('Only wibject instances can own a position.')
        self._owner = object
        self._Update() # will call change as the inpixels changes
    
    
    def _Update(self):
        """ _Update()
        Re-obtain the position in pixels. If the obtained position
        differs from the current position-in-pixels, _Changed()
        is called.
        """
        
        # get old version, obtain and store new version
        ip1 = self._inpixels
        ip2 = self._inpixels = self._CalculateInPixels()
        
        # current inpixels was still None
        if ip2:
            if ip1 != ip2: # also if ip1 is None
                self._Changed()
    
    
    def _Changed(self):
        """ _Changed()
        To be called when the position was changed. 
        Will fire the owners eventPosition and will call
        _Update() on the position objects of all the owners
        children.
        """
        if self._owner:           
            if hasattr(self._owner, 'eventPosition'):
                self._owner.eventPosition.Fire()
                #print 'firing position event for', self._owner
            for child in self._owner._children:
                if hasattr(child, '_position'):
                    child._position._Update()
    
    
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
        for i in range(2,4):            
            if self[i] >= -1 and self[i] <= 1 and self[i]!=0:
                relative[i] = 1
        # return
        return relative
    
    
    def _GetInPixels(self):
        """ Return the position in screen coordinates as a tuple. 
        A buffered instance is returned, that is kept up to date.
        """
        # should we calculate it?
        if not self._inpixels:
            self._inpixels = self._CalculateInPixels()        
        # return it
        return self._inpixels
    
    
    def _CalculateInPixels(self):
        """ Return the position in screen coordinates as a tuple. 
        """
        
        # test if this is easy
        relatives = self._GetRelative()
        negatives = [int(self[i]<0) for i in range(4)]
        if max(relatives)==0 and max(negatives)==0:
            return self._x, self._y, self._w, self._h
        
        # if owner is a figure, it cannot have relative values
        if hasattr(self._owner, '_SwapBuffers'):
            return self._x, self._y, self._w, self._h
            
        # test if we can calculate
        if not self._owner or not hasattr(self._owner,'parent'):
            raise Exception("Can only calculate the position in pixels"+
                            " if the position instance is owned by a wibject!")
        # else, the owner must have a parent...
        if self._owner.parent is None:
            print self._owner
            raise Exception("Can only calculate the position in pixels"+
                            " if the owner has a parent!")
        
        # get width/height of parent
        tmp = self._owner.parent.position
        whwh = tmp.width, tmp.height
        whwh = (whwh[0], whwh[1], whwh[0], whwh[1])
        
        # calculate!
        pos = [self._x, self._y, self._w, self._h]
        for i in range(4):
            if relatives[i]:
                pos[i] = pos[i]*whwh[i]
            if i>1 and negatives[i]:
                pos[i] = whwh[i] + pos[i]
            # make sure it's int (even if user supplied floats > 1)
            pos[i] = int(pos[i])
        
        # done
        return tuple(pos)
    
    
    ## For getting and setting
    
    
    def Correct(self, dx=0, dy=0, dw=0, dh=0):
        """ Correct the position by suplying a delta amount of pixels.
        The correction is only applied if the attribute is absolute.
        """
        
        # get relatives
        relatives = self._GetRelative()
        
        # apply correction if we can
        if dx and not relatives[0]:
            self._x += int(dx) 
        if dy and not relatives[1]:
            self._y += int(dy)
        if dw and not relatives[2]:
            self._w += int(dw) 
        if dh and not relatives[3]:
            self._h += int(dh) 
        
        # we need an update now
        self._Update()
    
    
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
    
    ## Long names properties expressed in pixels
    
    @property
    def left(self):
        tmp = self._GetInPixels()
        return tmp[0]
    
    @property
    def top(self):
        tmp = self._GetInPixels()
        return tmp[1]
    
    @property
    def width(self):
        tmp = self._GetInPixels()
        return tmp[2]
    
    @property
    def height(self):
        tmp = self._GetInPixels()
        return tmp[3]
    
    @property
    def right(self):
        tmp = self._GetInPixels()
        return tmp[0] + tmp[2]
    
    @property
    def bottom(self):
        tmp = self._GetInPixels()
        return tmp[1] + tmp[3]
    
    @property
    def topLeft(self):
        tmp = self._GetInPixels()
        return tmp[0], tmp[1]
    
    @property
    def bottomRight(self):
        tmp = self._GetInPixels()
        return tmp[0] + tmp[2], tmp[1] + tmp[3]
    
    @property
    def size(self):
        tmp = self._GetInPixels()
        return tmp[2], tmp[3]


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


