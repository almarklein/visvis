# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv

def clf():
    """ clf()
    Clear current figure. 
    """
    f = vv.gcf()
    f.Clear()
    return f

