""" FREEZING WITH CX_FREEZE
This script can be run as a script (no need to do distutils stuff...)
"""

import sys, os, shutil
from cx_Freeze import Executable, Freezer, setup
from visvis import freezeHelp

# define app name and such
name = "photoShow"
#baseDir = 'd:/almar/projects/_p/apps/'
#srcDir = 'd:/almar/projects/_p/visvis/examples/'
baseDir = 'c:/projects/PYTHON/apps/'
srcDir = 'C:/projects/PYTHON/visvis/examples/'
distDir = baseDir+name+'/'
scriptFiles = [ 'photoshow.py']
iconFile = srcDir + 'photoshow.ico'

## includes and excludes

# you usually do not need these
excludes = ['_ssl', 'pyreadline', 'pdb', "email", 
     "matplotlib", 'doctest', 
    "scipy.linalg", "scipy.special", "Pyrex", 
#      "numpy.core._dotblas", "numpy.linalg" 
    ]
# excludes for tk
tk_excludes = [ "pywin", "pywin.debugger", "pywin.debugger.dbgcon",
                "pywin.dialogs", "pywin.dialogs.list",
                "Tkconstants","Tkinter","tcl" ]
excludes.extend(tk_excludes)
# excludes.append('numpy')


includes = freezeHelp.getIncludes('wx')
# includes = ['sip', "PyQt4.QtCore", "PyQt4.QtGui", 'PyQt4.Qsci'] # for qt to work


## Go!
# see http://cx-freeze.sourceforge.net/cx_Freeze.html for docs.

executables = {}
for scriptFile in scriptFiles:
    scriptFile = srcDir+scriptFile
    
    ex = Executable(    scriptFile, 
                        icon=iconFile,
                        appendScriptToExe = True,
                        base = 'Win32GUI', # this is what hides the console
                        )
    executables[ex] = True

f = Freezer(    executables, 
                includes = includes,
                excludes = excludes,
                targetDir = distDir,
#                 copyDependentFiles = True,
#                 appendScriptToExe=True,
                optimizeFlag=2, 
                compress=False,
                silent=True,
            )

f.Freeze()

# copy resource files
freezeHelp.copyResources(distDir)