# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein

""" Example / test script.

This example shows on the left an image with overlaid contour.
On the top right is a volumerender using the iso render style. In the
bottom right is a mesh obtained using the isosurface function. They look
a lot the same...
""" 

import visvis as vv
import numpy as np
import time
from visvis.utils.iso import isosurface, isocontour 


if __name__ == '__main__':
    
    # Get image
    SELECT = 0
    if SELECT == 0:
        im = vv.imread('lena.png')[:,:,0].astype('float32')
    elif SELECT == 1:
        im = np.zeros((64,64), 'float32')
        im[20:50,30:40] = 1.0
        im[25:50,40] = 0.6
        im[30:40,20:50] = 1.0
    
    # Get contours
    t0 = time.time()
    for i in range(100):
        pp = isocontour(im)
    print('finding contours took %1.0f ms' % (100*(time.time()-t0)) )
    
    
    # Create test volume
    SELECT = 1
    if SELECT == 0:
        import pirt
        vol = np.zeros((100,100,100), 'float32')
        vol[50,50,50] = 200.0
        
        vol = pirt.gfilter(vol, 20)
        isovalue = vol.max() *0.5
    elif SELECT == 1:
        s = vv. ssdf.load('/home/almar/data/cropped/stents_valve/cropped_pat102.bsdf')
        vol = s.vol.astype('float32')
        isovalue = 800
    elif SELECT == 2:
        vol = vv.aVolume(20, 256) # Different every time
        isovalue = 0.2
    
    # Get surface mesh
    t0 = time.time()
    bm = isosurface(vol, isovalue, 1)
    print('finding surface took %1.0f ms' % (1000*(time.time()-t0)) )
    
    # Show
    vv.figure(1); vv.clf()
    vv.subplot(121); vv.imshow(im); vv.plot(pp, ls='+', lc='r', lw=2)
    a1=vv.subplot(222); t=vv.volshow(vol)
    a2=vv.subplot(224); m=vv.mesh(bm)
    a1.camera = a2.camera
    t.colormap = (1,1,1), (1,1,1)
    
    t.renderStyle = 'iso'
    t.isoThreshold = isovalue

        