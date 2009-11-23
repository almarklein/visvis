""" Show a title over the given or current axes. """

import visvis as vv


def title(text, axes=None):
    """ title(text, axes=None)
    Show a title over the given or current axes. """
    if axes is None:
        axes = vv.gca()
    
    return vv.Title(axes, text)

if __name__=='__main__':
    vv.use('wx')
    a = vv.gca()
    vv.title('test title')