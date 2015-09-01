# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_polarplots.png](http://wiki.visvis.googlecode.com/hg/images/examples/example_polarplots.png)

```
#!/usr/bin/env python

import visvis as vv
import numpy as np

# Define angles
angs = 0.1 + np.linspace(-90, 90, 181)  # 0.1+ get rid of singularity
angsRads = np.pi * angs / 180.0

# Define magnitude
mag = 10 * np.log10(np.abs(np.sin(10 * angsRads) / angsRads)) + angsRads
mag = mag - np.max(mag)

# Plot two versions of the signal, one rotated by 20 degrees
vv.polarplot( angs, mag, lc='b')
vv.polarplot(angs+20, mag, lc='r', lw=2)

# Set axis properties
ax = vv.gca()

ax.axis.angularRefPos = 90  # 0 deg points up
ax.axis.isCW = False  # changes angular sense (azimuth instead of phi)
ax.axis.SetLimits( rangeTheta=0, rangeR=vv.Range(-40, 5))

ax.axis.xLabel = 'degrees'
ax.axis.yLabel = 'dB'
ax.axis.showGrid = True

# Show some messages
print('drag mouse left button left-right to rotate plot.')
print('shift-drag mouse left button up-down to change lower')
print('radial limit. Drag mouse right button up-down to rescale')
print('radial axis while keeping lower radial limit fixed')

# Run mainloop
app = vv.use()
app.Run()

```