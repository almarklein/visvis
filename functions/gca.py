""" Get the current axes in the current figure. """

import visvis as vv

def gca():
    """ gca() - Get the current axes in the current figure.
    """
    f = vv.gcf()
    a = f.currentAxes
    if not a:
        # create axes
        a = vv.Axes(f)
        a.cameraType = 'twod'
        #a.position = vv.Position(0.1, 0.1, -0.2, -0.2)
        a.position = vv.Position(70, 40, -100, -90)
    return a
    
    
if __name__ == '__main__':
    a = vv.gca()
    