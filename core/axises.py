# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module axises

Defines the Axis wobject class to draw tickmarks and lines for each
dimension.

I chose to name this module using an awkward plural to avoid a name clash
with the axis() function.


"""

# todo: split in multiple modules axis_base axis_2d, axis_3d, axis_polar

import OpenGL.GL as gl
import OpenGL.GLU as glu

import numpy as np
import math

from visvis.utils.pypoints import Pointset, Point
#
from visvis.core import base
from visvis.core.misc import Range, getColor, basestring
from visvis.core.misc import Property, PropWithDraw, DrawAfter
#
from visvis.text import Text
from visvis.core.line import lineStyles, PolarLine
from visvis.core.cameras import depthToZ, TwoDCamera, FlyCamera


# A note about tick labels. We format these such that the width of the ticks
# never becomes larger than 10 characters (including sign bit).
# With a fontsize of 9, this needs little less than 70 pixels. The
# correction applied when visualizing axis (and ticks) is 60, because
# the default offset is 10 pixels for the axes.
# See the docstring of GetTickTexts() for more info.

# create tick units
_tickUnits = []
for e in range(-10, 98):
    for i in [10, 20, 25, 50]:
        _tickUnits.append( i*10**e)


class AxisText(Text):
    """ Text with a disabled Draw() method. """
    
    def Draw(self):
        pass
    
    @Property
    def x():
        """Get/Set the x position of the text."""
        def fget(self):
            return self._x
        def fset(self, value):
            self._x = value
        return locals()
    
    @Property
    def y():
        """Get/Set the y position of the text."""
        def fget(self):
            return self._y
        def fset(self, value):
            self._y = value
        return locals()
    
    @Property
    def z():
        """Get/Set the z position of the text."""
        def fget(self):
            return self._z
        def fset(self, value):
            self._z = value
        return locals()


class AxisLabel(AxisText):
    """ AxisLabel(parent, text)
    
    A special label that moves itself just past the tickmarks.
    The _textDict attribute should contain the Text objects of the tickmarks.

    This is a helper class for the axis classes, and has a disabled Draw()
    method.
    
    """

    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self._textDict = {}
        self._move = 0
        
        # upon creation, one typically needs a second draw; only after all
        # ticks are drawn can this label be positioned properly.
    
    def OnDrawScreen(self):
        
        # get current position
        pos = Point(self._screenx, self._screeny)
        
        # get normal vector eminating from that position
        if int(self.textAngle) == 90:
            a = (self.textAngle + 90) * np.pi/180
            self.valign = 1
            distance = 8
        else:
            a = (self.textAngle - 90) * np.pi/180
            self.valign = -1
            distance = 3
        normal = Point(np.cos(a), np.sin(a)).normalize()
        
        # project the corner points of all text objects to the normal vector.
        def project(p,normal):
            p = p-pos
            phi = abs(normal.angle(p))
            return float( p.norm()*np.cos(phi) )
        # apply
        alpha = []
        for text in self._textDict.values():
            if text is self:
                continue
            if not text.isPositioned:
                continue # Only consider drawn text objects
            x,y = text._screenx, text._screeny
            deltax, deltay = text.GetVertexLimits()
            xmin, xmax = deltax
            ymin, ymax = deltay
            alpha.append( project(Point(x+xmin, y+ymin), normal) )
            alpha.append( project(Point(x+xmin, y+ymax), normal) )
            alpha.append( project(Point(x+xmax, y+ymin), normal) )
            alpha.append( project(Point(x+xmax, y+ymax), normal) )
        
        # establish the amount of pixels that we should move along the normal.
        if alpha:
            self._move = distance+max(alpha)
        
        # move in the direction of the normal
        tmp = pos + normal * self._move
        self._screenx, self._screeny = int(tmp.x+0.5), int(tmp.y+0.5)
        
        # draw and reset position
        Text.OnDrawScreen(self)
        self._screenx, self._screeny = pos.x, pos.y


def GetTickTexts(ticks):
    """ GetTickTexts(ticks)
    
    Get tick labels of maximally 9 characters (plus sign char).
    
    All ticks will be formatted in the same manner, and with the same number
    of decimals. In exponential notation, the exponent is written with as
    less characters as possible, leaving more chars for the decimals.
    
    The algorithm is to first test for each tick the number of characters
    before the dot, the number of decimals, and the number of chars for
    the exponent. Then the ticks are formatted only without exponent if
    the first two chars (plus one for the dot) are less than 9.
    
    Examples are:
    xx.yyyyyy
    xxxxxxx.y
    x.yyyye+z
    x.yye+zzz
    
    """
    
    # For padding/unpadding exponent notation
    def exp_pad(s, i=1):
        return s.lstrip('0').rjust(i,'0')
    
    
    # Round 1: determine amount of chars before dot, after dot, in exp
    minChars1, maxChars1 = 99999, 0
    maxChars2 = 0
    maxChars3 = 0
    for tick in ticks:
        
        # Make abs, our goal is to format the ticks such that without
        # the sign char, the string is smaller than 9 chars.
        tick = abs(tick)
        
        # Format with exponential notation and get exponent
        t = '%1.0e' % tick
        i = t.find('e')
        expPart = t[i+2:]
        
        # Get number of chars before dot
        chars1 = int(expPart)+1
        maxChars1 = max(maxChars1, chars1)
        minChars1 = min(minChars1, chars1)
        
        # Get number of chars in exponent
        maxChars3 = max(maxChars3, len(exp_pad(expPart)))
        
        # Get number of chars after the dot
        t = '%1.7f' % tick
        i = t.find('.')
        decPart = t[i+1:]
        maxChars2 = max(maxChars2, len(decPart.rstrip('0')))
    
    # Round 2: Create actual texts
    ticks2 = []
    if maxChars1 + maxChars2 + 1 <= 9:
        # This one is easy
        
        chars2 = maxChars2
        f = '%%1.%if' % chars2
        for tick in ticks:
            # Format tick and store
            if tick == -0: tick = 0
            ticks2.append( f % tick )
    
    elif maxChars1 < 9:
        # Do the best we can
        
        chars2 = 9 - (maxChars1+1)
        f = '%%1.%if' % chars2
        for tick in ticks:
            # Format tick and store
            if tick == -0: tick = 0
            ticks2.append( f % tick )
    
    else:
        # Exponential notation
        chars2 = 9 - (4+maxChars3)  # 0.xxxe+yy
        f = '%%1.%ie' % chars2
        for tick in ticks:
            # Format tick
            if tick == -0: tick = 0
            t = f % tick
            # Remove zeros in exp
            i = t.find('e')
            t = t[:i+2] + exp_pad(t[i+2:], maxChars3)
            # Store
            ticks2.append(t)
    
    # Done
    return ticks2

def GetTickText_deprecated(tick):
    """ GetTickText(tick)
    
    Obtain text from a tick. Convert to exponential notation
    if necessary.
    
    """
    
    # Correct -0: 0 has on some systems been reported to be shown as -0
    if tick == -0:
        tick = 0
    # Get text
    text = '%1.4g' % tick
    iExp = text.find('e')
    if iExp>0:
        front = text[:iExp+2]
        text = front + text[iExp+2:].lstrip('0')
    return text


def GetTicks(p0, p1, lim, minTickDist=40, givenTicks=None):
    """ GetTicks(p0, p1, lim, minTickDist=40, ticks=None)
    
    Get the tick values, position and texts.
    These are calculated from a start end end position and the range
    of values to map on a straight line between these two points
    (which can be 2d or 3d). If givenTicks is given, use these values instead.
    
    """
    
    # Vector from start to end point
    vec = p1-p0
    
    # Init tick stuff
    tickValues = []
    tickTexts = []
    tickPositions = []
    
    if givenTicks is None:
        # Calculate all ticks if not given
        
        # Get pixels per unit
        if lim.range == 0:
            return [],[],[]
        
        # Pixels per unit (use float64 to prevent inf for large numbers)
        pixelsPerUnit = float( vec.norm() / lim.range )
        
        # Try all tickunits, starting from the smallest, until we find
        # one which results in a distance between ticks more than
        # X pixels.
        try:
            for tickUnit in _tickUnits:
                if tickUnit * pixelsPerUnit >= minTickDist:
                    break
            # if the numbers are VERY VERY large (which is very unlikely)
            # We use smaller-equal and a multiplication, so the error
            # is also raised when pixelsPerUnit and minTickDist are inf.
            # Thanks to Torquil Macdonald Sorensen for this bug report.
            if tickUnit*pixelsPerUnit <= 0.99*minTickDist:
                raise ValueError
        except (ValueError, TypeError):
            # too small
            return [],[],[]
        
        # Calculate the ticks (the values) themselves
        firstTick = np.ceil(  lim.min/tickUnit ) * tickUnit
        lastTick  = np.floor( lim.max/tickUnit ) * tickUnit
        count = 0
        tickValues.append(firstTick)
        while tickValues[-1] < lastTick-tickUnit/2:
            count += 1
            t = firstTick + count*tickUnit
            tickValues.append(t)
            if count > 1000:
                break # Safety
        # Get tick texts
        tickTexts = GetTickTexts(tickValues)
    
    elif isinstance(givenTicks, dict):
        # Use given ticks in dict
        
        for tickValue in givenTicks:
            if tickValue >= lim.min and tickValue <= lim.max:
                tickText = givenTicks[tickValue]
                tickValues.append(tickValue)
                if isinstance(tickText, basestring):
                    tickTexts.append(tickText)
                else:
                    tickTexts.append(str(tickText))
    
    elif isinstance(givenTicks, (tuple,list)):
        # Use given ticks as list
        
        # Init temp tick texts list
        tickTexts2 = []
        
        for i in range(len(givenTicks)):
            
            # Get tick
            t = givenTicks[i]
            if isinstance(t, basestring):
                tickValue = i
                tickText = t
            else:
                tickValue = float(t)
                tickText = None
            
            # Store
            if tickValue >= lim.min and tickValue <= lim.max:
                tickValues.append(tickValue)
                tickTexts2.append(tickText)
        
        # Get tick text that we normally would have used
        tickTexts = GetTickTexts(tickValues)
        
        # Replace with any given strings
        for i in range(len(tickTexts)):
            tmp = tickTexts2[i]
            if tmp is not None:
                tickTexts[i] = tmp
    
    
    # Calculate tick positions
    for t in tickValues:
        pos = p0 + vec * ( (t-lim.min) / lim.range )
        tickPositions.append( pos )
    
    # Done
    return tickValues, tickPositions, tickTexts


class BaseAxis(base.Wobject):
    """ BaseAxis(parent)
    
    This is the (abstract) base class for all axis classes, such
    as the CartesianAxis and PolarAxis.
    
    An Axis object represents the lines, ticks and grid that make
    up an axis. Not to be confused with an Axes, which represents
    a scene and is a Wibject.
    
    """
    #  This documentation holds for the 3D axis, the 2D axis is a bit
    #  simpeler in some aspects.
    #
    #  The scene is limits by the camera limits, thus forming a cube
    #  The axis is drawn on this square.
    #  The ASCI-art image below illustrates how the corners of this cube
    #  are numbered.
    #
    #  The thicks are drawn along three ridges of the cube. A reference
    #  corner is selected first, which has a corresponding ridge vector.
    #
    #  In orthogonal view, all ridges are parellel, but this is not the
    #  case in projective view. For each dimension there are 4 ridges to
    #  consider. Any grid lines are drawn between two ridges. The amount
    #  of ticks to draw (or minTickDist to be precise) should be determined
    #  based on the shortest ridge.
    #
    #          6 O---------------O 7
    #           /|              /|
    #          /               / |
    #         /  |            /  |
    #      3 O---------------O 5 |
    #        |   |           |   |
    #        | 2 o- - - - - -|- -O 4
    #        |  /            |  /
    #        |               | /
    #        |/              |/
    #      0 O---------------O 1
    #
    #  / \      _
    #   |       /|
    #   | z    /        x
    #   |     /  y    ----->
    #
    
    
    def __init__(self, parent):
        base.Wobject.__init__(self, parent)
        
        # Make the axis the first wobject in the list. This somehow seems
        # right and makes the Axes.axis property faster.
        if hasattr(parent, '_wobjects') and self in parent._wobjects:
            parent._wobjects.remove(self)
            parent._wobjects.insert(0, self)
        
        # Init property variables
        self._showBox =  True
        self._axisColor = (0,0,0)
        self._tickFontSize = 9
        self._gridLineStyle = ':'
        self._xgrid, self._ygrid, self._zgrid = False, False, False
        self._xminorgrid, self._yminorgrid, self._zminorgrid =False,False,False
        self._xticks, self._yticks, self._zticks = None, None, None
        self._xlabel, self._ylabel, self._zlabel = '','',''
        
        # For the cartesian 2D axis, xticks can be rotated
        self._xTicksAngle = 0
        
        # Define parameters
        self._lineWidth = 1 # 0.8
        self._minTickDist = 40
        
        # Corners of a cube in relative coordinates
        self._corners = tmp = Pointset(3)
        tmp.append(0,0,0);  tmp.append(1,0,0);  tmp.append(0,1,0)
        tmp.append(0,0,1);  tmp.append(1,1,0);  tmp.append(1,0,1)
        tmp.append(0,1,1);  tmp.append(1,1,1)
        
        # Indices of the base corners for each dimension.
        # The order is very important, don't mess it up...
        self._cornerIndicesPerDirection = [ [0,2,6,3], [3,5,1,0], [0,1,4,2] ]
        # And the indices of the corresponding pair corners
        self._cornerPairIndicesPerDirection = [ [1,4,7,5], [6,7,4,2], [3,5,7,6] ]
        
        # Dicts to be able to optimally reuse text objects; creating new
        # text objects or changing the text takes a relatively large amount
        # of time (if done every draw).
        self._textDicts = [{},{},{}]
    
    
    ## Properties
    
    
    @PropWithDraw
    def showBox():
        """ Get/Set whether to show the box of the axis. """
        def fget(self):
            return self._showBox
        def fset(self, value):
            self._showBox = bool(value)
        return locals()
    
    
    @PropWithDraw
    def axisColor():
        """ Get/Set the color of the box, ticklines and tick marks. """
        def fget(self):
            return self._axisColor
        def fset(self, value):
            self._axisColor = getColor(value, 'setting axis color')
        return locals()
    
    
    @PropWithDraw
    def tickFontSize():
        """ Get/Set the font size of the tick marks. """
        def fget(self):
            return self._tickFontSize
        def fset(self, value):
            self._tickFontSize = value
        return locals()
    
    
    @PropWithDraw
    def gridLineStyle():
        """ Get/Set the style of the gridlines as a single char similar
        to the lineStyle (ls) property of the line wobject (or in plot). """
        def fget(self):
            return self._gridLineStyle
        def fset(self, value):
            if value not in lineStyles:
                raise ValueError("Invalid lineStyle for grid lines")
            self._gridLineStyle = value
        return locals()
    
    
    @PropWithDraw
    def showGridX():
        """ Get/Set whether to show a grid for the x dimension. """
        def fget(self):
            return self._xgrid
        def fset(self, value):
            self._xgrid = bool(value)
        return locals()
    
    @PropWithDraw
    def showGridY():
        """ Get/Set whether to show a grid for the y dimension. """
        def fget(self):
            return self._ygrid
        def fset(self, value):
            self._ygrid = bool(value)
        return locals()
    
    @PropWithDraw
    def showGridZ():
        """ Get/Set whether to show a grid for the z dimension. """
        def fget(self):
            return self._zgrid
        def fset(self, value):
            self._zgrid = bool(value)
        return locals()
    
    @PropWithDraw
    def showGrid():
        """ Show/hide the grid for the x,y and z dimension. """
        def fget(self):
            return self._xgrid, self._ygrid, self._zgrid
        def fset(self, value):
            if isinstance(value, tuple):
                value = tuple([bool(v) for v in value])
                self._xgrid, self._ygrid, self._zgrid = value
            else:
                self._xgrid = self._ygrid = self._zgrid = bool(value)
        return locals()
    
    
    @PropWithDraw
    def showMinorGridX():
        """ Get/Set whether to show a minor grid for the x dimension. """
        def fget(self):
            return self._xminorgrid
        def fset(self, value):
            self._xminorgrid = bool(value)
        return locals()
    
    @PropWithDraw
    def showMinorGridY():
        """ Get/Set whether to show a minor grid for the y dimension. """
        def fget(self):
            return self._yminorgrid
        def fset(self, value):
            self._yminorgrid = bool(value)
        return locals()
    
    @PropWithDraw
    def showMinorGridZ():
        """ Get/Set whether to show a minor grid for the z dimension. """
        def fget(self):
            return self._zminorgrid
        def fset(self, value):
            self._zminorgrid = bool(value)
        return locals()
    
    @PropWithDraw
    def showMinorGrid():
        """ Show/hide the minor grid for the x, y and z dimension. """
        def fget(self):
            return self._xminorgrid, self._yminorgrid, self._zminorgrid
        def fset(self, value):
            if isinstance(value, tuple):
                tmp = tuple([bool(v) for v in value])
                self._xminorgrid, self._yminorgrid, self._zminorgridd = tmp
            else:
                tmp = bool(value)
                self._xminorgrid = self._yminorgrid = self._zminorgrid = tmp
        return locals()
    
    
    @PropWithDraw
    def xTicks():
        """ Get/Set the ticks for the x dimension.
        
        The value can be:
          * None: the ticks are determined automatically.
          * A tuple/list/numpy_array with float or string values: Floats
            specify at which location tickmarks should be drawn. Strings are
            drawn at integer positions corresponding to the index in the
            given list.
          * A dict with numbers or strings as values. The values are drawn at
            the positions specified by the keys (which should be numbers).
        """
        def fget(self):
            return self._xticks
        def fset(self, value):
            m = 'Ticks must be a dict/list/tuple/numpy array of numbers or strings.'
            if value is None:
                self._xticks = None
            elif isinstance(value, dict):
                try:
                    ticks = {}
                    for key in value:
                        ticks[key] = str(value[key])
                    self._xticks = ticks
                except Exception:
                    raise ValueError(m)
            elif isinstance(value, (list, tuple, np.ndarray)):
                try:
                    ticks = []
                    for val in value:
                        if isinstance(val, basestring):
                            ticks.append(val)
                        else:
                            ticks.append(float(val))
                    self._xticks = ticks
                except Exception:
                    raise ValueError(m)
            else:
                raise ValueError(m)
        return locals()
    
    
    @PropWithDraw
    def yTicks():
        """ Get/Set the ticks for the y dimension.
        
        The value can be:
          * None: the ticks are determined automatically.
          * A tuple/list/numpy_array with float or string values: Floats
            specify at which location tickmarks should be drawn. Strings are
            drawn at integer positions corresponding to the index in the
            given list.
          * A dict with numbers or strings as values. The values are drawn at
            the positions specified by the keys (which should be numbers).
        """
        def fget(self):
            return self._yticks
        def fset(self, value):
            m = 'Ticks must be a dict/list/tuple/numpy array of numbers or strings.'
            if value is None:
                self._yticks = None
            elif isinstance(value, dict):
                try:
                    ticks = {}
                    for key in value:
                        ticks[key] = str(value[key])
                    self._yticks = ticks
                except Exception:
                    raise ValueError(m)
            elif isinstance(value, (list, tuple, np.ndarray)):
                try:
                    ticks = []
                    for val in value:
                        if isinstance(val, basestring):
                            ticks.append(val)
                        else:
                            ticks.append(float(val))
                    self._yticks = ticks
                except Exception:
                    raise ValueError(m)
            else:
                raise ValueError(m)
        return locals()
    
    
    @PropWithDraw
    def zTicks():
        """ Get/Set the ticks for the z dimension.
        
        The value can be:
          * None: the ticks are determined automatically.
          * A tuple/list/numpy_array with float or string values: Floats
            specify at which location tickmarks should be drawn. Strings are
            drawn at integer positions corresponding to the index in the
            given list.
          * A dict with numbers or strings as values. The values are drawn at
            the positions specified by the keys (which should be numbers).
        """
        def fget(self):
            return self._zticks
        def fset(self, value):
            m = 'Ticks must be a dict/list/tuple/numpy array of numbers or strings.'
            if value is None:
                self._zticks = None
            elif isinstance(value, dict):
                try:
                    ticks = {}
                    for key in value:
                        ticks[key] = str(value[key])
                    self._zticks = ticks
                except Exception:
                    raise ValueError(m)
            elif isinstance(value, (list, tuple, np.ndarray)):
                try:
                    ticks = []
                    for val in value:
                        if isinstance(val, basestring):
                            ticks.append(val)
                        else:
                            ticks.append(float(val))
                    self._zticks = ticks
                except Exception:
                    raise ValueError(m)
            else:
                raise ValueError(m)
        return locals()
    
    
    @PropWithDraw
    def xLabel():
        """ Get/Set the label for the x dimension.
        """
        def fget(self):
            return self._xlabel
        def fset(self, value):
            self._xlabel = value
        return locals()
    
    @PropWithDraw
    def yLabel():
        """ Get/Set the label for the y dimension.
        """
        def fget(self):
            return self._ylabel
        def fset(self, value):
            self._ylabel = value
        return locals()
    
    @PropWithDraw
    def zLabel():
        """ Get/Set the label for the z dimension.
        """
        def fget(self):
            return self._zlabel
        def fset(self, value):
            self._zlabel = value
        return locals()
    
    
    ## Methods for drawing

    def OnDraw(self, ppc_pps_ppg=None):
        
        # Get axes and return if there is none,
        # or if it doesn't want to show an axis.
        axes = self.GetAxes()
        if not axes:
            return
        
        # Calculate lines and labels (or get from argument)
        if ppc_pps_ppg:
            ppc, pps, ppg = ppc_pps_ppg
        else:
            try:
                ppc, pps, ppg = self._CreateLinesAndLabels(axes)
            except Exception:
                self.Destroy() # So the error message does not repeat itself
                raise
        
        # Store lines to be drawn in screen coordinates
        self._pps = pps
        
        # Prepare for drawing lines
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        clr = self._axisColor
        gl.glColor(clr[0], clr[1], clr[2])
        gl.glLineWidth(self._lineWidth)
        
        # Draw lines
        if len(ppc):
            gl.glVertexPointerf(ppc.data)
            gl.glDrawArrays(gl.GL_LINES, 0, len(ppc))
        
        # Draw gridlines
        if len(ppg):
            # Set stipple pattern
            if not self.gridLineStyle in lineStyles:
                stipple = False
            else:
                stipple = lineStyles[self.gridLineStyle]
            if stipple:
                gl.glEnable(gl.GL_LINE_STIPPLE)
                gl.glLineStipple(1, stipple)
            # Draw using array
            gl.glVertexPointerf(ppg.data)
            gl.glDrawArrays(gl.GL_LINES, 0, len(ppg))
        
        # Clean up
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_LINE_STIPPLE)
    
    
    def OnDrawScreen(self):
        # Actually draw the axis
        
        axes = self.GetAxes()
        if not axes:
            return
        
        # get pointset
        if not hasattr(self, '_pps') or not self._pps:
            return
        pps = self._pps.copy()
        pps[:,2] = depthToZ( pps[:,2] )
        
        # Prepare for drawing lines
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(pps.data)
        if isinstance(axes.camera, TwoDCamera):
            gl.glDisable(gl.GL_LINE_SMOOTH)
        
        # Draw lines
        clr = self._axisColor
        gl.glColor(clr[0], clr[1], clr[2])
        gl.glLineWidth(self._lineWidth)
        if len(pps):
            gl.glDrawArrays(gl.GL_LINES, 0, len(pps))
        
        # Clean up
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnable(gl.GL_LINE_SMOOTH)


    ## Help methods
    
    def _DestroyChildren(self):
        """ Method to clean up the children (text objects).
        """
        if self._children:
            for child in self.children:
                child.Destroy()
    
    
    def _CalculateCornerPositions(self, xlim, ylim, zlim):
        """ Calculate the corner positions in world coorinates
        and screen coordinates, given the limits for each dimension.
        """
        
        # To translate to real coordinates
        pmin = Point(xlim.min, ylim.min, zlim.min)
        pmax = Point(xlim.max, ylim.max, zlim.max)
        def relativeToCoord(p):
            pi = Point(1,1,1) - p
            return pmin*pi + pmax*p
        
        # Get the 8 corners of the cube in real coords and screen pixels
        # Note that in perspective mode the screen coords for points behind
        # the near clipping plane are undefined. This results in odd values,
        # which should be accounted for. This is mostly only a problem for
        # the fly camera though.
        proj = glu.gluProject
        
        corners8_c = [relativeToCoord(p) for p in self._corners]
        corners8_s = [Point(proj(p.x,p.y,p.z)) for p in corners8_c]
        
        
        # Return
        return corners8_c, corners8_s


    def _GetTicks(self, tickUnit, lim):
        """ Given tickUnit (the distance in world units between the ticks)
        and the range to cover (lim), calculate the actual tick values.
        """
        
        # Get position of first and last tick
        firstTick = np.ceil(  lim.min/tickUnit ) * tickUnit
        lastTick  = np.floor( lim.max/tickUnit ) * tickUnit
        
        # Valid range?
        if firstTick > lim.max or lastTick < lim.min:
            return []
        
        # Create ticks
        count = 0
        ticks = [firstTick]
        while ticks[-1] < lastTick-tickUnit:
            count += 1
#             tmp = firstTick + count*tickUnit
#             if abs(tmp/tickUnit) < 10**-10:
#                 tmp = 0 # due round-off err, 0 can otherwise be 0.5e-17 or so
#             ticks.append(tmp)
            ticks.append( firstTick + count*tickUnit )
        return ticks


    def _NextCornerIndex(self, i, d, vector_s):
        """ Calculate the next corner index.
        """
        
        if d<2 and vector_s.x >= 0:
            i+=self._delta
        elif d==2 and vector_s.y < 0:
            i+=self._delta
        else:
            i-=self._delta
        if i>3: i=0
        if i<0: i=3
        return i
    
    
    def _CreateLinesAndLabels(self, axes):
        """ This is the method that calculates where lines should be
        drawn and where labels should be placed.
        
        It returns three point sets in which the pairs of points
        represent the lines to be drawn (using GL_LINES):
          * ppc: lines in real coords
          * pps: lines in screen pixels
          * ppg: dotted lines in real coords
        """
        raise NotImplementedError('This is the abstract base class.')


class CartesianAxis2D(BaseAxis):
    """ CartesianAxis2D(parent)
    
    An Axis object represents the lines, ticks and grid that make
    up an axis. Not to be confused with an Axes, which represents
    a scene and is a Wibject.

    The CartesianAxis2D is a straightforward axis, drawing straight
    lines for cartesian coordinates in 2D.
    """
    
    @PropWithDraw
    def xTicksAngle():
        """ Get/Set the angle of the tick marks for te x-dimension.
        This can be used when the tick labels are long, to prevent
        them from overlapping. Note that if this value is non-zero,
        the horizontal alignment is changed to left (instead of center).
        """
        def fget(self):
            return self._xTicksAngle
        def fset(self, value):
            self._xTicksAngle = value
        return locals()
    
    
    def _CreateLinesAndLabels(self, axes):
        """ This is the method that calculates where lines should be
        drawn and where labels should be placed.

        It returns three point sets in which the pairs of points
        represent the lines to be drawn (using GL_LINES):
          * ppc: lines in real coords
          * pps: lines in screen pixels
          * ppg: dotted lines in real coords
        """

        # Get camera instance
        cam = axes.camera

        # Get parameters
        drawGrid = [v for v in self.showGrid]
        drawMinorGrid = [v for v in self.showMinorGrid]
        ticksPerDim = [self.xTicks, self.yTicks]
        
        # Get limits
        lims = axes.GetLimits()
        lims = [lims[0], lims[1], cam._zlim]
        
        # Get labels
        labels = [self.xLabel, self.yLabel]
        
        
        # Init the new text object dictionaries
        newTextDicts = [{},{},{}]
        
        # Init pointsets for drawing lines and gridlines
        ppc = Pointset(3) # lines in real coords
        pps = Pointset(3) # lines in screen pixels
        ppg = Pointset(3) # dotted lines in real coords
        
        
        # Calculate cornerpositions of the cube
        corners8_c, corners8_s = self._CalculateCornerPositions(*lims)

        # We use this later to determine the order of the corners
        self._delta = 1
        for i in axes.daspect:
            if i<0: self._delta*=-1

        # For each dimension ...
        for d in range(2): # d for dimension/direction
            lim = lims[d]

            # Get the four corners that are of interest for this dimension
            # In 2D, the first two are the same as the last two
            tmp = self._cornerIndicesPerDirection[d]
            tmp = [tmp[i] for i in [0,1,0,1]]
            corners4_c = [corners8_c[i] for i in tmp]
            corners4_s = [corners8_s[i] for i in tmp]
            
            # Get directional vectors in real coords and screen pixels.
            # Easily calculated since the first _corner elements are
            # 000,100,010,001
            vector_c = corners8_c[d+1] - corners8_c[0]
            vector_s = corners8_s[d+1] - corners8_s[0]

            # Correct the tickdist for the x-axis if the numbers are large
            minTickDist = self._minTickDist
            if d==0:
                mm = max(abs(lim.min),abs(lim.max))
                if mm >= 10000:
                    minTickDist = 80

            # Calculate tick distance in world units
            minTickDist *= vector_c.norm() / vector_s.norm()

            # Get index of corner to put ticks at
            i0 = 0; bestVal = 999999999999999999999999
            for i in range(2):
                val = corners4_s[i].y
                if val < bestVal:
                    i0 = i
                    bestVal = val

            # Get indices of the two next corners on which
            # ridges we may draw grid lines
            i1 = self._NextCornerIndex(i0, d, vector_s)
            # i2 = self._NextCornerIndex(i1, d, vector_s)
            
            # Get first corner and grid vectors
            firstCorner = corners4_c[i0]
            gv1 = corners4_c[i1] - corners4_c[i0]
            # gv2 = corners4_c[i2] - corners4_c[i1]
            
            # Get tick vector to indicate tick
            gv1s = corners4_s[i1] - corners4_s[i0]
            #tv = gv1 * (5 / gv1s.norm() )
            npixels = ( gv1s.x**2 + gv1s.y**2 ) ** 0.5 + 0.000001
            tv = gv1 * (5.0 / npixels )

            # Always draw these corners
            pps.append(corners4_s[i0])
            pps.append(corners4_s[i0]+vector_s)

            # Add line pieces to draw box
            if self._showBox:
                for i in range(2):
                    if i != i0:
                        corner = corners4_s[i]
                        pps.append(corner)
                        pps.append(corner+vector_s)
            
            # Get ticks stuff
            tickValues = ticksPerDim[d] # can be None
            p1, p2 = firstCorner.copy(), firstCorner+vector_c
            tmp = GetTicks(p1,p2, lim, minTickDist, tickValues)
            ticks, ticksPos, ticksText = tmp
            tickUnit = lim.range
            if len(ticks)>=2:
                tickUnit = ticks[1] - ticks[0]
            
            # Apply Ticks
            for tick, pos, text in zip(ticks, ticksPos, ticksText):
                
                # Get little tail to indicate tick
                p1 = pos
                p2 = pos - tv
                
                # Add tick lines
                factor = ( tick-firstCorner[d] ) / vector_c[d]
                p1s = corners4_s[i0] + vector_s * factor
                tmp = Point(0,0,0)
                tmp[int(not d)] = 4
                pps.append(p1s)
                pps.append(p1s-tmp)
                
                # Put a textlabel at tick
                textDict = self._textDicts[d]
                if tick in textDict and textDict[tick] in self._children:
                    t = textDict.pop(tick)
                    t.text = text
                    t.x, t.y, t.z = p2.x, p2.y, p2.z
                else:
                    t = AxisText(self,text, p2.x,p2.y,p2.z)
                # Add to dict
                newTextDicts[d][tick] = t
                # Set other properties right
                t._visible = True
                t.fontSize = self._tickFontSize
                t._color = self._axisColor # Use private attr for performance
                if d==1:
                    t.halign = 1
                    t.valign = 0
                else:
                    t.textAngle = self._xTicksAngle
                    if self._xTicksAngle > 0:
                        t.halign = 1
                    elif self._xTicksAngle < 0:
                        t.halign = -1
                    else:
                        t.halign = 0
                    if abs(self._xTicksAngle) > 45:
                        t.valign = 0
                    else:
                        t.valign = -1
            
            # We should hide this last tick if it sticks out
            if d==0 and len(ticks):
                # Get positions
                fig = axes.GetFigure()
                if fig:
                    tmp1 = fig.position.width
                    tmp2 = glu.gluProject(t.x, t.y, t.z)[0]
                    tmp2 += t.GetVertexLimits()[0][1] # Max of x
                    # Apply
                    if tmp1 < tmp2:
                        t._visible = False
            
            # Get gridlines
            if drawGrid[d] or drawMinorGrid[d]:
                # Get more gridlines if required
                if drawMinorGrid[d]:
                    ticks = self._GetTicks(tickUnit/5, lim)
                # Get positions
                for tick in ticks:
                    # Get tick location
                    p1 = firstCorner.copy()
                    p1[d] = tick
                    # Add gridlines
                    p3 = p1+gv1
                    #p4 = p3+gv2
                    ppg.append(p1);  ppg.append(p3)
            
            # Apply label
            textDict = self._textDicts[d]
            p1 = corners4_c[i0] + vector_c * 0.5
            key = '_label_'
            if key in textDict and textDict[key] in self._children:
                t = textDict.pop(key)
                t.text = labels[d]
                t.x, t.y, t.z = p1.x, p1.y, p1.z
            else:
                #t = AxisText(self,labels[d], p1.x,p1.y,p1.z)
                t = AxisLabel(self,labels[d], p1.x,p1.y,p1.z)
                t.fontSize=10
            newTextDicts[d][key] = t
            t.halign = 0
            t._color = self._axisColor
            # Move label to back, so the repositioning works right
            if not t in self._children[-3:]:
                self._children.remove(t)
                self._children.append(t)
            # Get vec to calc angle
            vec = Point(vector_s.x, vector_s.y)
            if vec.x < 0:
                vec = vec * -1
            t.textAngle = float(vec.angle() * 180/np.pi)
            # Keep up to date (so label can move itself just beyond ticks)
            t._textDict = newTextDicts[d]
        
        # Correct gridlines so they are all at z=0.
        # The grid is always exactly at 0. Images are at -0.1 or less.
        # lines and poins are at +0.1
        ppg.data[:,2] = 0.0
        
        # Clean up the text objects that are left
        for tmp in self._textDicts:
            for t in list(tmp.values()):
                t.Destroy()

        # Store text object dictionaries for next time ...
        self._textDicts = newTextDicts

        # Return
        return ppc, pps, ppg


class CartesianAxis3D(BaseAxis):
    """ CartesianAxis3D(parent)
    
    An Axis object represents the lines, ticks and grid that make
    up an axis. Not to be confused with an Axes, which represents
    a scene and is a Wibject.

    The CartesianAxis3D is a straightforward axis, drawing straight
    lines for cartesian coordinates in 3D.

    """

    def _GetRidgeVector(self, d, corners8_c, corners8_s):
        """  _GetRidgeVector(d, corners8_c, corners8_s)
        
        Get the four vectors for the four ridges coming from the
        corners that correspond to the given direction.
        
        Also returns the lengths of the smallest vectors, for the
        calculation of the minimum tick distance.
        
        """
        
        # Get the vectors
        vectors_c = []
        vectors_s = []
        for i in range(4):
            i1 = self._cornerIndicesPerDirection[d][i]
            i2 = self._cornerPairIndicesPerDirection[d][i]
            vectors_c.append( corners8_c[i2] - corners8_c[i1])
            vectors_s.append( corners8_s[i2] - corners8_s[i1])
        
        # Select the smallest vector (in screen coords)
        smallest_i, smallest_L = 0, 9999999999999999999999999.0
        for i in range(4):
            L = vectors_s[i].x**2 + vectors_s[i].y**2
            if L < smallest_L:
                smallest_i = i
                smallest_L = L
        
        # Return smallest and the vectors
        norm_c = vectors_c[smallest_i].norm()
        norm_s = smallest_L**0.5
        return norm_c, norm_s, vectors_c, vectors_s
    
    
    def _CreateLinesAndLabels(self, axes):
        """ This is the method that calculates where lines should be
        drawn and where labels should be placed.

        It returns three point sets in which the pairs of points
        represent the lines to be drawn (using GL_LINES):
          * ppc: lines in real coords
          * pps: lines in screen pixels
          * ppg: dotted lines in real coords
        """

        # Get camera instance
        cam = axes.camera
        
        # Get parameters
        drawGrid = [v for v in self.showGrid]
        drawMinorGrid = [v for v in self.showMinorGrid]
        ticksPerDim = [self.xTicks, self.yTicks, self.zTicks]

        # Get limits
        lims = [cam._xlim, cam._ylim, cam._zlim]

        # Get labels
        labels = [self.xLabel, self.yLabel, self.zLabel]


        # Init the new text object dictionaries
        newTextDicts = [{},{},{}]

        # Init pointsets for drawing lines and gridlines
        ppc = Pointset(3) # lines in real coords
        pps = Pointset(3) # lines in screen pixels
        ppg = Pointset(3) # dotted lines in real coords


        # Calculate cornerpositions of the cube
        corners8_c, corners8_s = self._CalculateCornerPositions(*lims)

        # we use this later to determine the order of the corners
        self._delta = 1
        for i in axes.daspect:
            if i<0: self._delta*=-1


        # For each dimension ...
        for d in range(3): # d for dimension/direction
            lim = lims[d]
            
            # Get the four corners that are of interest for this dimension
            # They represent one of the faces that we might draw in.
            tmp = self._cornerIndicesPerDirection[d]
            corners4_c = [corners8_c[i] for i in tmp]
            corners4_s = [corners8_s[i] for i in tmp]
            
            # Get directional vectors (i.e. ridges) corresponding to
            # (emanating from) the four corners. Also returns the length
            # of the shortest ridges (in screen coords)
            _vectors = self._GetRidgeVector(d, corners8_c, corners8_s)
            norm_c, norm_s, vectors4_c, vectors4_s = _vectors
            
            # Due to cords not being defined behind the near clip plane,
            # the vectors4_s migt be inaccurate. This means the size and
            # angle of the tickmarks may be calculated wrong. It also
            # means the norm_s might be wrong. Since this is mostly a problem
            # for the fly camera, we use a fixed norm_s in that case. This
            # also prevents grid line flicker due to the constant motion
            # of the camera.
            if isinstance(axes.camera, FlyCamera):
                norm_s = axes.position.width
            
            # Calculate tick distance in units (using shortest ridge vector)
            minTickDist = self._minTickDist
            if norm_s > 0:
                minTickDist *= norm_c / norm_s
            
            # Get index of corner to put ticks at.
            # This is determined by chosing the corner which is the lowest
            # on screen (for x and y), or the most to the left (for z).
            i0 = 0; bestVal = 999999999999999999999999
            for i in range(4):
                if d==2: val = corners4_s[i].x  # chose leftmost corner
                else: val = corners4_s[i].y  # chose bottommost corner
                if val < bestVal:
                    i0 = i
                    bestVal = val
            
            # Get indices of next corners corresponding to the ridges
            # between which we may draw grid lines
            # i0, i1, i2 are all in [0,1,2,3]
            i1 = self._NextCornerIndex(i0, d, vectors4_s[i0])
            i2 = self._NextCornerIndex(i1, d, vectors4_s[i0])
            
            # Get first corner and grid vectors
            firstCorner = corners4_c[i0]
            gv1 = corners4_c[i1] - corners4_c[i0]
            gv2 = corners4_c[i2] - corners4_c[i1]
            
            # Get tick vector to indicate tick
            gv1s = corners4_s[i1] - corners4_s[i0]
            #tv = gv1 * (5 / gv1s.norm() )
            npixels = ( gv1s.x**2 + gv1s.y**2 ) ** 0.5 + 0.000001
            tv = gv1 * (5.0 / npixels )
            
            # Draw edge lines (optionally to create a full box)
            for i in range(4):
                if self._showBox or i in [i0, i1, i2]:
                    #if self._showBox or i ==i0: # for a real minimalistic axis
                    # Note that we use world coordinates, rather than screen
                    # as the 2D axis does.
                    ppc.append(corners4_c[i])
                    j = self._cornerPairIndicesPerDirection[d][i]
                    ppc.append(corners8_c[j])
            
            # Get ticks stuff
            tickValues = ticksPerDim[d] # can be None
            p1, p2 = firstCorner.copy(), firstCorner+vectors4_c[i0]
            tmp = GetTicks(p1,p2, lim, minTickDist, tickValues)
            ticks, ticksPos, ticksText = tmp
            tickUnit = lim.range
            if len(ticks)>=2:
                tickUnit = ticks[1] - ticks[0]
            
            # Apply Ticks
            for tick, pos, text in zip(ticks, ticksPos, ticksText):
            
                # Get little tail to indicate tick
                p1 = pos
                p2 = pos - tv
                
                # Add tick lines
                ppc.append(p1)
                ppc.append(p2)
                
                # z-axis has valign=0, thus needs extra space
                if d==2:
                    text+='  '
                
                # Put textlabel at tick
                textDict = self._textDicts[d]
                if tick in textDict and textDict[tick] in self._children:
                    t = textDict.pop(tick)
                    t.x, t.y, t.z = p2.x, p2.y, p2.z
                else:
                    t = AxisText(self,text, p2.x,p2.y,p2.z)
                # Add to dict
                newTextDicts[d][tick] = t
                # Set other properties right
                t._visible = True
                if t.fontSize != self._tickFontSize:
                    t.fontSize = self._tickFontSize
                t._color = self._axisColor  # Use private attr for performance
                if d==2:
                    t.valign = 0
                    t.halign = 1
                else:
                    if vectors4_s[i0].y*vectors4_s[i0].x >= 0:
                        t.halign = -1
                        t.valign = -1
                    else:
                        t.halign = 1
                        t.valign = -1
            
            # Get gridlines
            draw4 = self._showBox and isinstance(axes.camera, FlyCamera)
            if drawGrid[d] or drawMinorGrid[d]:
                # get more gridlines if required
                if drawMinorGrid[d]:
                    ticks = self._GetTicks(tickUnit/5, lim)
                # get positions
                for tick in ticks:
                    # get tick location
                    p1 = firstCorner.copy()
                    p1[d] = tick
                    if tick not in [lim.min, lim.max]: # not ON the box
                        # add gridlines (back and front)
                        if True:
                            p3 = p1+gv1
                            p4 = p3+gv2
                            ppg.append(p1);  ppg.append(p3)
                            ppg.append(p3);  ppg.append(p4)
                        if draw4:
                            p5 = p1+gv2
                            p6 = p5+gv1
                            ppg.append(p1);  ppg.append(p5)
                            ppg.append(p5);  ppg.append(p6)
            
            # Apply label
            textDict = self._textDicts[d]
            p1 = corners4_c[i0] + vectors4_c[i0] * 0.5
            key = '_label_'
            if key in textDict and textDict[key] in self._children:
                t = textDict.pop(key)
                t.text = labels[d]
                t.x, t.y, t.z = p1.x, p1.y, p1.z
            else:
                #t = AxisText(self,labels[d], p1.x,p1.y,p1.z)
                t = AxisLabel(self,labels[d], p1.x,p1.y,p1.z)
                t.fontSize=10
            newTextDicts[d][key] = t
            t.halign = 0
            t._color = self._axisColor  # Use private attr for performance
            # Move to back such that they can position themselves right
            if not t in self._children[-3:]:
                self._children.remove(t)
                self._children.append(t)
            # Get vec to calc angle
            vec = Point(vectors4_s[i0].x, vectors4_s[i0].y)
            if vec.x < 0:
                vec = vec * -1
            t.textAngle = float(vec.angle() * 180/np.pi)
            # Keep up to date (so label can move itself just beyond ticks)
            t._textDict = newTextDicts[d]
        
        
        # Clean up the text objects that are left
        for tmp in self._textDicts:
            for t in list(tmp.values()):
                t.Destroy()

        # Store text object dictionaries for next time ...
        self._textDicts = newTextDicts

        # Return
        return ppc, pps, ppg


class CartesianAxis(CartesianAxis2D, CartesianAxis3D):
    """ CartesianAxis(parent)
    
    An Axis object represents the lines, ticks and grid that make
    up an axis. Not to be confused with an Axes, which represents
    a scene and is a Wibject.

    The CartesianAxis combines the 2D and 3D axis versions; it uses
    the 2D version when the 2d camera is used, and the 3D axis
    otherwise.
    
    """
    # A bit ugly inheritance going on here, but otherwise the code below
    # would not work ...

    def _CreateLinesAndLabels(self, axes):
        """ Choose depending on what camera is used. """

        if isinstance(axes.camera, TwoDCamera):
            return CartesianAxis2D._CreateLinesAndLabels(self,axes)
        else:
            return CartesianAxis3D._CreateLinesAndLabels(self,axes)



def GetPolarTicks(p0, radius, lim, angularRefPos, sense , minTickDist=100, ticks=None):
    """ GetPolarTicks(p0, radius, lim, angularRefPos, sense , minTickDist=100,
                       ticks=None)
                        
    Get the tick values, position and texts.
    These are calculated from the polar center, radius and the range
    of values to map on a straight line between these two points
    (which can be 2d or 3d). If ticks is given, use these values instead.
    
    """
    
    pTickUnits = [1,2,3,5,6,9,18,30,45] # 90 = 3*3*2*5*1
    #circumference of circle
    circum = 2*np.pi*radius

    # Calculate all ticks if not given
    if ticks is None:
        # Get pixels per unit
        if lim.range == 0:
            return [],[],[]
        pixelsPerUnit = circum / 360 #lim.range
        # Try all tickunits, starting from the smallest, until we find
        # one which results in a distance between ticks more than
        # X pixels.
        try:
            for tickUnit in pTickUnits :
                if tickUnit * pixelsPerUnit >= minTickDist:
                    break
            # if the numbers are VERY VERY large (which is very unlikely)
            if tickUnit*pixelsPerUnit < minTickDist:
                raise ValueError
        except (ValueError, TypeError):
            # too small
            return [],[],[]

        # Calculate the ticks (the values) themselves
        ticks = []
        firstTick = np.ceil(  lim.min/tickUnit ) * tickUnit
        lastTick  = np.floor( lim.max/tickUnit ) * tickUnit
        count = 0
        ticks = [firstTick]
        while ticks[-1] < lastTick-tickUnit/2:
            count += 1
            ticks.append( firstTick + count*tickUnit )

    # Calculate tick positions and text
    ticksPos, ticksText = [], []
    for tick in ticks:
        theta = angularRefPos + sense*tick*np.pi/180.0
        x = radius*np.cos(theta)
        y = radius*np.sin(theta)
        pos = p0 + Point(x,y,0)
        if tick == -0:
            tick = 0
        text = '%1.4g' % tick
        iExp = text.find('e')
        if iExp>0:
            front = text[:iExp+2]
            text = front + text[iExp+2:].lstrip('0')
        # Store
        ticksPos.append( pos )
        ticksText.append( text )

    # Done
    return ticks, ticksPos, ticksText


class PolarAxis2D(BaseAxis):
    """ PolarAxis2D(parent)
    
    An Axis object represents the lines, ticks and grid that make
    up an axis. Not to be confused with an Axes, which represents
    a scene and is a Wibject.

    PolarAxis2D draws a polar grid, and modifies PolarLine objects
    to properly plot onto the polar grid.  PolarAxis2D has some
    specialized methods uniques to it for adjusting the polar plot.
    These include:
        SetLimits(thetaRange, radialRange):
        thetaRange, radialRange = GetLimits():
        
        angularRefPos: Get and Set methods for the relative screen
        angle of the 0 degree polar reference.  Default is 0 degs
        which corresponds to the positive x-axis (y =0)
        
        isCW: Get and Set methods for the sense of rotation CCW or
        CW. This method takes/returns a bool (True if the default CW).
        
        Drag mouse up/down to translate radial axis
        Drag mouse left/right to rotate angular ref position
        Drag mouse + shift key up/down to rescale radial axis (min R fixed)
    
    """
    
    def __init__(self, parent):
        BaseAxis.__init__(self, parent)
        self.ppb = None
        axes = self.GetAxes()
        axes.daspectAuto = False
        self.bgcolor = axes.bgcolor
        axes.bgcolor = None  # disables the default background
        # Size of the boarder where circular tick labels are drawn
        self.labelPix = 5
        
        self._radialRange = Range(-1, 1)  # default
        self._angularRange = Range(-179, 180)  # always 360 deg
        self._angularRefPos = 0
        self._sense = 1.0
        
        # Need to overrride this because the PolarAxis has
        # four sets of radial ticks (with same dict key!)
        self._textDicts = [{}, {}, {}, {}, {}]
        
        # reference stuff for interaction
        self.ref_loc = 0, 0, 0    # view_loc when clicked
        self.ref_mloc = 0, 0     # mouse location when clicked
        self.ref_but = 0        # mouse button when clicked
        
        self.controlIsDown = False
        self.shiftIsDown = False
        
        # bind special event for translating lower radial limit
        axes.eventKeyDown.Bind(self.OnKeyDown)
        axes.eventKeyUp.Bind(self.OnKeyUp)
        
        # Mouse events
        axes.eventMouseDown.Bind(self.OnMouseDown)
        axes.eventMouseUp.Bind(self.OnMouseUp)
        axes.eventMotion.Bind(self.OnMotion)
    
    
    @DrawAfter
    def RescalePolarData(self):
        """ RescalePolarData()
        
        This method finds and transforms all polar line data
        by the current polar radial axis limits so that data below
        the center of the polar plot is set to 0,0,0 and data beyond
        the maximum (outter radius) is clipped.
        
        """
        
        axes = self.GetAxes()
        drawObjs = axes.FindObjects(PolarLine)
        # Now set the transform for the PolarLine data
        for anObj in drawObjs:
            anObj.TransformPolar(self._radialRange, self._angularRefPos, self._sense)
    
    
    def _CreateLinesAndLabels(self, axes):
        """ This is the method that calculates where polar axis lines
        should be drawn and where labels should be placed.

        It returns three point sets in which the pairs of points
        represent the lines to be drawn (using GL_LINES):
          * ppc: lines in real coords
          * pps: lines in screen pixels
          * ppg: dotted lines in real coords
        """

        # Get camera
        # This camera has key bindings which are used to
        # rescale the lower radial limits.  Thus for polar plots the
        # user can slide the radial range up
        # and down and rotate the plot
        cam = axes.camera

        # Get axis grid and tick parameters
        drawGrid = [v for v in self.showGrid]
        drawMinorGrid = [v for v in self.showMinorGrid]
        # these are equivalent to axes.thetaTicks and axes.RadialTicks
        ticksPerDim = [self.xTicks, self.yTicks]

        # Get x-y limits  in world coordinates
        lims = axes.GetLimits()
        lims = [lims[0], lims[1], cam._zlim]

        # From current lims calculate the radial axis min and max

        # Get labels. These are equivalent to Theta and radial labels
        labels = [self.xLabel, self.yLabel]

        # Init the new text object dictionaries
        # (theta, R(0),R(90),R(180),R(270))
        newTextDicts = [{}, {}, {}, {}, {}]

        # Init pointsets for drawing lines and gridlines
        ppc = Pointset(3)  # lines in real coords
        pps = Pointset(3)  # lines in screen pixels, not used by PolarAxis
        ppg = Pointset(3)  # dotted lines in real coords (for grids)
        # circular background poly for polar (  rectangular bkgd is
        # turned off and a circular one drawn instead )
        self.ppb = Pointset(3)

        # outter circle at max radius
        self.ppr = Pointset(3)

        # Calculate corner positions of the x-y-z world and screen cube
        # Note:  Its not clear why you want, or what the meaning
        # of x-y-z screen coordinates is (corners8_s) since the
        # screen is only 2D
        corners8_c, corners8_s = self._CalculateCornerPositions(*lims)
        # We use this later to determine the order of the corners
        self._delta = 1
        for i in axes.daspect:
            if i < 0:
                self._delta *= -1

        # Since in polar coordinates screen and data x and y values
        # need to be mapped to theta and R
        # PolarAxis calculates things differently from Cartesian2D.
        # Also, polar coordinates need to be
        # fixed to world coordinates, not screen coordinates
        vector_cx = corners8_c[1] - corners8_c[0]
        vector_sx = corners8_s[1] - corners8_s[0]
        vector_cy = corners8_c[2] - corners8_c[0]
        vector_sy = corners8_s[2] - corners8_s[0]

        # The screen window may be any rectangular shape and
        # for PolarAxis, axes.daspectAuto = False so
        # that circles always look like circle
        # (x & y are always scaled together).
        # The first step is to find the radial extent of the PolarAxis.
        # For the axis to fit this will simply be the smallest window size in
        # x or y.  We also need to reduce it further so
        # that tick labels can be drawn
        if vector_cx.norm() < vector_cy.norm():
            dimMax_c = (vector_cx.norm() / 2)
            dimMax_s = (vector_sx.norm() / 2)
        else:
            dimMax_c = (vector_cy.norm() / 2)
            dimMax_s = (vector_sy.norm() / 2)

        pix2c = dimMax_c / dimMax_s  # for screen to world conversion
        txtSize = self.labelPix * pix2c
        radiusMax_c = dimMax_c - 3.0 * txtSize  # Max radial scale extent
        center_c = Point(0.0, 0.0, 0.0)
        #self._radialRange = radiusMax_c
        radiusMax_c = self._radialRange.range


        #==========================================================
        # Apply labels
        #==========================================================
        for d in range(2):
            # Get the four corners that are of interest for this dimension
            # In 2D, the first two are the same as the last two
            tmp = self._cornerIndicesPerDirection[d]
            tmp = [tmp[i] for i in [0, 1, 0, 1]]
            corners4_c = [corners8_c[i] for i in tmp]
            corners4_s = [corners8_s[i] for i in tmp]
            # Get index of corner to put ticks at
            i0 = 0
            bestVal = 999999999999999999999999
            for i in range(4):
                val = corners4_s[i].y
                if val < bestVal:
                    i0 = i
                    bestVal = val

            # Get directional vectors in real coords and screen pixels.
            # Easily calculated since the first _corner elements are
            # 000,100,010,001
            vector_c = corners8_c[d + 1] - corners8_c[0]
            vector_s = corners8_s[d + 1] - corners8_s[0]
            textDict = self._textDicts[d]
            p1 = corners4_c[i0] + vector_c * 0.5
            key = '_label_'
            if key in textDict and textDict[key] in self._children:
                t = textDict.pop(key)
                t.text = labels[d]
                t.x, t.y, t.z = p1.x, p1.y, p1.z
            else:
                #t = AxisText(self,labels[d], p1.x,p1.y,p1.z)
                t = AxisLabel(self, labels[d], p1.x, p1.y, p1.z)
                t.fontSize = 10
            newTextDicts[d][key] = t
            t.halign = 0
            t._color = self._axisColor  # Use private attr for performance
            # Move to back
            if not t in self._children[-3:]:
                self._children.remove(t)
                self._children.append(t)
            # Get vec to calc angle
            vec = Point(vector_s.x, vector_s.y)
            if vec.x < 0:
                vec = vec * -1

            # This was causing weird behaviour, so I commented it out
            # t.textAngle = float(vec.angle() * 180/np.pi)
            # Keep up to date (so label can move itself just beyond ticks)
            t._textDict = newTextDicts[d]

        # To make things easier to program I just pulled out
        # the Polar angular and radial calulations since they
        # are disimilar anyway (i.e. a 'for range(2)' doesn't really help here)

        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #      Angular Axis lines, tick and circular background calculations
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # theta axis is circle at the outer radius
        # with a line segment every 6 degrees to form circle
        theta = self._angularRefPos + \
                self._sense * np.linspace(0, 2 * np.pi, 61)

        # x,y for background
        xb = radiusMax_c * np.cos(theta)
        yb = radiusMax_c * np.sin(theta)

         #x,y for maximum scale radius
        xc = radiusMax_c * np.cos(theta)
        yc = radiusMax_c * np.sin(theta)
        # ppb is the largest circle that will fit
        # and is used  to draw the  polar background poly
        for x, y in np.column_stack((xb, yb)):
            self.ppb.append(x, y, -10.0)

        for x, y in np.column_stack((xc, yc)):
            self.ppr.append(x, y, -1.0)

        # polar ticks
        # Correct the tickdist for the x-axis if the numbers are large
        minTickDist = self._minTickDist
        minTickDist = 40  # This should be set by the font size

        # Calculate tick distance in world units
        minTickDist *= pix2c
        tickValues = ticksPerDim[0]  # can be None

        tmp = GetPolarTicks(center_c, radiusMax_c, self._angularRange,
                            self._angularRefPos, self._sense,
                            minTickDist, tickValues)
        ticks, ticksPos, ticksText = tmp
        textRadius = (2.2 * txtSize) + radiusMax_c
        # Get tick unit
        tickUnit = self._angularRange.range
        if len(ticks)>=2:
            tickUnit = ticks[1] - ticks[0]
        
        for tick, pos, text in zip(ticks, ticksPos, ticksText):
            # Get little tail to indicate tick, current hard coded to 4
            p1 = pos
            tv = 0.05 * radiusMax_c * p1 / p1.norm()
            # polar ticks are inline with vector to tick position
            p2s = pos - tv

            # Add tick lines
            ppc.append(pos)
            ppc.append(p2s)

            # Text is in word coordinates so need to create them based on ticks
            theta = self._angularRefPos + (self._sense * tick * np.pi / 180.0)
            p2 = Point((textRadius * np.cos(theta))[0], (textRadius * np.sin(theta))[0], 0)
            # Put a textlabel at tick
            textDict = self._textDicts[0]
            if tick in textDict and textDict[tick] in self._children:
                t = textDict.pop(tick)
                t.x, t.y, t.z = p2.x, p2.y, p2.z
            else:
                t = AxisText(self, text, p2.x, p2.y, p2.z)
            # Add to dict
            newTextDicts[0][tick] = t
            # Set other properties right
            t._visible = True
            if t.fontSize != self._tickFontSize:
                t.fontSize = self._tickFontSize
            t._color = self._axisColor  # Use private attr for performance
            t.halign = 0
            t.valign = 0
        #===================================================================
        # Get gridlines
        if drawGrid[0] or drawMinorGrid[0]:
            # Get more gridlines if required
            if drawMinorGrid[0]:
                ticks = self._GetPolarTicks(tickUnit / 5, self._angularRange)
            # Get positions
            for tick, p in zip(ticks, ticksPos):
                ppg.append(center_c)
                ppg.append(p)

        #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #  radial Axis lines, tick  calculations
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # the radial axis is vertical and horizontal lines through the center
        # radial lines every 90 deg
        theta = self._angularRefPos + \
                self._sense * np.arange(0, 2 * np.pi, np.pi / 2)
        xc = radiusMax_c * np.cos(theta)
        yc = radiusMax_c * np.sin(theta)

        for x, y in np.column_stack((xc, yc)):
            ppc.append(0.0, 0.0, 0.0)
            ppc.append(x, y, 0.0)

        # radial ticks
        # Correct the tickdist for the x-axis if the numbers are large
        minTickDist = self._minTickDist
        # Calculate tick distance in world units
        minTickDist *= pix2c
        tickValues = ticksPerDim[1]  # can be None

        ticks, ticksPos, ticksText, quadIndex = [], [], [], []
        for index, theta in enumerate(self._angularRefPos +
                    self._sense * np.array([0, np.pi / 2, np.pi, np.pi * 3 / 2])):
            xc = radiusMax_c * np.cos(theta)
            yc = radiusMax_c * np.sin(theta)
            p2 = Point(xc, yc, 0)
            tmp = GetTicks(center_c, p2, Range(0, radiusMax_c), minTickDist, tickValues)
            if index == 0:
                ticks = ticks + tmp[0]
                ticksPos = ticksPos + tmp[1]
                quadIndex = quadIndex + [index + 1] * len(tmp[0])
            else:
                ticks = ticks + tmp[0][1:]
                ticksPos = ticksPos + tmp[1][1:]
                quadIndex = quadIndex + [index + 1] * len(tmp[1][1:])
        
        for tick, pos,  qIndx in zip(ticks, ticksPos, quadIndex):
            # Get little tail to indicate tick
            tickXformed = tick + self._radialRange.min
            text = '%1.4g' % (tickXformed)
            iExp = text.find('e')
            if iExp > 0:
                front = text[:iExp + 2]
                text = front + text[iExp + 2:].lstrip('0')

            p1 = pos
            if (p1.norm() != 0):
                tv = (4 * pix2c[0]) * p1 / p1.norm()
                tvTxt = ((4 * pix2c[0]) + txtSize[0].view(float)) * p1 / p1.norm()
            else:
                tv = Point(0, 0, 0)
                tvTxt = Point(-txtSize[0], 0, 0)
            # radial ticks are orthogonal to tick position
            tv = Point(tv.y, tv.x, 0)
            tvTxt = Point(tvTxt.y, tvTxt.x, 0)
            ptic = pos - tv
            ptxt = pos - tvTxt

            # Add tick lines
            ppc = ppc + pos
            ppc = ppc + ptic

            textDict = self._textDicts[qIndx]

            if tickXformed in textDict and \
                              textDict[tickXformed] in self._children:
                t = textDict.pop(tickXformed)
                t.x, t.y, t.z = ptxt.x, ptxt.y, ptxt.z
            else:
                t = AxisText(self, text, ptxt.x, ptxt.y, ptxt.z)
            # Add to dict
            #print(tick, '=>',text, 'but', t.text)
            newTextDicts[qIndx][tickXformed] = t
           # Set other properties right
            t._visible = True
            if t.fontSize != self._tickFontSize:
                t.fontSize = self._tickFontSize
            t._color = self._axisColor  # Use private attr for performance
            t.halign = 1
            t.valign = 0

        #====================================================================
        # Get gridlines
        if drawGrid[1] or drawMinorGrid[1]:
            # Get more gridlines if required
            # line segment every 6 degrees to form circle
            theta = self._angularRefPos + \
                    self._sense * np.linspace(0, 2 * np.pi, 61)
            if drawMinorGrid[1]:
                ticks = self._GetTicks(tickUnit / 5, self._angularRange)
            # Get positions
            for tick in ticks:
                xc = tick * np.cos(theta)
                yc = tick * np.sin(theta)
                xlast = xc[:-1][0]
                ylast = yc[:-1][0]
                for x, y in np.column_stack((xc, yc)):
                    ppg.append(Point(xlast, ylast, 0.0))
                    ppg.append(Point(x, y, 0.0))
                    xlast = x
                    ylast = y

        # Clean up the text objects that are left
        for tmp in self._textDicts:
            for t in list(tmp.values()):
                t.Destroy()

        # Store text object dictionaries for next time ...
        self._textDicts = newTextDicts

        # Return points (note: Special PolarAxis points are set as class
        # variables since this method was overrridden)
        return ppc, pps, ppg
    
    
    def OnDraw(self):
        
        # Get axes
        axes = self.GetAxes()
        if not axes:
            return
        
        # Calculate lines and labels
        try:
            ppc, pps, ppg = self._CreateLinesAndLabels(axes)
        except Exception:
            self.Destroy() # So the error message does not repeat itself
            raise
        
        # Draw background and lines
        if self.ppb and self.ppr:
            
            # Set view params
            s = axes.camera.GetViewParams()
            if s['loc'][0] != s['loc'][1] != 0:
                axes.camera.SetViewParams(loc=(0,0,0))
            
            # Prepare data for polar coordinates
            self.RescalePolarData()
            
            # Prepare for drawing lines and background
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
            gl.glDisable(gl.GL_DEPTH_TEST)
            
            # Draw polygon background
            clr = 1, 1, 1
            gl.glColor3f(clr[0], clr[1], clr[2])
            gl.glVertexPointerf(self.ppb.data)
            gl.glDrawArrays(gl.GL_POLYGON, 0, len(self.ppb))
            
            # Draw lines
            clr = self._axisColor
            gl.glColor(clr[0], clr[1], clr[2])
            gl.glLineWidth(self._lineWidth)
            gl.glVertexPointerf(self.ppr.data)
            gl.glDrawArrays(gl.GL_LINE_LOOP, 0, len(self.ppr))
            
            # Clean up
            gl.glFlush()
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        
        
        # Draw axes lines and text etc.
        BaseAxis.OnDraw(self, (ppc, pps, ppg))
    
    
    def OnKeyDown(self, event):
        if event.key == 17 and self.ref_but == 1:
            self.shiftIsDown = True
        elif event.key == 19 and self.ref_but == 0:
            self.controlIsDown = True
        return True
    
    
    def OnKeyUp(self, event):
        self.shiftIsDown = False
        self.controlIsDown = False
        self.ref_but = 0  # in case the mouse was also down
        return True
    
    
    def OnMouseDown(self, event):
        # store mouse position and button
        self.ref_mloc = event.x, event.y
        self.ref_but = event.button
        self.ref_lowerRadius = self._radialRange.min
        self.ref_angularRefPos = self.angularRefPos
    
    
    def OnMouseUp(self, event):
        self.ref_but = 0
        self.Draw()
    
    
    def OnMotion(self, event):
        if not self.ref_but:
            return
        
        axes = event.owner
        mloc = axes.mousepos
        Rrange = self._radialRange.range
        if self.ref_but == 1:
            # get distance and convert to world coordinates
            refloc = axes.camera.ScreenToWorld(self.ref_mloc)
            loc = axes.camera.ScreenToWorld(mloc)
            # calculate radial and circular ref position translations
            dx = loc[0] - refloc[0]
            dy = loc[1] - refloc[1]

            if self.shiftIsDown:
                minRadius = self.ref_lowerRadius - dy
                self.SetLimits(rangeR=Range(minRadius, minRadius + Rrange))
            else:
                self.angularRefPos = self.ref_angularRefPos - (50 * dx / Rrange)
        
        elif self.ref_but == 2:
            # zoom
            
            # Don't care about x zooming for polar plot
            # get movement in x (in pixels) and normalize
            #factor_x = float(self.ref_mloc[0] - mloc[0])
            #factor_x /= axes.position.width
            
            # get movement in y (in pixels) and normalize
            factor_y = float(self.ref_mloc[1] - mloc[1])
            # normalize by axes height
            factor_y /= axes.position.height
            
            # apply (use only y-factor ).
            Rrange = Rrange * math.exp(-factor_y)
            self.SetLimits(rangeR=Range(self._radialRange.min, self._radialRange.min + Rrange))
            self.ref_mloc = mloc
        self.Draw()
        return True
    
    
    @DrawAfter
    def SetLimits(self, rangeTheta=None, rangeR=None, margin=0.04):
        """ SetLimits(rangeTheta=None, rangeR=None, margin=0.02)
        
        Set the Polar limits of the scene. These are taken as hints to set
        the camera view, and determine where the axis is drawn for the
        3D camera.
        
        Either range can be None, rangeTheta can be a scalar since only the
        starting position is used.  RangeTheta is always 360 degrees
        Both rangeTheta dn rangeR can be a 2 element iterable, or a
        visvis.Range object. If a range is None, the range is obtained from
        the wobjects currently in the scene. To set the range that will fit
        all wobjects, simply use "SetLimits()"
        
        The margin represents the fraction of the range to add (default 2%).
        
        """
        
        if rangeTheta is None or isinstance(rangeTheta, Range):
            pass  # ok
        elif hasattr(rangeTheta, '__len__') and len(rangeTheta) >= 1:
            rangeTheta = Range(rangeTheta[0], rangeTheta[0] + 359)
        else:
            rangeTheta = Range(float(rangeTheta), float(rangeTheta) + 359)
        
        if rangeR is None or isinstance(rangeR, Range):
            pass  # ok
        elif hasattr(rangeR, '__len__') and len(rangeR) == 2:
            rangeR = Range(rangeR[0], rangeR[1])
        else:
            raise ValueError("radial limits should be Range \
                               or two-element iterables.")
        
        if rangeTheta is not None:
            self._angularRange = rangeTheta
            
        
        rR = rangeR
        rZ = rangeZ = None
        
        axes = self.GetAxes()
        
        # find outmost range
        drawObjs = axes.FindObjects(PolarLine)
        # Now set the transform for the PolarLine data
        for ob in drawObjs:
            
            # Ask object what it's polar limits are
            tmp = ob._GetPolarLimits()
            if not tmp:
                continue
            tmpTheta, tmpR = tmp  # in the future may use theta limits
            if not tmp:
                continue
            tmp = ob._GetLimits()
            tmpX, tmpY, tmpZ = tmp
            
            # update min/max
            if rangeR:
                pass
            elif tmpR and rR:
                rR = Range(min(rR.min, tmpR.min), max(rR.max, tmpR.max))
            elif tmpR:
                rR = tmpR

            if rangeZ:
                pass
            elif tmpZ and rZ:
                rZ = Range(min(rZ.min, tmpZ.min), max(rZ.max, tmpZ.max))
            elif tmpX:
                rZ = tmpZ

        # default values
        if rR is None:
            rR = Range(-1, 1)

        if rZ is None:
            rZ = Range(0, 1)

        self._radialRange = rR
        # apply margins
        if margin:
            # x
            tmp = rR.range * margin
            if tmp == 0:
                tmp = margin
            adjDim = rR.range + tmp
            rX = Range(-adjDim, adjDim)
            rY = Range(-adjDim, adjDim)
            # z
            tmp = rZ.range * margin
            if tmp == 0:
                tmp = margin
            rZ = Range(rZ.min - tmp, rZ.max + tmp)

        # apply to each camera
        for cam in axes._cameras.values():
            cam.SetLimits(rX, rY, rZ)

    
    def GetLimits(self):
        """ GetLimits()
        
        Get the limits of the polar axis as displayed now.
        Returns a tuple of limits for theta and r, respectively.
        
        """
        return self._angularRange, self._radialRange
    
    
    @PropWithDraw
    def angularRefPos():
        """ Get/Set the angular reference position in
        degrees wrt +x screen axis.
        """
        # internal store in radians to avoid constant conversions
        def fget(self):
            return 180.0 * self._angularRefPos / np.pi
        
        def fset(self, value):
            self._angularRefPos = np.pi * int(value) / 180
            self.Draw()
        return locals()
    
    
    @PropWithDraw
    def isCW():
        """ Get/Set the sense of rotation.
        """
        def fget(self):
            return (self._sense == 1)

        def fset(self, value):
            if isinstance(value, bool):
                if value:
                    self._sense = 1.0
                else:
                    self._sense = -1.0
                self.Draw()
            else:
                raise Exception("isCW can only be assigned " +
                                "by a bool (True or False)")
        return locals()
