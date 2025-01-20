# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module motion

Defines the class to create animated data.

"""

import visvis as vv
from visvis import Wobject, Timer
from visvis.core.misc import basestring


class MotionMixin(object):
    """ MotionMixin(axes)
    
    A generic class that represents a wobject that has motion.
    
    This class implements the basic methods to control motion. It uses
    the concept of the motionIndex, which is basically the time parameter.
    Its value specifies the position in the motion sequence with a scalar
    (float) value. Some motion wobject implementations may only support
    integer values though, in which case they should round the motionIndex.
    
    Inheriting classes should implement _GetMotionCount() and
    _SetMotionIndex(index, ii, ww), where ii are four indices, and ww
    are four weights. Together they specify a spline.
    """
    
    def __init__(self):
        
        # Init motion stuff
        self._motionIndex = 0.0
        self._motionIndexDelta = 1.0
        self._motionIsCyclic = True
        self._motionSplineType = 'linear'
        
        # Timer for playing
        self._motionTimer = Timer(self)
        self._motionTimer.Bind(self._MotionTimerCallback)
    
    
    @vv.misc.Property
    def motionIsCyclic():
        """ Get/set whether the motion is cyclic. Default True.
        """
        def fget(self):
            return self._motionIsCyclic
        def fset(self, value):
            self._motionIsCyclic = bool(value)
            self.motionIndex = self.motionIndex
        return locals()
    
    
    @property
    def motionCount(self):
        """ Get the number of temporal instances of this object.
        For objects that do not have a fixed number of elements,
        the returned number may be an arbitrary large number above
        one thousand.
        """
        return self._GetMotionCount()
    
    
    @vv.misc.PropWithDraw
    def motionIndex():
        """ Get/set the motion index; the temporal position in the
        motion. With N the motionCount, if the motion is cyclic, the
        valid range is [0, N>, otherwise [0,N-1]. If the given index
        is not in the valid range, its modulo is taken (cyclic) or
        the index is clipped (not cyclic).
        """
        # This property is where the "reset" basically takes place
        def fget(self):
            return self._motionIndex
        def fset(self, value):
            # Make float
            value = float(value)
            
            # Get N and M (M is index limit)
            N = M = self.motionCount
            if not self.motionIsCyclic:
                M = N-1
            
            # Limit value and set
            if N<2:
                self._motionIndex = 0.0
            else:
                self._motionIndex = self._MotionCorrectIndex(value, M, True)
            
            # Create new deform array
            if N==0 or N==1:
                ii = 0,0,0,0
                ww = 1,0,0,0
            else:
                # Get index and factor
                i1 = int(self._motionIndex)
                t = self._motionIndex - i1
                i0 = self._MotionCorrectIndex(i1-1, M, self._motionIsCyclic)
                i2 = self._MotionCorrectIndex(i1+1, M, self._motionIsCyclic)
                i3 = self._MotionCorrectIndex(i1+2, M, self._motionIsCyclic)
                ii = i0, i1, i2, i3
                # Linear combine
                ww = self._MotionGetCoeff(t, self._motionSplineType)
            
            # Apply
            self._SetMotionIndex(self._motionIndex, ii, ww)
        
        return locals()
    
    
    def _MotionCorrectIndex(self, i, N, cyclic):
        """ _MotionCorrectIndex(i, N, cyclic)
        Correct the given motion index. If cyclic will take the modulo,
        otherwise will clip the index to the valid range.
        """
        if cyclic:
            while i>=N:
                i -= N
            while i<0:
                i += N
        else:
            if i>N:
                i = N
            if i<0:
                i = 0
        return i
    
    
    def _GetMotionCount(self):
        """ _GetMotionCount()
        
        Called to get the number of temporal instances. If there is no limit,
        just return a very large number above thousand. Should be overloaded.
        
        """
        raise NotImplementedError()
    
    
    def _SetMotionIndex(self, index, ii, ww):
        """ _SetMotionIndex(index, ii, ww)
        
        Called when the motion index is set. Should be overloaded.
        
        """
        raise NotImplementedError()
    
    
    def MotionPlay(self, interval=100, delta=1):
        """ MotionPlay(interval=100, delta=1)
        
        Start playing the motion.
        
        This starts a timer that is triggered every interval miliseconds.
        On every trigger the motionIndex is increased by delta.
        
        """
        self._motionIndexDelta = delta
        self._motionTimer.Start(interval, False)
    
    
    def MotionStop(self):
        """ MotionStop()
        
        Stop playing the motion.
        
        """
        self._motionTimer.Stop()
    
    
    def _MotionTimerCallback(self, event):
        """ _MotionTimerCallback(event)
        Callback for the motion timer.
        """
        if self._destroyed:
            # Auto-stop timer if wobject is destroyed
            self._motionTimer.Stop()
            return
        else:
            # Increase deform index
            self.motionIndex += self._motionIndexDelta

    
    @vv.misc.Property
    def motionSplineType():
        """ Get/set the spline type to interpolate the motion. Can be
        'nearest', 'linear', 'cardinal', 'B-spline', or a float between
        -1 and 1 specifying the tension of the cardinal spline. Note that
        the B-spline is an approximating spline. Default 'linear'. Note that
        an implementation may not support interpolation of the temporal
        instances.
        """
        def fget(self):
            return self._motionSplineType
        def fset(self, value):
            if isinstance(value, (float, int)):
                if value >= -1 and value <= 1:
                    self._motionSplineType = float(value)
                else:
                    raise ValueError('Tension parameter must be between -1 and 1.')
            elif isinstance(value, basestring):
                value = value.lower()
                if value in ['nearest', 'linear', 'cardinal', 'c', 'b-spline', 'b']:
                    self._motionSplineType = value
                else:
                    raise ValueError('Invalid spline type.')
            else:
                raise ValueError('motionSplineType must be scalar or string.')
            self.motionIndex = self.motionIndex
        return locals()
    
    
    def _MotionGetCoeff(self, t, spline_type):
        """ _MotionGetCoeff(t, splineType)
        Get the coefficients to interpolate the motion.
        """
        # Accept tension parameter as spline type
        tension = 0.0
        if isinstance(spline_type, (float, int)):
            tension = float(spline_type)
            spline_type = 'cardinal'
        
        # Get id
        spline_type = spline_type.lower()
        if spline_type in ['c', 'card', 'cardinal', 'catmull–rom']:
            tau = 0.5 * (1.0 - tension)
            w0 = - tau * (   t**3 - 2*t**2 + t )
            w3 =   tau * (   t**3 -   t**2     )
            w1 =           2*t**3 - 3*t**2 + 1  - w3
            w2 = -         2*t**3 + 3*t**2      - w0
        elif spline_type in ['b', 'basis', 'basic']:
            w0 = (1-t)**3                     /6.0
            w1 = ( 3*t**3 - 6*t**2 +       4) /6.0
            w2 = (-3*t**3 + 3*t**2 + 3*t + 1) /6.0
            w3 = (  t)**3                     /6.0
        elif spline_type in ['nn', 'nearest']:
            w0, w3 = 0.0, 0.0
            w1 = float(t<0.5)
            w2 = float(not w1)
        else: # Linear
            w0, w3 = 0.0, 0.0
            w1 = (1.0-t)
            w2 = float(t)
        
        # Return coefficients
        return w0, w1, w2, w3


class MotionSyncer(MotionMixin):
    """ MotionSyncer(*motionWobjects)
    
    Simple class to sync the motion of multiple motion objects.
    
    To sync multiple motion objects, give them to the initializer of this
    class, or register them via the append() method. Then use motionPlay()
    on this class.
    
    """
    def __init__(self, *args):
        MotionMixin.__init__(self)
        self._motionObjects = []
        
        # Append given objects
        for arg in args:
            self.append(arg)
    
    
    def append(self, wobject):
        """  append(wobject)
        
        Append (i.e. register) a motion wobject to be synced.
        
        """
        if not isinstance(wobject, MotionMixin):
            raise ValueError('Given object does not inherit from MotionMixin.')
        else:
            self.remove(wobject)
            self._motionObjects.append(wobject)
    
    
    def remove(self, wobject):
        """ remove(wobject)
        
        Remove (i.e. unregister) a motion wobject to be synced. This
        method does nothing if the given wobject was not in the list
        of wobjects to be synced.
        
        """
        while wobject in self._motionObjects:
            self._motionObjects.remove(wobject)
    
    
    def _GetMotionCount(self):
        """ _GetMotionCount()
        
        Get the smallest number of temporal instances for the
        registered MotionWobjects.
        
        """
        
        # Get count for each child
        counts = [child._GetMotionCount() for child in self._motionObjects]
        
        # Take minumum or return 0
        if counts:
            return min(counts)
        else:
            return 0
    
    
    def Draw(self):
        # To behave a bit like a wobject, so that the OnDraw props work
        for child in self._motionObjects:
            child.Draw()
    
    @property
    def _destroyed(self):
        # To stop if one of the motion objects is destroyed
        for child in self._motionObjects:
            if child._destroyed:
                return True
        else:
            return False
    
    
    def _SetMotionIndex(self, index, ii, ww):
        """ _SetMotionIndex(index, ii, ww)
        
        Sets the motion index for all registered MotionWobjects.
        
        """
        for child in self._motionObjects:
            child._SetMotionIndex(index, ii, ww)


class MotionDataContainer(Wobject, MotionMixin):
    """ MotionDataContainer(parent, interval=100)
    
    The motion data container is a wobject that can contain
    several data, which are displayed as a sequence.
    
    The data are simply stored as the wobject's children, and are
    made visible one at a time.
    
    Example
    -------
    # read image
    ims = [vv.imread('astronaut.png')]

    # make list of images: decrease red channel in subsequent images
    for i in range(9):
        im = ims[i].copy()
        im[:,:,0] = im[:,:,0]*0.9
        ims.append(im)

    # create figure, axes, and data container object
    a = vv.gca()
    m = vv.MotionDataContainer(a)

    # create textures, loading them into opengl memory, and insert into container.
    for im in ims:
        t = vv.imshow(im)
        t.parent = m
    
    """
    
    def __init__(self, parent, interval=100):
        Wobject.__init__(self,parent)
        MotionMixin.__init__(self)
        self.motionSplineType = 'nearest'
        self.MotionPlay(interval)
    
    
    @property
    def timer(self):
        """ Get the timer object used to make the objects visible.
        For backward compatibility.
        """
        return self._motionTimer
    
    
    def _GetMotionCount(self):
        """ _GetMotionCount()
        
        Get the number of temporal instances (i.e. children).
        """
        return len(self.children)
    
    
    def _SetMotionIndex(self, index, ii, ww):
        """ _SetMotionIndex(index, ii, ww)
        
        Make the right child visible.
        
        """
        
        # Get index
        index = int(round(index))
        if index<0:
            index = 0
        if index >= len(self.children):
            index = len(self.children)-1
        
        # set all invisible
        for child in self.children:
            child.visible = False
        
        # except one
        if self.children:
            self.children[index].visible = True
        
        # show it!
        self.Draw()
