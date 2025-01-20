# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def legend(*value, **kwargs):
    """ legend('name1', 'name2', 'name3', ..., axes=None)
    
    Can also be called with a single argument being a tuple/list of strings.
    
    Set the string labels for the legend. If no string labels are given,
    the legend wibject is hidden again.
    
    See also the Axes.legend property.
    
    """
    
    # Get axes
    axes = None
    if 'axes' in kwargs:
        axes = kwargs['axes']
    if axes is None:
        axes = vv.gca()
    
    if len(value) == 1 and isinstance(value[0], (list, tuple)):
        value = value[0]
    
    # Apply what was given
    axes.legend = value


if __name__ == '__main__':
    vv.plot([1,2,3,1])
    vv.plot([2,3,1,4],lc='r')
    vv.legend(['line one', 'line two'])
    vv.legend('line three', 'line four') # or
