#!/usr/bin/env python
""" This example demonstrates rendering a color volume.
We demonstrate two renderers capable of rendering color data:
the colormip and coloriso renderer.
"""

import visvis as vv
app = vv.use()

# Create volume (smooth a bit)
if False:
    
    vol0 = vv.aVolume()
    vol = vol0.copy()*0.5
    vol[1:,:,:] += 0.3 * vol0[:-1,:,:]
    vol[:-1,:,:] += 0.3 * vol0[1:,:,:]
    vol[:,1:,:] += 0.3 * vol0[:,:-1,:]
    vol[:,:-1,:] += 0.3 * vol0[:,1:,:]
    vol[:,:,1:] += 0.3 * vol0[:,:,:-1]
    vol[:,:,:-1] += 0.3 * vol0[:,:,1:]
else:
    # My personal test
    from visvis import ssdf
    s = ssdf.load('/home/almar/data/dicom/cropped/croppedReg_pat01.bsdf')
    vol = s.vol

##

# Create figure and make subplots with different renderers
vv.figure(1); vv.clf()
RS = ['mip', 'ray', 'iso', 'isoray']
a0 = None
tt = []
for i in range(4):
    a = vv.subplot(2,2,i+1)
    t = vv.volshow(vol)
    vv.title('Renderstyle ' + RS[i])
    t.colormap = vv.CM_CT1
    t.renderStyle = RS[i]
    tt.append(t)
    if a0 is None:
        a0 = a
    else:
        a.camera = a0.camera

# Create colormap editor in first axes
cme = vv.ColormapEditor(a0, *tt)

# Run app
app.Create()
app.Run()
