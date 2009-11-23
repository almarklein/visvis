""" Clear the current axes. """

import visvis as vv

def cla():
    """ cla() - Clear current axes. """
    a = vv.gca()
    a.Clear()
    return a

