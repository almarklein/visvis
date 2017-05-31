#!/usr/bin/env python
""" This example demonstrates rendering a color volume.
We demonstrate two renderers capable of rendering color data:
the colormip and coloriso renderer.
"""

import visvis as vv
app = vv.use()

# Load volume
vol = vv.volread('stent')

# Create figure and make subplots with different renderers
vv.figure(1); vv.clf()
RS = ['mip', 'iso', 'edgeray', 'ray', 'litray']
a0 = None
tt = []
for i in range(5):
    a = vv.subplot(3,2,i+2)
    t = vv.volshow(vol)
    vv.title('Renderstyle ' + RS[i])
    t.colormap = vv.CM_HOT
    t.renderStyle = RS[i]
    t.isoThreshold = 200  # Only used in iso render style
    tt.append(t)
    if a0 is None:
        a0 = a
    else:
        a.camera = a0.camera

# Create colormap editor in first axes
cme = vv.ColormapEditor(vv.gcf(), *tt[3:])

# Run app
app.Create()
app.Run()
