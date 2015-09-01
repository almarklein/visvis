# Wiki page auto-generated from visvis examples

![http://wiki.visvis.googlecode.com/hg/images/examples/example_images.png](http://wiki.visvis.googlecode.com/hg/images/examples/example_images.png)

```
#!/usr/bin/env python

import visvis as vv
app = vv.use()

im = vv.imread('lena.png')
im = im[:-1,:-1] # make not-power-of-two (to test if video driver is capable)
print(im.shape)

t = vv.imshow(im)
t.aa = 2 # more anti-aliasing (default=1)
t.interpolate = True # interpolate pixels 

app.Run()

```