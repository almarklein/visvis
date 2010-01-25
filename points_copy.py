""" MODULE points
usage:
from points import Point, Pointset [, Aarray]

A point represents a location or vector. The dimension of the point 
is at least 2D. A pointset represents an ordered set (or list) of 
points. It has methods to add and remove points. Both point instances 
and pointset instances have methods for mathematical operations, like 
for example calculating distances between points and cross correlation. 
For the Pointset these operations are efficiently applied to all points.

The Aarray class implements numpy.ndarray and provides a way to store
and handle anisotropic data.

For more information see the docs in the Point, Pointset, and Aarray classes.

This software is free for all to use, change and redistribute.

Author: Almar Klein
Date: August 2009

"""

import numpy as np
import sys

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


def nearestPowerOfTwo(i):
    ii = 1
    while ii<i:
        ii*=2
    return ii


def checkTheTwo(p1,p2, what='something'):
        """ Check if the two things (self and a second point/pointset)
        can be used to calculate stuff.
        Returns (p1,p2), if one is a point, p1 is it.
        """
        
        # define errors
        tmp = "To calculate %s between two pointsets, " % what
        er1 = tmp + "both pointsets must be of equal length."
        er2 = tmp + "the dimensions must be equal."
        
        # if one is a point, put in in p1
        if isinstance(p1,Pointset):
            p2,p1 = p1,p2
        
        # only pointsets of equal length can be used
        if not isinstance(p1, Point) and len(p1) != len(p2):
            raise ValueError(er1)
        
        # check dimensions
        if p1.ndim != p2.ndim:
            tmp = "the dimensions must be equal."
            raise ValueError(er2)
        
        return p1, p2


class BasePoints(object):
    """ Abstract class. Contains all the math stuff. 
    """
    
    ## Common stuff (of which most is overloaded)
    
    @property
    def ndim(self):
        """ Get the number of dimensions. """        
        return self._data.shape[-1]
    
    @property
    def data(self):
        raise NotImplemented()
    
    def Copy(self):
        raise NotImplemented()
    
    def __setitem__(self):
        raise NotImplemented()
    
    def __getitem__(self):
        raise NotImplemented()
    
    
    ## Math stuff on a single vector


    def Norm(self):
        """ Calculate the norm (length) of the vector.
        This is the same as the distance to point 0,0 or 0,0,0,
        but implemented a bit faster.
        """
        
        # we could do something like:
        #   return self.Distance(Point(0,0,0))
        # but we don't have to perform checks now, which is faster...
        
        data = self.data
        dists = np.zeros( (data.shape[0],) )
        for i in range(self.ndim):
            dists += data[:,i]**2            
        return np.sqrt(dists)


    def Normalize(self):
        """ "Return normalized vector (to unit length). 
        """
        
        # calculate factor array
        f = 1.0/self.Norm()
        f.shape = f.size,1
        f = f.repeat(self.ndim,1)
        
        # apply
        data = self.data * f
        
        # return as point or pointset
        if isinstance(self, Point):
            return Point(data)
        else:
            return Pointset(data)


    def Normal(self):
        """" Calculate normalized normal of vector, 
        use (p1-p2).Normal() to calculate the normal of the line p1-p2.
        Only works on 2D points. For 3D points use Cross()
        """
        # check dims
        if not self.ndim == 2:
            raise ValueError("Normal can only be calculated for 2D points.")
        
        # prepare
        a = self.Copy()        
        f = 1.0/self.Norm()
        
        # swap xy, y goes minus
        tmp = a.data[:,0].copy()
        a.data[:,0] = a.data[:,1] * f
        a.data[:,1] = -tmp * f
        return a


    ## Math stuff on two vectors
    
    
    def Distance(self, *p):
        """ Calculate the distance between two points or pointsets. 
        Use Norm() to calculate the length of a vector.
        """
        
        # the point directly given?
        if len(p)==1:
            p = p[0]
        
        # make sure p is a point or poinset
        if not isinstance(p,(Point, Pointset)):
            p = Point(p)        
        
        # check
        p1,p2 = checkTheTwo(self,p,'distance')
        
        # calculate
        dists = np.zeros( (p2.data.shape[0],) )
        for i in range(p1.ndim):
            tmp = p1.data[:,i] - p2.data[:,i]
            dists += tmp**2        
        return np.sqrt(dists)


    def Angle(self, *p):
        """ Calculate the angle (in radians) between two points 
        or pointsets. For 2D and 3D only.
        For 2D uses the arctan2 method so the angle has a sign.
        For 3D the angle is the smallest angles between the two
        vectors.
        If no point is given, the angle is calculates relative to the
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
        if not isinstance(p,(Point, Pointset)):
            p = Point(p)        
        
        # check. Keep the correct order!
        checkTheTwo(self,p,'angle')
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
            p1, p2 = p1.Normalize(), p2.Normalize()
            data = p1.Dot(p2)
            # correct for round off errors (or we will get NANs)
            data[data>1.0] = 1.0
            data[data<-1.0] = -1.0
            #return data
            return np.arccos(data)
        
        else:
            # not possible
            raise ValueError("Can only calculate angle for 2D and 3D vectors.")
            
    
    def Dot(self, *p):
        """ Calculate the dot product of the two points or pointsets. 
        The dot producet is the standard inner product of the 
        orthonormal Euclidean space.
        """
        
        # the point directly given?
        if len(p)==1:
            p = p[0]
            
        # make sure p is a point or poinset
        if not isinstance(p,(Point, Pointset)):
            p = Point(p)        
        
        # check
        p1,p2 = checkTheTwo(self,p,'dot')
        
        # calculate
        data1, data2 = p1.data, p2.data
        data = np.zeros( (p2.data.shape[0],) )
        for i in range(p1.ndim):
            tmp = p1.data[:,i] * p2.data[:,i]
            data += tmp
        return data
    
    
    def Cross(self, *p):
        """ The cross product of two 3D vectors. 
        Given two vectors, returns the vector that is orthogonal to
        both vectors. The right hand rule is applied. This vector is
        the middle finger, the argument the index finger, the returned
        vector points in the direction of the thumb.
        """
        
         # the point directly given?
        if len(p)==1:
            p = p[0]
        
        if not self.ndim == 3:
            raise ValueError("Cross product only works for 3D vectors!")
        
        # make sure p is a point or poinset
        if not isinstance(p,(Point, Pointset)):
            p = Point(p)        
        
        # check (note that we use the original order for calculation)
        p1, p2 = checkTheTwo(self,p,'cross')
        
        # calculate
        a, b = self.data, p.data
        data = np.zeros( p2.data.shape, np.float32 )
        data[:,0] = a[:,1]*b[:,2] - a[:,2]*b[:,1]
        data[:,1] = a[:,2]*b[:,0] - a[:,0]*b[:,2]
        data[:,2] = a[:,0]*b[:,1] - a[:,1]*b[:,0]
        
        # return
        if isinstance(p2,Pointset):
            return Pointset(data)
        else:
            return Point(data)


    def __add__(self, p):
        """ Add vectors. """
        
        # make sure p is a point or poinset
        if not isinstance(p,(Point, Pointset)):
            p = Point(p)        
        
        # check
        p1,p2 = checkTheTwo(self,p,'add')
        
        # apply and return
        data = p1.data + p2.data # this should go well
        if isinstance(self, Point):
            return Point(data)
        else:
            return Pointset(data)


    def __sub__(self, p):
        """ Subtract vectors. """
        
        # make sure p is a point or pointset
        if not isinstance(p,(Point, Pointset)):
            p = Point(p)        
        
        # check
        p1,p2 = checkTheTwo(self,p,'subtract')
        
        # apply and return
        data = p1.data - p2.data # this should go well
        if isinstance(self, Point):
            return Point(data)
        else:
            return Pointset(data)


    def __mul__(self,value):
        """ Scale vectors. """
        try:
            value = float(value)
            data1, data2 = self.data, value
        except TypeError:
            
            if not isinstance(value,(Point, Pointset)):
                value = Point(value)
                
            # check
            p1,p2 = checkTheTwo(self,value,'multiply')
            data1, data2 = self.data, value.data
            
        # apply and return
        data = data1 * data2 # this should go well
        if isinstance(self, Point):
            return Point(data)
        else:
            return Pointset(data)

    
    def __div__(self, value):
        """ Scale vectors. """
        try:
            value = float(value)
            data1, data2 = self.data, value
        except TypeError:
            
            if not isinstance(value,(Point, Pointset)):
                value = Point(value)
                
            # check (note that the order is important for division!)
            checkTheTwo(self,value,'divide')
            data1, data2 = self.data, value.data
            
        # apply and return
        data = data1 / data2 # this should go well
        if isinstance(self, Point):
            return Point(data)
        else:
            return Pointset(data)
    
    
    def __rmul__(self, value):
        """ Same as normal multiply. """
        return self.__mul__(value)
    
    
    def __rdiv__(self, value):
        """ Inverse scale vectors. """
        try:
            value = float(value)
            data1, data2 = self.data, value
        except TypeError:
            
            if not isinstance(value,(Point, Pointset)):
                value = Point(value)
                
            # check (note that the order is important for division!)
            checkTheTwo(self,value,'divide')
            data1, data2 = self.data, value.data
            
        # apply and return
        data = data2 / data1 # here's the difference
        if isinstance(self, Point):
            return Point(data)
        else:
            return Pointset(data)


class Point(BasePoints):
    """ The Point class - a point or vector
    
    The point class provides a way to store a vector and some common 
    mathematical operations common for vectors/points. There is no limit
    to the amount of dimensions for a point to have.
    
    Examples:
    p1 = Point(3.2,4)   # a 2D point
    p2 = p1.Copy()      # make a copy
    p1[0] = 9           # set the first element
    p1.x                # convenience property (.y and .z also available)
    p1.xi               # idem, but rounded to nearest integer
    p1.Distance(p2)     # calculate distance
    p1 + p2             # calculate the addition of the two vectors
    p2 = p1*2           # scale vector
    p2 = p1 * p2        # even for each dimension seperately
    p2 = p2.Normalize() # make unit length
    
    """
    
    def __init__(self, *point):
        BasePoints.__init__(self)
        
        if len(point)==0:
            raise ValueError("Cannot create an 'empty' point.")
        elif len(point)==1:
            point = point[0]
        
        # a point
        if isinstance(point, Point):
            self._data = point._data.astype(np.float32)
        # a tuple or list
        elif isinstance(point, (tuple,list)):
            try:
                self._data = np.array(point, dtype=np.float32)
            except ValueError, why:
                raise why
        # a numpy array
        elif isinstance(point, np.ndarray):
            self._data = point.astype(np.float32)
        # otherwise, what were we given?
        else:
            raise ValueError("Cannot create a point with that argument.")
        
        # remove singleton dimensions
        self._data = np.squeeze(self._data)
        
        # check integrity
        if len(self._data.shape) != 1:
            # this must be the case to allow indexing!
            raise ValueError("A point should be given as a 1D array.")
        if self._data.shape[0] < 2:
            raise ValueError("A point should consist of at least two values.")


    def Copy(self):
        return Point(self._data)
    
    
    @property
    def data(self):
        """ Get the point as the numpy array it is stored in. 
        The result is always 2D.
        """
        # this is overloaded in the Pointset class
        data = self._data[:]
        data.shape = 1, data.shape[0]
        return data
    

    ## string representation
    
    def __str__(self):
        """ Return a nice string representation of the point. 
        """
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
        if not isinstance(other, Point) or other.ndim != self.ndim:
            return False
        return (other.data == self.data).sum() == self.ndim
            

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
    
    @property
    def xi(self):
        """ Return p[0] rounded to the nearest integer, for indexing. """
        return int(self._data[0]+0.5)
    
    @Property    
    def y():
        """ Get/set p[1]. """
        def fget(self):
            return self._data[1]
        def fset(self, value):
            self._data[1] = value
       
    @property
    def yi(self):
        """ Return p[1] rounded to the nearest integer, for indexing. """
        return int(self._data[1]+0.5)
    
    @Property    
    def z():
        """ Get/set p[2]. """
        def fget(self):
            return self._data[2]
        def fset(self, value):
            self._data[2] = value
    
    @property
    def zi(self):
        """ Return p[2] rounded to the nearest integer, for indexing. """
        return int(self._data[2]+0.5)
    

class Pointset(BasePoints):
    """ The Poinset class - a list of points or vectors.
    
    A pointset provides an efficient and fast way to store points.
    Internally the points are stored in a numpy array that is
    resized by a factors of two when more space is required. Therefore
    mathematical operations can be applied on all the points in the set
    efficiently.
    
    Slicing:
    pp[7]       When indexing, the corresponding Point instance is get/set.
    pp[7:20]    When slicing, a new poinset (subset) is get/set. 
    pp[4:9,3]   When using two indices or slices, the indices are applied to 
                the internal data. (In this example returning the z-value for
                points 4 till 8.)
    
    The same mathematical operations that can be applied to a point 
    instance can also be applied to a pointset instance. The operation
    is applied to all points in the set. For example pp.Distance(3,4)
    returns an array with the distances of all points in pp to (3,4).
    
    Examples:
    a  = <...>          # an existing 100x2 array
    pp1= Pointset(2)    # pointset with two dimensions
    pp = Pointset(a)    # dito    
    pp1.Append(3,4)     # add a point
    pp1.Append(p)       # add an existing point p
    pp1.Extend(pp1)     # extend pp1 to itself
    pp[:4] = pp2        # replace first four points of pp
    pp[1]               # returns the point (3,4) (as a Point instance)
    pp[1,0]             # returns the value 3.0
    pp[:,1]             # get all y values
    pp.Contains(3,4)    # will return True
    
    """
    
    def __init__(self, ndim):
        BasePoints.__init__(self)
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
            if data.shape[1] < 2:
                tmp = "Each point should consist of at least two values."
                raise ValueError(tmp)            
            # create array            
            self._len = data.shape[0]
            L = max( nearestPowerOfTwo(data.shape[0]), initialLength)
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
        necesary. 
        
        This property returns a (sub)view of that array and is always 2D.        
        """
        return self._data[:self._len,:]

    
    def _AsPoint(self, *p):
        """ Return the input as a point instance, also
        check whether the dimensions match. """
        
        # the point directly given?
        if len(p)==1:
            p = p[0]
        
        # make sure we are dealing with a point
        if not isinstance(p, Point):
            p = Point(p)
        
        # check whether we can append it
        if self.ndim != p.ndim:
            tmp = "Given point does not match dimension of pointset."
            raise ValueError(tmp)
        
        # done
        return p
    
    
    def _ResizeIfRequired(self, n=None):
        """ Resize the internal array, n is the new required
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
            L = nearestPowerOfTwo(n)
        elif n*4 <= internalLen and internalLen > 16:
            L = nearestPowerOfTwo(n*2)
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
            if not isinstance(value, Pointset):
                tmp = "When slicing with a single index "
                raise ValueError(tmp+ "the supplied value must be a pointset.")
            self.data[index] = value.data
        # otherwise, return point
        else:
            value = self._AsPoint(value)
#             if not isinstance(value, Point):
#                 tmp = "When indexing with a single index "
#                 raise ValueError(tmp + "the supplied value must be a point.")
            self.data[index] = value.data
    
    
    def __getitem__(self, index):
        """ Get a point or part of the pointset. """
        # a tuple given: return as array
        if isinstance(index, tuple):
            return self.data[index]
        # for a slice, return subset
        elif isinstance(index, slice):
            return Pointset( self.data[index] )
        # otherwise, return point
        else:            
            return Point( self.data[index] )
    
    
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
        self._ResizeIfRequired()

    
    ## Appending / Extending
    
    
    def Append(self, *p):
        """Append a point to this pointset.
        Usage: Append(p)
        If p is not an instance of the Point class,  the constructor 
        of Point is called to create one from the given argument.
        """
        try:
            p = self._AsPoint(*p)
        except Exception, why:
            raise ValueError(why)
        
        # resize if we need to
        self._ResizeIfRequired(self._len+1)
        
        # append point
        self._data[self._len,:] = p._data
        self._len += 1
    
    
    def Extend(self, pp):
        """ Extend this pointset with another pointset, thus
        combining the two.         
        If pointset is not an instance of the Pointset class, the constructor 
        of Pointset is called to create one from the given argument.
        """
        
        # make sure we are dealing with a pointset
        if not isinstance(pp, Pointset):
            try:
                pp = Pointset(pp)            
            except Exception, why:
                raise ValueError(why)
        
        # check whether we can append it
        if self.ndim != pp.ndim:
            raise ValueError("Can only extend pointsets of equal dimensions.")
        
        # resize the array if needed
        newLen = self._len + pp._len
        self._ResizeIfRequired(newLen)
        
        # append new data
        i1 = self._len
        i2 = i1 + pp._len
        self._data[i1:i2,:] = pp._data[:pp._len,:]
        self._len = newLen


    def Insert(self, index, *p):
        """ Insert a point at the given index. 
        """
        # check index
        if index < 0:
            index = self._len + index
        if index<0 or index>self._len:
            raise IndexError("Index to insert point out of range.")
        
        # make sure p is a point
        try:
            p = self._AsPoint(*p)
        except Exception, why:
            raise ValueError(why)
        
        # resize if we need to
        self._ResizeIfRequired(self._len+1)
        
        # insert point
        tmp = self._data[index:self._len,:].copy()
        self._data[index,:] = p._data
        self._data[index+1:self._len+1,:] = tmp
        self._len += 1
    
    
    def Remove(self, *p):
        """ Remove first occurance of the given point from the list. 
        Produces an error if such a point is not present.
        See also RemoveAll()
        """
        
        # make sure p is a point
        try:
            p = self._AsPoint(*p)
        except Exception, why:
            raise ValueError(why)
        
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

    
    def RemoveAll(self, *p):
        """ Remove all occurances of the given point. If there
        is no occurance, no action is taken. 
        """
        
        # make sure p is a point
        try:
            p = self._AsPoint(*p)
        except Exception, why:
            raise ValueError(why)
        
        # calculate mask
        mask = np.zeros((len(self),),dtype='uint8')
        for i in range(self.ndim):
            mask += self.data[:,i]==p[i]
        
        # find points given
        I, = np.where(mask==self.ndim)
        
        # remove all points (backwards!)
        indices = sorted( [i for i in I] )
        for i in reverserd(indices):
            del self[i]
    
    
    def Pop(self, index=-1):
        """ Returns and removes a point in the pointset. Default
        removes last.
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
            self._ResizeIfRequired()            
        else:            
            del self[index]
        
        # return
        return p
    
    
    def Clear(self):
        """ Remove all points in the pointset. """
        self.__init__(self.ndim)
    
    
    def Copy(self):
        """ Return a copy of this pointset. """
        return Pointset(self._data[:self._len,:])
    
    
    ## Sequence stuff
    
    
    def __len__(self):
        return self._len
    
    def __iter__(self):
        self._index = -1
        return self
    
    def next(self):
        self._index +=1
        if self._index >= len(self):  raise StopIteration
        return self[self._index]
   
    
    def Contains(self, *p):
        """ Check whether a point is already in this set. """
        # make sure p is a point
        try:
            p = self._AsPoint(*p)
        except Exception, why:
            raise ValueError(why)
        
        mask = np.zeros((len(self),),dtype='uint8')
        for i in range(self.ndim):
            mask += self.data[:,i]==p[i]
        if mask.max() >= self.ndim:
            return True
        else:
            return False


    ## String representation
    
    def __str__(self):
        """ Return a nice string representation of the pointset. 
        """
        s = ""
        for i in range(len(self)):
            s += "%3d: " % (i)            
            s += str(self[i])
            s += "\n"
        return s

    def __repr__(self):
        """" Return short(one line) string representation of the pointset.
        """
        return "<pointset with %i points of %i dimensions>" % (
            len(self), self.ndim )

    

class Aarray(np.ndarray):
    """ Aarray(shapeOrArray, sampling=None, origin=None, fill=None, 
                dtype='float32', **kwargs)
    
    Anisotropic array, inherits from numpy.ndarray and adds a sampling 
    property which gives the sample distance in each dimension. Implements 
    the following properties and methods:
        sampling        The distance between samples
        origin          The origin of the data
        getStart()      Get the origin of the data in world coordinates
        getEnd()        Get the end of the data in world coordinates
        getSize()       Get the size of the data in world coordinates
        pointToIndex()  Given a poin, returns the index in the array
        indexToPoint()  Given an index, returns the world coordinate
    
    World coordinates are always expressed as points. Whereas indices
    as well as the "sampling" and "origin" attributes are expressed 
    as tuples in z,y,x order.
    
    Init using an existing array (which is copied), or the shape of 
    the new array, in which case it is filled with the value specified 
    by "fill".
    
    """
    def __new__(cls, shapeOrArray, sampling=None, origin=None, fill=None, 
                dtype='float32', **kwargs):
        
        data = None        
        if isinstance(shapeOrArray, np.ndarray):
            data = shapeOrArray
            shape = data.shape
        else:
            shape = shapeOrArray
        
        ob = np.ndarray.__new__(cls,shape,dtype=dtype,**kwargs)
        
        # init sampling and origin
        ob._sampling = tuple( [1.0 for i in ob.shape] )
        ob._origin = tuple( [0.0 for i in ob.shape] )
        
        # copy data?
        if data is not None:
            ob[:] = data[:]
        elif fill is not None:
            ob[:] = fill
        
        # set them
        if sampling:
            ob.sampling = sampling
        if origin:
            ob.origin = origin
        
        # return
        return ob
    
    def __array_finalize__(self, obj):
        """ So the sampling and origin is maintained when doing
        calculations with the array. """
        #if hasattr(obj, '_sampling') and hasattr(obj, '_origin'):
        if isinstance(obj, Aarray):
            self._sampling = tuple( [i for i in obj._sampling] )        
            self._origin = tuple( [i for i in obj._origin] )
    
    def _setSampling(self,sampling):
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
        
    def _getSampling(self):
        # todo: when an array is copied... _sampling and _origin are not copied
        # along... maybe wrap it?
        l1, l2 = len(self._sampling), len(self.shape)
        if  l1 < l2:
            tmp = list(self._sampling)
            tmp.extend( [1 for i in range(l2-l1)] )
            return tuple( tmp )
        elif l1 > l2:
            tmp = [self._sampling[i] for i in range(l2)]
            return tuple(tmp)
        else:
            return self._sampling
    
    sampling = property(_getSampling, _setSampling, None, 
        "A tuple with the sample distance in each dimension.")
    
    def _setOrigin(self,origin):
        if not isinstance(origin, (list,tuple)):
            raise ValueError("Origin must be specified as a tuple or list.")
        if len(origin) != len(self.shape):
            raise ValueError("Origin given must match shape.")
        # set
        tmp = [float(i) for i in origin]
        self._origin = tuple(tmp)
        
    def _getOrigin(self):
        l1, l2 = len(self._origin), len(self.shape)
        if  l1 < l2:
            tmp = list(self._origin)
            tmp.extend( [0 for i in range(l2-l1)] )
            return tuple( tmp )
        elif l1 > l2:
            tmp = [self._origin[i] for i in range(l2)]
            return tuple(tmp)
        else:
            return self._origin
    
    origin = property(_getOrigin, _setOrigin, None, 
        "A tuple with the origin for each dimension.")
    
    
    def pointToIndex(self, point, noneOnIndexError=False):
        """ Given a point returns the sample index (z,y,x,..) closest
        to the given point.
        Returns a tuple with as many elements as there are dimensions.
        If the point is outside the array an IndexError is raised by default,
        and None is returned when noneOnIndexError = True. In the latter case,
        we strongly advice to check if None was returned.
        """
        # check
        if not isinstance(point,Point):
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
        if ii is None and noneOnIndexError:
            return None
        elif ii is None:            
            raise IndexError("Sample position out of range: %s" % str(point))
        else:
            return tuple(ii)
    
    
    def sample(self, point, default=None):
        """ Take a sample of the array, given the given point
        in world-coordinates, i.e. transformed using sampling.
        By default raises an IndexError if the point is not inside
        the array, and returns the value of "default" if it is given.
        """
        tmp = self.pointToIndex(point,True)
        if tmp is None:
            if default is None:
                ps = str(point)
                raise IndexError("Sample position out of range: %s" % ps)
            else:
                return default
        return self[tmp]


    def indexToPoint(self, *index):
        """ Given an index, get the corresponding point in world
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


    def getSize(self):
        """ Get the size (as a vector) of the array 
        expressed in world coordinates. """ 
        pp = []
        for i in range(len(self.shape)):
            pp.append( self._sampling[i] * self.shape[i] )
        pp.reverse()
        return Point(pp)
    
    
    def getStart(self):
        """ Get the origin of the array expressed in world coordinates. 
        Differs from the property 'origin' in that this method returns
        a point rather than indices z,y,x. """
        pp = [i for i in self.origin]
        pp.reverse()
        return Point(pp)
    
    
    def getEnd(self):
        """ Get the end of the array expressed in world coordinates. 
        Same as the property 'origin'. """ 
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
    
    def __init__(self, w=1, x=0, y=0, z=0, normalize=True):
        self.w = w
        self.x, self.y, self.z = x, y, z
        if normalize:
            self._Normalize()
    
    
    def __repr__(self):
        return "<Quaternion object %1.3g + %1.3gi + %1.3gj + %1.3gk>" % (
                self.w, self.x, self.y, self.z)
    
    
    def Copy(self):
        """ Copy()
        Create an exact copy of this quaternion. 
        """
        return Quaternion(self.w, self.x, self.y, self.z, False)
    
    
    def Norm(self):
        """ Norm()
        Returns the norm of the quaternion.
        norm = w**2 + x**2 + y**2 + z**2
        """
        tmp = self.w**2 + self.x**2 + self.y**2 + self.z**2
        return tmp**0.5
    
    
    def _Normalize(self):
        """ _Normalize()
        Make the quaternion unit length.
        """
        # Get length
        L = self.Norm()
        if not L:
            raise ValueError('Quaternion cannot have 0-length.')
        # Correct
        self.w /= L
        self.x /= L
        self.y /= L
        self.z /= L
    
    
    def Normalized(self):
        """ Normalized()
        Returns a normalized (unit length) version of the quaternion.
        """
        new = self.Copy()
        new._Normalize()
        return new
    
    
    def Conjugate(self):
        """ Conjugate()
        Obtain the conjugate of the quaternion.
        This is simply the same quaternion but with the sign of the
        imaginary (vector) parts reversed.
        """
        new = self.Copy()
        new.x *= -1
        new.y *= -1
        new.z *= -1
        return new
    
    
    def Inverse(self):
        """ Inverse()
        returns q.Conjugate()/q.Norm()**2
        So if the quaternion is unit length, it is the same
        as the Conjugate.
        """
        new = self.Conjugate()
        tmp = self.Norm()**2
        new.w /= tmp
        new.x /= tmp
        new.y /= tmp
        new.z /= tmp
        return new
    
    
    def Exp(self):
        """ Exp()
        Returns the exponent of the quaternion. 
        (not tested)
        """
        
        # Init
        vecNorm = self.x**2 + self.y**2 + self.z**2
        wPart = np.e**self.w        
        q = Quaternion()
        
        # Calculate
        q.w = wPart * np.cos(vecNorm)
        q.x = wPart * self.x * np.sin(vecNorm) / vecNorm
        q.y = wPart * self.y * np.sin(vecNorm) / vecNorm
        q.z = wPart * self.z * np.sin(vecNorm) / vecNorm
    
    
    def Log(self):
        """ Log()
        Returns the natural logarithm of the quaternion. 
        (not tested)
        """
        
        # Init
        norm = self.Norm()
        vecNorm = self.x**2 + self.y**2 + self.z**2
        tmp = self.w / norm
        q = Quaternion()
        
        # Calculate
        q.w = np.log(norm)
        q.x = np.log(norm) * self.x * np.arccos(tmp) / vecNorm
        q.y = np.log(norm) * self.y * np.arccos(tmp) / vecNorm
        q.z = np.log(norm) * self.z * np.arccos(tmp) / vecNorm
    
    
    def __add__(self, q):
        """ Add quaternions. """
        new = self.Copy()
        new.w += q.w
        new.x += q.x
        new.y += q.y
        new.z += q.z
        return new
    
    
    def __sub__(self, q):
        """ Subtract quaternions. """
        new = self.Copy()
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
    
    
    def RotatePoint(self, p):
        """ RotatePoint(p)
        Rotate a Point instance using this quaternion.
        """
        # Prepare 
        p = Quaternion(0, p.x, p.y, p.z, False) # Do not normalize!
        q1 = self.Normalized()
        q2 = self.Inverse()
        # Apply rotation
        r = (q1*p)*q2
        # Make point and return        
        return Point(r.x, r.y, r.z)
    
    
    def GetMatrix(self):
        """ GetMatrix()
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
    
    
    def GetAxisAngle(self):
        """ GetAxisAngle()
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
            ax, ay, ax = 1, 0, 0 
        
        # Return
        return angle, ax, ay, az

    
    @classmethod
    def CreateFromAxisAngle(cls, angle, ax, ay, az):
        """ CreateFromAxisAngle(angle, ax, ay, ax)
        Classmethod to create a quaternion from an axis-angle representation. 
        (angle should be in radians).
        """
        angle2 = angle/2.0
        sinang2 = np.sin(angle2)
        return Quaternion( np.cos(angle2), ax*sinang2, ay*sinang2, az*sinang2 )
    
    
    @classmethod
    def CreateFromEulerAngles(cls, rx, ry, rz):
        """ CreateFromEulerAngles( rx, ry, rz)
        Classmethod to create a quaternion given the euler angles. 
        """
        
        # Obtain quaternions
        qx = Quaternion( np.cos(rx)/2, np.sin(rx/2), 0, 0 )
        qy = Quaternion( np.cos(ry)/2, 0, np.sin(ry/2), 0 )
        qz = Quaternion( np.cos(rz)/2, 0, 0, np.sin(rz/2) )
        
        # Almost done
        return qx*qy*qz

    
## Main

if __name__ =='__main__':

    pp = Pointset(3)

    pp.Append(1,200,3)
    pp.Append(-90,-3.4,0)
    pp.Append(-0.0031,0.00000498,0)
    pp.Append(2,3,4)
    pp.Extend(pp)
    print pp
    pp.Contains(2,3,4)
    