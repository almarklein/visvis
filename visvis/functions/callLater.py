# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import time
import visvis as vv

def callLater(delay, callable, *args, **kwargs):
    """ callLater(delay, callable, *args, **kwargs)
    
    Call a callable after a specified delay (in seconds),
    with the specified arguments and keyword-arguments.
    
    Parameters
    ----------
    delay : scalar
        The delay in seconds. If zero, the callable is called right
        after the current processing has returned to the main loop,
        before any other visvis events are processed.
    callable : a callable object
        The callback that is called when the delay has passed.
    
    See also vv.Event
    
    """
    calltime = time.time() + delay
    vv.events._callLater_callables[calltime]= (callable, args, kwargs)

if __name__ == '__main__':
    # Code to call a method after 2.0 seconds
    def foo():
        print('haha!')
    vv.callLater(2.0, foo)
    # For this to work, a visvis application must be Create'd.
    app = vv.use()
    app.Create()
    app.Run()
