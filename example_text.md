# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_text.png](http://wiki.visvis.googlecode.com/hg/images/examples/example_text.png)

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This example illustrate using text and formatting for text
world objects and labels.
"""

import visvis as vv

# The next import is just to create a Unicode char in a way that works on Python2 and Python3
from visvis.core.misc import unichr 

# Define a piece of Unicode text in a py2.x py3.x compatible manner
# On Py3.x you should do: hello = 'Привет пустошь'
# On Py3.x you should do: hello = u'Привет пустошь'
hello = 'Привет пустошь'
if hasattr(hello, 'decode'):
    hello = hello.decode('utf-8')


# Create figure and figure
fig = vv.figure()
a = vv.cla()
a.cameraType = '2d'
a.daspectAuto = True
a.SetLimits((0,8), (-1,10))

# Create text inside the axes
t1 = vv.Text(a, 'Visvis text', 0.2, 9, 0, 'mono', 30)
t2 = vv.Text(a, '... with FreeType!', 1, 8, 0, 'serif', 12)
t3 = vv.Text(a, '... and Unicode: %s!' % hello, 1, 7)
t3 = vv.Text(a, '\Gamma\rho\epsilon\epsilon\kappa letters and ' + 
                ' \rightarrow math \otimes symbols', 1, 6)

t2 = vv.Text(a, '\b{bold}, \i{italic}, and \b{\i{bolditalic}} \bfon\its' +
                ' and sup^{script} and sub_{script}', 1, 5, 0, 'serif')
t3 = vv.Text(a, 'Look, I\'m at an angle!', 1, 4)
t3.textAngle = -20
t3.fontSize = 12


# Create text labels
label1 = vv.Label(a, 'This is a Label')
label1.position = 10, 0.9
label1.bgcolor = (0.5, 1, 0.5)

## A quick brown fox jumps over the lazy dog

testText = 'A quick brown fox jumps over the lazy dog'

# Create figure and figure
fig = vv.figure()
a = vv.cla()
a.cameraType = '2d'

vv.title(testText)
# Create text labels
for i in range(20):
    offset = 0.1 * i
    label = vv.Label(a, '| ' + testText + ' - %1.2f pixels offset' % offset)
    label.bgcolor = None
    label.position = 10 + 0.1*i, 10 + i*15


# Enter main loop
app = vv.use()
app.Run()

```