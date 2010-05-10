# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv

def gca():
    """ gca() 
    Get the current axes in the current figure.
    """
    f = vv.gcf()
    a = f.currentAxes
    if not a:
        # create axes
        a = vv.Axes(f)
        #a.position = 2, 2, -4, -4
        a.position = 10, 10, -20, -20
    return a
    
    
if __name__ == '__main__':
    a = vv.gca()
    