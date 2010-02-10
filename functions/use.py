import visvis as vv

def use(backendName=None):
    """ use(backendName=None)
    Use the specified backend and return an App instance that has a run()
    method to enter the GUI toolkit's mainloop.
    
    If no backend is given, a suitable backend is tried automatically. 
    
    Normally, this function is only required to explicitly choose a 
    specific backend, or to obtain the application object.
    
    The backend can be changed even when figures are created with
    another backend, but this is not recommended.
    """
    return vv.backends.use(backendName)
    