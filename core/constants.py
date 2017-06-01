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


## Colormap data

_magma = b"""
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
0/ga98P+HOfT9/3z8/"""


_viridis = b"""
wLSIPhO2nzsVqag+JXqJPkpeHTwWvas+GjaKPrKdbzw6ya4+feiKPmhdozw+zbE+cZGLPn9p0TybyL
Q+sTCMPgADAT2Vu7c+gsaMPtehGj1hpbo+wVKNPnXoND0jhr0+TtWNPoM1Tj23XcA+SE6OPv+zZj13K8
M+sr2OPsGLfj1j78U+RiOPPprtij1Yqcg+KH+PPqdblj3zWMs+V9GPPv6ZoT0R/s0+sRmQPvevrD2RmN
A+WFiQPs+itz0PKNM+Ko2QPsR3wj1prNU+SriQPo8zzT1bJdg+lNmQPknY1z3mkto+TvGQPpxp4j2l9N
w+Mv+QPqPp7D13St8+ZAORPu9Z9z06lOE+4/2QPkzeAD7M0eM+0O6QPlcJBj7rAuY+LNaQPp0uCz6VJ+
g+9rOQPuhOED6rP+o+UYiQPvVpFT4KS+w+flOQPo2AGj6QSe4+PBWQPvOSHz4dO/A+7s2PPiehJD7RH/
I+lX2PPm2rKT6M9/M+UySPPoGxLj4rwvU+SMKOPqezMz7Qf/c+l1eOPiCyOD5ZMPk+guSNPmmsPT7p0/
o+TWmNPsKiQj6havw+1uWMPi2VRz5e9P0+gVqMPqmDTD5Dcf8+cceLPrFtUT7KcAA/Ci2LPodTVj6WIg
E/bouKPuc0Wz4pzgE/veKJPtMRYD6jcwI/GjOJPgfqZD71EgM/LH2IPoS9aT5grAM/FsGHPgWMbj7VPw
Q/1v6GPopVcz6WzQQ/9DaGPtIZeD6TVQU/kGmFPh/ZfD4O2AU/D5eEPnXJgD4ZVQY/tr+DPnkjgz7VzA
Y/5+OCPt16hT51Pwc/xQOCPl/Phz73rAc/kh+BPv8gij6QFQg/tTeAPr1vjD5weQg/mph+Ppm7jj6p2A
g/Brx8PnEEkT5uMwk/8dl6PiNKkz7fiQk/nfJ4PhWNlT4v3Ak/1QZ3PuLMlz5eKgo/Hhd1PqsJmj7BdA
o/vCNzPnBDnD5Wuwo/ui1xPlN6nj5h/go/oDVvPhCuoD7zPQs/8zttPsreoj4+egs/s0BrPoAMpT5jsw
s/7URpPlQ3pz6F6Qs/oUhnPkZfqT7FHAw/mExlPlWEqz40TQw/FlFjPoOmrT4Deww/n1ZhPu/Frz5Vpg
w/eV1fPpvisT5Kzww/J2ZdPmX8sz7k9Qw/73BbPrITtj5lGg0/E35ZPl8ouD7ePA0/GY5XPm06uj5fXQ
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
w+gEV+P+j5Zz/1YxM+"""


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

import numpy as np
import base64
colormaps['magma'] = np.frombuffer(base64.decodestring(_magma), np.float32).reshape(256, 3)
colormaps['viridis'] = np.frombuffer(base64.decodestring(_viridis), np.float32).reshape(256, 3)

# Medical colormaps
c1, c2 = 1200 / 4096.0, 1550 / 4096.0
colormaps['ct1'] = {    'r': [(0, 0), (c2, 1.0), (1.0, 0.0)],
                        'g': [(0, 0), (c1, 0.0), (c2, 1.0)],
                        'b': [(0, 0), (c1, 0.0), (c2, 1.0), (1.0, 0.0) ]}
# Colormap design by Maaike Koenrades, best viewed with clim (0, 2500)
colormaps['ct2'] = {    'r': [(0, 0), (0.1773, 1.0)],
                        'g': [(0, 0), (0.2727, 1.0)],
                        'b': [(0, 0), (0.3454, 1.0)],
                        'a': [(0, 1), (1.0, 1.0)]}
del c1, c2, base64, np


# Inject colormaps in this namespace as constants
L = locals()
for key in colormaps:
    key2 = 'CM_' + key.upper()
    L[key2] = colormaps[key]
del L, key, key2
