# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module colorWibjects

Implements a few widgets to interactively change color properties of textures.

"""

import OpenGL.GL as gl

import numpy as np
import weakref

from visvis.utils.pypoints import Point, Pointset
from visvis import Colormapable
#
from visvis import Box, DraggableBox
from visvis import Label
from visvis import BaseFigure, Axes
from visvis.core.axises import GetTicks
#
from visvis.wibjects.buttons import RadioButton
from visvis.wibjects.sliders import RangeSlider


class BaseMapableEditor(DraggableBox):
    """ BaseMapableEditor(parent)
    
    Base class for widgets that are used to edit the mapable properties
    of objects: colormap and clim.
    
    """
    
    def __init__(self, parent):
        DraggableBox.__init__(self, parent)
        
        # Objects to map
        self._mapables = []
    
    
    def GetMapables(self):
        """ GetMapables()
        
        Get a list of mappable objects that was given earlier using
        SetMapables. If an axes or figure was given, all eligable
        objects are queried from their children.
        
        """
        
        # Remove dead refs
        self._mapables = [ref for ref in self._mapables if ref() is not None]
        
        # Get the actual mapable objects
        mapables = []
        for arg in self._mapables:
            # Get real ref
            arg = arg()
            if isinstance(arg, (BaseFigure, Axes)):
                mapables.extend(arg.FindObjects(Colormapable))
            elif isinstance(arg, Colormapable):
                mapables.append(arg)
        
        # Done
        return mapables
    
    
    def SetMapables(self, *args):
        """ SetMapables(mapable1, mapable2, mapable3, etc.)
        
        Set the mapables to take into account. A mapable is any
        wibject or wobject that inherits from Colormapable (and can
        be recognized by having a colormap and clim property).
        
        The argument may also be a list or tuple of objects, or an Axes
        or Figure instance, in which case all mapable children are used.
        If args is not given, the parent is used.
        
        """
        
        # Parse input
        if not args:
            args = [self.parent]
        elif len(args)==1 and hasattr(args[0], '__len__'):
            args = args[0]
        if not args:
            return
        
        # Get the weak refs to the actual wobjects
        self._mapables = []
        for arg in args:
            if isinstance(arg, (BaseFigure,Axes)) or isinstance(arg, Colormapable):
                self._mapables.append( weakref.ref(arg) )
            else:
                print('Warning object is not mappable: %s' % str(arg))


class ClimEditor(BaseMapableEditor):
    """ CLimEditor(parent, *args)
    
    A wibject to edit the clim property of textures (thereby setting
    window-width and window-level).
    
    During initialization, SetMapables(*args) is called. The easiest way
    to use this wibject is to attach it to an axes or figure instance.
    The wibject then controls the colormaps of all mapable objects in them.
    
    """
    
    def __init__(self, parent, *args):
        BaseMapableEditor.__init__(self, parent)
        
        # init size
        self.position.w = 300
        self.position.h = 50
        
        # Init mappables
        self._mapables = []
        
        # Create slider widget
        self._slider = RangeSlider(self)
        self._slider.position = 15,5,-30,-30 # 80 = 55+25
        self._slider.showTicks = True
        
        # Bind events
        self._slider.eventSliderChanged.Bind(self._UpdateFull)
        
        # Set mappables
        self.SetMapables(*args)
        self._InitFromMapables()
    
    
    @property
    def slider(self):
        """ Get the slider instance of this tool.
        """
        return self._slider
    
    def _UpdateFull(self, event):
        for mappable in self.GetMapables():
            ra = self._slider.range
            if hasattr(mappable, 'SetClim'):
                mappable.SetClim(ra.min, ra.max)
            else:
                mappable.clim = ra.min, ra.max
    
    
    def _InitFromMapables(self):
        """ _InitFromMapables()
        
        The clim of the last mapable obtained by GetMapables is used
        to initialize the editor (if possible).
        
        """
        
        # Get the last one and obtain its limits
        mappables = self.GetMapables()
        if mappables:
            # Update widget
            data = mappables[-1]._texture1._dataRef
            self._slider.fullRange = data.min(), data.max()
            self._slider.range = mappables[-1].clim


class ColormapEditor(BaseMapableEditor):
    """ ColormapEditor(parent *args)
    
    A wibject to edit colormaps.
    
    During initialization, SetMapables(*args) is called. The easiest way
    to use this wibject is to attach it to an axes or figure instance.
    The wibject then controls the colormaps of all mapable objects in them.
    
    """
    
    def __init__(self, parent, *args):
        BaseMapableEditor.__init__(self, parent)
        
        # init size
        self.position.w = 300
        self.position.h = 80
        
        # Init mappables
        self._mapables = []
        
        # Create node widget
        self._nodeWidget = CM_NodeWidget(self)
        self._nodeWidget.position = 55,35,-80,-40 # 80 = 55+25
        
        # Create buttons
        self._rBut = RadioButton(self, 'R'); self._rBut.position =  5,35, 12,14
        self._gBut = RadioButton(self, 'G'); self._gBut.position = 20,35, 12,14
        self._bBut = RadioButton(self, 'B'); self._bBut.position = 35,35, 12,14
        self._aBut = RadioButton(self, 'A'); self._aBut.position =  5,52, 12,14
        self._aBut.state = True
        
        # Create colorbar wibject
        cb = Colorbar(self)
        pos = self._nodeWidget.position
        cb.position = pos.x, 5, pos.w, 10
        
        # Bind events
        self._aBut.eventStateChanged.Bind(self._OnChannelSelect)
        
        # Bind events to THIS wibject, and process them in the nodeWidget
        # This is to allow the user to click just outside the wibject also.
        self.eventMouseDown.Bind(self._OnDown)
        self.eventMouseUp.Bind(self._OnUp)
        self.eventDoubleClick.Bind(self._OnDoubleClick)
        
        # Set mappables
        self.SetMapables(*args)
        self._InitFromMapables()
    
    
    def _OnDown(self, event):
        """ Pass event on """
        # Get event of nodeWibject and its position
        event2 = self._nodeWidget.eventMouseDown
        pos = self._nodeWidget.position
        # Calc location and limit
#         event2.Set(event.x-pos.left, event.y-pos.top, event.button)
        event2.Set(event.absx, event.absy, event.button)
        # Fire!
        if event2.x > -10 and event2.x < pos.width + 10:
            if event2.y > -10 and event2.y < pos.height + 10:
                event2.Fire()
                return True # Prevent dragging
    
    def _OnUp(self, event):
        """ Pass event on """
        # Get event of nodwWibject and its position
        event2 = self._nodeWidget.eventMouseUp
        event2.Set(event.absx, event.absy, event.button)
        # Fire!
        event2.Fire()
    
    
    def _OnDoubleClick(self, event):
        """ Pass event on """
        # get event of nodwWibject and its position
        event2 = self._nodeWidget.eventDoubleClick
        
        # Calc location and limit
#         pos = self._nodeWidget.position
#         event2.Set(event.x-pos.left, event.y-pos.top, event.button)
        event2.Set(event.absx, event.absy, event.button)
        # Fire!
        event2.Fire()
    
    
    def _OnChannelSelect(self, event):
        
        # Apply
        if self._rBut.state:
            self._nodeWidget._nodes = self._nodeWidget._allNodes[0]
            self._nodeWidget._line = self._nodeWidget._allLines[0]
        elif self._gBut.state:
            self._nodeWidget._nodes = self._nodeWidget._allNodes[1]
            self._nodeWidget._line = self._nodeWidget._allLines[1]
        elif self._bBut.state:
            self._nodeWidget._nodes = self._nodeWidget._allNodes[2]
            self._nodeWidget._line = self._nodeWidget._allLines[2]
        elif self._aBut.state:
            self._nodeWidget._nodes = self._nodeWidget._allNodes[3]
            self._nodeWidget._line = self._nodeWidget._allLines[3]
        
        # Show
        self._nodeWidget._OnUp()
    
    
    def _InitFromMapables(self):
        """ _InitFromMapables()
        
        The colormap of the last mapable obtained by GetMapables is used
        to initialize the editor (if possible).
        
        """
        
        # Get the last mappable and obtain its colormap
        mappables = self.GetMapables()
        if not mappables:
            return
        cmap = mappables[-1]._GetColormap()
        if not cmap:
            return
        
        # Get node data
        nodeData = cmap
        
        # Can we make nodes of it?
        if isinstance(nodeData, list):
            
            # Obtain position
            tt = np.linspace(0,1,len(nodeData))
            
            # Clear nodes
            for i in range(4):
                self._nodeWidget._allNodes[i].clear()
                
            # Create nodes
            for t, node in zip(tt,nodeData):
                for i in range(4):
                    nodes = self._nodeWidget._allNodes[i]
                    if i< len(node):
                        nodes.append(t,1-node[i])
                    else:
                        nodes.append(t,0)
        
        elif isinstance(nodeData, dict):
            # Allow several color names
            for key in list(nodeData.keys()):
                if key.lower() in ['r', 'red']:
                    nodeData['r'] = nodeData[key]
                elif key.lower() in ['g', 'green']:
                    nodeData['g'] = nodeData[key]
                if key.lower() in ['b', 'blue']:
                    nodeData['b'] = nodeData[key]
                if key.lower() in ['a', 'alpha']:
                    nodeData['a'] = nodeData[key]
            
            # Create nodes
            for i in range(4):
                key = 'rgba'[i]
                if key in nodeData:
                    nodes = self._nodeWidget._allNodes[i]
                    nodes.clear()
                    for t, val in nodeData[key]:
                        nodes.append(t,1-val)
        
        # Update
        self._nodeWidget._UpdateFull()

    
class CM_NodeWidget(Box):
    """ CM_NodeWidget(parent)
    
    Class to modify node positions using the mouse.
    
    """
    
    def __init__(self, parent):
        Box.__init__(self, parent)
        
        # Set color
        self.bgcolor = 'w'
        
        # How soon the mouse snaps to a node
        self._snapWidth = 5
        
        # The currently selected node (or None if nothing is selected)
        self._selectedNode = None
        
        # The nodes and lines of R,G,B and A
        self._allNodes = [Pointset(2) for i in range(4)]
        self._allLines = [Pointset(2) for i in range(4)]
        
        # Init nodes
        for nodes in self._allNodes:
            nodes.append(0,1)
            nodes.append(1,0)
        self._allNodes[3][0,1] = 0 # alpha is completele ones by default
        
        # Init lines
        for line in self._allLines:
            for i in np.linspace(0,1,256):
                line.append(i,1) # the actual map will be 1-line
        
        # Make lines correct now
        for nodes, line in zip(self._allNodes, self._allLines):
            self._NodesToLine(nodes, line)
        
        # The node and line currently in control
        self._nodes = self._allNodes[3]
        self._line = self._allLines[3]
        
        # Bind events
        self.eventMotion.Bind(self._OnMotion)
        self.eventMouseUp.Bind(self._OnUp)
        self.eventMouseDown.Bind(self._OnDown)
        self.eventDoubleClick.Bind(self._OnDoubleClick)
    
    
    def _OnDown(self, event):
        
        # calculate distance of mouse to all points
        p = Point(event.x, event.y)
        dists = p.distance( self._nodes * Point(self.position.size) )
        
        # is one close enough?
        i = -1
        if self._nodes: # or .min() will not work
            tmp = dists.min()
            if tmp <= self._snapWidth:
                i, = np.where(dists==tmp)
        
        # if so, store that point
        if i>= 0:
            self._selectedNode = i
        else:
            self._selectedNode = None
    
    
    def _OnUp(self, event=None):
        if self._selectedNode is None:
            return
        
        # clean up
        self._selectedNode =  None
        
        # Calculate the lines one last time
        self._NodesToLine(self._nodes, self._line, True)
        
        # Draw (not fast)
        self.Draw()
    
    
    def _OnMotion(self, event):
        
        # should we proceed?
        if self._selectedNode is None:
            return
        if self._selectedNode >= len(self._nodes):
            self._OnUp()
            return
        
        # calculate and limit new position
        x, y = event.x, event.y
        pos = Point(x,y) / Point(self.position.size)
        if pos.x<0: pos.x=0
        if pos.y<0: pos.y=0
        if pos.x>1: pos.x = 1
        if pos.y>1: pos.y = 1
        
        # Change node's position
        self._nodes[self._selectedNode,0] = pos.x
        self._nodes[self._selectedNode,1] = pos.y
        
        # Apply to line
        self._NodesToLine(self._nodes, self._line)
        
        # Draw (fast)
        self.Draw(True)
    
    
    def _OnDoubleClick(self, event):
        
        # use OnDown method to test if and which node was clicked
        self._OnDown(event)
        
        if self._selectedNode is None:
            # create new node?
            pos = self.position
            x, y = event.x, event.y
            if x>-5 and x<pos.width+5 and y>-5 and y<pos.height-5:
                pos = Point(event.x, event.y) / Point(self.position.size)
                self._nodes.append( pos )
        else:
            # remove point
            self._nodes.pop(self._selectedNode)
        # Update
        self._UpdateFull()
    
    
    def _UpdateFull(self):
        """ Update all lines and draw. """
        
        # Create the lines
        for nodes, line in zip(self._allNodes, self._allLines):
            self._NodesToLine(nodes, line)
        
        # Draw
        self.Draw(True)
    
    
    def _NodesToLine(self, nodes, line, update=False):
        """ Convert nodes to a full 256 element line.
        """
        
        # sort nodes
        nn = [n for n in nodes]
        nn.sort(key=lambda n:n.x)
        nodes = Pointset(2)
        for n in nn:
            nodes.append(n)
        
        # interpolate
        xx = np.linspace(0,1,256)
        if nodes:
            yy = np.interp(xx, nodes[:,0], nodes[:,1])
            if np.isnan(yy[-1]): # happens when last two nodes on same pos
                yy[-1] = yy[-2]
            line[:,1] = yy
        else:
            line[:,1] = np.zeros((256,),dtype=np.float32) # no nodes
        
        if update:
            # Create colormap
            map = {}
            for i in range(4):
                nn = self._allNodes[i]
                tmp = []
                for ii in range(len(nn)):
                    tmp.append((nn[ii,0], 1-nn[ii,1]))
                if tmp:
                    key = 'rgba'[i]
                    map[key] = sorted(tmp, key=lambda x:x[0])
            
            # Apply colormap to all registered objects
            if self.parent:
                for ob in self.parent.GetMapables():
                    ob._SetColormap(map)
                    ob.Draw()
    
    
    def OnDraw(self):
        Box.OnDraw(self)
        
        # Create color dict
        colors = {  self._allLines[0]:(1,0,0), self._allLines[1]:(0,1,0),
                    self._allLines[2]:(0,0,1), self._allLines[3]:(0,0,0) }

        # prepare scaling
        gl.glPushMatrix()
        w,h = self.position.size
        gl.glScale(w, h, 1)
        
        
        # prepare
        gl.glPointSize(7)
        gl.glLineWidth(1)
        gl.glEnable(gl.GL_POINT_SMOOTH) # round points
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        
        # Draw lines
        for line in self._allLines:
            if len(line) and line is not self._line:
                gl.glColor( *colors[line] )
                gl.glVertexPointerf(line.data)
                gl.glDrawArrays(gl.GL_LINE_STRIP, 0, len(line))
        
        # Draw the line under control (using a thicker line)
        gl.glColor( *colors[self._line] )
        gl.glLineWidth(2)
        gl.glVertexPointerf(self._line.data)
        gl.glDrawArrays(gl.GL_LINE_STRIP, 0, len(self._line))
        
        # draw nodes
        gl.glColor( *colors[self._line] )
        gl.glVertexPointerf(self._nodes.data)
        gl.glDrawArrays(gl.GL_POINTS, 0, len(self._nodes))
        
        # clean up
        gl.glPopMatrix()
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_POINT_SMOOTH)


class Colorbar(Box):
    """ Colorbar(parent)
    
    This wibject displays the colormap applied to a certain mapable.
    It should be attached to an Axes or Figure. The displayed colormap
    is that of the last added (or last added in the last axes) mapable
    object.
    
    A Colorbar can be created with the function vv.colorbar().
    
    """
    
    def __init__(self, parent):
        Box.__init__(self, parent)
        
        self._label = Label(self, '')
        self._label.bgcolor = ''
        self.eventPosition.Bind(self._OnPositionChange)
        
        # Pool of labels for tickmarks, to reuse them
        self._wobjects = [] # So we can have Text objects
        self._labelPool = {}
        
        # If attached to axes, correct that axes' size
        if isinstance(parent, Axes):
            
            # Init position
            x = parent.position.width + 5
            self.position = x, 0.0, 30, 1.0
            
            # Keep informed of axes movment
            self.parent.eventPosition.Bind(self._OnAxesPositionChange)
            
            # Correct axes' position
            self.parent.position.Correct(dw=-100) # 30 + 70
    
    
    def _OnPositionChange(self, event):
        """ Adjust the position of the label.
        """
        self._label.halign = 'center'
        self._label.valign = 'center'

        w,h = self.position.size
        if w > h:
            self._label.textAngle = 0
            self._label.position.w = 100
            self._label.position.h = self._label.fontSize
            self._label.position.x = (w - 100)/2.
            self._label.position.y = h + 20
        else:
            self._label.textAngle = 90
            self._label.position.w = self._label.fontSize
            self._label.position.h = 100
            self._label.position.x = w + 40
            self._label.position.y = (h - 100)/2.
    
    def _OnAxesPositionChange(self, event):
        axes = event.owner
        if axes:
            self.position.x = axes.position.width+5
    
    @property
    def label(self):
        """ Get the label instance for this colorbar.
        """
        return self._label
    
    
    def SetLabel(self, value):
        """ SetLabel(value)
        
        A convenience function to set the label text.
        
        """
        self._label.text = value
    
    
    def OnDraw(self):
        
        # Get colormaps that apply
        par = self.parent
        if par is None:
            return
        elif isinstance(par, (BaseFigure, Axes)):
            mapables = par.FindObjects(Colormapable)
        elif isinstance(par, ColormapEditor):
            mapables = par.GetMapables()
        elif isinstance(par, ClimEditor):
            mapables = par.GetMapables()
        else:
            mapables = []
        
        # Get the last one
        mapable = None
        if mapables:
            mapable = mapables[-1]
        
        
        # get dimensions
        w,h = self.position.size
        
        # Calc map direction
        if w > h:
            texCords = [0,0,1,1]
        else:
            texCords = [1,0,0,1]
        
        
        # draw plane
        if mapable:
            # Use it's colormap texture
            mapable._EnableColormap()
            # Disable alpha channel (by not blending)
            gl.glDisable(gl.GL_BLEND)
            gl.glColor(1.0, 1.0, 1.0, 1.0)
            # Draw quads
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord1f(texCords[0]); gl.glVertex2f(0,0)
            gl.glTexCoord1f(texCords[1]); gl.glVertex2f(0,h)
            gl.glTexCoord1f(texCords[2]); gl.glVertex2f(w,h)
            gl.glTexCoord1f(texCords[3]); gl.glVertex2f(w,0)
            gl.glEnd()
            
            # Clean up
            gl.glEnable(gl.GL_BLEND)
            gl.glFlush()
            mapable._DisableColormap()
        
        # prepare
        gl.glDisable(gl.GL_LINE_SMOOTH)
        
        # draw edges
        if self.edgeWidth and self.edgeColor:
            clr = self.edgeColor
            gl.glColor(clr[0], clr[1], clr[2], 1.0)
            gl.glLineWidth(self.edgeWidth)
            #
            gl.glBegin(gl.GL_LINE_LOOP)
            gl.glVertex2f(0,0)
            gl.glVertex2f(0,h)
            gl.glVertex2f(w,h)
            gl.glVertex2f(w,0)
            gl.glEnd()
        
        if hasattr(mapable, 'clim'):
            # Draw ticks
            if w>h:
                p0 = Point(0, h)
                p1 = Point(w, h)
                delta = Point(0,3)
                halign, valign = 0, 0
                xoffset, yoffset = -8, -2
            else:
                p0 = Point(w, h)
                p1 = Point(w, 0)
                delta = Point(3,0)
                halign, valign = -1, 0
                xoffset, yoffset = 5, -8
            
            # Get tickmarks
            ticks, ticksPos, ticksText = GetTicks(p0, p1, mapable.clim)
            
            newLabelPool = {}
            linePieces = Pointset(2)
            for tick, pos, text in zip(ticks, ticksPos, ticksText):
                pos2 = pos + delta
                
                # Add line piece
                linePieces.append(pos); linePieces.append(pos2)
                
                # Create or reuse label
                if tick in self._labelPool:
                    label = self._labelPool.pop(tick)
                else:
                    label = Label(self, ' '+text+' ')
                    label.bgcolor = ''
                
                # Position label and set text alignment
                newLabelPool[tick] = label
                label.halign, label.valign = halign, valign
                label.position.x = pos2.x + xoffset
                label.position.w = 16
                label.position.y = pos2.y + yoffset
            
            # Clean up label pool
            for label in list(self._labelPool.values()):
                label.Destroy()
            self._labelPool = newLabelPool
            
            # Draw line pieces
            # prepare
            gl.glLineWidth(1)
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
            gl.glVertexPointerf(linePieces.data)
            gl.glDrawArrays(gl.GL_LINES, 0, len(linePieces))
            gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        # clean up
        gl.glEnable(gl.GL_LINE_SMOOTH)
