# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

def reportIssue():
    """ help()
    
    Open a webbrowser with the visvis website at the issue list.
    
    
    """
    import webbrowser
    webbrowser.open("https://github.com/almarklein/visvis/issues")

if __name__ == '__main__':
    import visvis as vv
    vv.reportIssue()
