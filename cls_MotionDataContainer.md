
---

#### <font color='#FFF'>motiondatacontainer</font> ####
# <font color='#00B'>class MotionDataContainer(parent, interval=100)</font> #

Inherits from [Wobject](cls_Wobject.md), [MotionMixin](cls_MotionMixin.md).

The motion data container is a wobject that can contain several data, which are displayed as a sequence.

The data are simply stored as the wobject's children, and are made visible one at a time.

<b><u><font color='#A50'>Example</font></u></b><br />
```
# read image
ims = `[`vv.imread('lena.png')`]`

# make list of images: decrease red channel in subsequent images
for i in range(9):
    im = ims`[`i`]`.copy()
    im`[`:,:,0`]` = im`[`:,:,0`]``*`0.9
    ims.append(im)

# create figure, axes, and data container object
a = vv.gca()
m = vv.MotionDataContainer(a)

# create textures, loading them into opengl memory, and insert into container.
for im in ims:
    t = vv.imshow(im)
    t.parent = m

```


**The MotionDataContainer class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#timer.md'>timer</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>timer</font> ####
### <font color='#070'>MotionDataContainer.timer</font> ###

> Get the timer object used to make the objects visible.  For backward compatibility.



---

