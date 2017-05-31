#!/usr/bin/env python

""" Example that demonstrates how movies can be recorded
and exported to gif/swf/avi.

This is not an interactive example, but a script.

"""

import visvis as vv

# Create something to show, let's show a red teapot!
mesh = vv.solidTeapot()
mesh.faceColor = 'r'

# Prepare
Nangles = 36
a = vv.gca()
f = vv.gcf()
rec = vv.record(a)

# Rotate camera
for i in range(Nangles):
    a.camera.azimuth = 360 * float(i) / Nangles
    if a.camera.azimuth>180:
        a.camera.azimuth -= 360
    a.Draw() # Tell the axes to redraw
    f.DrawNow() # Draw the figure NOW, instead of waiting for GUI event loop


# Export
rec.Stop()
rec.Export('teapot.gif')


""" NOTES

A note on a.Draw()
------------------

This is necessary to tell the axes to redraw itself instead of using its
buffered image. Changing a property of the axes or any object inside it
will automatically trigger a redraw, but this is not so for the camera,
since it's a bit of a low level thing...

More explicit (and better documented) control over the camera may be
implemented later.


A note on f.DrawNow()
---------------------

This is necessary to invoke a redraw at THAT moment. Normal draw calls
(such as the one to a.Draw(), will post a paint request to the GUI toolkit,
which is handled when the GUI event loop returns. In this example, that would
be never, since we do not start an event loop :)

"""
