import visvis as vv

def getOpenGlInfo():
    """ getOpenGlInfo()
    Get information about the OpenGl version on this system. 
    Returned is a tuple (version, vendor, renderer, extensions) 
    
    A figure is created and removed to create an openGl context if
    this is necessary.
    """
    
    # Try fast
    result = vv.misc.getOpenGlInfo()
    
    # Should we open a figure and try again?
    if result[0] is None:
        f = vv.figure() 
        result = vv.misc.getOpenGlInfo()
        f.Destroy()
        f._ProcessGuiEvents() # so it can close
    
    return result
