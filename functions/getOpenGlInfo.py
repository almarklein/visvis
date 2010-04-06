import visvis as vv

def getOpenGlInfo():
    """ getOpenGlInfo()
    Get information about the OpenGl version on this system. 
    Returned is a tuple (version, vendor, renderer, extensions) 
    
    A figure is created and removed to create an openGl context if
    this is necessary.
    """
    
    # Open figure first. On Windows we can try obtaining the information,
    # but I found that on Ubuntu a segfault will happen (but this might
    # very well have to do with the OpenGl drivers).
    fig = vv.figure()
    result = vv.misc.getOpenGlInfo()
    
    # Should we open a figure and try again?    
    fig.Destroy()
    fig._ProcessGuiEvents() # so it can close
    
    return result
