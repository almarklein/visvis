import visvis as vv
import numpy as np
from scipy.spatial import Delaunay

vxyz = patternObj.obsPoints.xyz
fig = vv.figure()
fig._bgcolor = [0.95, 0.95, 0.95]
ax = vv.gca()
ax.bgcolor = [0.95, 0.95, 0.95]
dly = Delaunay(vxyz)
meshIndx = dly.convex_hull
# some facets are backwards. Take the cross prod
# of two triangle mesh sides and compare them
# to one of the triangle vertex data points by taking
# the dot prod. The sign of the dot prod is used to
# change the triangle vertex order for backwards
# faces
for index, (I1, I2, I3) in enumerate(meshIndx):
    a = vxyz[I1,:] - vxyz[I2,:]
    b = vxyz[I2,:] - vxyz[I3,:]
    c = a.crossProd(b)
    if c.dotProd(vxyz[I2,:]) > 0:
        meshIndx[index] = (I1, I3, I2)

thetaPhi = patternObj.obsPoints.thetaPhi
#['dB', 'contour', 'polEff', 'polVec']
if dependValue=='dB' or dependValue=='contour':
    db = patternObj.field.totalField.u('dB')
    db[db < -40] = -40
    db = db - np.min(db)
    if dependValue=='dB':
        vxyz[:,0]= db.T*np.sin(thetaPhi[:,0])*np.cos(thetaPhi[:,1])
        vxyz[:,1] = db.T*np.sin(thetaPhi[:,0])*np.sin(thetaPhi[:,1])
        vxyz[:,2] = db.T*np.cos(thetaPhi[:,0])
        ax.SetLimits(rangeX=[-40,40], rangeY=[-40,40], rangeZ=[-40, 40])
#dbxyz = vector(np.array([[x],[y],[z]]).T)

ms = vv.Mesh(ax,vxyz, normals=vxyz, faces=meshIndx)
ms.SetTexcords(np.reshape(db,np.size(db))/40)
ms.ambient = ambient
ms.diffuse = diffuse
ms.colormap = colormap
ms.faceShading = faceShading
ms.edgeColor = edgeColor
ms.edgeShading = edgeShading
ms.faceColor = faceColor
ms.shininess = shininess
ms.specular = specular
ms.emission = emission
