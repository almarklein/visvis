# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_slicesInVolume.gif](http://wiki.visvis.googlecode.com/hg/images/examples/example_slicesInVolume.gif)

```
#!/usr/bin/env python
""" This example illustrates how you can visualize 
a volume using 2D slices. 

We explicitly use volshow2() here. Note that volshow() calls 
volshow3() by default, but volshow2() when the system does 
not support 3D rendering (OpenGL version <2.0).

"""


import visvis as vv
vol = vv.aVolume()

t = vv.volshow2(vol)
t.colormap = vv.CM_HOT
t.edgeColor = (0.8, 0.8, 0.8)
app = vv.use()
app.Run()

```