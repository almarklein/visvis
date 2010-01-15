""" Close all figures. """
import visvis as vv

def closeAll():
    """ closeAll()
    Closes all figures.
    """
    
    for fig in vv.BaseFigure._figures.values():
        fig.Destroy()
