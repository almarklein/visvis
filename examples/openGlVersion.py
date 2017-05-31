#!/usr/bin/env python

import visvis as vv
app = vv.use()

def ensureString(s):
    if isinstance(s, str):
        return s
    else:
        return s.decode('ascii')

# get info
version, vendor, renderer, ext = vv.getOpenGlInfo()

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
    raw_input('\nPress enter to continue...') # noqa - Python 2
