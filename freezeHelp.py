# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module freezeHelp

Helps freezing apps made using visvis.

"""

import os
import sys
import shutil

import visvis as vv


backendAliases = {'qt4': 'pyqt4'}


def copyResources(destPath):
    """ copyResources(destinationPath)
    
    Copy the visvis resource dir to the specified folder
    (The folder containing the frozen executable).
    
    """
    # Create folder (if required)
    destPath = os.path.join(destPath, 'visvisResources')
    if not os.path.isdir(destPath):
        os.makedirs(destPath)
    # Copy files
    for filename, _ in collectResourcePaths():
        fname = os.path.basename(filename)
        shutil.copy(filename, os.path.join(destPath, fname))


def collectResourcePaths():
    paths = []  # list of (abs_source, rel_dest)
    # Collect files
    src_dir = vv.misc.getResourceDir()
    dist_dir = "visvisResources"
    for fname in os.listdir(src_dir):
        if fname.startswith('.') or fname.startswith('_'):
            continue
        paths.append((os.path.join(src_dir, fname), dist_dir))
    # Collect FreeType library to resource dir
    try:
        ft_filename = vv.text.freetype.FT.filename
    except Exception:
        ft_filename = None
    if ft_filename and not os.path.isfile(ft_filename):
        # Try harder to get absolute path for the freetype lib
        for dir in ['/usr/lib/', '/usr/local/lib/',
                    '/usr/lib/x86_64-linux-gnu/', '/usr/lib/i386-linux-gnu/']:
            if os.path.isfile(dir+ft_filename):
                ft_filename = dir+ft_filename
                break
    if ft_filename and os.path.isfile(ft_filename):
        fname = os.path.split(ft_filename)[1]
        paths.append((ft_filename, dist_dir))
    else:
        print('Warning: could not find freetype library.')
    return paths


def getIncludes(backendName):
    """ getIncludes(backendName)
    
    Get a list of includes to extend the 'includes' list
    with of py2exe or bbfreeze. The list contains:
      * the module of the specified backend
      * all the functionnames, which are dynamically loaded and therefore
        not included by default.
      * opengl stuff
    
    """
    # init
    includes = []
    backendName = backendAliases.get(backendName, backendName)
    
    # backend
    backendModule = 'visvis.backends.backend_'+ backendName
    includes.append(backendModule)
    if backendName == 'pyqt4':
        includes.extend(["sip", "PyQt4.QtCore", "PyQt4.QtGui", "PyQt4.QtOpenGL"])
    elif backendName == 'pyside':
        includes.extend(["PySide.QtCore", "PySide.QtGui", "PySide.QtOpenGL"])
    
    # functions
    for funcName in vv.functions._functionNames:
        includes.append('visvis.functions.'+funcName)
    
    # processing functions
    for funcName in vv.processing._functionNames:
        includes.append('visvis.processing.'+funcName)
    
    # opengl stuff
    arrayModules = ["nones", "strings","lists","numbers","ctypesarrays",
        "ctypesparameters", "ctypespointers", "numpymodule",
        "formathandler"]
    GLUModules = ["glustruct"]
    for name in arrayModules:
        name = 'OpenGL.arrays.'+name
        if name in sys.modules:
            includes.append(name)
    for name in GLUModules:
        name = 'OpenGL.GLU.'+name
        if name in sys.modules:
            includes.append(name)
    if sys.platform.startswith('win'):
        includes.append("OpenGL.platform.win32")
    if sys.platform.startswith('linux'):
        includes.append("OpenGL.platform.glx")
    
    # done
    return includes

def getExcludes(backendName):
    """ getExcludes(backendName)
    
    Get a list of excludes. If using the 'wx' backend, you don't
    want all the qt4 libaries.
    
    backendName is the name of the backend which you do want to use.
    
    """
    
    # init
    excludes = []
    backendName = backendAliases.get(backendName, backendName)
    
    # Neglect pyqt4
    if 'pyqt4' != backendName:
        excludes.extend(["sip", "PyQt4", "PyQt4.QtCore", "PyQt4.QtGui"])
    
    # Neglect PySide
    if 'pyside' != backendName:
        excludes.extend(["PySide", "PySide.QtCore", "PySide.QtGui"])
    
    # Neglect wx
    if 'wx' != backendName:
        excludes.extend(["wx"])
    
    # done
    return excludes
