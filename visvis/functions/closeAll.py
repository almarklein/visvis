# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

def closeAll():
    """ closeAll()
    
    Closes all figures.
    
    """
    
    for fig in [fig for fig in vv.BaseFigure._figures.values()]:
        fig.Destroy()

if __name__ == '__main__':
    import time
    # Create figures
    vv.figure()
    vv.figure()
    vv.processEvents(); vv.processEvents()
    time.sleep(1.0)
    # Close all
    vv.closeAll()
