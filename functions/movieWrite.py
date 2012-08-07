# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv
from visvis.vvmovie import movieWrite


if __name__ == '__main__':
    ims = vv.movieRead('newtonscradle.gif')
    vv.movieWrite('newtonscradle.swf', ims)
