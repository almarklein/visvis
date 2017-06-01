# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

def help():
    """ help()
    
    Open a webbrowser with the API documentation of visvis.
    
    Note that all visvis classes and functions have docstrings, so
    typing for example "vv.Mesh?" in IPython or IEP gives you
    documentation on the fly.
    
    """
    import webbrowser
    webbrowser.open("https://github.com/almarklein/visvis/wiki")

if __name__ == '__main__':
    import visvis as vv
    vv.help()
