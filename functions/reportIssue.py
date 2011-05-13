# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
import webbrowser

def reportIssue():    
    """ help()
    
    Open a webbrowser with the visvis website at the issue list.
    
    
    """
    webbrowser.open("http://code.google.com/p/visvis/issues/list")

if __name__ == '__main__':
    reportIssue()
