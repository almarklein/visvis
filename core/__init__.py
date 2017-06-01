# -*- coding: utf-8 -*-
# flake8: noqa
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Subpackage core

The core of visvis. Defines the core classes of visvis (such as Wibject
and Wobject), and the core visualization system (such as the BaseFigure
and Axes classes, and auxiliary classes).

Notes for developers
--------------------
In this __init__ of this class, all classes that we want to expose to
the user are imported. In the root __init__ of visvis, we do an "import *",
such that all these classes are inserted in the main visvis namespace.
Note that the modules in this package are also insertect in the root
namespace. This is ok, since it makes it easier for people to access
the deeper functionality of visvis if they want to.
("Flat is better than nested")

"""


## The primary core

# Import everything that we want to expose to the user
from visvis.core.constants import *
from visvis.core.misc import (Range, settings,
        Transform_Base, Transform_Translate, Transform_Rotate, Transform_Scale)
from visvis.core.events import Timer
from visvis.core.base import BaseObject, Wibject, Wobject, Position
from visvis.core.baseTexture import TextureObject, Colormap, Colormapable
from visvis.core.shaders import GlslProgram

## The secondary core (contains important wibjects and wobjects)

# Import everything that we want to expose to the user
from visvis.core.orientation import OrientationForWobjects_mixClass
from visvis.core.cameras import TwoDCamera, ThreeDCamera, FlyCamera
from visvis.core.light import Light

# Also imported by wobjects and wibjects subpackages
from visvis.core.axes import AxesContainer, Axes, Legend
from visvis.core.baseFigure import BaseFigure
from visvis.core.line import Line, PolarLine
from visvis.core.baseWibjects import Box, DraggableBox
from visvis.text import Text, Label
