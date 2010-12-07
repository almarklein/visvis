# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def title(text, axes=None):
    """ title(text, axes=None)
    
    Show a title over the given or current axes. 
    Remove the title by suplying an empty string. 
    
    """
    
    if axes is None:
        axes = vv.gca()
    
    # seek Title object
    for child in axes.children:
        if isinstance(child, vv.Title):
            ob = child
            ob.text = text
            break
    else:
        ob = vv.Title(axes, text)
    
    # destroy if no text, return object otherwise
    if not text:
        ob.Destroy()
        return None
    else:
        return ob


if __name__=='__main__':
    vv.use('wx')
    a = vv.gca()
    vv.title('test title')
