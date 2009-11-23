import visvis as vv
import visvis as vv
#reload(vv.cameras)
#reload(vv.datatypes);reload(vv.cameras);reload(vv.core);reload(vv)

app = vv.App('qt4')

from points import Point, Pointset
import numpy as np

## get data
pp = Pointset(2)
pp.Append(2,3)
pp.Append(2,4)
pp.Append(3,5)
pp.Append(8,6)
pp.Append(1,4)

pp2 = Pointset(2)
pp2.Append(5,6)
pp2.Append(3,1)
pp2.Append(1,1)

pp *=20
pp2 *=20

# pp._points = np.random.uniform(20,1500,(1000,2))

im = vv.imread('D:/almar/projects/_p/mountain1.jpg')#[:,:,1]
#im = pl.imread('c:/projects/PYTHON/wiki.jpg')#[:-1,:,1]
#im = im.astype('float32')/255.0
im = im[:-1,:-1,0].astype('int16')-100


## lala

f = vv.figure() # generator function

a = vv.Axes(f)
a.cameraType = 'polar'


pos1 = 0.1,0.1,0.8,0.3
pos2 = 0.1, 0.5, 0.85, 0.4

a.position = pos1

# add points
l1 = vv.plot(pp, mw=20, ms='o', mc='r')
l2 = vv.plot([-20,-50,-30,-10],[20,60,10,10], [-30,-30,-30,-30], lw=3,mc='y', 
    markerWidth=30, markerStyle='>')

# add axes
l11=vv.plot([0,500],[0,0],[0,0],lineWidth=5,lineColor='r', markerWidth=0)
l12=vv.plot([0,0],[0,500],[0,0],lineWidth=5,lineColor='g', mw=0)
l13=vv.plot([0,0],[0,0],[0,500],lineWidth=5,lineColor='b', mw=0)

t1 = vv.imshow(im,axes=a)
#t1 = vv.datatypes.Texture2D(a,im)
b1 = vv.Box(f)
b2 = vv.textRender.Label(b1, r"\Leftarrow\Rightarrow\Uparrow\Downarrow", 'sans')
b2.text += 'the quick brown fox (012 xyz)'
b2.fontSize = 20
b1.position = 10,10,100,100
b2.position = 10,10,120,40
b2.bgcolor = 0.8,0.5,0.5

# add text
t2 = vv.textRender.Text(a,r"\pm\euro", 0,0,0, 'sans')
t2.textSize = 20

def fly(event):
    l2._points[:,0] = l2._points[:,0] + 2
    f.Draw()

flyTimer = vv.Timer(None,100,False)
flyTimer.Bind(fly)
flyTimer.Start()

a2 = vv.Axes(f)
a2.position = pos2
l3=vv.plot([1,3,5,2])
a2.xLabel = 'this is an xlabel (012 xyz)'
a2.yLabel = 'this is an ylabel (012 xyz)'
a.xLabel = 'testing (012 xyz)'

app.run()
