# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import time
import visvis as vv

def callLater(delay, callable, *args, **kwargs):
    """ callLater(delay, callable, *args, **kwargs)
    
    Call a callable after a specified delay (in seconds), 
    with the specified arguments and keyword-arguments. 
    
    If delay = 0, the callable is called right after the current processing
    has returned to the main loop, before any other visvis events are 
    processed.
    
    See also vv.Event
    
    """
    calltime = time.time() + delay
    vv.events._callLater_callables[calltime]= (callable, args, kwargs)
    