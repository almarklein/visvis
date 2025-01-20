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
    
    This function is now more or less deprecated; visvis is designed to
    invoke a draw whenever necessary.
    
    """
    
    # Get figure
    if figure is None:
        figure = vv.gcf()
    
    # Draw!
    figure.Draw(fast)


if __name__ == '__main__':
    import time
    fig = vv.figure()
    l = vv.plot([1,2,3,1,4])
    for i in range(20):
        l.SetYdata([1+i/10.0, 2,3,1,4])
        vv.draw(fig) # Note: not even necessary
        vv.processEvents()
        time.sleep(0.1)
