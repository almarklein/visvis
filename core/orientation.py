# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module baseWobjects

Defines the mix class for orientable wobjects.

"""

import numpy as np
from visvis.core import misc
from visvis.utils.pypoints import Point, is_Point


# todo: is this the best way to allow users to orient their objects,
# or might there be other ways?
class OrientationForWobjects_mixClass(object):
    """ OrientationForWobjects_mixClass()
    
    This class can be mixed with a wobject class to enable easy
    orientation of the objects in space. It makes use of the
    tranformation list that each wobject has.
    
    The functionality provided by this class is not made part of the
    Wobject class because it does not make sense for all kind of wobjects
    (for example lines and images). The OrientableMesh is a class that
    inherits from this class.
    
    """
    
    def __init__(self):
        
        # Set current and reference direction (default up)
        self._refDirection = Point(0,0,1)
        self._direction = Point(0,0,1)
        
        # Create transformations
        self._scaleTransform = misc.Transform_Scale()
        self._translateTransform = misc.Transform_Translate()
        self._rotateTransform = misc.Transform_Rotate()
        self._directionTransform = misc.Transform_Rotate()
        
        # Append transformations to THE list
        self.transformations.append(self._translateTransform)
        self.transformations.append(self._directionTransform)
        self.transformations.append(self._rotateTransform)
        self.transformations.append(self._scaleTransform)
    
    
    @misc.PropWithDraw
    def scaling():
        """ Get/Set the scaling of the object. Can be set using
        a 3-element tuple, a 3D point, or a scalar. The getter always
        returns a Point.
        """
        def fget(self):
            s = self._scaleTransform
            return Point(s.sx, s.sy, s.sz)
        def fset(self, value):
            if isinstance(value, (float, int)):
                self._scaleTransform.sx = float(value)
                self._scaleTransform.sy = float(value)
                self._scaleTransform.sz = float(value)
            elif isinstance(value, (list, tuple)) and len(value) == 3:
                self._scaleTransform.sx = float(value[0])
                self._scaleTransform.sy = float(value[1])
                self._scaleTransform.sz = float(value[2])
            elif is_Point(value) and value.ndim == 3:
                self._scaleTransform.sx = value.x
                self._scaleTransform.sy = value.y
                self._scaleTransform.sz = value.z
            else:
                raise ValueError('Scaling should be a scalar, 3D Point, or 3-element tuple.')
        return locals()
    
    
    @misc.PropWithDraw
    def translation():
        """ Get/Set the transaltion of the object. Can be set using
        a 3-element tuple or a 3D point. The getter always returns
        a Point.
        """
        def fget(self):
            d = self._translateTransform
            return Point(d.dx, d.dy, d.dz)
        def fset(self, value):
            if isinstance(value, (list, tuple)) and len(value) == 3:
                self._translateTransform.dx = value[0]
                self._translateTransform.dy = value[1]
                self._translateTransform.dz = value[2]
            elif is_Point(value) and value.ndim == 3:
                self._translateTransform.dx = value.x
                self._translateTransform.dy = value.y
                self._translateTransform.dz = value.z
            else:
                raise ValueError('Translation should be a 3D Point or 3-element tuple.')
        return locals()
    
    
    @misc.PropWithDraw
    def direction():
        """ Get/Set the direction (i.e. orientation) of the object. Can
        be set using a 3-element tuple or a 3D point. The getter always
        returns a Point.
        """
        def fget(self):
            return self._direction.copy()
        def fset(self, value):
            # Store direction
            if isinstance(value, (list, tuple)) and len(value) == 3:
                self._direction = Point(*tuple(value))
            elif is_Point(value) and value.ndim == 3:
                self._direction = value
            else:
                raise ValueError('Direction should be a 3D Point or 3-element tuple.')
            
            # Normalize
            if self._direction.norm()==0:
                raise ValueError('Direction vector must have a non-zero length.')
            self._direction = self._direction.normalize()
            
            # Create ref point
            refPoint = self._refDirection
            
            # Convert to rotation. The cross product of two vectors results
            # in a vector normal to both vectors. This is the axis of rotation
            # over which the minimal rotation is achieved.
            axis = self._direction.cross(refPoint)
            if axis.norm() < 0.01:
                if self._direction.z > 0:
                    # No rotation
                    self._directionTransform.ax = 0.0
                    self._directionTransform.ay = 0.0
                    self._directionTransform.az = 1.0
                    self._directionTransform.angle = 0.0
                else:
                    # Flipped
                    self._directionTransform.ax = 1.0
                    self._directionTransform.ay = 0.0
                    self._directionTransform.az = 0.0
                    self._directionTransform.angle = 180.0
            else:
                axis = axis.normalize()
                angle = -refPoint.angle(self._direction)
                self._directionTransform.ax = axis.x
                self._directionTransform.ay = axis.y
                self._directionTransform.az = axis.z
                self._directionTransform.angle = angle * 180 / np.pi
        return locals()
    
    
    @misc.PropWithDraw
    def rotation():
        """ Get/Set the rotation of the object (in degrees, around its
        direction vector).
        """
        def fget(self):
            return self._rotateTransform.angle
        def fset(self, value):
            self._rotateTransform.angle = float(value)
        return locals()
