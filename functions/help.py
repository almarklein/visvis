# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import webbrowser

def help():    
    """ help()
    
    Open a webbrowser with the API documentation of visvis.
    
    Note that all visvis classes and functions have docstrings, so 
    typing for example "vv.Mesh?" in IPython or IEP gives you 
    documentation on the fly.
    
    """
    webbrowser.open("http://code.google.com/p/visvis/wiki/Documentation")

if __name__ == '__main__':
    help()
