# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv

def cla():
    """ cla()
    Clear the current axes. 
    """
    a = vv.gca()
    a.Clear()
    return a

