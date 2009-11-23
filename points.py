""" MODULE POINTS
This is the visvis.points module. It will try to import the original
points module, and if that fails, imports the version shipped with
visvis.
This is done such that isinstance(object, point.Point) will always 
work as expected.
"""

try:
    # try importing the original module.
    mod = __import__('points')
    # insert in the namespace
    g = globals()
    for key in mod.__dict__:
        g[key] = mod.__dict__[key]
    # clean up
    del mod
    del g

except Exception:
    # import the visvis' version
    from points_copy import *

    