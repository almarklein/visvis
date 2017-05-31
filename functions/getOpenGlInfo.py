# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def getOpenGlInfo():
    """ getOpenGlInfo()
    
    Get information about the OpenGl version on this system.
    Returned is a tuple (version, vendor, renderer, extensions)
    
    A figure is created and removed to create an openGl context if
    this is necessary.
    
    """
    
    # Open figure first. On Windows we can try obtaining the information,
    # but I found that on Ubuntu a segfault will happen (but this might
    # very well have to do with the OpenGl drivers).
    fig = vv.figure()
    result = vv.misc.getOpenGlInfo()
    
    # Should we open a figure and try again?
    fig.Destroy()
    fig._ProcessGuiEvents() # so it can close
    
    return result

if __name__ == '__main__':
    # get info
    version, vendor, renderer, ext = vv.getOpenGlInfo()
    # print!
    print('Information about the OpenGl version on this system:\n')
    print('version:    ' + version)
    print('vendor:     ' + vendor)
    print('renderer:   ' + renderer)
    print('extensions: ' + str(len(ext.split())) + ' different extensions')
