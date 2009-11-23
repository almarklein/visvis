import visvis as vv
app = vv.App('wx')

im = vv.imread('d:/almar/projects/ims/lena.png')
vv.imshow(im)

app.run()