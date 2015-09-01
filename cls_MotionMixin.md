
---

#### <font color='#FFF'>motionmixin</font> ####
# <font color='#00B'>class MotionMixin(axes)</font> #

Inherits from [object](cls_object.md).

A generic class that represents a wobject that has motion.

This class implements the basic methods to control motion. It uses the concept of the motionIndex, which is basically the time parameter. Its value specifies the position in the motion sequence with a scalar (float) value. Some motion wobject implementations may only support integer values though, in which case they should round the motionIndex.

Inheriting classes should implement `_`GetMotionCount() and  `_`SetMotionIndex(index, ii, ww), where ii are four indices, and ww are four weights. Together they specify a spline.



**The MotionMixin class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#motionCount.md'>motionCount</a><br /><a href='#motionIndex.md'>motionIndex</a><br /><a href='#motionIsCyclic.md'>motionIsCyclic</a><br /><a href='#motionSplineType.md'>motionSplineType</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The MotionMixin class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#MotionPlay.md'>MotionPlay</a><br /><a href='#MotionStop.md'>MotionStop</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>motionCount</font> ####
### <font color='#070'>MotionMixin.motionCount</font> ###

> Get the number of temporal instances of this object. For objects that do not have a fixed number of elements, the returned number may be an arbitrary large number above one thousand.


#### <font color='#FFF'>motionIndex</font> ####
### <font color='#070'>MotionMixin.motionIndex</font> ###

> Get/set the motion index; the temporal position in the motion. With N the motionCount, if the motion is cyclic, the  valid range is `[`0, N>, otherwise `[`0,N-1`]`. If the given index is not in the valid range, its modulo is taken (cyclic) or  the index is clipped (not cyclic).


#### <font color='#FFF'>motionIsCyclic</font> ####
### <font color='#070'>MotionMixin.motionIsCyclic</font> ###

> Get/set whether the motion is cyclic. Default True.


#### <font color='#FFF'>motionSplineType</font> ####
### <font color='#070'>MotionMixin.motionSplineType</font> ###

> Get/set the spline type to interpolate the motion. Can be 'nearest', 'linear', 'cardinal', 'B-spline', or a float between -1 and 1 specifying the tension of the cardinal spline. Note that the B-spline is an approximating spline. Default 'linear'. Note that an implementation may not support interpolation of the temporal  instances.




---


## Methods ##

#### <font color='#FFF'>MotionPlay</font> ####
### <font color='#066'>MotionMixin.MotionPlay(interval=100, delta=1)</font> ###

> Start playing the motion.

> This starts a timer that is triggered every interval miliseconds. On every trigger the motionIndex is increased by delta.




#### <font color='#FFF'>MotionStop</font> ####
### <font color='#066'>MotionMixin.MotionStop()</font> ###

> Stop playing the motion.





---

