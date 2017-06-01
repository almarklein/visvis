# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def cla():
    """ cla()
    
    Clear the current axes.
    
    """
    a = vv.gca()
    a.Clear()
    return a


if __name__ == '__main__':
    # Show plot
    vv.plot([1,2,3,1,4])
    # Clear the plot
    vv.cla()
