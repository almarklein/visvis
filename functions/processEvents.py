import visvis as vv

def processEvents():
    """ processEvents()
    Processes all GUI events (and thereby all visvis events).
    Users can periodically call this function during running 
    an algorithm to keep the figures responsove.
    
    Note that IEP and IPython with the -wthread option will 
    periodically update the GUI events when idle.
    
    Also see Figure.DrawNow()
    """
    
    app = vv.backends.currentBackend.app
    if app:
        app.ProcessEvents()
    