# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# SSDF is distributed under the terms of the (new) BSD License.
# See http://www.opensource.org/licenses/bsd-license.php

# This module was first called points.py. In this newer version, PEP8 is
# followed more strictly, in order to make it easier to adopt by others.

""" Module pypoints

Provides several classes to represent points, pointsets, anisotropic arrays,
and quaternions.


Usage
-----
from pypoints import Point, Pointset, Aarray, Quaternion


The Point and Pointset classes
------------------------------
A point represents a location or vector. The dimension of the point
can be of any dimension.

A pointset represents an ordered (list) of points.
It has methods to add and remove points. Both point instances
and pointset instances have methods for mathematical operations, like
for example calculating distances between points and cross correlation.
For the Pointset these operations are efficiently applied to all points.


The Aarray class
----------------
The Aarray class implements numpy.ndarray and provides a way to manage
anisotropic data.


The Quaternion class
--------------------
A Quaternion is a method to describe and work with rotations. It avoids
the problem of Gimbal lock.


Module compatibility
--------------------
Use the is_* methods to test for points, pointsets etc, this will
make different packages using this module compatible.

from pypoints import is_Point, is_Pointset, is_Aarray, is_Quaternion


More information and license
----------------------------
For more information see the docstrings of the classes.

Copyright (C) 2012, Almar Klein.
This software distributed under the BSD license.

"""

# Set version number
__version__ = 2.2

import numpy as np
import sys


# todo: mention in next release notes that warning is not displayed by default
SHOW_SUBTRACTBUG_WARNING = False


def getExceptionInstance():
    type, value, tb = sys.exc_info()
    del tb
    return value


def Property(function):
    """ Property(function)
    
    A property decorator which allows to define fget, fset and fdel
    inside the function.
    
    Note that the class to which this is applied must inherit from object!
    Code based on an example posted by Walker Hale:
    http://code.activestate.com/recipes/410698/#c6
    
    """
    
    # Define known keys
    known_keys = 'fget', 'fset', 'fdel', 'doc'
    
    # Get elements for defining the property. This should return a dict
    func_locals = function()
    if not isinstance(func_locals, dict):
        raise RuntimeError('Property function should "return locals()".')
    
    # Create dict with kwargs for property(). Init doc with docstring.
    D = {'doc': function.__doc__}
    
    # Copy known keys. Check if there are invalid keys
    for key in func_locals.keys():
        if key in known_keys:
            D[key] = func_locals[key]
        else:
            raise RuntimeError('Invalid Property element: %s' % key)
    
    # Done
    return property(**D)


def nearest_power_of_two(i):
    """ nearest_power_of_two(i)
    Returns the nearest power of two that is at least i.
    """
    ii = 1
    while ii<i:
        ii*=2
    return ii


def check_the_two(p1,p2, what='something'):
    """ check_the_two(p1,p2, what='something')
    Check if the two things (self and a second point/pointset)
    can be used to calculate stuff.
    Returns (p1,p2), if one is a point, p1 is it.
    """
    
    # if one is a point, put it in p1
    if is_Pointset(p1):
        p2,p1 = p1,p2
    
    # only pointsets of equal length can be used
    if not is_Point(p1) and len(p1) != len(p2):
        # define errors
        tmp = "To calculate %s between two pointsets, " % what
        err = tmp + "both pointsets must be of equal length."
        raise ValueError(err)
    
    # check dimensions
    if p1.ndim != p2.ndim:
        tmp = "To calculate %s between two pointsets, " % what
        err = tmp + "the dimensions must be equal."
        raise ValueError(err)
    
    return p1, p2


# Methods to replace isinstance, so this module becomes compatible with
# other version
def is_Point(ob):
    return hasattr(ob, '_is_Point')
def is_Pointset(ob):
    return hasattr(ob, '_is_Pointset')
def is_Point_or_Pointset(ob):
    return hasattr(ob, '_is_Point') or hasattr(ob, '_is_Pointset')
def is_Aarray(ob):
    return hasattr(ob, '_is_Aarray')
def is_Quaternion(ob):
    return hasattr(ob, '_is_Quaternion')


class BasePoints(object):
    """ BasePoints
    
    Abstract class for the Point and Pointset classes. It defines
    addition, substraction, multiplication and devision for points and
    pointsets, and it implements some mathematical methods.
    
    """
    
    ## Common stuff (of which most is overloaded)
    
    @property
    def ndim(self):
        """ Get the number of dimensions.
        """
        return self._data.shape[-1]
    
    @property
    def data(self):
        """ Get the internal numpy array.
        """
        raise NotImplementedError()
    
    def copy(self):
        """ copy()
        
        Make a copy of the point or pointset.
        
        """
        raise NotImplementedError()
    
    def __setitem__(self):
        raise NotImplementedError()
    
    def __getitem__(self):
        raise NotImplementedError()
    
    
    ## Math stuff on a single vector


    def norm(self):
        """ norm()
        
        Calculate the norm (length) of the vector.
        This is the same as the distance to point 0,0 or 0,0,0,
        but implemented a bit faster.
        
        """
        
        # we could do something like:
        #   return self.distance(Point(0,0,0))
        # but we don't have to perform checks now, which is faster...
        
        data = self.data
        dists = np.zeros( (data.shape[0],) )
        for i in range(self.ndim):
            dists += data[:,i].astype(np.float64)**2
        return np.sqrt(dists)


    def normalize(self):
        """ normalize()
        
        Return normalized vector (to unit length).
        
        """
        
        # calculate factor array
        f = self.norm()
        where = f > 0
        f[where] = 1.0 / f[where]
        f.shape = f.size,1
        f = f.repeat(self.ndim,1)
        
        # apply
        data = self.data * f
        
        # return as point or pointset
        if is_Point(self):
            return Point(data)
        else:
            return Pointset(data)


    def normal(self):
        """ normal()
        
        Calculate the normalized normal of a vector.
        Use (p1-p2).normal() to calculate the normal of the line p1-p2.
        Only works on 2D points. For 3D points use cross().
        
        """
        
        # check dims
        if not self.ndim == 2:
            raise ValueError("Normal can only be calculated for 2D points.")
        
        # prepare
        a = self.copy()
        f = 1.0/self.norm()
        
        # swap xy, y goes minus
        tmp = a.data[:,0].copy()
        a.data[:,0] = a.data[:,1] * f
        a.data[:,1] = -tmp * f
        return a


    ## Math stuff on two vectors
    
    
    def distance(self, *p):
        """ distance(p)
        
        Calculate the Euclidian distance between two points or pointsets.
        Use norm() to calculate the length of a vector.
        
        """
        
        # the point directly given?
        if len(p)==1:
            p = p[0]
        
        # make sure p is a point or poinset
        if not is_Point_or_Pointset(p):
            p = Point(p)
        
        # check
        p1,p2 = check_the_two(self,p,'distance')
        
        # calculate
        dists = np.zeros( (p2.data.shape[0],) )
        for i in range(p1.ndim):
            tmp = p1.data[:,i] - p2.data[:,i]
            dists += tmp.astype(np.float64)**2
        return np.sqrt(dists)


    def angle(self, *p):
        """ angle(p)
        
        Calculate the angle (in radians) between two vectors.
        For 2D uses the arctan2 method so the angle has a sign.
        For 3D the angle is the smallest angles between the two
        vectors.
        
        If no point is given, the angle is calculated relative to the
        positive x-axis.
        
        """
        
        # the point directly given?
        if len(p)==1:
            p = p[0]
        elif len(p)==0:
            # use default point
            p = Point([0 for i in range(self.ndim)])
            p.x = 1
            
        # make sure p is a point or poinset
        if not is_Point_or_Pointset(p):
            p = Point(p)
        
        # check. Keep the correct order!
        check_the_two(self,p,'angle')
        p1,p2 = self, p
        
        if p1.ndim ==2:
            # calculate 2D case
            data1, data2 = p1.data, p2.data
            angs1 = np.arctan2( data1[:,1], data1[:,0] )
            angs2 = np.arctan2( data2[:,1], data2[:,0] )
            dangs =  angs1 - angs2
            # make number between -pi and pi
            I = np.where(dangs<-np.pi)
            dangs[I] += 2*np.pi
            I = np.where(dangs>np.pi)
            dangs[I] -= 2*np.pi
            return dangs
            
        elif p1.ndim ==3:
            # calculate 3D case
            p1, p2 = p1.normalize(), p2.normalize()
            data = p1.dot(p2)
            # correct for round off errors (or we will get NANs)
            data[data>1.0] = 1.0
            data[data<-1.0] = -1.0
            #return data
            return np.arccos(data)
        
        else:
            # not possible
            raise ValueError("Can only calculate angle for 2D and 3D vectors.")
    
    
    def angle2(self, *p):
        """ angle2(p)
        
        Calculate the angle (in radians) of the vector between
        two points.
        
        Notes
        -----
        Say we have p1=(3,4) and p2=(2,1).
        
        p1.angle(p2) returns the difference of the angles of the two vectors:
        0.142 = 0.927 - 0.785
        
        p1.angle2(p2) returns the angle of the difference vector (1,3):
        p1.angle2(p2) == (p1-p2).angle()
        
        """
        
        # the point directly given?
        if len(p)==1:
            p = p[0]
        elif len(p)==0:
            raise ValueError("Function angle2() requires another point.")
        else:
            p = Point(*p)
        
        # check. Keep the correct order!
        check_the_two(self,p,'angle')
        p1,p2 = self, p
        
        if p1.ndim in [2,3]:
            # subtract and use angle()
            return (p1-p2).angle()
            #meaning: dangs = np.arctan2( data2[:,1]-data1[:,1], data2[:,0]-data1[:,0] )
        else:
            # not possible
            raise ValueError("Can only calculate angle for 2D and 3D vectors.")
    
    
    def dot(self, *p):
        """ dot(p)
        
        Calculate the dot product of the two points or pointsets.
        The dot producet is the standard inner product of the
        orthonormal Euclidean space.
        
        """
        
        # the point directly given?
        if len(p)==1:
            p = p[0]
            
        # make sure p is a point or poinset
        if not is_Point_or_Pointset(p):
            p = Point(p)
        
        # check
        p1,p2 = check_the_two(self,p,'dot')
        
        # calculate
        data1, data2 = p1.data, p2.data
        data = np.zeros( (data2.shape[0],) )
        for i in range(p1.ndim):
            tmp = data1[:,i] * data2[:,i]
            data += tmp
        return data
    
    
    def cross(self, *p):
        """ cross(p)
        
        Calculate the cross product of two 3D vectors.
        
        Given two vectors, returns the vector that is orthogonal to
        both vectors. The right hand rule is applied; this vector is
        the middle finger, the argument the index finger, the returned
        vector points in the direction of the thumb.
        
        """
        
        # the point directly given?
        if len(p)==1:
            p = p[0]
        
        if not self.ndim == 3:
            raise ValueError("Cross product only works for 3D vectors!")
        
        # make sure p is a point or poinset
        if not is_Point_or_Pointset(p):
            p = Point(p)
        
        # check (note that we use the original order for calculation)
        p1, p2 = check_the_two(self,p,'cross')
        
        # calculate
        a, b = self.data, p.data
        data = np.zeros( p2.data.shape, np.float32 )
        data[:,0] = a[:,1]*b[:,2] - a[:,2]*b[:,1]
        data[:,1] = a[:,2]*b[:,0] - a[:,0]*b[:,2]
        data[:,2] = a[:,0]*b[:,1] - a[:,1]*b[:,0]
        
        # return
        if is_Pointset(p2):
            return Pointset(data)
        else:
            return Point(data)


    def __add__(self, p):
        """ Add vectors. """
        
        # make sure p is a point or poinset
        if not is_Point_or_Pointset(p):
            p = Point(p)
        
        # check
        p1,p2 = check_the_two(self,p,'add')
        
        # apply and return
        data = p1.data + p2.data # this should go well
        if is_Point(self):
            return Point(data)
        else:
            return Pointset(data)
    
    
    def _showTrace(self):
        # Get traceback info
        type, value, tb = sys.exc_info()
        err = ''
        frame = tb.tb_frame.f_back
        count = 0
        try:
            while frame and count < 5:
                count += 1
                if 'iepRemote' in frame.f_code.co_filename:
                    break
                err +=  "line %i of %s.\n" % (
                        frame.f_lineno, frame.f_code.co_filename)
                frame = frame.f_back
        finally:
            del tb, frame
        print(err[:-1])
    
    
    def __sub__(self, p):
        """ Subtract vectors. """
        
        # make sure p is a point or pointset
        if not is_Point_or_Pointset(p):
            p = Point(p)
        
        # check. Keep the correct order!
        p3, p4 = check_the_two(self,p,'subtract')
        p1, p2 = self, p
        
        # Check for the subtract bug ...
        if SHOW_SUBTRACTBUG_WARNING and p1 is not p3:
            # In previous versions the subtract bug would have occured
            # do not allow...
            try:
                raise ValueError()
            except Exception:
                print('+'*79)
                print('Note that previous versions of pypoints contained a ' +
                'bug in the minus operator. To prevent this message, use the ' +
                'subtract method instead of the operator. To get the ' +
                'same behavior as before, replace "A-B" with "B.subtract(A)". ' +
                'Info: https://github.com/almarklein/visvis/issues/30. ' +
                'Trace:')
                self._showTrace()
                print('+'*79)
        
        # apply and return
        data = p1.data - p2.data # this should go well
        if is_Pointset(p1) or is_Pointset(p2):
            return Pointset(data)
        else:
            return Point(data)
    
    
    def subtract(self, p):
        """ subtract(other)
        
        Subtract Pointset/Point instances.
        
        
        Notes
        -----
        This method was introduced because of the minus-bug. To get the
        same behaviour of when the bug was still there, replace
        "A-B" with B.subtract(A).
        
        """
        
        # make sure p is a point or pointset
        if not is_Point_or_Pointset(p):
            p = Point(p)
        
        # check. Keep the correct order!
        check_the_two(self,p,'subtract')
        p1, p2 = self, p
        
        # apply and return
        data = p1.data - p2.data # this should go well
        if is_Pointset(p1) or is_Pointset(p2):
            return Pointset(data)
        else:
            return Point(data)
    

    def __mul__(self,value):
        """ Scale vectors. """
        
        p1, p2 = self, None
        try:
            value = float(value)
            data1, data2 = self.data, value
        except TypeError:
            
            if not is_Point_or_Pointset(value):
                value = Point(value)
            
            # check
            p1,p2 = check_the_two(self,value,'multiply')
            data1, data2 = self.data, value.data
        
        # apply and return
        data = data1 * data2 # this should go well
        if is_Pointset(p1) or is_Pointset(p2):
            return Pointset(data)
        else:
            return Point(data)
    
    
    def __truediv__(self, value):
        """ Scale vectors. """
        
        p1, p2 = self, None
        try:
            value = float(value)
            data1, data2 = self.data, value
        except TypeError:
            
            if not is_Point_or_Pointset(value):
                value = Point(value)
                
            # check (note that the order is important for division!)
            check_the_two(self,value,'divide')
            data1, data2 = self.data, value.data
            
        # apply and return
        data = data1 / data2 # this should go well
        if is_Pointset(p1) or is_Pointset(p2):
            return Pointset(data)
        else:
            return Point(data)
    
    
    def __rmul__(self, value):
        """ Same as normal multiply. """
        
        return self.__mul__(value)
    
    
    def __rtruediv__(self, value):
        """ Inverse scale vectors. """
        
        p1, p2 = self, None
        try:
            value = float(value)
            data1, data2 = self.data, value
        except TypeError:
            
            if not is_Point_or_Pointset(value):
                value = Point(value)
                
            # check (note that the order is important for division!)
            check_the_two(self,value,'divide')
            data1, data2 = self.data, value.data
            
        # apply and return
        data = data2 / data1 # here's the difference
        if is_Pointset(p1) or is_Pointset(p2):
            return Pointset(data)
        else:
            return Point(data)
    
    __div__ = __truediv__ # For Python 2.x
    __rdiv__ = __rtruediv__


class Point(BasePoints):
    """ Point(x,y,[z,[...]])
    
    Represents a point or vector (of any dimension).
    
    This class implements many usefull operators such as addition
    and multiplication, and provides common mathematical operations
    that can be applied to points and pointsets.
    
    Example
    -------
    p1 = Point(3.2,4)   # a 2D point
    p2 = p1.copy()      # make a copy
    p1[0] = 9           # set the first element
    p1.x                # convenience property (.y and .z also available)
    p1.xi               # idem, but rounded to nearest integer
    p1.distance(p2)     # calculate distance
    p1 + p2             # calculate the addition of the two vectors
    p2 = p1*2           # scale vector
    p2 = p1 * p2        # even for each dimension seperately
    p2 = p2.normalize() # make unit length
    
    """
    
    _is_Point = True
    
    def __init__(self, *point):
        BasePoints.__init__(self)
        
        if len(point)==0:
            raise ValueError("Cannot create an 'empty' point.")
        elif len(point)==1:
            point = point[0]
        
        if is_Point(point):
            # a point
            self._data = point._data.astype(np.float32)
        elif isinstance(point, (tuple,list)):
            # a tuple or list
            self._data = np.array(point, dtype=np.float32)
        elif isinstance(point, np.ndarray):
            # a numpy array
            self._data = point.astype(np.float32)
        elif isinstance(point, (float,int)):
            # 1D point
            self._data = np.empty((1,), dtype=np.float32)
            self._data[0] = point
        else:
            # otherwise, what were we given?
            raise ValueError("Cannot create a point with that argument.")
        
        # remove singleton dimensions
        if self._data.size>1:
            self._data = np.squeeze(self._data)
        
        # check integrity
        if len(self._data.shape) != 1:
            # this must be the case to allow indexing!
            raise ValueError("A point should be given as a 1D array.")
        if self._data.shape[0] < 1:
            raise ValueError("A point should consist of at least one value.")


    def copy(self):
        """ copy()
        
        Get a copy of this point.
        
        """
        return Point(self._data)
    
    
    @property
    def data(self):
        """ Get the point as the (2D) numpy array it is stored in.
        """
        # this is overloaded in the Pointset class
        data = self._data[:]
        data.shape = 1, data.shape[0]
        return data
    

    ## string representation
    
    def __str__(self):
        """ Return a nice string representation of the point. """
        s = "<point  "
        for value in self._data.flatten():
            # '% x.yg': x signif, y length '-1.111e+000'. x = y+7
            s += "% 12.5g, " % (value)
            #str(value).ljust(7,' ') # '%5f' % (value)
        s = s[:-2] + " >"
        return s

    __repr__ = __str__
    
    ## Comparison
    
    def __eq__(self, other):
        """ Test whether two poins are the same. """
        if not is_Point(other) or other.ndim != self.ndim:
            return False
        return (other.data == self.data).sum() == self.ndim
    
    def __ne__(self, other):
        """ Test whether two poins are NOT the same. """
        if not is_Point(other) or other.ndim != self.ndim:
            return True
        return (other.data == self.data).sum() != self.ndim
    
    ## indexing etc
        
    def __setitem__(self,index,value):
        self._data[index] = value

    def __getitem__(self, index):
        return self._data[index]
    
    
    @Property
    def x():
        """ Get/set p[0]. """
        def fget(self):
            return self._data[0]
        def fset(self, value):
            self._data[0] = value
        return locals()
    
    @property
    def xi(self):
        """ Get p[0] rounded to the nearest integer, for indexing. """
        return int(self._data[0]+0.5)
    
    @Property
    def y():
        """ Get/set p[1]. """
        def fget(self):
            return self._data[1]
        def fset(self, value):
            self._data[1] = value
        return locals()
       
    @property
    def yi(self):
        """ Get p[1] rounded to the nearest integer, for indexing. """
        return int(self._data[1]+0.5)
    
    @Property
    def z():
        """ Get/set p[2]. """
        def fget(self):
            return self._data[2]
        def fset(self, value):
            self._data[2] = value
        return locals()
    
    @property
    def zi(self):
        """ Get p[2] rounded to the nearest integer, for indexing. """
        return int(self._data[2]+0.5)



class Pointset(BasePoints):
    """ Pointset(ndim)
    
    Represents a set of points or vectors (of any dimension).
    
    Can also be initialized using: Pointset(<ndim times npoints numpy array>)
    
    A pointset provides an efficient way to store points.
    Internally the points are stored in a numpy array that is
    resized by a factor of two when more space is required. This makes adding
    and removing points (from the end) very efficient. Also mathematical
    operations can be applied on all the points in the set efficiently.
    
    Notes on slicing and indexing
    -----------------------------
      * pp[7]: When indexing, the corresponding Point instance is get/set.
      * pp[7:20]: When slicing, a new poinset (subset) is get/set.
      * pp[4:9,3] When using two indices or slices, the indices are applied to
        the internal data. (In this example returning the z-value for
        points 4 till 8.)
    
    Math
    ----
    The same mathematical operations that can be applied to a Point
    instance can also be applied to a Pointset instance. The operation
    is applied to all points in the set. For example pp.distance(3,4)
    returns an array with the distances of all points in pp to (3,4).
    
    Example
    -------
    a  = <...>          # an existing 100x2 array
    pp1 = Pointset(2)   # pointset with two dimensions
    pp2 = Pointset(a)   # dito
    pp1.append(3,4)     # add a point
    pp1.append(p)       # add an existing point p
    pp1.extend(pp1)     # extend pp1 to itself
    pp2[:4] = pp1       # replace first four points of pp2
    pp[1]               # returns the point (3,4) (as a Point instance)
    pp[1,0]             # returns the value 3.0
    pp[:,1]             # get all y values
    pp.contains(3,4)    # will return True
    
    """
    
    _is_Pointset = True
    
    def __init__(self, ndim):
        BasePoints.__init__(self)
        
        # init
        data = ndim
        initialLength = 16
        
        # convert numpy scalars to int
        if isinstance(data, np.ndarray):
            if data.size==1 and len(data.shape) in [0,1]:
                data = ndim = int(data)
        
        # set using a numpy array
        if isinstance(data, np.ndarray):
            # do some checks
            if len(data.shape) != 2:
                raise ValueError("A pointset should be given as a 2D array.")
            if data.shape[1] < 1:
                tmp = "Each point should consist of at least one value."
                raise ValueError(tmp)
            # create array
            self._len = data.shape[0]
            L = max( nearest_power_of_two(data.shape[0]), initialLength)
            self._data = np.zeros((L, data.shape[1]), dtype=np.float32)
            # fill values
            self._data[:data.shape[0],:] = data
        
        # we were given the dimension
        else:
            self._len = 0
            self._data = np.zeros((initialLength, ndim), dtype=np.float32)
    
    
    @property
    def data(self):
        """ Get a view of the data. Note that internally the points
        are stored in a numpy array that is in general longer than
        the amount of points (at most 4 times as long). This is to
        make adding/removing points much faster by prevening reallocating
        memory. The internal array is resized with a factor two when
        necesary. This property returns a (sub)view of that array and is
        always 2D.
        """
        return self._data[:self._len,:]

    
    def _as_point(self, *p):
        """ _as_point(*p)
        
        Return the input as a point instance, also
        check whether the dimensions match.
        
        """
        
        # the point directly given?
        if len(p)==1:
            p = p[0]
        
        # make sure we are dealing with a point
        if not is_Point(p):
            p = Point(p)
        
        # check whether we can append it
        if self.ndim != p.ndim:
            tmp = "Given point does not match dimension of pointset."
            raise ValueError(tmp)
        
        # done
        return p
    
    
    def _resize_if_required(self, n=None):
        """ _resize_if_required(n=None)
        
        Resize the internal array, n is the new required
        amount of poinst that we should be able to fit in.
        If not given, self._len is used.
        This method checks if we should reduce our size (if
        the internal length is larger than four times n).
        
        """
        
        # n given?
        if n is None:
            n = self._len
        
        # reduce or increase size?
        internalLen = self._data.shape[0]
        if n > internalLen:
            L = nearest_power_of_two(n)
        elif n*4 <= internalLen and internalLen > 16:
            L = nearest_power_of_two(n*2)
        else:
            # return Now
            return
        
        # keep reference of old data
        tmp = self._data
        # create new data array
        self._data = np.zeros( (L, self.ndim), dtype=np.float32 )
        # copy data
        self._data[:self._len,:] = tmp[:self._len,:]


    
    ## Indexing
    
    def __setitem__(self, index, value):
        """ Set a point or part of the pointset. """
        
        # a tuple given: set as array
        if isinstance( index, tuple):
            self.data[index] = value
        # for a slice, return subset
        elif isinstance(index, slice):
            if not is_Pointset(value):
                tmp = "When slicing with a single index "
                raise ValueError(tmp+ "the supplied value must be a pointset.")
            self.data[index] = value.data
        # otherwise, return point
        else:
            value = self._as_point(value)
#             if not is_Point(value):
#                 tmp = "When indexing with a single index "
#                 raise ValueError(tmp + "the supplied value must be a point.")
            self.data[index] = value.data
    
    
    def __getitem__(self, index):
        """ Get a point or part of the pointset. """
        
        # Single index from numpy scalar
        if isinstance(index, np.ndarray) and index.size==1:
            index = int(index)
        
        if isinstance(index, tuple):
            # Multiple indexes: return as array
            return self.data[index]
        elif isinstance(index, slice):
            # Slice: return subset
            return Pointset( self.data[index] )
        elif isinstance(index, int):
            # Single index: return point
            return Point( self.data[index] )
        else:
            # Probably some other form of subslicing
            try:
                return Pointset( self.data[index])
            except Exception:
                return Point( self.data[index])
    
    
    def __delitem__(self, index):
        """ Remove one or multiple points from the pointset. """
        
        # if tuple, not valid
        if isinstance(index, tuple):
            raise IndexError("Can only remove points using 1D slicing.")
        
        # get start/stop/step
        if isinstance(index, slice):
            start, stop, step = index.indices(self._len)
        else:
            start, stop, step = index, index+1, 1
        
        # if stepping, do it the slow way
        if step > 1:
            indices = [i for i in range(start,stop, step)]
            for i in reversed(indices):
                del self[i]
            return
            
        # move latter block forward
        tmp = self.data[stop:,:]
        self._data[start:start+len(tmp),:] = tmp
        
        # reduce length
        self._len = start + len(tmp)
        
        # should we resize?
        self._resize_if_required()

    
    ## Appending / Extending
    
    
    def append(self, *p):
        """ append(*p)
        
        Append a point to this pointset.
        If p is not an instance of the Point class,  the constructor
        of Point is called to create one from the given argument. This
        enables pp.append(x,y,z)
        
        """
        try:
            p = self._as_point(*p)
        except Exception:
            raise ValueError(str(getExceptionInstance()))
        
        # resize if we need to
        self._resize_if_required(self._len+1)
        
        # append point
        self._data[self._len,:] = p._data
        self._len += 1
    
    
    def extend(self, pp):
        """ extend(pp)
        
        Extend this pointset with another pointset, thus combining the two.
        If pp is not an instance of the Pointset class, the constructor
        of Pointset is called to create one from the given argument.
        
        """
        
        # make sure we are dealing with a pointset
        if not is_Pointset(pp):
            try:
                pp = Pointset(pp)
            except Exception:
                raise ValueError(str(getExceptionInstance()))
        
        # check whether we can append it
        if self.ndim != pp.ndim:
            raise ValueError("Can only extend pointsets of equal dimensions.")
        
        # resize the array if needed
        newLen = self._len + pp._len
        self._resize_if_required(newLen)
        
        # append new data
        i1 = self._len
        i2 = i1 + pp._len
        self._data[i1:i2,:] = pp._data[:pp._len,:]
        self._len = newLen


    def insert(self, index, *p):
        """ insert(index, *p)
        
        Insert a point at the given index.
        
        """
        
        # check index
        if index < 0:
            index = self._len + index
        if index<0 or index>self._len:
            raise IndexError("Index to insert point out of range.")
        
        # make sure p is a point
        try:
            p = self._as_point(*p)
        except Exception:
            raise ValueError(str(getExceptionInstance()))
        
        # resize if we need to
        self._resize_if_required(self._len+1)
        
        # insert point
        tmp = self._data[index:self._len,:].copy()
        self._data[index,:] = p._data
        self._data[index+1:self._len+1,:] = tmp
        self._len += 1
    
    
    def remove(self, *p):
        """ remove(*p)
        
        Remove first occurance of the given point from the list.
        Produces an error if such a point is not present.
        See also remove_all()
        
        """
        
        # make sure p is a point
        try:
            p = self._as_point(*p)
        except Exception:
            raise ValueError(str(getExceptionInstance()))
        
        # calculate mask
        mask = np.zeros((len(self),),dtype='uint8')
        for i in range(self.ndim):
            mask += self.data[:,i]==p[i]
        
        # find points given
        I, = np.where(mask==self.ndim)
        
        # produce error if not found
        if len(I) == 0:
            raise ValueError("Given point to remove was not found.")
        
        # remove first point
        del self[ I[0] ]

    
    def remove_all(self, *p):
        """ remove_all(*p)
        
        Remove all occurances of the given point. If there
        is no occurance, no action is taken.
        
        """
        
        # make sure p is a point
        try:
            p = self._as_point(*p)
        except Exception:
            raise ValueError(str(getExceptionInstance()))
        
        # calculate mask
        mask = np.zeros((len(self),),dtype='uint8')
        for i in range(self.ndim):
            mask += self.data[:,i]==p[i]
        
        # find points given
        I, = np.where(mask==self.ndim)
        
        # remove all points (backwards!)
        indices = sorted( [i for i in I] )
        for i in reversed(indices):
            del self[i]
    
    
    def pop(self, index=-1):
        """ pop(index=-1)
        
        Removes and returns a point from the pointset. Removes the last
        by default (which is more efficient than popping from anywhere else).
        
        """
        
        # check index
        index2 = index
        if index < 0:
            index2 = self._len + index
        if index2<0 or index2>self._len:
            raise IndexError("Index to insert point out of range.")
        
        # get point
        p = self[index]
        
        # remove it
        if index == -1:
            # ooh this is fast
            self._len -= 1
            self._resize_if_required()
        else:
            del self[index]
        
        # return
        return p
    
    
    def clear(self):
        """ clear()
        
        Remove all points in the pointset.
        
        """
        self.__init__(self.ndim)
    
    
    def copy(self):
        """ copy()
        
        Return a copy of this pointset.
        
        """
        return Pointset(self._data[:self._len,:])
    
    
    ## Sequence stuff
    
    
    def __len__(self):
        return self._len
    
    def __iter__(self):
        self._index = -1
        return self
    
    def __next__(self):
        self._index +=1
        if self._index >= len(self): raise StopIteration
        return self[self._index]
    
    def next(self): # Python 2.x
        return self.__next__()
    
    def contains(self, *p):
        """ contains(*p)
        
        Check whether a point is already in this set.
        
        """
        
        # make sure p is a point
        try:
            p = self._as_point(*p)
        except Exception:
            raise ValueError(str(getExceptionInstance()))
        
        mask = np.zeros((len(self),),dtype='uint8')
        for i in range(self.ndim):
            mask += self.data[:,i]==p[i]
        if mask.max() >= self.ndim:
            return True
        else:
            return False


    ## String representation
    
    def __str__(self):
        """ Return a nice string representation of the pointset. """
        s = ""
        for i in range(len(self)):
            s += "%3d: " % (i)
            s += str(self[i])
            s += "\n"
        return s

    def __repr__(self):
        """" Return short(one line) string representation of the pointset. """
        return "<pointset with %i points of %i dimensions>" % (
            len(self), self.ndim )



class Aarray(np.ndarray):
    """ Aarray(shape_or_array, sampling=None, origin=None, fill=None,
                dtype='float32', **kwargs)
    
    Anisotropic array; inherits from numpy.ndarray and adds a sampling
    and origin property which gives the sample distance and offset for
    each dimension.
    
    Parameters
    ----------
    shape_or_array : shape-tuple or numpy.ndarray
        Specifies the shape of the produced array. If an array instance is
        given, the returned Aarray is a view of the same data (i.e. no data
        is copied).
    sampling : tuple of ndim elements
        Specifies the sample distance (i.e. spacing between elements) for
        each dimension. Default is all ones.
    origin : tuple of ndim elements
        Specifies the world coordinate at the first element for each dimension.
        Default is all zeros.
    fill : scalar (optional)
        If given, and the first argument is not an existing array,
        fills the array with this given value.
    dtype : any valid numpy data type
        The type of the data
    
    All extra arguments are fed to the constructor of numpy.ndarray.
    
    Implemented properties and methods
    -----------------------------------
      * sampling - The distance between samples as a tuple
      * origin - The origin of the data as a tuple
      * get_start() - Get the origin of the data as a Point instance
      * get_end() - Get the end of the data as a Point instance
      * get_size() - Get the size of the data as a Point instance
      * sample() - Sample the value at the given point
      * point_to_index() - Given a poin, returns the index in the array
      * index_to_point() - Given an index, returns the world coordinate
    
    Slicing
    -------
    This class is aware of slicing. This means that when obtaining a part
    of the data (for exampled 'data[10:20,::2]'), the origin and sampling
    of the resulting array are set appropriately.
    
    When applying mathematical opertaions to the data, or applying
    functions that do not change the shape of the data, the sampling
    and origin are copied to the new array. If a function does change
    the shape of the data, the sampling are set to all zeros and ones
    for the origin and sampling, respectively.
    
    World coordinates vs tuples
    ---------------------------
    World coordinates are expressed as Point instances (except for the
    "origin" property). Indices as well as the "sampling" and "origin"
    attributes are expressed as tuples in z,y,x order.
    
    """
    
    _is_Aarray = True
    
    def __new__(cls, shapeOrArray, sampling=None, origin=None, fill=None,
                dtype='float32', **kwargs):
        
        if isinstance(shapeOrArray, np.ndarray):
            shape = shapeOrArray.shape
            ob = shapeOrArray.view(cls)
            if is_Aarray(shapeOrArray):
                if sampling is None:
                    sampling = shapeOrArray.sampling
                if origin is None:
                    origin = shapeOrArray.origin
        else:
            shape = shapeOrArray
            ob = np.ndarray.__new__(cls, shape, dtype=dtype, **kwargs)
            if fill is not None:
                ob.fill(fill)
        
        # init sampling and origin
        ob._sampling = tuple( [1.0 for i in ob.shape] )
        ob._origin = tuple( [0.0 for i in ob.shape] )
        
        # set them
        if sampling:
            ob.sampling = sampling
        if origin:
            ob.origin = origin
        
        # return
        return ob
    
    
    def __array_finalize__(self, ob):
        """ So the sampling and origin is maintained when doing
        calculations with the array. """
        #if hasattr(ob, '_sampling') and hasattr(ob, '_origin'):
        if isinstance(ob, Aarray):
            if self.shape == ob.shape:
                # Copy sampling and origin for math operation
                self._sampling = tuple( [i for i in ob._sampling] )
                self._origin = tuple( [i for i in ob._origin] )
            else:
                # Don't bother (__getitem__ will set them after this)
                # Other functions that change the shape cannot be trusted.
                self._sampling = tuple( [1.0 for i in self.shape] )
                self._origin = tuple( [0.0 for i in self.shape] )
        elif isinstance(self, Aarray):
            # This is an Aarray, but we do not know where it came from
            self._sampling = tuple( [1.0 for i in self.shape] )
            self._origin = tuple( [0.0 for i in self.shape] )
    
    
    def __getslice__(self, i, j):
        # Called only when indexing first dimension and without a step
        
        # Call base getitem method
        ob = np.ndarray.__getslice__(self, i, j)
        
        # Perform sampling and origin corrections
        sampling, origin = self._correct_sampling(slice(i,j))
        ob.sampling = sampling
        ob.origin = origin
        
        # Done
        return ob
    
    
    def __getitem__(self, index):
        
        # Call base getitem method
        ob = np.ndarray.__getitem__(self, index)
        
        if isinstance(index, np.ndarray):
            # Masked or arbitrary indices; sampling and origin irrelevant
            ob = np.asarray(ob)
        elif isinstance(ob, Aarray):
            # If not a scalar, perform sampling and origin corrections
            # This means there is only a very small performance penalty
            sampling, origin = self._correct_sampling(index)
            if sampling:
                ob.sampling = sampling
                ob.origin = origin
        
        # Return
        return ob
    
    
    def _correct_sampling(self, index):
        """ _correct_sampling(index)
        
        Get the new sampling and origin when slicing.
        
        """
        
        # Init origin and sampling
        _origin = self._origin
        _sampling = self._sampling
        origin = []
        sampling = []
        
        # Get index always as a tuple and complete
        index2 = [None]*len(self._sampling)
        if not isinstance(index, (list,tuple)):
            index2[0] = index
        else:
            try:
                for i in range(len(index)):
                    index2[i] = index[i]
            except Exception:
                index2[0] = index
        
        # Process
        for i in range(len(index2)):
            ind = index2[i]
            if isinstance(ind, slice):
                # print(ind.start, ind.step)
                if ind.start is None:
                    origin.append( _origin[i] )
                else:
                    origin.append( _origin[i] + ind.start*_sampling[i] )
                if ind.step is None:
                    sampling.append(_sampling[i])
                else:
                    sampling.append(_sampling[i]*ind.step)
            elif ind is None:
                origin.append( _origin[i] )
                sampling.append(_sampling[i])
            else:
                pass # singleton dimension that pops out
        
        # Return
        return sampling, origin
    
    
    def _set_sampling(self,sampling):
        if not isinstance(sampling, (list,tuple)):
            raise ValueError("Sampling must be specified as a tuple or list.")
        if len(sampling) != len(self.shape):
            raise ValueError("Sampling given must match shape.")
        for i in sampling:
            if i <= 0:
                raise ValueError("Sampling elements must be larger than zero.")
        # set
        tmp = [float(i) for i in sampling]
        self._sampling = tuple(tmp)
    
    
    def _get_sampling(self):
        l1, l2 = len(self._sampling), len(self.shape)
        if l1 < l2:
            tmp = list(self._sampling)
            tmp.extend( [1 for i in range(l2-l1)] )
            return tuple( tmp )
        elif l1 > l2:
            tmp = [self._sampling[i] for i in range(l2)]
            return tuple(tmp)
        else:
            return self._sampling
    
    sampling = property(_get_sampling, _set_sampling, None,
        "A tuple with the sample distance for each dimension.")
    
    
    def _set_origin(self,origin):
        if not isinstance(origin, (list,tuple)):
            raise ValueError("Origin must be specified as a tuple or list.")
        if len(origin) != len(self.shape):
            raise ValueError("Origin given must match shape.")
        # set
        tmp = [float(i) for i in origin]
        self._origin = tuple(tmp)
    
    
    def _get_origin(self):
        l1, l2 = len(self._origin), len(self.shape)
        if l1 < l2:
            tmp = list(self._origin)
            tmp.extend( [0 for i in range(l2-l1)] )
            return tuple( tmp )
        elif l1 > l2:
            tmp = [self._origin[i] for i in range(l2)]
            return tuple(tmp)
        else:
            return self._origin
    
    origin = property(_get_origin, _set_origin, None,
        "A tuple with the origin for each dimension.")
    
    
    def point_to_index(self, point, non_on_index_error=False):
        """ point_to_index(point, non_on_index_error=False)
        
        Given a point returns the sample index (z,y,x,..) closest
        to the given point. Returns a tuple with as many elements
        as there are dimensions.
        
        If the point is outside the array an IndexError is raised by default,
        and None is returned when non_on_index_error == True.
        
        """
        
        # check
        if not is_Point(point):
            raise ValueError("Given point must be an instance of Point.")
        if point.ndim != len(self.shape):
            raise ValueError("Given point must match the number of dimensions.")
        
        # calculate indices
        ii = []
        for i in range(point.ndim):
            s = self.shape[i]
            p = ( point[-(i+1)] - self._origin[i] ) / self._sampling[i]
            p = int(p+0.5)
            if p<0 or p>=s:
                ii = None
                break
            ii.append(p)
        
        # return
        if ii is None and non_on_index_error:
            return None
        elif ii is None:
            raise IndexError("Sample position out of range: %s" % str(point))
        else:
            return tuple(ii)
    
    
    def sample(self, point, default=None):
        """ sample(point, default=None)
        
        Take a sample of the array, given the given point
        in world-coordinates, i.e. transformed using sampling.
        By default raises an IndexError if the point is not inside
        the array, and returns the value of "default" if it is given.
        
        """
        
        tmp = self.point_to_index(point,True)
        if tmp is None:
            if default is None:
                ps = str(point)
                raise IndexError("Sample position out of range: %s" % ps)
            else:
                return default
        return self[tmp]


    def index_to_point(self, *index):
        """ index_to_point(*index)
        
        Given a multidimensional index, get the corresponding point in world
        coordinates.
        
        """
        # check
        if len(index)==1:
            index = index[0]
        if not hasattr(index,'__len__'):
            index = [index]
        if len(index) != len(self.shape):
            raise IndexError("Invalid number of indices.")
        
        # init point as list
        pp = []
        # convert
        for i in range(len(self.shape)):
            ii = index[i]
            if ii<0:
                ii = self.shape[i] - ii
            p = ii * self._sampling[i] + self._origin[i]
            pp.append(p)
        # return
        pp.reverse()
        return Point(pp)


    def get_size(self):
        """ get_size()
        
        Get the size (as a vector) of the array expressed in world coordinates.
        
        """
        pp = []
        for i in range(len(self.shape)):
            pp.append( self._sampling[i] * self.shape[i] )
        pp.reverse()
        return Point(pp)
    
    
    def get_start(self):
        """ get_start()
        
        Get the origin of the array expressed in world coordinates.
        Differs from the property 'origin' in that this method returns
        a point rather than indices z,y,x.
        
        """
        pp = [i for i in self.origin]
        pp.reverse()
        return Point(pp)
    
    
    def get_end(self):
        """ get_end()
        
        Get the end of the array expressed in world coordinates.
        
        """
        pp = []
        for i in range(len(self.shape)):
            pp.append( self._origin[i] + self._sampling[i] * self.shape[i] )
        pp.reverse()
        return Point(pp)



class Quaternion(object):
    """ Quaternion(w=1, x=0, y=0, z=0, normalize=True)
    
    A quaternion is a mathematically convenient way to
    describe rotations.
    
    """
    
    _is_Quaternion = True
    
    def __init__(self, w=1, x=0, y=0, z=0, normalize=True):
        
        self.w = float(w)
        self.x, self.y, self.z = float(x), float(y), float(z)
        if normalize:
            self._normalize()
    
    
    def __repr__(self):
        return "<Quaternion object %1.3g + %1.3gi + %1.3gj + %1.3gk>" % (
                self.w, self.x, self.y, self.z)
    
    
    def copy(self):
        """ copy()
        
        Create an exact copy of this quaternion.
        
        """
        return Quaternion(self.w, self.x, self.y, self.z, False)
    
    
    def norm(self):
        """ norm()
        
        Returns the norm of the quaternion.
        norm = w**2 + x**2 + y**2 + z**2
        
        """
        tmp = self.w**2 + self.x**2 + self.y**2 + self.z**2
        return tmp**0.5
    
    
    def _normalize(self):
        """ _normalize()
        
        Make the quaternion unit length.
        
        """
        # Get length
        L = self.norm()
        if not L:
            raise ValueError('Quaternion cannot have 0-length.')
        # Correct
        self.w /= L
        self.x /= L
        self.y /= L
        self.z /= L
    
    
    def normalize(self):
        """ normalize()
        
        Returns a normalized (unit length) version of the quaternion.
        
        """
        new = self.copy()
        new._normalize()
        return new
    
    
    def conjugate(self):
        """ conjugate()
        
        Obtain the conjugate of the quaternion.
        This is simply the same quaternion but with the sign of the
        imaginary (vector) parts reversed.
        
        """
        new = self.copy()
        new.x *= -1
        new.y *= -1
        new.z *= -1
        return new
    
    
    def inverse(self):
        """ inverse()
        returns q.conjugate()/q.norm()**2
        So if the quaternion is unit length, it is the same
        as the conjugate.
        """
        new = self.conjugate()
        tmp = self.norm()**2
        new.w /= tmp
        new.x /= tmp
        new.y /= tmp
        new.z /= tmp
        return new
    
    
    def exp(self):
        """ exp()
        
        Returns the exponent of the quaternion.
        (not tested)
        
        """
        
        # Init
        vecNorm = self.x**2 + self.y**2 + self.z**2
        wPart = np.exp(self.w)
        q = Quaternion()
        
        # Calculate
        q.w = wPart * np.cos(vecNorm)
        q.x = wPart * self.x * np.sin(vecNorm) / vecNorm
        q.y = wPart * self.y * np.sin(vecNorm) / vecNorm
        q.z = wPart * self.z * np.sin(vecNorm) / vecNorm
        
        return q
    
    
    def log(self):
        """ log()
        
        Returns the natural logarithm of the quaternion.
        (not tested)
        
        """
        
        # Init
        norm = self.norm()
        vecNorm = self.x**2 + self.y**2 + self.z**2
        tmp = self.w / norm
        q = Quaternion()
        
        # Calculate
        q.w = np.log(norm)
        q.x = np.log(norm) * self.x * np.arccos(tmp) / vecNorm
        q.y = np.log(norm) * self.y * np.arccos(tmp) / vecNorm
        q.z = np.log(norm) * self.z * np.arccos(tmp) / vecNorm
        
        return q
    
    
    def __add__(self, q):
        """ Add quaternions. """
        new = self.copy()
        new.w += q.w
        new.x += q.x
        new.y += q.y
        new.z += q.z
        return new
    
    
    def __sub__(self, q):
        """ Subtract quaternions. """
        new = self.copy()
        new.w -= q.w
        new.x -= q.x
        new.y -= q.y
        new.z -= q.z
        return new
    
    
    def __mul__(self, q2):
        """ Multiply two quaternions. """
        new = Quaternion()
        q1 = self
        new.w = q1.w*q2.w - q1.x*q2.x - q1.y*q2.y - q1.z*q2.z
        new.x = q1.w*q2.x + q1.x*q2.w + q1.y*q2.z - q1.z*q2.y
        new.y = q1.w*q2.y + q1.y*q2.w + q1.z*q2.x - q1.x*q2.z
        new.z = q1.w*q2.z + q1.z*q2.w + q1.x*q2.y - q1.y*q2.x
        return new
    
    
    def rotate_point(self, p):
        """ rotate_point(p)
        
        Rotate a Point instance using this quaternion.
        
        """
        # Prepare
        p = Quaternion(0, p.x, p.y, p.z, False) # Do not normalize!
        q1 = self.normalize()
        q2 = self.inverse()
        # Apply rotation
        r = (q1*p)*q2
        # Make point and return
        return Point(r.x, r.y, r.z)
    
    
    def get_matrix(self):
        """ get_matrix()
        
        Create a 4x4 homography matrix that represents the rotation
        of the quaternion.
        
        """
        
        # Init matrix (remember, a matrix, not an array)
        a = np.zeros((4,4), dtype=np.float32)
        w, x, y, z = self.w, self.x, self.y, self.z
        
        # First row
        a[0,0] = 1.0 -  2.0 * ( y * y + z * z )
        a[1,0] =        2.0 * ( x * y + z * w )
        a[2,0] =        2.0 * ( x * z - y * w )
        a[3,0] = 0.0
        
        # Second row
        a[0,1] =        2.0 * ( x * y - z * w )
        a[1,1] = 1.0 -  2.0 * ( x * x + z * z )
        a[2,1] =        2.0 * ( z * y + x * w )
        a[3,1] = 0.0
        
        # Third row
        a[0,2] =        2.0 * ( x * z + y * w )
        a[1,2] =        2.0 * ( y * z - x * w )
        a[2,2] = 1.0 -  2.0 * ( x * x + y * y )
        a[3,2] = 0.0
        
        # Fourth row
        a[0,3] = 0.0
        a[1,3] = 0.0
        a[2,3] = 0.0
        a[3,3] = 1.0
        
        return a
    
    
    def get_axis_angle(self):
        """ get_axis_angle()
        
        Get the axis-angle representation of the quaternion.
        (The angle is in radians)
        
        """
        
        # Init
        angle = 2 * np.arccos(self.w)
        scale = ( self.x**2 + self.y**2 + self.z**2 )**0.5
        
        # Calc axis
        if scale:
            ax = self.x / scale
            ay = self.y / scale
            az = self.z / scale
        else:
            # No rotation, so arbitrary axis
            ax, ay, az = 1, 0, 0
        
        # Return
        return angle, ax, ay, az

    
    @classmethod
    def create_from_axis_angle(cls, angle, ax, ay, az):
        """ create_from_axis_angle(angle, ax, ay, ax)
        
        Classmethod to create a quaternion from an axis-angle representation.
        (angle should be in radians).
        
        """
        angle2 = angle/2.0
        sinang2 = np.sin(angle2)
        return Quaternion( np.cos(angle2), ax*sinang2, ay*sinang2, az*sinang2 )
    
    
    @classmethod
    def create_from_euler_angles(cls, rx, ry, rz):
        """ create_from_euler_angles( rx, ry, rz)
        
        Classmethod to create a quaternion given the euler angles.
        
        """
        
        # Obtain quaternions
        qx = Quaternion( np.cos(rx/2), np.sin(rx/2), 0, 0 )
        qy = Quaternion( np.cos(ry/2), 0, np.sin(ry/2), 0 )
        qz = Quaternion( np.cos(rz/2), 0, 0, np.sin(rz/2) )
        
        # Almost done
        return qx*qy*qz



## Main

if __name__ =='__main__':
    # A small test
    
    pp = Pointset(3)

    pp.append(1,200,3)
    pp.append(-90,-3.4,0)
    pp.append(-0.0031,0.00000498,0)
    pp.append(2,3,4)
    pp.extend(pp)
    print(pp)
    pp.contains(2,3,4)
    
    print(pp-pp[0])
    print(pp.subtract(pp[0]))
