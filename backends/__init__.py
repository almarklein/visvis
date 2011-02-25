# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Package visvis.backends

Visvis allows multiple backends. I tried to make implementing a 
backend as easy as possible. Each backend is defined in a single
module called "backend_xx.py", where xx is the backend name, which 
we recommend making all lowercase.

This module should ...
1.  ... contain a class called "Figure" (inherited from visvis.BaseFigure). 
    The Figure class should wrap (not inherit from) a widget native to 
    the backend, in which visvis can draw with OpenGl. The Figure class 
    should also overload a number of functions (such as _SwapBuffers()).    
2.  ... contain a function called "newFigure". This function should generate 
    a window with a single Figure widget in it, and return the Figure 
    Object.
3.  Contain a class called "App" (inherited from visvis.events.App) that
    implements a method "Run" that enters the GUI toolkit's mainloop, and
    a method "ProcessEvents" that processes the GUI toolkits events.
4.  ... call visvis.Timer._TestAllTimers() on a regular basis (every 10 ms
    or so). To enable timer events.
5.  ... pass through the events enter, leaver, keydown, keyup, resize, close
    via visvis' event system. Pass through events mouseDown, mouseUp, 
    mouseDoubleClick, mouseMove via the figure's _GenerateMouseEvent() method,
    that will fire the events of the appropriate wibjects and wobjects.

The BaseFigure class is defined in visvis.core.baseFigure. In the comments it is
shown what methods need to be overloaded and what events need to be
transfered. There is a wiki page on implementing a backend, and a text
file in the source. Also look at the already implemented backends!

The backend is chosen/selected as follows:
- A user can call vv.use() to load a specific backend and obtain an 
  App instance.
- When a figure is created it is checked whether a backend is already
  selected. If not, one is selected automatically; it tries loading the
  backends in the order that is defined in the variable "backendOrder" 
  in this file. 



"""

# An overview:
# - testLoaded tests to see whether any of the backends is already loaded
# - _loadBackend imports the backend and sets newFigure and app
# - use is the user friendly function that calls _loadBackend

import os, sys
import imp
import visvis
from visvis.core.misc import isFrozen

# The order in which to try loading a backend
backendOrder = ['qt4', 'wx', 'gtk', 'fltk'] # I'd love to put tk in this list


# Establish preference based on loaded backends modules
# In this way, in an interactive interpreter the right backend is picked
backendMap = {'qt4':'PyQt4', 'wx':'wx', 'gtk':'gtk', 'fltk':'fltk'}
for be in [be for be in reversed(backendOrder)]:
    # Determine backend module name
    modName = backendMap[be]
    # If loaded, move up front
    if modName in sys.modules:
        backendOrder.remove(be)
        backendOrder.insert(0,be)


# Placeholder
class BackendDescription:
    def __init__(self):
        self.name = ''
        self.newFigure = None
        self.app = None
currentBackend = BackendDescription()

# Set __file__ absolute when loading
__file__ = os.path.abspath(__file__)

def testLoaded():
    """ Tests to see whether a backend is already loaded.
    Returns the name of the loaded backend, or an empty
    string if nothing is loaded.
    If visvis is part of a frozen app, returns "" always.
    """
    
    if isFrozen():
        return "" 
    
    else:
        
        # see which backends we have
        path = __file__
        path = os.path.dirname( path )
        files = os.listdir(path)
        
        for filename in files:
            if filename.startswith('__'):
                continue
            if not filename.endswith('.py'):
                continue
            be = filename[:-3]
            modNameFull = 'visvis.backends.' + be
            if sys.modules.has_key(modNameFull):
                i = be.find('_')
                return be[i+1:]
        # nothing found...
        return ''


def _loadBackend(name):
    """ Load the backend with the specified name.
    Returns True on success and False otherwise.
    """
    
    # Get module names
    modName = 'backend_' + name
    modNameFull = 'visvis.backends.backend_'+name
    modFileName = os.path.join(os.path.dirname(__file__), modName+'.py')
    
    # Test whether to use the pyc version
    load_module = imp.load_source    
    if not os.path.isfile(modFileName):
        modFileName += "c" # Probably a frozen app
    
    # Try importing the backend toolkit
    try:
        modNameTk = backendMap[name]
        __import__(modNameTk)
    except ImportError:
        return False
    
    # Try importing the visvis backend module
    try:
        if modFileName.endswith('.pyc'):
            module = __import__(modNameFull, fromlist=[modName])
        else:
            module = imp.load_source(modNameFull, modFileName)
        globals()[modName] = module
    except Exception, why:
        if not isFrozen():
            # Only show if not frozen. If frozen, it can easily happen that
            # the GUI toolkit is available, but the visvis backend is not.
            print 'Error importing %s backend:' % name, why
        return False
    
    # Do some tests
    if not hasattr(module,'newFigure'):
        raise Exception("Backend %s does not implement newFigure!" % be)
    elif not hasattr(module,'Figure'):
        raise Exception("Backend %s does not implement Figure class!" % be)
    else:
        # All good (as far as I can tell). Update stuff if name does not match.
        if currentBackend.name != name:
            currentBackend.name = name
            currentBackend.newFigure = module.newFigure
            currentBackend.app = module.app
        return True


def use(backendName=None):
    """ use(backendName=None)
    
    Use the specified backend and return an App instance that has a run()
    method to enter the GUI toolkit's mainloop.
    
    If no backend is given, a suitable backend is tried automatically. 
    
    """
    
    # Make case insensitive and check
    if backendName:
        backendName = backendName.lower()    
        if backendName not in backendOrder:
            raise RuntimeError('Invalid backend name given: "%s".'%backendName)
    
    # Get name of the backend currently loaded (can be '')            
    loadedName = testLoaded()
    
    # Prevent resetting the backend to use
    if loadedName and backendName and loadedName != backendName:
        print "Warning: changing backend while %s already loaded." % loadedName
        #raise RuntimeError("Cannot change backend, %s already loaded." % loadedName)
    
    # Process
    if backendName:
        # Use given
        if not _loadBackend(backendName):
            tmp = backendName
            tmp = os.path.join(os.path.dirname(__file__), backendName+'.xxx')
            raise RuntimeError('Given backend "%s" could not be loaded.' % tmp)
    elif loadedName:
        # Use loaded (redo to make sure the placeholder is ok)
        if not _loadBackend(loadedName):
            raise RuntimeError('Could not reload backend "%s".' % loadedName)
    else:
        # Try any backend        
        for name in backendOrder:
            if _loadBackend(name):
                break
        else:
            tmp = "Install PyQt4, wxPython, or fltk."
            raise RuntimeError("None of the backends could be loaded. "+tmp)
    
    # Return instance
    return currentBackend.app

