import visvis as vv
import numpy as np 
import Image

import strux
#import diffgeo

from points import Point, Pointset
vv.backends.use('wx')

# vv.shading.loadGLSLCode() # reload shading code

## create phantom


#im = Image.open('../mountain1.jpg')#[:,:,1]
#im = Image.open('c:/projects/PYTHON/wiki.jpg')#[:-1,:,1]
#im = np.asarray(im,dtype=np.int16)[:,:,0]*6


a = strux.load('d:/almar/projects/_p/tools/visvis/vol.xml')
#a = strux.load('c:/projects/PYTHON/tools/visvis/vol.xml')
vol = a.vol*1
#vol = vol.astype(np.float32)

# make smaller
#vol = vol[:199,:311,:311] # make uneven
vol = vol[:128,:256,:256]
#vol = vol[:32,:32,:32]

# smooth
#vol = diffgeo.gfilter(vol,1)

# make axis
vol[:,0:10,0:10] = 1000
vol[0:10,:,0:10] = 1000
vol[0:10,0:10,:] = 1000


## set up

f = vv.figure()

a = vv.Axes(f)
a.cameraType = 'polar'
a.position = vv.Position(0.1,0.1,0.8,0.9)
a.SetLimits(vv.Range(-10,110), vv.Range(-10,110) )
a.daspect = 1,-1,-2

t1 = vv.Texture3D(a,vol)
t2 = vv.Line(a,Pointset(3))
#t3 = vv.datatypes.Texture2D(a,im)

t2.ls = ''
t2.mw = 3
vv.plot([0,500],[0,0],[0,0],lw=5,lc='r', mw=0)
vv.plot([0,0],[0,500],[0,0],lw=5,lc='g', mw=0)
vv.plot([0,0],[0,0],[0,500],lw=5,lc='b', mw=0)
a.Draw()

