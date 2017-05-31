# -*- coding: utf-8 -*-
# flake8: noqa
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module wobjects

All wobjects are inserted in this namespace, thereby providing
the user with a list of all wobjects. All wobjects are also
inserted in the root visvis namespace.

"""

from visvis.core import (   Wobject, Line, PolarLine, Text )

from visvis.wobjects.textures import BaseTexture, Texture2D, Texture3D
from visvis.wobjects.textures import MotionTexture2D, MotionTexture3D
from visvis.wobjects.sliceTextures import SliceTexture, SliceTextureProxy
from visvis.wobjects.polygonalModeling import Mesh, OrientableMesh
from visvis.wobjects.motion import MotionDataContainer, MotionMixin, MotionSyncer
