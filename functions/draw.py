# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

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
