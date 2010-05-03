#!/usr/bin/env python

import visvis as vv
import numpy as np
app = vv.use()
vv.clf()

# create volume
vol = np.zeros((128,128,128), dtype=np.float32)
vol[50:70,80:90, 10:100] = 0.2
vol[50:70,10:100,80:90] = 0.5
vol[10:100,50:70,80:90] = 1

# set labels
vv.xlabel('x axis')
vv.ylabel('y axis')
vv.zlabel('z axis')

# show
t = vv.volshow(vol, renderStyle='mip')
# try the differtent render styles, for examample 
# "t.renderStyle='iso'" or "t.renderStyle='ray'"
# If the drawing hangs, your video drived decided to render in software mode.
# This is unfortunately (as far as I know) not possible to detect. 
# It might help if your data is shaped a power of 2.

vv.cm.ColormapEditor(vv.gca())

app.Run()
