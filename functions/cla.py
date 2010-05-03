import visvis as vv

def cla():
    """ cla()
    Clear the current axes. 
    """
    a = vv.gca()
    a.Clear()
    return a

