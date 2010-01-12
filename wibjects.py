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

""" Module wibjects

All wibjects are inserted in this namespace, thereby providing
the user with a list of all wibjects. All wibjects are also
inserted in the root visvis namespace.

$Author$
$Date$
$Rev$

"""

from base import Wibject, Box
from textRender import Label
from core import Axes, BaseFigure, Axis
from simpleWibjects import PushButton, ToggleButton, RadioButton, DraggableBox
from cm import Colorbar, ColormapEditor

class Title(Label):
    def __init__(self, axes, text):
        Label.__init__(self, axes, text)
        
        # set textsize and align
        self.halign = 0
        self.fontSize = 12
        
        # set back color to be transparant
        self.bgcolor = ''
        
        # set position
        self.position = 0, -20, 1, 15
        
        # correct axes' position
        dy = -20        
        axes.position.Correct(0, -dy, 0, dy) 
    
    
    def OnDestroy(self):
        Label.OnDestroy(self)
        
        # correct axes' position
        axes = self.parent
        if axes:
            dy = 20
            axes.position.Correct(0, -dy, 0, dy) 

class Polygon:
    """ A generic polygon. 
    """
    pass

