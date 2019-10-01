# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module misc

Various things are defined here that did not fit nicely in any
other module.

This module is also meant to be imported by many
other visvis modules, and therefore should not depend on other
visvis modules.

"""

import os
import sys
import zipfile

import numpy as np
import OpenGL.GL as gl

from visvis.utils import ssdf
from visvis.utils.pypoints import getExceptionInstance  # noqa


V2 = sys.version_info[0] == 2
if V2:
    unichr = unichr  # noqa
    basestring = basestring  # noqa
else:
    basestring = str
    unichr = chr


# Used to load resources when in a zipfile
def splitPathInZip(path):
    """ splitPathInZip(path)
    Split a filename in two parts: the path to a zipfile, and the path
    within the zipfile. If the given path is a native file or direcory,
    returns ('', path). Raises an error if no valid zipfile can be found.
    """
    ori_path = path
    if os.path.exists(path):
        return '', path
    # Split path in parts
    zipPath = []
    while True:
        path, sub = os.path.split(path)
        if not sub:
            raise RuntimeError('Not a real path nor in a zipfile: "%s"' % ori_path)
        zipPath.insert(0, sub)
        if os.path.isfile(path):
            if zipfile.is_zipfile(path):
                return path, os.path.join(*zipPath)
            else:
                raise RuntimeError('Not a zipfile: "%s"' % ori_path)
    


## For info about OpenGL version


# To store openGl info
_glInfo = [None]*4


def ensureString(s):
    if isinstance(s, str):
        return s
    else:
        return s.decode('ascii')

def getOpenGlInfo():
    """ getOpenGlInfo()
    
    Get information about the OpenGl version on this system.
    Returned is a tuple (version, vendor, renderer, extensions)
    Note that this function will return 4 Nones if the openGl
    context is not set.
    
    """
    
    if gl.glGetString(gl.GL_VERSION) is None:
        raise RuntimeError('There is currently no OpenGL context')
    
    if not _glInfo[0]:
        _glInfo[0] = ensureString(gl.glGetString(gl.GL_VERSION))
        _glInfo[1] = ensureString(gl.glGetString(gl.GL_VENDOR))
        _glInfo[2] = ensureString(gl.glGetString(gl.GL_RENDERER))
        _glInfo[3] = ensureString(gl.glGetString(gl.GL_EXTENSIONS))
    return tuple(_glInfo)

_glLimitations = {}
def getOpenGlCapable(version, what=None):
    """ getOpenGlCapable(version, what)
    
    Returns True if the OpenGl version on this system is equal or higher
    than the one specified and False otherwise.
    
    If False, will display a message to inform the user, but only the first
    time that this limitation occurs (identified by the second argument).
    
    """
    
    # obtain version of system
    curVersion = _glInfo[0]
    if not curVersion:
        curVersion, dum1, dum2, dum3 = getOpenGlInfo()
        if not curVersion:
            return False # OpenGl context not set, better safe than sory
    
    # make sure version is a string
    if isinstance(version, (int,float)):
        version = str(version)
    
    # test
    if curVersion >= version :
        return True
    else:
        # show message?
        if what and (what not in _glLimitations):
            _glLimitations[what] = True
            tmp = "Warning: the OpenGl version on this system is too low "
            tmp += "to support " + what + ". "
            tmp += "Try updating your drivers or buy a new video card."
            print(tmp)
        return False


## Decorators


def Property(function):
    """ Property(function)
    
    A property decorator which allows to define fget, fset and fdel
    inside the function.
    
    Note that the class to which this is applied must inherit from object!
    Code based on an example posted by Walker Hale:
    http://code.activestate.com/recipes/410698/#c6
    
    Example
    -------
    
    class Example(object):
        @Property
        def myattr():
            ''' This is the doc string.
            '''
            def fget(self):
                return self._value
            def fset(self, value):
                self._value = value
            def fdel(self):
                del self._value
            return locals()
    
    """
    
    # Define known keys
    known_keys = 'fget', 'fset', 'fdel', 'doc'
    
    # Get elements for defining the property. This should return a dict
    func_locals = function()
    if not isinstance(func_locals, dict):
        raise RuntimeError('Property function should "return locals()".')
    
    # Create dict with kwargs for property(). Init doc with docstring.
    D = {'doc': function.__doc__}
    
    # Copy known keys. Check if there are invalid keys
    for key in list(func_locals.keys()):
        if key in known_keys:
            D[key] = func_locals[key]
        else:
            raise RuntimeError('Invalid Property element: %s' % key)
    
    # Done
    return property(**D)


def PropWithDraw(function):
    """ PropWithDraw(function)
    
    A property decorator which allows to define fget, fset and fdel
    inside the function.
    
    Same as Property, but calls self.Draw() when using fset.
    
    """
    
    # Define known keys
    known_keys = 'fget', 'fset', 'fdel', 'doc'
    
    # Get elements for defining the property. This should return a dict
    func_locals = function()
    if not isinstance(func_locals, dict):
        raise RuntimeError('Property function should "return locals()".')
    
    # Create dict with kwargs for property(). Init doc with docstring.
    D = {'doc': function.__doc__}
    
    # Copy known keys. Check if there are invalid keys
    for key in list(func_locals.keys()):
        if key in known_keys:
            D[key] = func_locals[key]
        else:
            raise RuntimeError('Invalid Property element: %s' % key)
    
    # Replace fset
    fset = D.get('fset', None)
    def fsetWithDraw(self, *args):
        fset(self, *args)
        if hasattr(self, 'Draw'):
            self.Draw()
        #print(fset._propname, self, time.time())
    if fset:
        fset._propname = function.__name__
        D['fset'] = fsetWithDraw
    
    # Done
    return property(**D)
    

def DrawAfter(function):
    """ DrawAfter(function)
    
    Decorator for methods that make self.Draw() be called right after
    the function is called.
    
    """
    def newFunc(self, *args, **kwargs):
        retval = function(self, *args, **kwargs)
        if hasattr(self, 'Draw'):
            self.Draw()
        return retval
    newFunc.__doc__ = function.__doc__
    return newFunc


def PropertyForSettings(function):
    """ PropertyForSettings(function)
    
    A property decorator that also supplies the function name to the
    fget and fset function. The fset method also calls _Save()
    
    """
    
    # Define known keys
    known_keys = 'fget', 'fset', 'fdel', 'doc'
    
    # Get elements for defining the property. This should return a dict
    func_locals = function()
    if not isinstance(func_locals, dict):
        raise RuntimeError('From visvis version 1.6, Property function should "return locals()".')
    
    # Create dict with kwargs for property(). Init doc with docstring.
    D = {'doc': function.__doc__}
    
    # Copy known keys. Check if there are invalid keys
    for key in list(func_locals.keys()):
        if key in known_keys:
            D[key] = func_locals[key]
        else:
            raise RuntimeError('Invalid Property element: %s' % key)
    
    # Replace fset and fget
    fset = D.get('fset', None)
    fget = D.get('fget', None)
    def fsetWithKey(self, *args):
        fset(self, function.__name__, *args)
        self._Save()
    def fgetWithKey(self, *args):
        return fget(self, function.__name__)
    if fset:
        D['fset'] = fsetWithKey
    if fget:
        D['fget'] = fgetWithKey
    
    # Done
    return property(**D)


## The range class


class Range(object):
    """ Range(min=0, max=0)
    
    Represents a range (a minimum and a maximum ). Can also be instantiated
    using a tuple.
    
    If max is set smaller than min, the min and max are flipped.
    
    """
    def __init__(self, min=0, max=1):
        self.Set(min,max)
    
    def Set(self, min=0, max=1):
        """ Set the values of min and max with one call.
        Same signature as constructor.
        """
        if isinstance(min, Range):
            min, max = min.min, min.max
        elif isinstance(min, (tuple,list)):
            min, max = min[0], min[1]
        self._min = float(min)
        self._max = float(max)
        self._Check()
    
    @property
    def range(self):
        return self._max - self._min
    
    @Property # visvis.Property
    def min():
        """ Get/Set the minimum value of the range. """
        def fget(self):
            return self._min
        def fset(self,value):
            self._min = float(value)
            self._Check()
        return locals()
    
    @Property # visvis.Property
    def max():
        """ Get/Set the maximum value of the range. """
        def fget(self):
            return self._max
        def fset(self,value):
            self._max = float(value)
            self._Check()
        return locals()
    
    def _Check(self):
        """ Flip min and max if order is wrong. """
        if self._min > self._max:
            self._max, self._min = self._min, self._max
    
    def Copy(self):
        return Range(self.min, self.max)
        
    def __repr__(self):
        return "<Range %1.2f to %1.2f>" % (self.min, self.max)


## Transform classes for wobjects
    
    
class Transform_Base(object):
    """ Transform_Base
    
    Base transform object.
    Inherited by classes for translation, scale and rotation.
    
    """
    pass
    
class Transform_Translate(Transform_Base):
    """ Transform_Translate(dx=0.0, dy=0.0, dz=0.0)
    
    Translates the wobject.
    
    """
    def __init__(self, dx=0.0, dy=0.0, dz=0.0):
        self.dx = dx
        self.dy = dy
        self.dz = dz

class Transform_Scale(Transform_Base):
    """ Transform_Scale(sx=1.0, sy=1.0, sz=1.0)
    
    Scales the wobject.
    
    """
    def __init__(self, sx=1.0, sy=1.0, sz=1.0):
        self.sx = sx
        self.sy = sy
        self.sz = sz

class Transform_Rotate(Transform_Base):
    """ Transform_Rotate( angle=0.0, ax=0, ay=0, az=1, angleInRadians=None)
    
    Rotates the wobject. Angle is in degrees.
    Use angleInRadians to specify the angle in radians,
    which is then converted in degrees.
    """
    def __init__(self, angle=0.0, ax=0, ay=0, az=1, angleInRadians=None):
        if angleInRadians is not None:
            angle = angleInRadians * 180 / np.pi
        self.angle = angle
        self.ax = ax
        self.ay = ay
        self.az = az

## Colour stuff

# Define named colors
colorDict = {}
colorDict['black']  = colorDict['k'] = (0,0,0)
colorDict['white']  = colorDict['w'] = (1,1,1)
colorDict['red']    = colorDict['r'] = (1,0,0)
colorDict['green']  = colorDict['g'] = (0,1,0)
colorDict['blue']   = colorDict['b'] = (0,0,1)
colorDict['cyan']   = colorDict['c'] = (0,1,1)
colorDict['yellow'] = colorDict['y'] = (1,1,0)
colorDict['magenta']= colorDict['m'] = (1,0,1)

def getColor(value, descr='getColor'):
    """ getColor(value, descr='getColor')
    
    Make sure a value is a color. If a character is given, returns the color
    as a tuple.
    
    """
    tmp = ""
    if not value:
        value = None
    elif isinstance(value, basestring):
        if value not in colorDict:
            tmp = "string color must be one of 'rgbycmkw' !"
        else:
            value = colorDict[value]
    elif isinstance(value, (list, tuple)):
        if len(value) != 3:
            tmp = "tuple color must be length 3!"
        value = tuple(value)
    else:
        tmp = "color must be a three element tuple or a character!"
    # error or ok?
    if tmp:
        raise ValueError("Error in %s: %s" % (descr, tmp) )
    return value


## More functions ...

def isFrozen():
    """ isFrozen
    
    Returns whether this is a frozen application
    (using bbfreeze or py2exe). From pyzolib.paths.py
    
    """
    return bool( getattr(sys, 'frozen', None) )


# todo: cx_Freeze and friends should provide a mechanism to store
# resources automatically ...
def getResourceDir():
    """ getResourceDir()
    
    Get the directory to the visvis resources.
    
    """
    if isFrozen():
        # See application_dir() in pyzolib/paths.py
        path =  os.path.abspath(os.path.dirname(sys.path[0]))
    else:
        path = os.path.abspath( os.path.dirname(__file__) )
        path = os.path.split(path)[0]
    return os.path.join(path, 'visvisResources')


# From pyzolib/paths.py
import os, sys  # noqa
def appdata_dir(appname=None, roaming=False, macAsLinux=False):
    """ appdata_dir(appname=None, roaming=False,  macAsLinux=False)
    Get the path to the application directory, where applications are allowed
    to write user specific files (e.g. configurations). For non-user specific
    data, consider using common_appdata_dir().
    If appname is given, a subdir is appended (and created if necessary).
    If roaming is True, will prefer a roaming directory (Windows Vista/7).
    If macAsLinux is True, will return the Linux-like location on Mac.
    """
    
    # Define default user directory
    userDir = os.path.expanduser('~')
    
    # Get system app data dir
    path = None
    if sys.platform.startswith('win'):
        path1, path2 = os.getenv('LOCALAPPDATA'), os.getenv('APPDATA')
        path = (path2 or path1) if roaming else (path1 or path2)
    elif sys.platform.startswith('darwin') and not macAsLinux:
        path = os.path.join(userDir, 'Library', 'Application Support')
    # On Linux and as fallback
    if not (path and os.path.isdir(path)):
        path = userDir
    
    # Maybe we should store things local to the executable (in case of a
    # portable distro or a frozen application that wants to be portable)
    prefix = sys.prefix
    if getattr(sys, 'frozen', None): # See application_dir() function
        prefix = os.path.abspath(os.path.dirname(sys.path[0]))
    for reldir in ('settings', '../settings'):
        localpath = os.path.abspath(os.path.join(prefix, reldir))
        if os.path.isdir(localpath):
            try:
                open(os.path.join(localpath, 'test.write'), 'wb').close()
                os.remove(os.path.join(localpath, 'test.write'))
            except IOError:
                pass # We cannot write in this directory
            else:
                path = localpath
                break
    
    # Get path specific for this app
    if appname:
        if path == userDir:
            appname = '.' + appname.lstrip('.') # Make it a hidden directory
        path = os.path.join(path, appname)
        if not os.path.isdir(path):
            os.mkdir(path)
    
    # Done
    return path


class Settings(object):
    """ Global settings object.
    
    This object can be used to set the visvis settings in an easy way
    from the Python interpreter.
    
    The settings are stored in a file in the user directory (the filename
    can be obtained using the _fname attribute).
    
    Note that some settings require visvis to restart.
    
    """
    def __init__(self):
        
        # Define settings file name
        self._fname = os.path.join(appdata_dir('visvis'), 'config.ssdf')
        
        # Init settings
        self._s = ssdf.new()
        
        # Load settings if we can
        if os.path.exists(self._fname):
            try:
                self._s = ssdf.load(self._fname)
            except Exception:
                pass
        
        # Update any missing settings to their defaults
        for key in dir(self):
            if key.startswith('_'):
                continue
            self._s[key] = getattr(self, key)
        
        # Save now so the config file contains all settings
        self._Save()
    
    def _Save(self):
        try:
            ssdf.save(self._fname, self._s)
        except IOError:
            pass # Maybe an installed frozen application (no write-rights)
    
    @PropertyForSettings
    def preferredBackend():
        """ The preferred backend GUI toolkit to use
        ('pyside', 'pyqt4', 'wx', 'gtk', 'fltk').
          * If the selected backend is not available, another one is selected.
          * If preferAlreadyLoadedBackend is True, will prefer a backend that
            is already imported.
          * Requires a restart.
        """
        def fget(self, key):
            if key in self._s:
                return self._s[key]
            else:
                return 'pyside'  # Default value
        def fset(self, key, value):
            # Note that 'qt4' in valid for backward compatibility
            value = value.lower()
            if value in ['pyside', 'qt4', 'pyqt4', 'wx', 'gtk', 'fltk', 'foo']:
                self._s[key] = value
            else:
                raise ValueError('Invalid backend specified.')
        return locals()
    
    @PropertyForSettings
    def preferAlreadyLoadedBackend():
        """ Bool that indicates whether visvis should prefer an already
        imported backend (even if it's not the preferredBackend). This is
        usefull in interactive session in for example IEP, Spyder or IPython.
        Requires a restart.
        """
        def fget(self, key):
            if key in self._s:
                return bool(self._s[key])
            else:
                return True  # Default value
        def fset(self, key, value):
            self._s[key] = bool(value)
        return locals()
    
#     @PropertyForSettings
#     def defaultInterpolation2D():
#         """ The default interpolation mode for 2D textures (bool). If False
#         the pixels are well visible, if True the image looks smoother.
#         Default is False.
#         """
#         def fget(self, key):
#             if key in self._s:
#                 return bool(self._s[key])
#             else:
#                 return False  # Default value
#         def fset(self, key, value):
#             self._s[key] = bool(value)
#         return locals()
    
    @PropertyForSettings
    def figureSize():
        """ The initial size for figure windows. Should be a 2-element
        tuple or list. Default is (560, 420).
        """
        def fget(self, key):
            if key in self._s:
                return tuple(self._s[key])
            else:
                return (560, 420)  # Default value
        def fset(self, key, value):
            if not isinstance(value, (list,tuple)) or len(value) != 2:
                raise ValueError('Figure size must be a 2-element list or tuple.')
            value = [int(i) for i in value]
            self._s[key] = tuple(value)
        return locals()
    
    @PropertyForSettings
    def volshowPreference():
        """ Whether the volshow() function prefers the volshow2() or volshow3()
        function. By default visvis prefers volshow3(), but falls back to
        volshow2() when the OpenGl version is not high enough. Some OpenGl
        drivers, however, support volume rendering only in ultra-slow software
        mode (seen on ATI). In this case, or if you simply prefer volshow2()
        you can set this setting to '2'.
        """
        def fget(self, key):
            if key in self._s:
                return self._s[key]
            else:
                return 3  # Default value
        def fset(self, key, value):
            if value not in [2,3]:
                raise ValueError('volshowPreference must be 2 or 3.')
            self._s[key] = int(value)
        return locals()
    
    @PropertyForSettings
    def defaultFontName():
        """ The default font to use. Can be 'mono', 'sans' or 'serif', with
        'sans' being the default.
        """
        def fget(self, key):
            if key in self._s:
                return self._s[key]
            else:
                return 'sans'  # Default value
        def fset(self, key, value):
            value = value.lower()
            if value not in ['mono', 'sans', 'serif', 'humor']:
                raise ValueError("defaultFontName must be 'mono', 'sans', 'serif' or 'humor'.")
            self._s[key] = value
        return locals()
    
    @PropertyForSettings
    def defaultRelativeFontSize():
        """ The default relativeFontSize of new figures. The relativeFontSize
        property can be used to scale all text simultenously, as well as
        increase/decrease the margins availavle for the text. The default is
        1.0.
        """
        def fget(self, key):
            if key in self._s:
                return self._s[key]
            else:
                return 1.0
        def fset(self, key, value):
            self._s[key] = float(value)
        return locals()
    
    # todo: more? maybe axes bgcolor and axisColor?

# Create settings instance, this is what gets inserted in the visvis namespace
settings = Settings()

# Set __file__ absolute when loading
__file__ = os.path.abspath(__file__)
