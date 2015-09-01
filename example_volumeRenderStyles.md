# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_volumeRenderStyles.gif](http://wiki.visvis.googlecode.com/hg/images/examples/example_volumeRenderStyles.gif)

```
#!/usr/bin/env python
""" This example demonstrates rendering a color volume.
We demonstrate two renderers capable of rendering color data:
the colormip and coloriso renderer.
"""

import visvis as vv
app = vv.use()

# Create volume (smooth a bit)
if True:
    
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
    s = ssdf.load('/home/almar/data/dicom/cropped/croppedReg_pat01_gravity.bsdf')
    vol = s.vol

##

# Create figure and make subplots with different renderers
vv.figure(1); vv.clf()
RS = ['mip', 'iso', 'edgeray', 'ray', 'litray']
a0 = None
tt = []
for i in range(5):
    a = vv.subplot(3,2,i+2)
    t = vv.volshow(vol)
    vv.title('Renderstyle ' + RS[i])
    t.colormap = vv.CM_HOT #vv.CM_CT1
    t.renderStyle = RS[i]
    tt.append(t)
    if a0 is None:
        a0 = a
    else:
        a.camera = a0.camera

# Create colormap editor in first axes
cme = vv.ColormapEditor(vv.gcf(), *tt[3:])

# Run app
app.Create()
app.Run()

```