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

""" Module axis

Defines the Axis wobject class to draw tickmarks and lines for each
dimension.

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
from line import lineStyles
from cameras import depthToZ, TwoDCamera


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


class PolarAxis2D(BaseAxis):
    """ PolarAxis2D(parent)
    An Axis object represents the lines, ticks and grid that make
    up an axis. Not to be confused with an Axes, which represents
    a scene and is a Wibject.
    
    Polax axis.
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
        return Pointset(3), Pointset(3), Pointset(3)
        
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
        