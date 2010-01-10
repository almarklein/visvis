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

""" Module simpleWibjects

Implements basic wibjects like buttons, and, maybe later, sliders etc.

$Author: almar.klein $
$Date: 2010-01-05 18:03:45 +0100 (di, 05 jan 2010) $
$Rev: 118 $

"""

from events import BaseEvent
from misc import Property
from textRender import Label


class PushButton(Label):
    """ PushButton(parent, text='', fontname='sans')
    A button to click on. It is a label with an edgewidth of 1 by default.
    It's background color changes when the mouse is moved over it.
    """
    
    def __init__(self, parent, *args, **kwargs):
        Label.__init__(self, parent, *args, **kwargs)
        
        # Get an edge
        self.edgeWidth = 1
        
        # variable to store original bg color
        self._bgcolor2 = self.bgcolor
        
        # Bind events
        self.eventEnter.Bind(self._OnEnter)
        self.eventLeave.Bind(self._OnLeave)
        self.hitTest = True
    
    def _OnEnter(self, event):
        self._bgcolor2 = self.bgcolor
        self.bgcolor = (0.8,0.9,0.8)
        fig = self.GetFigure()
        if fig:
            fig.Draw()
    
    def _OnLeave(self, event):
        self.bgcolor = self._bgcolor2
        fig = self.GetFigure()
        if fig:
            fig.Draw()


class ToggleButton(PushButton):
    """ ToggleButton(parent, text='', fontname='sans')
    Inherits from PushButton. This button can be set on and off by clicking
    on it, or by using it's property "state". The on state is indicated by
    making the edge thicker. The event eventStateChanged is fired when its
    state is changed.
    """
    
    def __init__(self, parent, *args, **kwargs):
        PushButton.__init__(self, parent, *args, **kwargs)
        
        # The state of the button, and an event to notify its change
        self._state = False
        self._eventStateChanged = BaseEvent(self)
        
        # Bind event
        self.eventMouseDown.Bind(self._OnDown)
    
    @Property
    def state():
        """ The state of the toggle button: on, or off.
        """
        def fset(self, value):
            self._state = bool(value)
            self._Update()
        def fget(self):
            return self._state
    
    @property
    def eventStateChanged(self):
        return self._eventStateChanged
    
    def _OnDown(self, event):
        self.state = not self.state
    
    def _Update(self, event=None):
        if self._state:
            self.edgeWidth = 2
        else:
            self.edgeWidth = 1        
        fig = self.GetFigure()
        if fig:
            fig.Draw()
        self._eventStateChanged.Fire()


class RadioButton(ToggleButton):
    """ RadioButton(parent, text='', fontname='sans')
    Inherits from ToggleButton. If pressed upon, sets the state of all
    sibling RadioButton instances to False, and its own state to True.
    
    When this happens, all instances will fire eventStateChanged (after
    the states are set). So it's only necessary to bind to one of them 
    to detect the selection of  another item.
    """
    
    def _OnDown(self, event):
        
        # Get me and all my siblings
        toggleButtons = []
        if self.parent:
            for sibling in self.parent.children:
                if isinstance(sibling, ToggleButton):
                    toggleButtons.append(sibling)
        
        # Disable all siblings (including self) and set own state
        for but in toggleButtons:
            but._state = False
        self._state = True
        
        # Update all so the events are fired
        for but in toggleButtons:
            but._Update()
        