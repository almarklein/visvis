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

""" Module wobjects

All wobjects are inserted in this namespace, thereby providing
the user with a list of all wobjects. All wobjects are also
inserted in the root visvis namespace.

$Author: almar@SAS $
$Date: 2009-11-23 11:27:16 +0100 (Mon, 23 Nov 2009) $
$Rev: 1305 $

"""

from base import Wobject
from textRender import Text
from line import Line
from textures import Texture2D, Texture3D

class MotionDataContainer(Wobject):
    """ The motion data container is a wobject that can contain
    several data, which are displayed alternatively using a 
    timer.
    The data are simply stored as the wobject's children, and are
    made visible one at a time.
    """
    
    def __init__(self, parent, interval=100):
        Wobject.__init__(self,parent)    
        
        # setup timer        
        from events import Timer
        self._timer = Timer(self, interval, False)
        self._timer.Bind(self._Next)
        self._timer.Start()
        
        
        # counter to keep track which object was visible.
        self._counter = -1
    
    @property
    def timer(self):
        """ Get the timer object used to make the objects visible. """
        return self._timer
    
    
    def _Next(self, event):
        
        a = self.axes
        if not a:            
            return
        
        # increase counter
        self._counter += 1
        if self._counter >= len(self._children):
            self._counter = 0
        
        # set all invisible
        for child in self._children:
            child.visible = False
        # except one
        if self._children:
            self._children[self._counter].visible = True
        
        # show it!        
        a.Draw()
