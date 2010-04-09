''' Test Case for polar plots'''
import visvis as vv
import numpy as np
angs = 0.1+ np.linspace(-90,90,181) # 0.1+ get rid of singularity
angsRads = np.pi*angs/180.0
mag = 10*np.log10(np.abs(np.sin(10*angsRads)/angsRads)) + angsRads
mag = mag - np.max(mag)
vv.polarplot( angs, mag, lc='b')
vv.polarplot(angs+20, mag, lc='r', lw=3)
ax = vv.gca()
#ax.SetLimits(rangeX=[-90,90], rangeY=[-40,0])

ax.showGrid = 1

ax.axis.angularRefPos = 90  #0 deg points up

ax.axis.isCW = False  # changes angular sense (azimuth instead of phi)

ax.axis.SetLimits( rangeTheta= 0, rangeR = vv.Range(-40,5))

ax.xLabel = 'degrees'
ax.yLabel = 'dB'



