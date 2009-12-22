import visvis as vv
app = vv.App('wx')

im = vv.imread('lena.png')
t = vv.imshow(im)
t.aa = 2 # more anti-aliasing (default=1)
t.interpolate = True # interpolate pixels 

app.run()