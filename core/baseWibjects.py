# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module baseWibjects

Defines the Box class and the DraggableBox class.

"""

import OpenGL.GL as gl

from visvis.core import Wibject
from visvis.core import misc
from visvis.utils.pypoints import Pointset


class Box(Wibject):
    """ Box(parent)
    
    A simple, multi-purpose, rectangle object.
    It implements functionality to draw itself. Most wibjects will
    actually inherit from Box, rather than from Wibject.
    
    """
    
    def __init__(self, parent):
        Wibject.__init__(self, parent)
        self._edgeColor = (0,0,0)
        self._edgeWidth = 1.0
    
    @misc.PropWithDraw
    def edgeColor():
        """ Get/Set the edge color of the wibject.
        """
        def fget(self):
            return self._edgeColor
        def fset(self, value):
            self._edgeColor = misc.getColor(value, 'setting edgeColor')
        return locals()
    
    @misc.PropWithDraw
    def edgeWidth():
        """ Get/Set the edge width of the wibject.
        """
        def fget(self):
            return self._edgeWidth
        def fset(self, value):
            self._edgeWidth = float(value)
        return locals()
    
    def _GetBgcolorToDraw(self):
        """ Can be overloaded to indicate mouse over in buttons.
        """
        return self._bgcolor
    
    def OnDraw(self, fast=False):
        
        # get dimensions
        w, h = self.position.size
        
        # draw plane
        if self._bgcolor:
            # Get positions
            x1, x2 = 0, w
            y1, y2 = 0, h
            # Set color
            clr = self._GetBgcolorToDraw()
            gl.glColor(clr[0], clr[1], clr[2], 1.0)
            #
            gl.glBegin(gl.GL_POLYGON)
            gl.glVertex2f(x1,y1)
            gl.glVertex2f(x1,y2)
            gl.glVertex2f(x2,y2)
            gl.glVertex2f(x2,y1)
            gl.glEnd()
        
        # prepare
        gl.glDisable(gl.GL_LINE_SMOOTH)
        
        # draw edges
        if self.edgeWidth and self.edgeColor:
            
            # Get positions
            # Draw edges on top of the first and last pixel
            x1, x2 = 0.5, w-0.5
            y1, y2 = 0.5, h-0.5
            # Set color and line width
            clr = self.edgeColor
            gl.glColor(clr[0], clr[1], clr[2], 1.0)
            gl.glLineWidth(self.edgeWidth)
            #
            gl.glBegin(gl.GL_LINE_LOOP)
            gl.glVertex2f(x1,y1)
            gl.glVertex2f(x1,y2)
            gl.glVertex2f(x2,y2)
            gl.glVertex2f(x2,y1)
            gl.glEnd()
        
        # clean up
        gl.glEnable(gl.GL_LINE_SMOOTH)


class DraggableBox(Box):
    """ DraggableBox(parent)
    
    A Box wibject, but draggable and resizable.
    Intended as a base class.
    
    """
    
    def __init__(self, parent):
        Box.__init__(self, parent)
        
        # Make me draggable
        self._dragStartPos = None
        self._dragResizing = False
        self._dragMouseOver = False
        
        # Prepare points to draw
        self._DragCalcDots()
        
        # Bind to own events
        self.eventMouseDown.Bind(self._DragOnDown)
        self.eventMouseUp.Bind(self._DragOnUp)
        self.eventEnter.Bind(self._DragOnEnter)
        self.eventLeave.Bind(self._DragOnLeave)
        self.eventPosition.Bind(self._DragCalcDots)
        
        # Bind to figure events
        self.eventMotion.Bind(self._DragOnMove)
    
    
    def _DragCalcDots(self, event=None):
        w,h = self.position.size
        dots = Pointset(2)
        #
        dots.append(3,3); dots.append(3,6); dots.append(3,9)
        dots.append(6,3); dots.append(6,6); dots.append(6,9)
        dots.append(9,3); dots.append(9,6); dots.append(9,9)
        #
        dots.append(w-3, h-3); dots.append(w-3, h-6); dots.append(w-3, h-9)
        dots.append(w-6, h-3); dots.append(w-6, h-6)
        dots.append(w-9, h-3)
        self._dots = dots
    
    def _DragOnEnter(self, event):
        self._dragMouseOver = True
        self.Draw()
    
    def _DragOnLeave(self, event):
        self._dragMouseOver = False
        self.Draw()
   
    def _DragOnDown(self, event):
        pos = self.position
        # Store position if clicked on draggable arreas
        if event.x < 10 and event.y < 10:
            self._dragStartPos = event.absx, event.absy
        elif event.x > pos.width-10 and event.y > pos.height-10:
            self._dragStartPos = event.absx, event.absy
            self._dragResizing = True
    
    
    def _DragOnMove(self, event):
        if not self._dragStartPos:
            return
        elif self._dragResizing:
            self.position.w += event.absx - self._dragStartPos[0]
            self.position.h += event.absy - self._dragStartPos[1]
            event.owner.Draw()
        else: # dragging
            self.position.x += event.absx - self._dragStartPos[0]
            self.position.y += event.absy - self._dragStartPos[1]
            event.owner.Draw()
        self._dragStartPos = event.absx, event.absy
    
    
    def _DragOnUp(self, event):
        self._dragStartPos = None
        self._dragResizing = False
    
    def OnDraw(self):
        Box.OnDraw(self)
        
        if self._dragMouseOver:
            
            # Prepare
            gl.glColor(0,0,0,1)
            gl.glPointSize(1)
            gl.glDisable(gl.GL_POINT_SMOOTH)
            
            # Draw dots
            if len(self._dots):
                gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
                gl.glVertexPointerf(self._dots.data)
                gl.glDrawArrays(gl.GL_POINTS, 0, len(self._dots))
                gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
