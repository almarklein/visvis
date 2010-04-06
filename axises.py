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

""" Module axises

Defines the Axis wobject class to draw tickmarks and lines for each
dimension.

I chose to name this module using an awkward plural to avoid a name clash
with the axis() function.

$Author: almar.klein $
$Date: 2010-02-24 15:25:05 +0100 (Wed, 24 Feb 2010) $
$Rev: 252 $

"""

import OpenGL.GL as gl
import OpenGL.GLU as glu

import numpy as np
from points import Pointset, Point

import base
from textRender import Text 
from line import lineStyles, PolarLine
from cameras import depthToZ, TwoDCamera
from misc import Range, Property

# A note about tick labels. We format these using '%1.4g', which means
# they will have 4 significance, and will automatically displayed in
# exp notation if necessary. This means that the largest string is
# x.xxxE+yyy -> 10 characters. 
# In practice, the exp will hardly ever be larger than 2 characters. So we
# strip the zeros in the exponent and assume the (in practice) max string
# to be "-0.001e+99". With a fontsize of 9, this needs little less than 70
# pixels. The correction applied when visualizing axis (and ticks) is 60,
# because the default offset is 10 pixels for axes.

# create tick units
_tickUnits = []
for e in range(-10, 21):
    for i in [10, 20, 25, 50]:
        _tickUnits.append( i*10**e)


class AxisLabel(Text):
    """ AxisLabel(parent, text)
    A special label that moves itself just past the tickmarks. 
    The _textDict attribute should contain the Text objects of the tickmarks.
    
    This is a helper class.
    """
    
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self._textDict = {}
        self._move = 0
    
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
        normal = Point(np.cos(a), np.sin(a)).Normalize()
        
        # project the corner points of all text objects to the normal vector.
        def project(p,normal):
            p = p-pos
            phi = abs(normal.Angle(p))
            return float( p.Norm()*np.cos(phi) )
        # apply
        alpha = []          
        for text in self._textDict.values():
            if text is self:
                continue
            if text._vertices2 is None or not len(text._vertices2):
                continue            
            x,y = text._screenx, text._screeny
            xmin, xmax = text._deltax
            ymin, ymax = text._deltay
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



def GetTicks(p0, p1, lim, minTickDist=40, ticks=None):
    """ GetTicks(p0, p1, lim, minTickDist=40, ticks=None)
    Get the tick values, position and texts.
    These are calculated from a start end end position and the range
    of values to map on a straight line between these two points 
    (which can be 2d or 3d). If ticks is given, use these values instead.
    """
    
    # Vector from start to end point
    vec = p1-p0
    
    # Calculate all ticks if not given
    if ticks is None:
        
        # Get pixels per unit
        if lim.range == 0:
            return [],[],[]
        pixelsPerUnit = vec.Norm() / lim.range
        
        # Try all tickunits, starting from the smallest, until we find 
        # one which results in a distance between ticks more than
        # X pixels.
        try:
            for tickUnit in _tickUnits:
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
        pos = p0 + vec * ( (tick-lim.min) / lim.range )
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
    

class BaseAxis(base.Wobject):
    """ BaseAxis(parent)
    This is the (abstract) base class for the axis classes defined
    in this module.
    
    An Axis object represents the lines, ticks and grid that make
    up an axis. Not to be confused with an Axes, which represents
    a scene and is a Wibject.
    """
    def __init__(self, parent):
        base.Wobject.__init__(self, parent)
        
        # Define parameters
        self._lineWidth = 1 # 0.8
        self._minTickDist = 40
        
         # Corners of a cube in relative coordinates
        self._corners = tmp = Pointset(3)
        tmp.Append(0,0,0);  tmp.Append(1,0,0);  tmp.Append(0,1,0);  
        tmp.Append(0,0,1);  tmp.Append(1,1,0);  tmp.Append(1,0,1); 
        tmp.Append(0,1,1);  tmp.Append(1,1,1); 
        
        # Indices of the base corners for each dimension. 
        # The order is very important, don't mess it up...
        self._cornerIndicesPerDirection = [ [0,2,6,3], [3,5,1,0], [0,1,4,2] ]
        
        # Dicts to be able to optimally reuse text objects; creating new
        # text objects or changing the text takes a relatively large amount
        # of time (if done every draw).
        self._textDicts = [{},{},{}]
    
    
    def OnDraw(self):
        
        # Get axes and return if there is none,
        # or if it doesn't want to show an axis.
        axes = self.GetAxes()
        if not axes:
            return
        if not axes.showAxis:
            self._DestroyChildren()
            return
        
        # Calculate lines and labels
        try:
            ppc, pps, ppg = self.CreateLinesAndLabels(axes)            
        except Exception:
            self.Destroy() # So the error message does not repeat itself
            raise
        
        # Store lines to be drawn in screen coordinates
        self._pps = pps
        
        
        # Prepare for drawing lines
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)        
        gl.glVertexPointerf(ppc.data) 
        
        # Draw lines
        clr = axes._axisColor
        gl.glColor(clr[0], clr[1], clr[2])
        gl.glLineWidth(self._lineWidth)
        if len(ppc):
            gl.glDrawArrays(gl.GL_LINES, 0, len(ppc))
        
        # Clean up        
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        
        
        # Prepare for drawing grid
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)        
        gl.glVertexPointerf(ppg.data)        
        
        # Set stipple pattern
        if not axes.gridLineStyle in lineStyles:
            stipple = False
        else:
            stipple = lineStyles[axes.gridLineStyle]
        if stipple:
            gl.glEnable(gl.GL_LINE_STIPPLE)
            gl.glLineStipple(1, stipple)
        
        # Draw gridlines
        clr = axes._axisColor
        gl.glColor(clr[0], clr[1], clr[2])
        gl.glLineWidth(self._lineWidth)            
        if len(ppg):
            gl.glDrawArrays(gl.GL_LINES, 0, len(ppg))
        
        # Clean up
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_LINE_STIPPLE)
    
    
    def OnDrawScreen(self):
        # Actually draw the axis
        
        axes = self.GetAxes()
        if not axes:
            return
        if not axes._axis: # == showAxis
            return
        
        # get pointset
        if not hasattr(self, '_pps') or not self._pps:
            return
        pps = self._pps
        pps[:,2] = depthToZ( pps[:,2] )
        
        
        # Prepare for drawing lines
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(pps.data)
        if axes.camera is axes._cameras['twod']:
            gl.glDisable(gl.GL_LINE_SMOOTH)
        
        # Draw lines
        clr = axes._axisColor
        gl.glColor(clr[0], clr[1], clr[2])
        gl.glLineWidth(self._lineWidth)
        if len(pps):
            gl.glDrawArrays(gl.GL_LINES, 0, len(pps))
        
        # Clean up
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnable(gl.GL_LINE_SMOOTH)
    
    
    
    def _DestroyChildren(self):
        """ Method to clean up the children (text objects). """
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
        proj = glu.gluProject
        corners8_c = [relativeToCoord(p) for p in self._corners]            
        corners8_s = [Point(proj(p.x,p.y,p.z)) for p in corners8_c]
        
        # Return
        return corners8_c, corners8_s
    
    
    def _GetTicks(self, tickUnit, lim):
        """ _GetTicks(tickUnit, lim)
        Given tickUnit (the distance in world units between the ticks)
        and the range to cover (lim), calculate the actual tick values. 
        """
        
        firstTick = np.ceil(  lim.min/tickUnit ) * tickUnit
        lastTick  = np.floor( lim.max/tickUnit ) * tickUnit
        count = 0
        ticks = [firstTick]
        while ticks[-1] < lastTick-tickUnit/2:
            count += 1
#             tmp = firstTick + count*tickUnit
#             if abs(tmp/tickUnit) < 10**-10:
#                 tmp = 0 # due round-off err, 0 can otherwise be 0.5e-17 or so
#             ticks.append(tmp)
            ticks.append( firstTick + count*tickUnit )
        return ticks
    
    
    def _NextCornerIndex(self, i, d, vector_s):
        """ Calculate the next corner index. """
        
        if d<2 and vector_s.x >= 0:
            i+=self._delta
        elif d==2 and vector_s.y < 0:
            i+=self._delta
        else:
            i-=self._delta
        if i>3: i=0
        if i<0: i=3
        return i
    
    
    def CreateLinesAndLabels(self, axes):
        """ This is the method that calculates where lines should be 
        drawn and where labels should be placed. 
        
        It returns three point sets in which the pairs of points
        represent the lines to be drawn (using GL_LINES):
          * ppc: lines in real coords
          * pps: lines in screen pixels
          * ppg: dotted lines in real coords
        """
        raise NotImplemented('This is the abstract base class.')
    
    

class CartesianAxis2D(BaseAxis):
    """ CartesianAxis2D(parent)
    An Axis object represents the lines, ticks and grid that make
    up an axis. Not to be confused with an Axes, which represents
    a scene and is a Wibject.
    
    The CartesianAxis2D is a straightforward axis, drawing straight
    lines for cartesian coordinates in 2D.
    """
    
    def CreateLinesAndLabels(self, axes):
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
        drawGrid = [v for v in axes.showGrid]
        drawMinorGrid = [v for v in axes.showMinorGrid]
        ticksPerDim = [axes.xTicks, axes.yTicks]
        
        # Get limits            
        lims = axes.GetLimits()
        lims = [lims[0], lims[1], cam.zlim]
        
        # Get labels
        labels = [axes.xLabel, axes.yLabel]
        
        
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
            minTickDist *= vector_c.Norm() / vector_s.Norm()
            
            # Get index of corner to put ticks at
            i0 = 0; bestVal = 999999999999999999999999
            for i in range(2):
                val = corners4_s[i].y
                if val < bestVal:
                    i0 = i
                    bestVal = val
            
            # Get indices of next corners in line               
            i1 = self._NextCornerIndex(i0, d, vector_s)
            i2 = self._NextCornerIndex(i1, d, vector_s)
            # Get first corner and grid vectors
            firstCorner = corners4_c[i0]
            gv1 = corners4_c[i1] - corners4_c[i0]
            gv2 = corners4_c[i2] - corners4_c[i1]
            # Get tick vector to indicate tick
            gv1s = corners4_s[i1] - corners4_s[i0]
            #tv = gv1 * (5 / gv1s.Norm() )
            npixels = ( gv1s.x**2 + gv1s.y**2 ) ** 0.5 + 0.000001
            tv = gv1 * (5.0 / npixels )
            
            # Always draw these corners
            pps.Append(corners4_s[i0])
            pps.Append(corners4_s[i0]+vector_s)
            
            # Add line pieces to draw box
            if axes.showBox:
                for i in range(2):
                    if i != i0:
                        corner = corners4_s[i]
                        pps.Append(corner)
                        pps.Append(corner+vector_s)
            
            # Apply label
            textDict = self._textDicts[d]
            p1 = corners4_c[i0] + vector_c * 0.5
            key = '_label_'
            if key in textDict and textDict[key] in self._children:
                t = textDict.pop(key)
                t.text = labels[d]
                t.x, t.y, t.z = p1.x, p1.y, p1.z
            else:
                #t = Text(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                t = AxisLabel(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                t.fontSize=10
            newTextDicts[d][key] = t                
            t.halign = 0
            t.textColor = axes._axisColor
            # Move up front
            if not t in self._children[-3:]:                    
                self._children.remove(t) 
                self._children.append(t)
            # Get vec to calc angle
            vec = Point(vector_s.x, vector_s.y)
            if vec.x < 0:
                vec = vec * -1                
            t.textAngle = float(vec.Angle() * 180/np.pi)
            # Keep up to date (so label can move itself just beyond ticks)
            t._textDict = newTextDicts[d] 
            
            # Get ticks stuff
            tickValues = ticksPerDim[d] # can be None
            p1, p2 = firstCorner.Copy(), firstCorner+vector_c                
            tmp = GetTicks(p1,p2, lim, minTickDist, tickValues)
            ticks, ticksPos, ticksText = tmp
            
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
                pps.Append(p1s)
                pps.Append(p1s-tmp)
                
                # Put a textlabel at tick                     
                textDict = self._textDicts[d]
                if tick in textDict and textDict[tick] in self._children:
                    t = textDict.pop(tick)
                    t.x, t.y, t.z = p2.x, p2.y, p2.z
                else:
                    t = Text(self,text, p2.x,p2.y,p2.z, 'sans')                    
                # Add to dict 
                newTextDicts[d][tick] = t                    
                # Set other properties right
                t.visible = True
                if t.fontSize != axes._tickFontSize:
                    t.fontSize = axes._tickFontSize
                t.textColor = axes._axisColor
                if d==1:
                    t.halign = 1
                    t.valign = 0
                else:
                    t.halign = 0
                    t.valign = -1
            
            # We should hide this last tick if it sticks out
            if d==0:
                # Prepare text object to produce _vertices and _screenx
                t._Compile()
                t.OnDraw()
                # Get positions
                fig = axes.GetFigure()
                if fig:
                    tmp1 = fig.position.width
                    tmp2 = t._screenx + t._vertices1[:,0].max() / 2
                    # Apply
                    if t._vertices1 and tmp1 < tmp2:
                        t.visible = False
            
            # Get gridlines
            if drawGrid[d] or drawMinorGrid[d]:
                # Get more gridlines if required
                if drawMinorGrid[d]:
                    ticks = self._GetTicks(tickUnit/5, lim)
                # Get positions
                for tick in ticks:
                    # Get tick location
                    p1 = firstCorner.Copy()
                    p1[d] = tick
                    # Add gridlines
                    p3 = p1+gv1
                    p4 = p3+gv2
                    ppg.Append(p1);  ppg.Append(p3)
        
        # Correct gridlines so they are all at z=0.
        # The grid is always exactly at 0. Images are at -0.1 or less.
        # lines and poins are at +0.1            
        ppg.data[:,2] = 0.0
        
        # Clean up the text objects that are left
        for tmp in self._textDicts:                
            for t in tmp.values():
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
    
    def CreateLinesAndLabels(self, axes):
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
        drawGrid = [v for v in axes.showGrid]
        drawMinorGrid = [v for v in axes.showMinorGrid]
        ticksPerDim = [axes.xTicks, axes.yTicks, axes.zTicks]
        
        # Get limits        
        lims = [cam.xlim, cam.ylim, cam.zlim]
        
        # Get labels
        labels = [axes.xLabel, axes.yLabel, axes.zLabel]
        
        
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
            tmp = self._cornerIndicesPerDirection[d]
            corners4_c = [corners8_c[i] for i in tmp]
            corners4_s = [corners8_s[i] for i in tmp]
            
            # Get directional vectors in real coords and screen pixels. 
            # Easily calculated since the first _corner elements are 
            # 000,100,010,001
            vector_c = corners8_c[d+1] -corners8_c[0]
            vector_s = corners8_s[d+1] -corners8_s[0]
            
            # Calculate tick distance in units
            minTickDist = self._minTickDist
            minTickDist *= vector_c.Norm() / vector_s.Norm()
            
            # Get index of corner to put ticks at
            i0 = 0; bestVal = 999999999999999999999999
            for i in range(4):
                if d==2: val = corners4_s[i].x
                else: val = corners4_s[i].y
                if val < bestVal:
                    i0 = i
                    bestVal = val
            
            # Get indices of next corners in line               
            i1 = self._NextCornerIndex(i0, d, vector_s)
            i2 = self._NextCornerIndex(i1, d, vector_s)
            # Get first corner and grid vectors
            firstCorner = corners4_c[i0]
            gv1 = corners4_c[i1] - corners4_c[i0]
            gv2 = corners4_c[i2] - corners4_c[i1]
            # Get tick vector to indicate tick
            gv1s = corners4_s[i1] - corners4_s[i0]
            #tv = gv1 * (5 / gv1s.Norm() )
            npixels = ( gv1s.x**2 + gv1s.y**2 ) ** 0.5 + 0.000001
            tv = gv1 * (5.0 / npixels )
            
            # Always draw these corners
            pps.Append(corners4_s[i0])
            pps.Append(corners4_s[i0]+vector_s)
            # Add line pieces to draw box
            if axes.showBox:
                for i in range(4):
                    if i != i0:
                        corner = corners4_s[i]
                        pps.Append(corner)
                        pps.Append(corner+vector_s)
            
            # Apply label
            textDict = self._textDicts[d]
            p1 = corners4_c[i0] + vector_c * 0.5
            key = '_label_'
            if key in textDict and textDict[key] in self._children:
                t = textDict.pop(key)
                t.text = labels[d]
                t.x, t.y, t.z = p1.x, p1.y, p1.z
            else:
                #t = Text(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                t = AxisLabel(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                t.fontSize=10
            newTextDicts[d][key] = t                
            t.halign = 0
            t.textColor = axes._axisColor
            # Move up front
            if not t in self._children[-3:]:                    
                self._children.remove(t) 
                self._children.append(t)
            # Get vec to calc angle
            vec = Point(vector_s.x, vector_s.y)
            if vec.x < 0:
                vec = vec * -1                
            t.textAngle = float(vec.Angle() * 180/np.pi)
            # Keep up to date (so label can move itself just beyond ticks)
            t._textDict = newTextDicts[d] 
            
            # Get ticks stuff
            tickValues = ticksPerDim[d] # can be None
            p1, p2 = firstCorner.Copy(), firstCorner+vector_c                
            tmp = GetTicks(p1,p2, lim, minTickDist, tickValues)
            ticks, ticksPos, ticksText = tmp
            
            # Apply Ticks
            for tick, pos, text in zip(ticks, ticksPos, ticksText):
                
                # Get little tail to indicate tick
                p1 = pos
                p2 = pos - tv
                
                # Add tick lines                
                ppc.Append(p1)
                ppc.Append(p2)
                
                # z-axis has valign=0, thus needs extra space
                if d==2:
                    text+='  '
                
                # Put textlabel at tick                     
                textDict = self._textDicts[d]
                if tick in textDict and textDict[tick] in self._children:
                    t = textDict.pop(tick)
                    t.x, t.y, t.z = p2.x, p2.y, p2.z
                else:
                    t = Text(self,text, p2.x,p2.y,p2.z, 'sans')
                # Add to dict 
                newTextDicts[d][tick] = t                    
                # Set other properties right
                t.visible = True
                if t.fontSize != axes._tickFontSize:
                    t.fontSize = axes._tickFontSize
                t.textColor = axes._axisColor
                if d==2:
                    t.valign = 0
                    t.halign = 1
                else: 
                    if vector_s.y*vector_s.x >= 0:
                        t.halign = -1
                        t.valign = -1
                    else:
                        t.halign = 1
                        t.valign = -1
            
            # Get gridlines
            if drawGrid[d] or drawMinorGrid[d]:
                # get more gridlines if required
                if drawMinorGrid[d]:
                    ticks = self._GetTicks(tickUnit/5, lim)
                # get positions
                for tick in ticks:
                    # get tick location
                    p1 = firstCorner.Copy()
                    p1[d] = tick
                    # add gridlines (back and front)
                    p3 = p1+gv1
                    p4 = p3+gv2
                    ppg.Append(p1);  ppg.Append(p3)                    
                    ppg.Append(p3);  ppg.Append(p4)
        
        
        # Clean up the text objects that are left
        for tmp in self._textDicts:                
            for t in tmp.values():
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
    
    def CreateLinesAndLabels(self, axes):
        """ Choose depending on what camera is used. """
        
        if axes.camera.isTwoD:
            return CartesianAxis2D.CreateLinesAndLabels(self,axes)
        else:
            return CartesianAxis3D.CreateLinesAndLabels(self,axes)

def GetPolarTicks(p0, radius, lim, angularRefPos, sense , minTickDist=100, \
                  ticks=None):
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
        pos = p0 + Point(x[0],y[0],0)
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
        lowerRadialLim: Get and Set methods for the lower radial limit.  
        The upper limit is calulated from the current cartesian x-y 
        camera limits.

        angularRefPos: Get and Set methods for the relative screen 
        angle of the 0 degree polar reference.  Default is 0 degs 
        which corresponds to the positive x-axis (y =0)
        
        isCCW: Get and Set methods for the sense of rotation CCW or 
        CW. This method takes/returns a bool (True if the default CCW). 
    """
    
    def __init__(self, parent):
        BaseAxis.__init__(self,parent)
        self.ppb = None  
        axes = self.GetAxes()
        axes.daspectAuto = False
        self.axes = axes
        axes.bgcolor = None #disbables the default background
        self._minRadius = -40
        self._maxRadius = 0
        self._radius = self._maxRadius - self._minRadius
        self._angularRefPos = 0
        self._sense = 1.0
        
        # Need to overrride this because the PolarAxis has four sets of radial ticks (with same dict key!)
        self._textDicts = [{},{},{},{},{}]

        # indicate part that we view.
        # view_loc is the coordinate that we center on
        # view_zoomx and view_zoomx is the range of data visualized in
        # each direction
        self.view_zoomx = 100
        self.view_zoomy = 100
        self.view_loc = 0,0,0 # we only use the 2D part
        self._fx, self._fy = 0,0
        
        # reference stuff for interaction
        self.ref_loc = 0,0,0    # view_loc when clicked
        self.ref_mloc = 0,0     # mouse location when clicked
        self.ref_but = 0        # mouse button when clicked   
        self.ref_zoomx = 100.0  # zoom factors when clicked
        self.ref_zoomy = 100.0    

        self.controlIsDown = False
        self.shiftIsDown = False
         
        # bind special event for translating lower radial limit
        #axes.camera.eventCameraSpecial.Bind(self.processTranslate)
        self.axes.eventKeyDown.Bind(self.OnKeyDown)
        self.axes.eventKeyUp.Bind(self.OnKeyUp)        
        # 
        self.axes.eventMouseDown.Bind(self.OnMouseDown)
        self.axes.eventMouseUp.Bind(self.OnMouseUp)        
        self.axes.eventMotion.Bind(self.OnMotion)
 
    def rescalePolarData(self):
        """ This method finds and transforms all polar line data
        by the current polar radial axis limits so that data below
        the center of the polar plot is set to 0,0,0 and data beyond
        the maximum (outter radius) is clipped """
        
        axes = self.GetAxes()
        drawObjs = axes.FindObjects(PolarLine)
        # Now set the transform for the PolarLine data
        for anObj in drawObjs:
            anObj.transformPolar(self._minRadius, self._maxRadius, \
            self._angularRefPos, self._sense)

    def CreateLinesAndLabels(self, axes):
        """ This is the method that calculates where polar axis lines  
        should be drawn and where labels should be placed. 
        
        It returns three point sets in which the pairs of points
        represent the lines to be drawn (using GL_LINES):
          * ppc: lines in real coords
          * pps: lines in screen pixels
          * ppg: dotted lines in real coords
        """

        """  I completely rewrote this method as I ended up in a morass 
        trying to write polar axis code that stuck closly to the prior 
        work that Almar did.
        
        Once this works then hopefully it can be cleaned up and perhaps 
        brought into better alignent with visvis programming design
        -Curt
        """
            
        # Get camera instance which should be a TwoDCameraWithKeys camera.  
        # This camera has key bindings which are used to
        # rescale the lower radial limits.  Thus for polar plots the usr can pan, rescale the radial range 
        # AND slide the radial range up 
        # and down
        cam = axes.camera
        
        # Get axis grid and tick parameters
        drawGrid = [v for v in axes.showGrid]
        drawMinorGrid = [v for v in axes.showMinorGrid]
        # these are equivalent to axes.thetaTicks and axes.RadialTicks
        ticksPerDim = [axes.xTicks, axes.yTicks] 
        
        # Get x-y limits  in world coordinates          
        lims = axes.GetLimits()
        lims = [lims[0], lims[1], cam.zlim]

        
        # From current lims calculate the radial axis min and max
        
        # Get labels
        labels = [axes.xLabel, axes.yLabel]  # These are equivalent to Theta and radial labels
        
        
        # Init the new text object dictionaries (theta, R(0),R(90),R(180),R(270))
        newTextDicts = [{},{},{},{},{}]
        
        # Init pointsets for drawing lines and gridlines 
        ppc = Pointset(3) # lines in real coords
        pps = Pointset(3) # lines in screen pixels, currently not used by PolarAxis
        ppg = Pointset(3) # dotted lines in real coords (for grids)
        # circular background poly for polar (  rectangular bkgd is turned off and a circular one drawn instead )    
        self.ppb = Pointset(3)
        
        # outter circle at max radius
        self.ppr = Pointset(3) 
        
        # Calculate corner positions of the x-y-z world and screen cube
        # Note:  Its not clear why you want, or what the meaning of x-y-z screen 
        # coordinates is (corners8_s) since the screen is only 2D
        corners8_c, corners8_s = self._CalculateCornerPositions(*lims)
        
        # We use this later to determine the order of the corners
        self._delta = 1 
        for i in axes.daspect:
            if i<0: self._delta*=-1   
        
        # Since in polar coordinates screen and data x and y values need to be mapped to theta and R
        # PolarAxis calculates things differently from Cartesian2D.   Also, polar coordinates need to be
        # fixed to world coordinates, not screen coordinates
        vector_cx = corners8_c[1] - corners8_c[0]
        vector_sx = corners8_s[1] - corners8_s[0]
        vector_cy = corners8_c[2] - corners8_c[0]
        vector_sy = corners8_s[2] - corners8_s[0]
        
        # The screen window may be any rectangular shape and for PolarAxis, axes.daspectAuto = False so
        # that circles always look like circle (x & y are always scaled together).  the first step is to find the 
        # radial extent of the PolarAxis.  For the axis to fit this will simply be the smallest window size in
        # x or y.  We also need to reduce it further so that tick labels can be drawn
        txtSize = axes._tickFontSize
        if vector_cx.Norm() < vector_cy.Norm():
            dimMax_c = (vector_cx.Norm()/2)
            dimMax_s = (vector_sx.Norm()/2) 
        else:
            dimMax_c = (vector_cy.Norm()/2)
            dimMax_s = (vector_sy.Norm()/2) 

        pix2c = dimMax_c /dimMax_s  # for screen to world conversion
        txtSize = txtSize*pix2c
        radiusMax_c = dimMax_c - txtSize  #This is the max radial scale extent
        center_c = Point(0.0,0.0,0.0)
        self._maxRadius = self._minRadius + radiusMax_c
        self._radius = radiusMax_c
        


        #==========================================================
        # Apply label
        #==========================================================
        if False:
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
            textDict = self._textDicts[d]
            p1 = corners4_c[i0] + vector_c * 0.5
            key = '_label_'
            if key in textDict and textDict[key] in self._children:
                t = textDict.pop(key)
                t.text = labels[d]
                t.x, t.y, t.z = p1.x, p1.y, p1.z
            else:
                #t = Text(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                t = AxisLabel(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                t.fontSize=10
            newTextDicts[d][key] = t                
            t.halign = 0
            t.textColor = axes._axisColor
            # Move up front
            if not t in self._children[-3:]:                    
                self._children.remove(t) 
                self._children.append(t)
            # Get vec to calc angle
            vec = Point(vector_s.x, vector_s.y)
            if vec.x < 0:
                vec = vec * -1                
            t.textAngle = float(vec.Angle() * 180/np.pi)
            # Keep up to date (so label can move itself just beyond ticks)
            t._textDict = newTextDicts[d] 




        # To make things easier to program I just pulled out the Polar angular and radial calulations since they
        # are disimilar anyway (i.e. a 'for range(2)' doesn't really help here)
        
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #      Angular Axis lines, tick and circular background calculations
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # theta axis is circle at the outer radius
        # with a line segment every 6 degrees to form circle
        theta = self._angularRefPos + np.linspace(0, 2*np.pi,61) 
         
         # x,y for background
        xb =  dimMax_c * np.cos(theta)
        yb =  dimMax_c * np.sin(theta)
         
         #x,y for maximum scale radius
        xc =  radiusMax_c * np.cos(theta)
        yc =  radiusMax_c * np.sin(theta)
        # ppb is the largest circle that will fit and is used  to draw the  polar background poly
        for x,y in  np.column_stack((xb, yb)):
            self.ppb.Append(x,y,-10.0)
 
        for x,y in  np.column_stack((xc, yc)):
            self.ppr.Append(x,y,-1.0)
 
 

        # polar ticks 
        # Correct the tickdist for the x-axis if the numbers are large
        minTickDist = self._minTickDist
        minTickDist = 40  #This should be set by the font size  
        
        # Calculate tick distance in world units
        minTickDist *= pix2c
        tickValues = ticksPerDim[0] # can be None
        tmp = GetPolarTicks(center_c, radiusMax_c, Range(0, 359), \
                            self._angularRefPos, self._sense , \
                            minTickDist, tickValues)
        ticks, ticksPos, ticksText = tmp
        textRadius = (2.2*txtSize) + radiusMax_c
        for tick, pos, text in zip(ticks, ticksPos, ticksText):
            # Get little tail to indicate tick, current hard coded to 4
            p1 = pos 
            tv = 0.05*radiusMax_c[0]*p1/p1.Norm()
            # polar ticks are inline with vector to tick position
            p2s = pos - tv
             
            # Add tick lines                    
            ppc.Append(pos)
            ppc.Append(p2s)
            
        
            # Text is in word coordinates so need to create them based on ticks
            theta = self._angularRefPos + (tick*np.pi/180.0)
            p2 = Point((textRadius*np.cos(theta))[0], \
                       (textRadius*np.sin(theta))[0], 0)
            # Put a textlabel at tick                     
            textDict = self._textDicts[0]
            if tick in textDict and textDict[tick] in self._children:
                t = textDict.pop(tick)
                t.x, t.y, t.z = p2.x, p2.y, p2.z
            else:
                t = Text(self,text, p2.x,p2.y,p2.z, 'sans') 
            # Add to dict 
            newTextDicts[0][tick] = t                    
            # Set other properties right
            t.visible = True
            if t.fontSize != axes._tickFontSize:
                t.fontSize = axes._tickFontSize
            t.textColor = axes._axisColor
            t.halign = 0
            t.valign = 0
        #=======================================================================================
        # Get gridlines
        if drawGrid[0] or drawMinorGrid[0]:
            # Get more gridlines if required
            if drawMinorGrid[0]:
                ticks = self._GetPolarTicks(tickUnit/5, lim)
            # Get positions
            for tick,p in zip(ticks,ticksPos):
                ppg.Append(center_c)  
                ppg.Append(p)
            
            
            
            
            
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #  radial Axis lines, tick  calculations
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            
        # the radial axis is vertical and horizontal lines through the center  
        # radial lines every 90 deg
        theta = self._angularRefPos + np.arange(0, 2*np.pi,np.pi/2) 
        xc =  radiusMax_c * np.cos(theta)
        yc =  radiusMax_c * np.sin(theta)

        for x,y in  np.column_stack((xc, yc)):
            ppc.Append(0.0, 0.0, 0.0)
            ppc.Append(x,y,0.0)
            
        # radial ticks
        # Correct the tickdist for the x-axis if the numbers are large
        minTickDist = self._minTickDist
        # Calculate tick distance in world units
        minTickDist *= pix2c
        tickValues = ticksPerDim[1] # can be None

        ticks, ticksPos, ticksText, quadIndex = [],[],[],[]
        for index,theta in  enumerate(self._angularRefPos + \
                            np.array([0,np.pi/2,np.pi,np.pi*3/2])):
            xc = radiusMax_c * np.cos(theta)
            yc = radiusMax_c * np.sin(theta)
            p2 =  Point(xc[0],yc[0],0)                
            tmp = GetTicks(center_c, p2, Range(0,radiusMax_c), \
                           minTickDist, tickValues)
            if index == 0:
                ticks = ticks + tmp[0]
                ticksPos = ticksPos +tmp[1]
                quadIndex = quadIndex + [index+1]*len(tmp[0])
            else:
                ticks = ticks + tmp[0][1:]
                ticksPos = ticksPos +tmp[1][1:]
                quadIndex = quadIndex + [index+1]*len(tmp[1][1:])
            
       

        for tick, pos,  qIndx in zip(ticks, ticksPos, quadIndex):
            # Get little tail to indicate tick
            tickXformed = tick + self._minRadius
            text = '%1.4g' % (tickXformed)
            iExp = text.find('e')
            if iExp>0:
                front = text[:iExp+2]
                text = front + text[iExp+2:].lstrip('0') 
                
            p1 = pos 
            if (p1.Norm() != 0):
                tv = (4*pix2c[0])*p1/p1.Norm()
                tvTxt = ((4*pix2c[0]) + txtSize[0].view(float))*p1/p1.Norm()
            else:
                tv = Point(0, 0, 0)
                tvTxt = Point(-txtSize[0], 0, 0)
            # radial ticks are orthogonal to tick position
            tv = Point(tv.y, tv.x, 0)
            tvTxt = Point(tvTxt.y, tvTxt.x, 0)
            ptic = pos - tv
            ptxt = pos - tvTxt
            
            # Add tick lines                    
            ppc = ppc+pos
            ppc = ppc+ptic
            
            textDict = self._textDicts[qIndx]

            if tickXformed in textDict and \
                              textDict[tickXformed] in self._children:
                t = textDict.pop(tickXformed)
                t.x, t.y, t.z = ptxt.x, ptxt.y, ptxt.z
            else:
                t = Text(self, text, ptxt.x, ptxt.y, ptxt.z, 'sans') 
            # Add to dict 
            #print tick, '=>',text, 'but', t.text
            newTextDicts[qIndx][tickXformed] = t 
           # Set other properties right
            t.visible = True
            if t.fontSize != axes._tickFontSize:
                t.fontSize = axes._tickFontSize
            t.textColor = axes._axisColor
            t.halign = 1
            t.valign = 0

        #=======================================================================================
        # Get gridlines
        if drawGrid[1] or drawMinorGrid[1]:
            # Get more gridlines if required
            # line segment every 6 degrees to form circle
            theta = self._angularRefPos + np.linspace(0, 2*np.pi,61)  
            if drawMinorGrid[1]:
                ticks = self._GetTicks(tickUnit/5, lim)
            # Get positions
            for tick in ticks:
                xc =  tick * np.cos(theta)
                yc =  tick * np.sin(theta)
                xlast = xc[:-1][0]
                ylast = yc[:-1][0]
                for x,y in  np.column_stack((xc, yc)):
                    ppg.Append(Point(xlast, ylast, 0.0))
                    ppg.Append(Point(x, y, 0.0))
                    xlast = x
                    ylast = y
  
            
        if False: # d for dimension/direction
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
                minTickDist = 80  #This should be set by the font size  
            
            # Calculate tick distance in world units
            minTickDist *= vector_c.Norm() / vector_s.Norm()
            
            # Get index of corner to put ticks at
            i0 = 0; bestVal = 999999999999999999999999
            for i in range(2):
                val = corners4_s[i].y
                if val < bestVal:
                    i0 = i
                    bestVal = val
            
            # Get indices of next corners in line               
            i1 = self._NextCornerIndex(i0, d, vector_s)
            i2 = self._NextCornerIndex(i1, d, vector_s)
            # Get first corner and grid vectors
            firstCorner = corners4_c[i0]
            gv1 = corners4_c[i1] - corners4_c[i0]
            gv2 = corners4_c[i2] - corners4_c[i1]
            # Get tick vector to indicate tick
            gv1s = corners4_s[i1] - corners4_s[i0]
            #tv = gv1 * (5 / gv1s.Norm() )
            npixels = ( gv1s.x**2 + gv1s.y**2 ) ** 0.5 + 0.000001
            tv = gv1.Norm() * (5.0 / npixels )

                
            #==========================================================
            # Apply label
            textDict = self._textDicts[d]
            p1 = corners4_c[i0] + vector_c * 0.5
            key = '_label_'
            if key in textDict and textDict[key] in self._children:
                t = textDict.pop(key)
                t.text = labels[d]
                t.x, t.y, t.z = p1.x, p1.y, p1.z
            else:
                #t = Text(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                t = AxisLabel(self,labels[d], p1.x,p1.y,p1.z, 'sans')
                t.fontSize=10
            newTextDicts[d][key] = t                
            t.halign = 0
            t.textColor = axes._axisColor
            # Move up front
            if not t in self._children[-3:]:                    
                self._children.remove(t) 
                self._children.append(t)
            # Get vec to calc angle
            vec = Point(vector_s.x, vector_s.y)
            if vec.x < 0:
                vec = vec * -1                
            t.textAngle = float(vec.Angle() * 180/np.pi)
            # Keep up to date (so label can move itself just beyond ticks)
            t._textDict = newTextDicts[d] 
            
            #===========================================================
            # Get ticks stuff
            tickValues = ticksPerDim[d] # can be None
            if d==0:
                # polar ticks -- Need to generalize Range (-180, 180,  etc,)
                tmp = GetPolarTicks(s_center,radiusMax_c, Range(0, 359), \
                                    minTickDist, tickValues)
                ticks, ticksPos, ticksText = tmp
                
            elif d==1:
                # radial ticks
                ticks, ticksPos, ticksText = [],[],[]
                for theta in [0,np.pi/2,np.pi,np.pi*3/2]:
                    xc = radiusMax_c * np.cos(theta)
                    yc = radiusMax_c * np.sin(theta)
                    p2 =  Point(xc[0],yc[0],0)                
                    tmp = GetTicks(s_center,p2, lim, minTickDist, tickValues)
                    ticks = ticks+tmp[0]
                    ticksPos = ticksPos+tmp[1]
                    ticksText = ticksText+tmp[2]
            
            for tick, pos, text in zip(ticks, ticksPos, ticksText):
                # Get little tail to indicate tick, current hard coded to 4
                p1 = pos 
                tv = 0.05*radiusMax_c[0]*p1/p1.Norm()
                if d==0:
                    # polar ticks are inline with vector to tick position
                    p2s = pos + tv
                elif d==1:
                    # radial ticks are orthogonal to tick position
                    tv = Point(tv.y, tv.x, 0)
                    p2s = pos - tv
                
                # Add tick lines                    
                ppc.Append(pos)
                ppc.Append(p2s)
                
                # Text is in word coordinates so need to create them based on ticks
                if d==0:
                    p2 = Point((radiusMax_c*np.cos(tick*np.pi/180.0))[0], \
                               (radiusMax_c*np.sin(tick*np.pi/180.0))[0], 0)
                elif d==1:
                    if pos.x == s_center.x and pos.y > s_center.y:
                        p2 = Point(0, tick, 0)
                    elif pos.x == s_center.x and pos.y < s_center.y:
                        p2 = Point(0, -tick, 0)
                    elif pos.x > s_center.x and pos.y == s_center.y:
                        p2 = Point( tick,0, 0)
                    elif pos.x <s_center.x and pos.y == s_center.y:
                        p2 = Point(-tick,0,  0)
                # Put a textlabel at tick                     
                textDict = self._textDicts[d]
                if tick in textDict and textDict[tick] in self._children:
                    t = textDict.pop(tick)
                    t.x, t.y, t.z = p2.x, p2.y, p2.z
                else:
                    t = Text(self,text, p2.x,p2.y,p2.z, 'sans') 
                # Add to dict 
                newTextDicts[d][tick] = t                    
                # Set other properties right
                t.visible = True
                if t.fontSize != axes._tickFontSize:
                    t.fontSize = axes._tickFontSize
                t.textColor = axes._axisColor
                if d==1:
                    t.halign = 1
                    t.valign = 0
                else:
                    t.halign = 0
                    t.valign = -1
          
            #=======================================================================================
            # Get gridlines
            if drawGrid[d] or drawMinorGrid[d]:
                # Get more gridlines if required
                if drawMinorGrid[d]:
                    ticks = self._GetTicks(tickUnit/5, lim)
                # Get positions
                for tick in ticks:
                    # Get tick location
                    p1 = firstCorner.Copy()
                    p1[d] = tick
                    # Add gridlines
                    p3 = p1+gv1
                    p4 = p3+gv2
                    #ppg.Append(p1);  ppg.Append(p3)
        
        # Correct gridlines so they are all at z=0.
        # The grid is always exactly at 0. Images are at -0.1 or less.
        # lines and poins are at +0.1            
        #ppg.data[:,2] = 0.0
        
        # Clean up the text objects that are left
        for tmp in self._textDicts:                
            for t in tmp.values():
                t.Destroy()
        
        # Store text object dictionaries for next time ...
        self._textDicts = newTextDicts
        
        # Return
        

        return ppc, pps, ppg
       
    def OnDraw(self):
        BaseAxis.OnDraw(self)
        self.rescalePolarData()
        # draw background
        if self.ppb and self.ppr:
            clr = 1,1,1
            gl.glColor3f(clr[0], clr[1], clr[2])
            
            # Prepare for drawing lines
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)        
            gl.glVertexPointerf(self.ppb.data) 
            
            # Draw lines and polygon background
            if len(self.ppb):
                gl.glDrawArrays(gl.GL_POLYGON, 0, len(self.ppb))
            gl.glEnable(gl.GL_DEPTH_TEST)
            # Clean up        
            gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
            
            # Prepare for drawing lines
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)        
            gl.glVertexPointerf(self.ppr.data) 
            
            # Draw lines and polygon background
            if len(self.ppb):
                axes = self.GetAxes()
                clr = axes._axisColor
                gl.glColor(clr[0], clr[1], clr[2])
                gl.glLineWidth(self._lineWidth)
                gl.glDrawArrays(gl.GL_LINE_LOOP, 0 , len(self.ppr))
            gl.glEnable(gl.GL_DEPTH_TEST)
            # Clean up        
            gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
            

            
    def OnKeyDown(self, event):
        if event.key ==17 and self.ref_but==0:
            self.shiftIsDown = True
        elif event.key == 19 and self.ref_but==0:
            self.controlIsDown = True
        return True

    def OnKeyUp(self, event):
        self.shiftIsDown = False
        self.controlIsDown = False
        self.ref_but = 0 # in case the mouse was also down
        return True
    
    def OnMouseDown(self, event):
        # store mouse position and button
        self.ref_mloc = event.x, event.y
        self.ref_but = event.button
        self.ref_lowerRadius = self.minRadius
        self.ref_angularRefPos = self.angularRefPos 
    
    def OnMouseUp(self, event): 
        self.ref_but = 0
        self.axes.Draw()

        
    def OnMotion(self, event):
        if not self.ref_but:
            return
        
        if self.ref_but==1:
            # get loc (as the event comes from the figure, not the axes)
            mloc = self.axes.mousepos
                 
            # translate
            # get distance and convert to world coordinates
            refloc = self.axes.camera.ScreenToWorld(self.ref_mloc)
            loc = self.axes.camera.ScreenToWorld(mloc)
            # calculate translation
            dx = loc[0] - refloc[0]
            dy = loc[1] - refloc[1]
            
            
            if self.controlIsDown:
                #change lower graph limit

                self.minRadius  = self.ref_lowerRadius - dy

                self.axes.Draw()
                return True
            elif self.shiftIsDown:
                self.angularRefPos = self.ref_angularRefPos + \
                                     (10*dy/self._radius)
                self.axes.Draw()
                return True
            else:
                return False
 
        
    def processTranslate(self, event):
        if event.key == 19: #Ctrl key
            print self.minRadius, event.y
            self.minRadius  = self.minRadius + event.y
        elif event.key == 17: #hift  key
            self.angularRefPos = self.angularRefPos + (10*event.y/self._radius)

        

           
    @Property
    def minRadius():
        """ Get/Set the lower radial polar data limit 
        """
        def fget(self):
            return self._minRadius
        def fset(self, value):
            self._minRadius = int(value)
            self.OnDraw()
            
    @Property
    def angularRefPos():
        """ Get/Set the angular reference position in 
            degrees wrt +x screen axis"""
        # internal store in radians to avoid constant conversions
        def fget(self):
            return 180.0*self._angularRefPos/np.pi
        def fset(self, value):
            self._angularRefPos = np.pi*int(value)/180
            self.OnDraw()
            
    @Property
    def isCCW():
        """ Get/Set the sense of rotation. 
        If zero, the line is not drawn. """
        def fget(self):
            return (self._sense == 1)
        def fset(self, value):
            if isinstance(value, bool):
                if value:
                    self._sense = 1.0
                else:
                    self._sense = -1.0
            else:
                raise Exception("isCCW can only be assigned \
                                 by a bool (True or False)")
                    
        # @ Curt: 
        # All you have to do is implement this method, you can reuse
        # a lot from the cartesian2D version, so that would probably a good
        # starting point.
        # In your function "polar()" just use the new Axes.axisType property
        # to set it to 'polar'.
        # You probably also want to re-implement the GetTicks function, as it
        # creates ticks at a straight line, while you also need ticks that
        # are positioned in a circle.
        # Good luck!
        