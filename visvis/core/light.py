# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module light

Defines a light source to light polygonal surfaces. Each axes has up
to eight lights associated with it.

"""

import OpenGL.GL as gl

from visvis.core import misc
from visvis.core.misc import PropWithDraw, DrawAfter, basestring


def _testColor(value, canBeScalar=True):
    """ _testColor(value, canBeScalar=True)
    
    Tests a color whether it is a sequence of 3 or 4 values.
    It returns a 4 element tuple or raises an error if the suplied
    data is incorrect.
    
    """
    
    # Deal with named colors
    if isinstance(value, basestring):
        value = misc.getColor(value)
    
    # Value can be a scalar
    if canBeScalar and isinstance(value, (int, float)):
        if value <= 0:
            value = 0.0
        if value >= 1:
            value = 1.0
        return value
    
    # Otherwise it must be a sequence of 3 or 4 elements
    elif not hasattr(value, '__len__'):
        raise ValueError("Given value can not represent a color.")
    elif len(value) == 4:
        return (value[0], value[1], value[2], value[3])
    elif len(value) == 3:
        return (value[0], value[1], value[2], 1.0)
    else:
        raise ValueError("Given value can not represent a color.")


def _getColor(color, ref):
    """ _getColor(color, reference)
    
    Get the real color as a 4 element tuple, using the reference
    color if the given color is a scalar.
    
    """
    if isinstance(color, float):
        return (color*ref[0], color*ref[1], color*ref[2], ref[3])
    else:
        return color



# todo: implement spot light and attenuation
class Light(object):
    """ Light(axes, index)
    
    A Light object represents a light source in the scene. It
    determines how lit objects (such as Mesh objects) are visualized.
    
    Each axes has 8 light sources, of which the 0th is turned on
    by default. De 0th light source provides the ambient light in the
    scene (the ambient component is 0 by default for the other light
    sources). Obtain the lights using the axes.light0 and axes.lights
    properties.
    
    The 0th light source is a directional camera light by default; it
    shines in the direction in which you look. The other lights are
    oriented at the origin by default.
    
    """
    
    def __init__(self, axes, index):
        
        # Store axes and index of the light (OpenGl can handle up to 8 lights)
        self._axes = axes.GetWeakref()
        self._index = index
        self._on = False
        
        # The three light properties
        self._color = (1, 1, 1, 1)
        self._ambient = 0.0
        self._diffuse = 1.0
        self._specular = 1.0
        
        # The main light has an ambien component by default
        if index == 0:
            self._ambient = 0.2
        
        # Position or direction
        if index == 0:
            self._position = (0,0,1,0)
            self._camLight = True
        else:
            self._position = (0,0,0,1)
            self._camLight = False
    
    
    def Draw(self):
        # Draw axes
        axes = self._axes()
        if axes:
            axes.Draw()
    
    @PropWithDraw
    def color():
        """ Get/Set the reference color of the light. If the ambient,
        diffuse or specular properties specify a scalar, that scalar
        represents the fraction of *this* color.
        """
        def fget(self):
            return self._color
        def fset(self, value):
            self._color = _testColor(value, True)
        return locals()
    
    
    @PropWithDraw
    def ambient():
        """ Get/Set the ambient color of the light. This is the color
        that is everywhere, coming from all directions, independent of
        the light position.
        
        The value can be a 3- or 4-element tuple, a character in
        "rgbycmkw", or a scalar between 0 and 1 that indicates the
        fraction of the reference color.
        """
        def fget(self):
            return self._ambient
        def fset(self, value):
            self._ambient = _testColor(value)
        return locals()
    
    
    @PropWithDraw
    def diffuse():
        """ Get/Set the diffuse color of the light. This component is the
        light that comes from one direction, so it's brighter if it comes
        squarely down on a surface than if it barely glances off the
        surface. It depends on the light position how a material is lit.
        """
        def fget(self):
            return self._diffuse
        def fset(self, value):
            self._diffuse = _testColor(value)
        return locals()
    
    
    @PropWithDraw
    def specular():
        """ Get/Set the specular color of the light. This component
        represents the light that comes from the light source and bounces
        off a surface in a particular direction. This is what makes
        materials appear shiny.
        
        The value can be a 3- or 4-element tuple, a character in
        "rgbycmkw", or a scalar between 0 and 1 that indicates the
        fraction of the reference color.
        """
        def fget(self):
            return self._specular
        def fset(self, value):
            self._specular = _testColor(value)
        return locals()
    
    
    @PropWithDraw
    def position():
        """ Get/Set the position of the light. Can be represented as a
        3 or 4 element tuple. If the fourth element is a 1, the light
        has a position, if it is a 0, it represents a direction (i.o.w. the
        light is a directional light, like the sun).
        """
        def fget(self):
            return self._position
        def fset(self, value):
            if len(value) == 3:
                self._position = value[0], value[1], value[2], 1
            elif len(value) == 4:
                self._position = value[0], value[1], value[2], value[3]
            else:
                tmp = "Light position should be a 3 or 4 element sequence."
                raise ValueError(tmp)
        return locals()
    
    
    @PropWithDraw
    def isDirectional():
        """ Get/Set whether the light is a directional light. A directional
        light has no real position (it can be thought of as infinitely far
        away), but shines in a particular direction. The sun is a good
        example of a directional light.
        """
        def fget(self):
            return self._position[3] == 0
        def fset(self, value):
            # Get fourth element
            if value:
                fourth = 0
            else:
                fourth = 1
            # Set position
            tmp = self._position
            self._position = tmp[0], tmp[1], tmp[2], fourth
        return locals()
    
    
    @PropWithDraw
    def isCamLight():
        """ Get/Set whether the light is a camera light. A camera light
        moves along with the camera, like the lamp on a miner's hat.
        """
        def fget(self):
            return self._camLight
        def fset(self, value):
            self._camLight = bool(value)
        return locals()
    
    
    @DrawAfter
    def On(self, on=True):
        """ On(on=True)
        Turn the light on.
        """
        self._on = bool(on)
    
    
    @DrawAfter
    def Off(self):
        """ Off()
        Turn the light off.
        """
        self._on = False
    
    
    @property
    def isOn(self):
        """ Get whether the light is on.
        """
        return self._on
    
    
    def _Apply(self):
        """ _Apply()
        
        Apply the light position and other properties.
        
        """
        thisLight = gl.GL_LIGHT0 + self._index
        if self._on:
            # Enable and set position
            gl.glEnable(thisLight)
            gl.glLightfv(thisLight, gl.GL_POSITION, self._position)
            # Set colors
            amb, dif, spe = gl.GL_AMBIENT, gl.GL_DIFFUSE, gl.GL_SPECULAR
            gl.glLightfv(thisLight, amb, _getColor(self._ambient, self._color))
            gl.glLightfv(thisLight, dif, _getColor(self._diffuse, self._color))
            gl.glLightfv(thisLight, spe, _getColor(self._specular, self._color))
        else:
            # null-position means that the ligth is off
            gl.glLightfv(thisLight, gl.GL_POSITION, (0.0, 0.0, 0.0, 0.0))
            gl.glDisable(thisLight)
