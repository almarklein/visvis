#!/usr/bin/env python

""" This example illustrates picking using the simple event system.
It also shows the working of the picking in an environment.

Notice for example that the leave event is not fired when you move
the mouse beyond the boundaries of the yellow rectangle as long
as it's still inside the red rectangle. This is because the red
rectangle is a child of the yellow rectangle.
"""

import visvis as vv
app = vv.use()

# Create figure and axes
f = vv.clf()
f.description = 'Figure'
#
a = vv.gca()
a.daspectAuto = True
a.description = 'Axes'

# Create three lines
l1 = vv.plot([1,2,3,2,4], lc='b', lw=7)
l1.description = 'blue line'
#
l2 = vv.plot([4,6,5,1,3], lc='r', lw=7)
l2.description = 'red line'
#
l3 = vv.plot([2,3,1,3,2], lc='c', lw=7)
l3.description = 'cyan line'

# Create two boxes, one a child of the other
b1 = vv.Box(f)
b1.position = 0.1, 0.2, 100, 40
b1.bgcolor=(1,1,0)
b1.description = 'yellow box'
#
b2 = vv.Box(b1)
b2.position = 5, 20, 20, 50
b2.bgcolor=(1,0,1)
b2.description = 'purple box'

# Define callback functions

def picker(event):
    print("Picking %s (%i,%i - %3.2f, %3.2f)" % (event.owner.description,
            event.x, event.y, event.x2d, event.y2d))

def ignoringPicker(event):
    picker(event)
    event.Ignore() # The parent object will be picked too!

def entering(event):
    print("Entering %s" % event.owner.description)
    if hasattr(event.owner, 'lc'):
        event.owner.original_lc = event.owner.lc
        event.owner.lc = 'k'

def leaving(event):
    print("Leaving %s" % event.owner.description)
    if hasattr(event.owner, 'original_lc'):
        event.owner.lc = event.owner.original_lc

def keyCallback(event):
    print('Received key %i at %s' % (event.key, event.owner.description))


def ignoringKeyCallback(event):
    keyCallback(event)
    event.Ignore() # The parent object will receive the event too

# Subscribe to events

# Note how clicking on the red line also picks the axes,
# and clicking on the purple box also picks the yellow box.
# Note also that no mouseDown event is registered for the 3d line,
# and that clicking on it is equivalent to clicking on the axes;
# the event is propagated to the line's parent.
#
# Same goes for key events. But in addition, the figure *always*
# receives a key event.

for ob in [f, a, b1, b2, l1, l2, l3]:
    ob.eventEnter.Bind(entering)
    ob.eventLeave.Bind(leaving)
for ob in [f, a, b1, l1]:
    ob.eventMouseDown.Bind(picker)
    ob.eventKeyDown.Bind(keyCallback)
for ob in [b2, l2]:
    ob.eventMouseDown.Bind(ignoringPicker)
    ob.eventKeyDown.Bind(ignoringKeyCallback)

# Start app
app.Run()
