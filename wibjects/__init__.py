# -*- coding: utf-8 -*-
# flake8: noqa
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module wibjects

All wibjects are inserted in this namespace, thereby providing
the user with a list of all wibjects. All wibjects are also
inserted in the root visvis namespace.

"""

from visvis.core import (  Wibject, BaseFigure, AxesContainer, Axes,
                           Box, DraggableBox, Label, Legend,
                        )

from visvis.wibjects.buttons import PushButton, ToggleButton, RadioButton
from visvis.wibjects.sliders import BaseSlider, Slider, RangeSlider
from visvis.wibjects.colorWibjects import (BaseMapableEditor, Colorbar,
                                    ColormapEditor, ClimEditor)
from visvis.wibjects.title import Title
