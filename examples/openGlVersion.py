#!/usr/bin/env python

import visvis as vv
app = vv.use()

def ensureString(s):
    if isinstance(s, str):
        return s
    else:
        return s.decode('ascii')
        
import OpenGL.GL as gl
# a = ensureString(gl.glGetString(gl.GL_VERSION))
# print(a)



    
# get info
print(vv.misc._glInfo[0])
version, vendor, renderer, ext = vv.getOpenGlInfo()
print(vv.misc._glInfo[0])
if not ext:
    ext = ''


# from OpenGL import extensions
# print(extensions.CURRENT_GL_VERSION)
# print(extensions.getGLVersion())
# print(extensions.CURRENT_GL_VERSION)


# print!
print('Information about the OpenGl version on this system:\n')
print('version:    ' + version)
print('vendor:     ' + vendor)
print('renderer:   ' + renderer)
print('extensions: ' + str(len(ext.split())) + ' different extensions')

# Wait
try:
    input('\nPress enter to continue...') # Python 3
except NameError:
    raw_input('\nPress enter to continue...') # Python 2
    