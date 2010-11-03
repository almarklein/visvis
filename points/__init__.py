""" MODULE POINTS

This is the visvis.points module. It will try to import the standalone
version of the points module, and if that fails, imports the version 
shipped with visvis.

This is done such that isinstance(object, point.Point) will always 
work as expected.

Note that this docstring is replaced with the documentation of the points
module.

"""

# Init names (which are deleted at the bottom)
mod = L = key = name = None

# Create variable to indicate what source was used
usedVisvisVersion = False

try:
    
    # Try importing the original module.
    mod = __import__('points')
    
    # Test if it really is the module we need (thanks Matt)
    for name in ['Point', 'Pointset', 'Aarray', 'Quaternion']:
        if not hasattr(mod,name):
            raise ImportError
    
except Exception:
    # Import the copy shipped with visvis
    import points as mod
    usedVisvisVersion = True


# Insert all names in *this* namespace
L = locals()
for key in mod.__dict__:
    if not key.startswith('_'):
        L[key] = mod.__dict__[key]
    
# Set docs
L['__doc__'] = mod.__doc__

# Clean up any variables we created
del mod, L, key, name
