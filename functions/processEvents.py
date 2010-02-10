import visvis as vv

def processEvents():
    """ processEvents()
    Processes all GUI events (and thereby all visvis events).
    Users can periodically call this function during running 
    an algorithm to keep the figures responsove.
    
    Note that IEP and IPython with the -wxthread option will 
    periodically update the GUI events when idle.
    
    Also see Figure.DrawNow()
    """
    
    fig = vv.gcf()
    if fig is not None:
        fig._ProcessEvents()
    