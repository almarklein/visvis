# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv

def closeAll():
    """ closeAll()
    Closes all figures.
    """
    
    for fig in vv.BaseFigure._figures.values():
        fig.Destroy()
