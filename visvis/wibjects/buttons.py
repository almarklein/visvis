# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module buttons

Implements a few button widgets.

"""

from visvis.core.events import BaseEvent, MouseEvent
from visvis.core.misc import Property
from visvis import Label


class PushButton(Label):
    """ PushButton(parent, text='', fontname=None)
    
    A button to click on. It is a label with an edgewidth of 1, in which
    text is horizontally aligned. Plus the hittest is put on by default.
    
    """
    
    def __init__(self, parent, *args, **kwargs):
        Label.__init__(self, parent, *args, **kwargs)
        
        # Get an edge
        self.edgeWidth = 1
        
        # Text is centered by default
        self.halign = 0
        
        # And changes appearance on mouse over
        self._isOver = False
        self.eventEnter.Bind(self._OnEnter)
        self.eventLeave.Bind(self._OnLeave)
        
        # Create new event and bind handlers to implement it
        self._eventPress = MouseEvent(self)
        self.eventMouseUp.Bind(self._OnPressDetectUp)
    
    
    def _OnEnter(self, event):
        self._isOver = True
        self.Draw()
    
    def _OnLeave(self, event):
        self._isOver = False
        self.Draw()
    
    def _GetBgcolorToDraw(self):
        """ _GetBgcolorToDraw()
        
        Can be overloaded to indicate mouse over in buttons.
        
        """
        clr = list(self._bgcolor)
        if self._isOver:
            clr = [c+0.05 for c in clr]
        return clr
    
    @property
    def eventPress(self):
        """ Fired when the mouse released over the button after a mouseDown.
        """
        return self._eventPress
    
    def _OnPressDetectUp(self, evt):
        if self._isOver:
            self._eventPress.Set(evt.absx, evt.absy, evt.button)
            self._eventPress.Fire()


class ToggleButton(PushButton):
    """ ToggleButton(parent, text='', fontname=None)
    
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
    
    @Property # _Update will invoke a draw
    def state():
        """ A boolean expressing the state of the toggle button: on or off.
        """
        def fset(self, value):
            self._state = bool(value)
            self._Update()
        def fget(self):
            return self._state
        return locals()
    
    @property
    def eventStateChanged(self):
        """ Fires when the state of the button changes.
        """
        return self._eventStateChanged
    
    def _OnDown(self, event):
        self.state = not self.state
    
    def _Update(self, event=None):
        if self._state:
            self.edgeWidth = 2
        else:
            self.edgeWidth = 1
        #self.Draw() Setting edgeWidth will invoke redraw
        self._eventStateChanged.Fire()


class RadioButton(ToggleButton):
    """ RadioButton(parent, text='', fontname=None)
    
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
