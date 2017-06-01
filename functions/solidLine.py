# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
from visvis.utils.pypoints import Pointset, is_Pointset
from visvis.processing import lineToMesh

def solidLine(pp, radius=1.0, N=16, axesAdjust=True, axes=None):
    """ solidLine(pp, radius=1.0, N=16, axesAdjust=True, axes=None)
    
    Creates a solid line in 3D space.
    
    Parameters
    ----------
    Note that translation, scaling, and direction can also be given
    using a Point instance.
    pp : Pointset
        The sequence of points of which the line consists.
    radius : scalar or sequence
        The radius of the line to create. If a sequence if given, it
        specifies the radius for each point in pp.
    N : int
        The number of subdivisions around its centerline. If smaller
        than 8, flat shading is used instead of smooth shading.
    axesAdjust : bool
        If True, this function will call axes.SetLimits(), and set
        the camera type to 3D. If daspectAuto has not been set yet,
        it is set to False.
    axes : Axes instance
        Display the bars in the given axes, or the current axes if not given.
    
    """
    
    # Check first argument
    if is_Pointset(pp):
        pass
    else:
        raise ValueError('solidLine() needs a Pointset or list of pointsets.')
    
    # Obtain mesh and make a visualization mesh
    baseMesh = lineToMesh(pp, radius, N)
    
    
    ## Visualize
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    # Create mesh object
    m = vv.Mesh(axes, baseMesh)
    
    # Adjust axes
    if axesAdjust:
        if axes.daspectAuto is None:
            axes.daspectAuto = False
        axes.cameraType = '3d'
        axes.SetLimits()
    
    # Return
    axes.Draw()
    return m
    
    
    
if __name__ == '__main__':
    # Create series of points
    pp = Pointset(3)
    pp.append(0,1,0)
    pp.append(3,2,1)
    pp.append(4,5,2)
    pp.append(2,3,1)
    pp.append(0,4,0)
    #pp.append(0,1,0) # Circular
    # Make a surface-line with varying diameter
    m = vv.solidLine(pp, [0.1, 0.2, 0.3, 0.1, 0.2], 8)
