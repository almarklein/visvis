# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def axis(command, axes=None):
    """ axis(command, axes=None)
    
    Convenience function to set axis properties. Note that all functionality
    can also be applied via the properties of the Axis object.
    
    Parameters
    ----------
    command : string
        The setting command to apply. See below.
    axes : Axes instance
        The axes to apply the setting to. Uses the current axes by default.
    
    Possible string commands
    ------------------------
      * off: hide the axis (Axes.axis.visible = False)
      * on: show the axis (Axes.axis.visible = True)
      * equal: make a circle be displayed circular (Axes.daspectAuto = False)
      * auto: change the range for each dimension indepdently (Axes.daspectAuto = True)
      * tight: show all data (Axes.SetLimits())
      * ij: flip the y-axis (make second element of Axes.daspect negative)
      * xy: (make all elements of Axes.daspect positive)
    If you want to set an Axes' limits, use Axes.SetLimits(xlim, ylim, zlim).
    
    """
    
    # Get axes
    if axes is None:
        axes = vv.gca()
    
    if command == 'off':
        axes.axis.visible = 0
    elif command == 'on':
        axes.axis.visible = 1
    elif command == 'equal':
        axes.daspectAuto = 0
    elif command == 'auto':
        axes.daspectAuto = 1
    elif command == 'tight':
        axes.SetLimits()
    elif command == 'ij':
        da = [abs(tmp) for tmp in axes.daspect]
        axes.daspect = da[0], -abs(da[1]), da[2]
    elif command == 'xy':
        da = [abs(tmp) for tmp in axes.daspect]
        axes.daspect = da[0], abs(da[1]), da[2]
    else:
        raise ValueError('Unknown command in vv.axis().')


if __name__ == '__main__':
    l = vv.plot([1,2,3,1,4,0])
    vv.axis('off')
