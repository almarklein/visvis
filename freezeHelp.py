# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module freezeHelp

Helps freezing apps made using visvis.


"""

import visvis as vv
import os, shutil, sys

def copyResources(destPath):   
    """ copyResources(destinationPath)
    
    Copy the visvis resource dir to the specified folder 
    (The folder containing the frozen executable).
    
    """
    # create folder (if required)
    destPath = os.path.join(destPath, 'visvisResources')
    if not os.path.isdir(destPath):
        os.makedirs(destPath)
    # copy files
    path = vv.misc.getResourceDir()
    for file in os.listdir(path):
        if file.startswith('.') or file.startswith('_'):
            continue
        shutil.copy(os.path.join(path,file), os.path.join(destPath,file))


def getIncludes(backendName):
    """ getIncludes(backendName)
    
    Get a list of includes to extend the 'includes' list
    with of py2exe or bbfreeze. The list contains:
      * the module of the specified backend 
      * all the functionnames, which are dynamically loaded and therefore not included by default.
      * opengl stuff
    
    """
    # init
    includes = []
    
    # backend
    backendModule = 'visvis.backends.backend_'+ backendName
    includes.append(backendModule)
    if backendName == 'qt4':
        includes.extend(["sip", "PyQt4.QtCore", "PyQt4.QtGui"])
    
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
    if os.name == 'nt':
        includes.append("OpenGL.platform.win32")
    
    # done
    return includes

