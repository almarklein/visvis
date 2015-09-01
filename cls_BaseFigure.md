
---

#### <font color='#FFF'>basefigure</font> ####
# <font color='#00B'>class BaseFigure()</font> #

Inherits from [\_BaseFigure](cls__BaseFigure.md).

Abstract class representing the root of all wibjects.

A Figure is a wrapper around the OpenGL widget in which it is drawn;  this way different backends are possible. Each backend inherits this class and implements the required methods and makes sure all GUI events are translated to visvis events.

Since the figure represents the OpenGl context and is the root of the visualization tree; a Figure Wibject does not have a parent.

A Figure can be created with the function vv.figure() or vv.gcf().





**The BaseFigure class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#currentAxes.md'>currentAxes</a><br /><a href='#enableUserInteraction.md'>enableUserInteraction</a><br /><a href='#eventAfterDraw.md'>eventAfterDraw</a><br /><a href='#eventClose.md'>eventClose</a><br /><a href='#mousepos.md'>mousepos</a><br /><a href='#nr.md'>nr</a><br /></td>
<td valign='top'>
<a href='#parent.md'>parent</a><br /><a href='#position.md'>position</a><br /><a href='#relativeFontSize.md'>relativeFontSize</a><br /><a href='#title.md'>title</a><br /><a href='#underMouse.md'>underMouse</a><br /></td>
<td valign='top'>
</td>
</tr></table>

**The BaseFigure class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Clear.md'>Clear</a><br /><a href='#Destroy.md'>Destroy</a><br /><a href='#Draw.md'>Draw</a><br /><a href='#DrawNow.md'>DrawNow</a><br /><a href='#MakeCurrent.md'>MakeCurrent</a><br /><a href='#OnDraw.md'>OnDraw</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>currentAxes</font> ####
### <font color='#070'>BaseFigure.currentAxes</font> ###

> Get/Set the currently active axes of this figure.  Returns None if no axes are present.


#### <font color='#FFF'>enableUserInteraction</font> ####
### <font color='#070'>BaseFigure.enableUserInteraction</font> ###

> Whether to allow user interaction. The default is True. This property can be set to False to improve performance (expensive calls to glDrawPixels can be omitted).


#### <font color='#FFF'>eventAfterDraw</font> ####
### <font color='#070'>BaseFigure.eventAfterDraw</font> ###

> Fired after each drawing pass.


#### <font color='#FFF'>eventClose</font> ####
### <font color='#070'>BaseFigure.eventClose</font> ###

> Fired when the figure is closed.


#### <font color='#FFF'>mousepos</font> ####
### <font color='#070'>BaseFigure.mousepos</font> ###

> Get the position of the mouse in figure coordinates.


#### <font color='#FFF'>nr</font> ####
### <font color='#070'>BaseFigure.nr</font> ###

> Get the number (id) of this figure.


#### <font color='#FFF'>parent</font> ####
### <font color='#070'>BaseFigure.parent</font> ###

> The parent of a figure always returns None and cannot be set.


#### <font color='#FFF'>position</font> ####
### <font color='#070'>BaseFigure.position</font> ###

> The position for the figure works a bit different than for other wibjects: it only works with absolute values and it  represents the position on screen or the position in the  parent widget in an application.


#### <font color='#FFF'>relativeFontSize</font> ####
### <font color='#070'>BaseFigure.relativeFontSize</font> ###

> The (global) relative font size; all texts in this figure are scaled by this amount. This is intended to (slighly) increase or descrease font size in the figure for publication purposes.


#### <font color='#FFF'>title</font> ####
### <font color='#070'>BaseFigure.title</font> ###

> Get/Set the title of the figure. If an empty string or None,  will display "Figure X", with X the figure nr.


#### <font color='#FFF'>underMouse</font> ####
### <font color='#070'>BaseFigure.underMouse</font> ###

> Get the object currently under the mouse. Can be None.




---


## Methods ##

#### <font color='#FFF'>!Clear</font> ####
### <font color='#066'>BaseFigure.Clear()</font> ###

> Clear the figure, removing all wibjects inside it and clearing all callbacks.




#### <font color='#FFF'>!Destroy</font> ####
### <font color='#066'>BaseFigure.Destroy()</font> ###

> Close the figure and clean up all children.




#### <font color='#FFF'>!Draw</font> ####
### <font color='#066'>BaseFigure.Draw(fast=False, timeout=10)</font> ###

> Draw the figure within 10 ms (if the events are handled).  Multiple calls in a short amount of time will result in only one redraw.




#### <font color='#FFF'>DrawNow</font> ####
### <font color='#066'>BaseFigure.DrawNow(fast=False)</font> ###

> Draw the figure right now and let the GUI toolkit process its events. Call this from time to time if you want to update your figure while  running some algorithm, and let the figure stay responsive.




#### <font color='#FFF'>MakeCurrent</font> ####
### <font color='#066'>BaseFigure.MakeCurrent()</font> ###

> Make this the current figure.  Equivalent to "vv.figure(fig.nr)".




#### <font color='#FFF'>OnDraw</font> ####
### <font color='#066'>BaseFigure.OnDraw()</font> ###

> Perform the actual drawing. Called by the GUI toolkit paint event handler. Users should not call this method, but use Draw() or DrawNow().





---

