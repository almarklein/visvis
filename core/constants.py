# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module constants

"""

# (The keys values are the same as for wx, but this is arbitrary.)

KEY_SHIFT = 17
KEY_ALT = 18
KEY_CONTROL = 19
KEY_ENTER = 13
KEY_LEFT = 314
KEY_UP = 315
KEY_RIGHT = 316
KEY_DOWN = 317
KEY_PAGEUP = 366
KEY_PAGEDOWN = 367
KEY_ESCAPE = 27
KEY_DELETE = 127


## Create Build-in colormaps
# Note: hsv should interpolate in HSV colorspace, so it not really correct.

colormaps = {}

colormaps['gray'] = [(0,0,0), (1,1,1)]
colormaps['cool'] = [(0,1,1), (1,0,1)]
colormaps['hot'] = [(0,0,0), (1,0,0), (1,1,0), (1,1,1)]
colormaps['bone'] = [(0,0,0), (0.333, 0.333, 0.444), (0.666, 0.777, 0.777), (1,1,1)]
colormaps['copper'] = [(0,0,0), (1,0.7,0.5)]
colormaps['pink'] = [(0.1,0,0), (0.75,0.5,0.5), (0.9,0.9,0.7), (1,1,1)]

colormaps['spring'] = [(1,0,1), (1,1,0)]
colormaps['summer'] = [(0,0.5,0.4), (1,1,0.4)]
colormaps['autumn'] = [(1,0,0), (1,1,0)]
colormaps['winter'] = [(0,0,1), (0,1,0.5)]

colormaps['jet'] = [(0,0,0.5), (0,0,1), (0,0.5,1), (0,1,1), (0.5,1,0.5), 
                    (1,1,0), (1,0.5,0), (1,0,0), (0.5,0,0)]
colormaps['hsv'] = [(1,0,0), (1,1,0), (0,1,0), (0,1,1),(0,0,1), (1,0,1), (1,0,0)]

# Medical colormaps
c1, c2 = 1200 / 4096.0, 1550 / 4096.0
colormaps['ct1'] = {    'red': [(0,0), (c2,1), (1,0)], 
                        'green': [(0,0), (c1,0), (c2,1)],
                        'blue': [(0,0), (c1,0), (c2,1), (1,0) ]}
del c1, c2


# Inject colormaps in this namespace as constants
L = locals()
for key in colormaps:
  key2 = 'CM_' + key.upper()
  L[key2] = colormaps[key]
del L, key, key2
