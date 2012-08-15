#!/usr/bin/env python

""" This example illustrates picking using the simple event system.
It also shows the working of the picking in an environment.

Notice for example that the leave event is not fired when you move 
the mouse beyond the boundaries of the yellow rectangle as long
as it's still inside the red rectangle. This is because the red
rectangle is a child of the yellow rectangle. 
"""

import numpy as np
import visvis as vv
app = vv.use()

f= vv.clf()
l1 = vv.plot([1,2,3,2,4], lw=3)
l2 = vv.plot([4,6,5,1,3], lc='r', mc='r', lw=3)

# im = np.zeros((10,10)); im[7:9,:]=1; im[:,7:9]=0.6
# t1 = vv.imshow(im)

b1 = vv.Box(f)
b1.position = 0.1, 0.2, 100, 40
b1.bgcolor=(1,1,0)

b2 = vv.Box(b1)
b2.position = 5, 20, 20, 50
#b2.bgcolor=(1,0,0)

a = vv.gca()
a.daspectAuto = True

def picker(event):
    print("Picking (%i,%i) (%3.2f, %3.2f)" % (event.x, event.y, 
            event.x2d, event.y2d), event.owner)
def entering(event):
    print("Entering", event.x, event.y, event.owner)
    if hasattr(event.owner, 'lc'):
        event.owner.picker_lc = event.owner.lc
        event.owner.lc = 'y'

def leaving(event):
    print("Leaving", event.x,event.y, event.owner)
    if hasattr(event.owner, 'picker_lc'):
        event.owner.lc = event.owner.picker_lc

for ob in [f,a,b1,b2, l1, l2]:#, t1]:
    ob.eventMouseDown.Bind(picker)
    ob.eventEnter.Bind(entering)
    ob.eventLeave.Bind(leaving)
    
app.Run()
