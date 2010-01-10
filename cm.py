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

""" Module cm

Provides functionality, wibjects and other helper classes to provide
colormaps in visvis.

Also provides the default colormaps.

$Author: almar.klein $
$Date: 2010-01-05 18:03:45 +0100 (di, 05 jan 2010) $
$Rev: 118 $

"""

import OpenGL.GL as gl
import numpy as np

from misc import Property
from base import Box
from core import BaseFigure, Axes
from simpleWibjects import RadioButton
from points import Point, Pointset

import weakref


class ColormapEditor(Box):
    def __init__(self, parent, *args):
        Box.__init__(self, parent)
        
        # init size
        self.position.w = 300
        
        # Init mappables
        self._mapables = []
        self.SetMapables(*args)
        
        # Create node widget
        self._nodeWidget = CM_NodeWidget(self)
        self._nodeWidget.position = 70,5,-75,-10
        
        # Create buttons
        self._rBut = RadioButton(self, 'R'); self._rBut.position = 05,5, 12,16
        self._gBut = RadioButton(self, 'G'); self._gBut.position = 20,5, 12,16
        self._bBut = RadioButton(self, 'B'); self._bBut.position = 35,5, 12,16
        self._aBut = RadioButton(self, 'A'); self._aBut.position = 50,5, 12,16
        self._rBut.halign = self._gBut.halign = self._bBut.halign = 0
        self._aBut.halign = 0
        
        
        
        # Bind events
        self.hitTest = True # enable firing events
        self._aBut.eventStateChanged.Bind(self._OnChannelSelect)
        
        # Bind events to THIS wibject, and process them in the nodeWidget
        # This is to allow the user to click just outside the wibject also.
        self.eventMouseDown.Bind(self._OnDown)
        self.eventDoubleClick.Bind(self._OnDoubleClick)
        
        
    
    
    def _OnDown(self, event):
        """ Pass event on """
        # Get event of nodwWibject and its position
        event2 = self._nodeWidget.eventMouseDown
        pos = self._nodeWidget.position
        # Calc location and limit
        event2.x = event.x - pos.left
        event2.y = event.y - pos.top
        # Fire!
        event2.Fire()
    
    
    def _OnDoubleClick(self, event):
        """ Pass event on """
        # get event of nodwWibject and its position
        event2 = self._nodeWidget.eventDoubleClick
        pos = self._nodeWidget.position
        # Calc location and limit
        event2.x = event.x - pos.left
        event2.y = event.y - pos.top
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
    
    
    def SetMapables(self, *args):
        """ SetMapables(mapable1, mapable2, mapable3, etc.)
        
        Set the mapables to apply the colormap to. A mapable is any
        wibject or wobject that has a _colormap attribute. 
        
        The argument may also be a list or tuple of objects, or an Axes 
        or Figure, in which case the tree is searched for mappables. If 
        args is not given, the parent is used.
        
        Note that the list of mappables is querried when called. When 
        for example adding a new texture to the scene of which you want 
        this wibject to edit the colormap, you should re-call this method.
        """
        
        # Parse input
        if not args:
            args = [self.parent]
        elif len(args)==1 and hasattr(args, '__len__'):
            args = args[0]
        if not args:
            return
        
        # Get the weak refs to the actual wobjects
        mapables = []
        for arg in args:
            if isinstance(arg, BaseFigure):
                tmp = arg.FindObjects(attr='_colormap')
                mapables.extend(tmp)
            elif isinstance(arg, Axes):
                tmp = arg.FindObjects(attr='_colormap')
                mapables.extend(tmp)
            elif hasattr(arg, '_colormap'):
                mapables.append( weakref.ref(arg) )
            else:
                print 'Warning object is not mappable: ', arg 
        
        # Store weak refs
        self._mapables = [weakref.ref(m) for m in mapables]

# todo: when showaxis is off, fps is much higher

class CM_NodeWidget2(Box):
    
    def __init__(self, parent):
        Box.__init__(self, parent)
        
        # set color
        self.bgcolor = 'w'
        
        # how soon the mouse snaps to a node
        self._snapWidth = 5
        
        # The currently selected node (or None if nothing is selected)
        self._selectedNode = None
        
        # Which channel to edit
        self._activeChannel = 3 # alpha
        
        # The nodes to be placed and moved by user
        self._nodes = Pointset(5) # r g b a t
        self._nodes.Append(1,1,1,0,0) # Note that rgba are reversed
        self._nodes.Append(0,0,0,0,1)
        
        # The resulting colormap
        self._map = Pointset(4)
        for i in range(256):
            self._map.Append(0,0,0,0)
        
        # Bind events
        fig = self.GetFigure()
        if fig:
            fig.eventMouseUp.Bind(self._OnUp)
            fig.eventMotion.Bind(self._OnMotion)
        self.eventMouseDown.Bind(self._OnDown)
        self.eventDoubleClick.Bind(self._OnDoubleClick)
        self.hitTest = True # enable firing events
    
    
    def _OnDown(self, event):
        
        # Get pointset of nodes in 2D
        i = self._activeChannel
        pp = Pointset( self._nodes[:,(i,4)] )
        
        # calculate distance of mouse to all points
        p = Point(event.x, event.y)
        dists = p.Distance( pp * Point(self.position.size) )
        
        # is one close enough?
        i = -1
        if self._nodes: # or .min() will not work if empty
            tmp = dists.min()
            if tmp <= self._snapWidth:
                i, = np.where(dists==tmp)
        
        # if so, store that point
        if i>= 0:
            self._selectedNode = i
        else:
            self._selectedNode = None
    
    
    def _OnUp(self, event=None):
        
        # clean up
        self._selectedNode =  None
        
        # sort nodes
        nn = [n for n in self._nodes]
        nn.sort(key=lambda n:n[4])
        self._nodes.Clear()
        for n in nn:
            self._nodes.Append(n)
        
        # interpolate
        xx = np.linspace(0,1,256)
        for i in range(4):
            data = np.interp(xx, self._nodes[:,4], self._nodes[:,i])
            self._map[:,i] = data
        
        # Draw (not fast)
        fig = self.GetFigure()
        if fig:
            fig.Draw()
    
    
    def _OnMotion(self, event):
        
        # should we proceed?
        if self._selectedNode is None:
            return
        
        # calculate and limit new position
        x, y = event.x - self.position.absLeft, event.y - self.position.absTop
        pos = Point(x,y) / Point(self.position.size)
        if pos.x<0: pos.x=0
        if pos.y<0: pos.y=0
        if pos.x>1: pos.x = 1
        if pos.y>1: pos.y = 1
        
        # change node's position
        self._nodes[self._selectedNode,0] = pos.x
        self._nodes[self._selectedNode,1] = pos.y
        
        # Draw (fast)
        fig = self.GetFigure()
        if fig:
            fig.Draw(True)
    
    
    def _OnDoubleClick(self, event):
        
        # use OnDown method to test if and which node was clicked
        self._OnDown(event)
        
        if self._selectedNode is None:
            # create new node?
            pos = self.position
            x, y = event.x, event.y
            if x>-5 and x<pos.width+5 and y>-5 and y<pos.height-5:
                pos = Point(event.x, event.y) / Point(self.position.size)
                self._nodes.Append( pos )
        else:
            # remove point
            self._nodes.Pop(self._selectedNode)
    
    
    def _NodesToLine(self, nodes, line):
        # sort nodes
        nn = [n for n in self._nodes]
        nn.sort(key=lambda n:n.x)
        self._nodes.Clear()
        for n in nn:
            self._nodes.Append(n)
        
        # interpolate
        xx = np.linspace(0,1,256)
        yy = np.interp(xx, self._nodes[:,0], self._nodes[:,1])
        self._line[:,1] = yy
    
    
    def OnDraw(self):
        Box.OnDraw(self)
        
        # Create color dict
        colors = {  self._nr:(1,0,0), self._ng:(0,1,0), self._nb:(0,0,1), 
                    self._lr:(1,0,0), self._lg:(0,1,0), self._lb:(0,0,1), 
                    self._na:(0,0,0), self._la:(0,0,0)}
        
        # prepare scaling
        gl.glPushMatrix()
        w,h = self.position.size
        gl.glScale(w, h, 1)
        
        
        # prepare         
        gl.glPointSize(7)
        gl.glLineWidth(1)
        gl.glEnable(gl.GL_POINT_SMOOTH) # round points
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        
        # draw lines
        for line in [self._lr, self._lg, self._lb, self._la]:
            gl.glColor( colors[line] )
            gl.glVertexPointerf(line.data)
            gl.glDrawArrays(gl.GL_LINE_STRIP, 0, len(line))
        
        # draw nodes
        gl.glColor( colors[self._nodes] )
        gl.glVertexPointerf(self._nodes.data)
        gl.glDrawArrays(gl.GL_POINTS, 0, len(self._nodes))
        
        # clean up
        gl.glPopMatrix()
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_POINT_SMOOTH)


class CM_NodeWidget(Box):
    
    def __init__(self, parent):
        Box.__init__(self, parent)
        
        # Set color
        self.bgcolor = 'w'
        
        # The nodes to be placed and moved by user
        self._allNodes = [Pointset(2) for i in range(4)]
        self._allLines = [Pointset(2) for i in range(4)]
        
        self._nodes = self._allNodes[3]
        for nodes in self._allNodes:
            nodes.Append(0,1)
            nodes.Append(1,0)
        self._allNodes[3][0,1] = 0 # alpha is completele ones by default
        
        self._line = self._allLines[3] 
        # Init lines
        for line in self._allLines:
            for i in np.linspace(0,1,256):
                line.Append(i,1) # the actual map will be 1-line
        
        # Make lines correct now
        for nodes, line in zip(self._allNodes, self._allLines):
            self._NodesToLine(nodes, line)
#         # The nodes to be placed and moved by user
#         self._nr = Pointset(2)
#         self._ng = Pointset(2)
#         self._nb = Pointset(2)
#         self._na = Pointset(2)
#         # The current nodelist to edit
#         self._nodes = self._nr
#         # Init nodes
#         for nodes in [self._nr, self._ng, self._nb, self._na]:
#             nodes.Append(0,1)
#             nodes.Append(1,0)
#         self._na[0,1] = 0 # alpha is completele ones by default
#         
#         # The interpolated lines
#         self._lr = Pointset(2)
#         self._lg = Pointset(2)
#         self._lb = Pointset(2)
#         self._la = Pointset(2)
#         # The  current line to edit
#         self._line = self._lr 
#         # Init lines
#         for line in [self._lr, self._lg, self._lb, self._la]:
#             for i in np.linspace(0,1,256):
#                 line.Append(i,1) # the actual map will be 1-line
#         
#        
        
        # how soon the mouse snaps to a node
        self._snapWidth = 5
        
        # the currently selected node (or None if nothing is selected)
        self._selectedNode = None
        
        # Bind events
        fig = self.GetFigure()
        if fig:
            fig.eventMouseUp.Bind(self._OnUp)
            fig.eventMotion.Bind(self._OnMotion)
        self.eventMouseDown.Bind(self._OnDown)
        self.eventDoubleClick.Bind(self._OnDoubleClick)
        self.hitTest = True # enable firing events

    
    
    def _OnDown(self, event):
        
        # calculate distance of mouse to all points
        p = Point(event.x, event.y)
        dists = p.Distance( self._nodes * Point(self.position.size) )
        
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
        
        # clean up
        self._selectedNode =  None
        
        # Calculate the lines one last time
        self._NodesToLine(self._nodes, self._line)
        
        # Draw (not fast)
        fig = self.GetFigure()
        if fig:
            fig.Draw()
    
    
    def _OnMotion(self, event):
        
        # should we proceed?
        if self._selectedNode is None:
            return
        
        # calculate and limit new position
        x, y = event.x - self.position.absLeft, event.y - self.position.absTop
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
        fig = self.GetFigure()
        if fig:
            fig.Draw(True)
    
    
    def _OnDoubleClick(self, event):
        
        # use OnDown method to test if and which node was clicked
        self._OnDown(event)
        
        if self._selectedNode is None:
            # create new node?
            pos = self.position
            x, y = event.x, event.y
            if x>-5 and x<pos.width+5 and y>-5 and y<pos.height-5:
                pos = Point(event.x, event.y) / Point(self.position.size)
                self._nodes.Append( pos )
        else:
            # remove point
            self._nodes.Pop(self._selectedNode)
    
    
    def _NodesToLine(self, nodes, line):
        """ Convert nodes to a full 245 element line.
        """
        
        # sort nodes
        nn = [n for n in nodes]
        nn.sort(key=lambda n:n.x)
        nodes = Pointset(2)
        for n in nn:
            nodes.Append(n)
        
        # interpolate
        xx = np.linspace(0,1,256)
        yy = np.interp(xx, nodes[:,0], nodes[:,1])
        if np.isnan(yy[-1]): # happens when last two nodes on same pos
            yy[-1] = yy[-2]
        line[:,1] = yy
        
        # Create colormap
        map = np.zeros((256,4), dtype=np.float32)
        for i in range(4):
            map[:,i] = 1-self._allLines[i][:,1]
        
        # Apply colormap to all registered objects
        if self.parent:
            for ref in self.parent._mapables:
                ob = ref()
                if ob is not None:
                    ob._colormap.SetMap(map)
    
    
    def OnDraw(self):
        Box.OnDraw(self)
        
#         # Create color dict
#         colors = {  self._nr:(1,0,0), self._ng:(0,1,0), self._nb:(0,0,1), 
#                     self._lr:(1,0,0), self._lg:(0,1,0), self._lb:(0,0,1), 
#                     self._na:(0,0,0), self._la:(0,0,0)}
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
#         for line in [self._lr, self._lg, self._lb, self._la]:
        for line in self._allLines:
            if line is not self._line:
                gl.glColor( colors[line] )
                gl.glVertexPointerf(line.data)
                gl.glDrawArrays(gl.GL_LINE_STRIP, 0, len(line))
        
        # Draw the line under control (using a thicker line)
        gl.glColor( colors[self._line] )
        gl.glLineWidth(2)
        gl.glVertexPointerf(self._line.data)
        gl.glDrawArrays(gl.GL_LINE_STRIP, 0, len(self._line))
        
        # draw nodes
        gl.glColor( colors[self._line] )
        gl.glVertexPointerf(self._nodes.data)
        gl.glDrawArrays(gl.GL_POINTS, 0, len(self._nodes))
        
        # clean up
        gl.glPopMatrix()
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisable(gl.GL_POINT_SMOOTH)
        