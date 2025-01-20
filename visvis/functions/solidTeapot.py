# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

# About the vertex data ...
# The teapot model is a well-known and often used geometric model
# originally based on Bezier patches.


def solidTeapot(translation=None, scaling=None, direction=None, rotation=None,
                    axesAdjust=True, axes=None):
    """ solidTeapot(
            translation=None, scaling=None, direction=None, rotation=None,
            axesAdjust=True, axes=None)
    
    Create a model of a teapot (a teapotahedron) with its bottom at the
    origin. Returns an OrientableMesh instance.
    
    Parameters
    ----------
    Note that translation, scaling, and direction can also be given
    using a Point instance.
    translation : (dx, dy, dz), optional
        The translation in world units of the created world object.
    scaling: (sx, sy, sz), optional
        The scaling in world units of the created world object.
    direction: (nx, ny, nz), optional
        Normal vector that indicates the direction of the created world object.
    rotation: scalar, optional
        The anle (in degrees) to rotate the created world object around its
        direction vector.
    axesAdjust : bool
        If True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet,
        it is set to False.
    axes : Axes instance
        Display the bars in the given axes, or the current axes if not given.
    
    """
    
    # Load mesh data
    bm = vv.meshRead('teapot.ssdf')
    
    # Use current axes?
    if axes is None:
        axes = vv.gca()
    
    # Create Mesh object
    m = vv.OrientableMesh(axes, bm)
    #
    if translation is not None:
        m.translation = translation
    if scaling is not None:
        m.scaling = scaling
    if direction is not None:
        m.direction = direction
    if rotation is not None:
        m.rotation = rotation
    
    # Adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = False
        axes.cameraType = '3d'
        axes.SetLimits()
    
    # Done
    axes.Draw()
    return m


if __name__ == '__main__':
    m = vv.solidTeapot(direction=(0.1, 0.2, 1))
    m.faceShading = 'toon' # Let's try the 'toon' shader for a change!
