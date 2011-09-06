#!/usr/bin/env python

""" This example illustrate using text and formatting for text
world objects and labels.
"""

import visvis as vv

# Create figure and figure
fig = vv.figure()
a = vv.cla()
a.cameraType = '2d'
a.daspectAuto = True
a.SetLimits((0,8), (-1,10))

# Create text inside the axes
vv.Text(a, 'These are texts living in the scene:', 1, 3)
vv.Text(a, 'Text can be made \b{bold} easil\by!', 1, 2)
vv.Text(a, 'Text can be made \i{italic} easil\iy!', 1, 1)

# Create text labels
label0 = vv.Label(a, 'These are texts in widget coordinates:')
label0.position = 10, 20
label1 = vv.Label(a, 'Sub_{script} and super^{script} are easy as pi^2.')
label1.position = 10, 40
label2 = vv.Label(a, u'You can use many Unicode characters: \\u0183 = \u0183')
label2.position = 10, 60
label3 = vv.Label(a, 'And can use many Latex like commands: \\alpha \\Alpha' +
                    '\\approx, \sigma, \pi, ')
label3.position = 10, 80

for label in [label0, label1, label2, label3]:
    label.bgcolor = (0.5, 1, 0.5)
    label.position.w = 400

# Enter main loop
app = vv.use()
app.Run()
