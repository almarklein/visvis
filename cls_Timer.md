
---

#### <font color='#FFF'>timer</font> ####
# <font color='#00B'>class Timer(owner, interval=1000, oneshot=True)</font> #

Inherits from [BaseEvent](cls_BaseEvent.md).

Timer class. You can bind callbacks to the timer. The timer is  fired when it runs out of time. You can do one-shot runs and  continuous runs.

Setting timer.nolag to True will prevent the timer from falling behind. If the previous Fire() was a bit too late the next Fire  will take place sooner. This will make that at an interval of  1000, 3600 events will have been fired in one hour.





**The Timer class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#isRunning.md'>isRunning</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The Timer class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Destroy.md'>Destroy</a><br /><a href='#Start.md'>Start</a><br /><a href='#Stop.md'>Stop</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>isRunning</font> ####
### <font color='#070'>Timer.isRunning</font> ###

> Get whether the timer is running.




---


## Methods ##

#### <font color='#FFF'>!Destroy</font> ####
### <font color='#066'>Timer.Destroy()</font> ###

> Destroy the timer, preventing it from ever fyring again.




#### <font color='#FFF'>!Start</font> ####
### <font color='#066'>Timer.Start(interval=None, oneshot=None)</font> ###

> Start the timer. If interval end oneshot are not given,  their current values are used.




#### <font color='#FFF'>!Stop</font> ####
### <font color='#066'>Timer.Stop()</font> ###

> Stop the timer from running.





---

