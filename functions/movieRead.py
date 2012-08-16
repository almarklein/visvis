# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import os
import visvis as vv
from visvis.vvmovie import movieRead as _movieRead

# todo: vvmovie will be replaced by imageio
# todo: I tried some animated gifs from wiki using the PIL wrapper, and most did not read in correctly ...

# like newtons cradle and rotating earth

def movieRead(filename, *args, **kwargs):
    
    if not os.path.isfile(filename):
        # try loadingpil from the resource dir
        path = vv.misc.getResourceDir()
        filename2 = os.path.join(path, filename)
        if os.path.isfile(filename2):
            filename = filename2
    
    return _movieRead(filename, *args, **kwargs)

movieRead.__doc__ = _movieRead.__doc__


if __name__ == '__main__':
    ims = vv.movieRead('newtonscradle.gif')
    vv.movieShow(ims)
