import visvis as vv

def use(backendName=None):
    """ use(backendName=None)
    Use the specified backend and return an App instance that has a Run()
    method to enter the GUI toolkit's mainloop, and a ProcessEvents()
    method to process any GUI events.
    
    If no backend is given returns the previously selected backend. If no
    backend was yet selected, a suitable backend is selected automatically.
    
    This function is only required to explicitly choose a specific backend, 
    or to obtain the application object; when this function is not used,
    vv.figure() will select a backend automatically.
    
    Note: the backend can be changed even when figures are created with
    another backend, but this is not recommended.
    """
    return vv.backends.use(backendName)
    