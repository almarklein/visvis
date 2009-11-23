#   This file is part of VISVIS.
#    
#   VISVIS is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as 
#   published by the Free Software Foundation, either version 3 of 
#   the License, or (at your option) any later version.
# 
#   VISVIS is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
# 
#   You should have received a copy of the GNU Lesser General Public 
#   License along with this program.  If not, see 
#   <http://www.gnu.org/licenses/>.
#
#   Copyright (C) 2009 Almar Klein

""" Package visvis.backends

Visvis allows multiple backends. We try to make implementing a 
backend as easy as possible. Each backend is defined in a single
module called "backend_xx.py", where xx is the backend name, which 
we recommend making all lowercase.

This module should:
1.  Contain a class called "Figure" (inherited from visvis.BaseFigure). 
    The Figure class should wrap (not inherit from) a widget native to 
    the backend. 
    The Figure class should implement BaseFigure and overload a number
    of functions. .Draw() should be called on a paint request. When
    the widget is closed, it should also be destroyed and call ._Destroy(). 
2.  Contain a function called "newFigure". This function should generate 
    a window with a single Figure widget in it, and return the Figure 
    Object.
3.  Call visvis.Timer._TestAllTimers() on a regular basis (every 10 ms or
    so). To enable timer events.
4.  Pass through the events enter, leaver, keydown, keyup, resize, close via
    visvis event system. Pass through events mouseDown, mouseUp, 
    mouseDoubleClick, mouseMove via the figure's _GenerateMouseEvent() method,
    that will fire the events of the appropriate wibjects and wobjects.

The BaseFigure class is defined in visvis.core. In the comments it is
shown what methods need to be overloaded and what events need to be
transfered. Also look at the already implemented backends!

The backend is chosen/selected as follows:
- Just before the first figure is created visvis checks which
  backends are available. 
- If one of them is already loaded, that one is used. If not, it 
  will try loading backends in the order that is defined in the
  variable "backendOrder" in this file. 
- By calling visvis.backends.use(), the "backendOrder" variable
  is set to contain only the specified backend.

The appropriate backend is thus automatically determined. Or chosen
in two ways:
import visvis as vv
vv.use('wx')
or,
app = vv.App('wx')

$Author$
$Date$
$Rev$

"""

import os, sys
from visvis.misc import isFrozen

# The order in which to try loading a backend
backendOrder = ['qt4','wx','fltk', 'tk']

# placeholders
newFigure = []
appClass = []

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
        path = os.path.dirname( os.path.abspath(path) )
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


def loadBackend():
    """ Load a backend. and set the newFigure to the appropriate
    function. If a backend is already loaded, will use that one...
    """
    
    be = testLoaded()
    
    if be:
        # already loaded
        modNameFull = 'visvis.backends.backend_'+be
        module = sys.modules[modNameFull]
    
    else:
        
        # try loading backends in the right order
        module = None    
        for be in backendOrder:
            modName = 'backend_' + be
            modNameFull = 'visvis.backends.backend_'+be
            # try importing the backend
            try:
                module = __import__(modNameFull, fromlist=[modName])
            except ImportError, why:
                #print "Skipping backend %s: %s" % (be, why)
                continue
            # if ok, use it!
            break

    # do some tests
    if not module:
        raise Exception("No suitable backend found!")
    elif not hasattr(module,'newFigure'):
        raise Exception("Backend %s does not implement newFigure!" % be)
    elif not hasattr(module,'Figure'):
        raise Exception("Backend %s does not implement Figure class!" % be)
    else:
        # all good (as far as I can tell)
        # set newFigure function!
        while(len(newFigure)):
            newFigure.pop()      
        newFigure.append( module.newFigure )
        appClass.append( module.App )


def App(backendName):
    """ App(backendName)
    
    Factory function that returns an application object.
    This object wraps the application instance of the selected
    backend, and has a 'run' method, which starts the backend's
    main loop.
    
    The selected backend is then the backend that visvis will 
    use from now, and cannot be changed. 
    """
    
    # make case insensitive
    backendName = backendName.lower()
    
    # check name
    if backendName not in backendOrder:
        raise RuntimeError('Invalid backend name given.')
    
    # check if a backend was already loaded
    be = testLoaded()
    if be and be != backendName:
        raise RuntimeError("Cannont change backend, %s already loaded." % be)
    
    # ok, put chosen backendname in front
    while backendName in backendOrder:
        backendOrder.remove(backendName)
    backendOrder.insert(0,backendName)
    
    # load it and check
    loadBackend()
    name2 = testLoaded()
    if not name2 and not isFrozen():
        print 'Warning: no backend could be loaded. Install PyQt4 or wxPython' 
    elif testLoaded() != backendName:
        print 'warning, could not load requested backend, loaded %s instead' % name2
    
    # return instance
    App = appClass[0]
    return App()


def use(backendName):
    """ Function to let the user explicitly choose a 
    backend. Can only be used if no figures have been
    created. Same as App.
    """
    return App(backendName)
