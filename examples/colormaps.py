import visvis as vv
app = vv.use()

# Get green channel of lena image
im = vv.imread('lena.png')[:,:,1]

# Make 4 subplots with different colormaps
cmaps = [vv.gray, vv.jet, vv.summer, vv.hot]
for i in range(4):
    a = vv.subplot(2,2,i+1)
    t = vv.imshow(im)
    a.showAxis = 0
    t.colormap = cmaps[i]
    vv.colorbar()


app.Run()