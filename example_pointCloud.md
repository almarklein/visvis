# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_pointCloud.gif](http://wiki.visvis.googlecode.com/hg/images/examples/example_pointCloud.gif)

```
#!/usr/bin/env python

import numpy as np
import visvis as vv
from visvis import Point, Pointset
app = vv.use()

# create random points
a = np.random.normal(size=(1000,3))
pp = Pointset(a)
pp *= Point(2,5,1)

# prepare axes
a = vv.gca()
a.cameraType = '3d'
a.daspectAuto = False

# draw points
l = vv.plot(pp, ms='.', mc='r', mw='9', ls='', mew=0 )
l.alpha = 0.1

app.Run()

```