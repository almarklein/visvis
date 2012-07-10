# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def draw(figure=None, fast=False):
    """ draw(figure=None, fast=False)
    
    Makes the given figure (or the current figure if None) draw itself.
    If fast is True, some wobjects can draw itself faster at reduced
    quality.
    
    """ 
    
    # Get figure
    if figure is None:
        figure = vv.gcf()
    
    # Draw!
    figure.Draw(fast)
