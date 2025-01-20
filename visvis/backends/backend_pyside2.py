# -*- coding: utf-8 -*-
# flake8: noqa
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

# This file is a placeholder. The backend system of visvis assumes one
# backend per module. Since the PyQt and PySide backends share almost
# all code, its nonsense to duplicate it. Instead we use these small
# placeholder modules that import qtcommon.

import visvis

# Check if qtlib is already set
if visvis.backends.qtlib not in [None, '', 'pyside2']:
    raise ImportError('Cannot import PySide2 because Qt was already loaded from "%s".' %
                        visvis.backends.qtlib)

# Set qtlib so that the qtcommon module knows how it should import Qt.
visvis.backends.qtlib = 'pyside2'

# Load backend from qtcommon
from visvis.backends.qtcommon import Figure, newFigure, App, app
