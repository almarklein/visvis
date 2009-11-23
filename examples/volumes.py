import visvis as vv
import numpy as np
app = vv.App('wx')
vv.clf()

# create volume
vol = np.zeros((128,128,128), dtype=np.float32)
vol[50:70,80:90, 10:100] = 0.2
vol[50:70,10:100,80:90] = 0.5
vol[10:100,50:70,80:90] = 1

# set labels
vv.xlabel('x axis')
vv.ylabel('y axis')
vv.zlabel('z axis')

# show
vv.volshow(vol)

app.run()
