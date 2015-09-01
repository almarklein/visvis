# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_colorVolume.png](http://wiki.visvis.googlecode.com/hg/images/examples/example_colorVolume.png)

```
#!/usr/bin/env python
""" This example demonstrates rendering a color volume.
This example demonstrates two render styles. Note that
all render styles are capable of rendering color data.
"""

import numpy as np
import visvis as vv
app = vv.use()

# Use vv.aVolume to create random bars for each color plane
N = 64
vol = np.empty((N,N,N,3), dtype='float32')
for i in range(3):
    vol[:,:,:,i] = vv.aVolume(10,N)

# Show
vv.figure()
a1 = vv.subplot(121); 
t1 = vv.volshow(vol[:,:,:,:], renderStyle = 'mip')
vv.title('color MIP render')
a2 = vv.subplot(122); 
t2 = vv.volshow(vol[:,:,:,:], renderStyle = 'iso')
t2.isoThreshold = 0.5
vv.title('color ISO-surface render')

# Share cameras
a1.camera = a2.camera

# Run app
app.Run()

```