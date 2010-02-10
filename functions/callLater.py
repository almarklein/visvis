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
    calltime = time.clock() + delay
    vv.events._callLater_callables[calltime]= (callable, args, kwargs)
    