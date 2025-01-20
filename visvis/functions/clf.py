# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def clf():
    """ clf()
    
    Clear current figure.
    
    """
    f = vv.gcf()
    f.Clear()
    return f


if __name__ == '__main__':
    # Show plot
    vv.plot([1,2,3,1,4])
    # Clear the whole figure
    vv.clf()
