
---

#### <font color='#FFF'>baseobject</font> ####
# <font color='#00B'>class BaseObject(parent)</font> #

Inherits from [object](cls_object.md).

The base class for wibjects and wobjects. Instances of classes inherited from this class represent  something that can be drawn.

Wibjects and wobjects can have children and have a parent  (which can be None in which case they are in orphan and never  drawn). To change the structure, use the ".parent" property.  They also can be set visible/invisible using the property ".visible".





**The BaseObject class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#children.md'>children</a><br /><a href='#eventDoubleClick.md'>eventDoubleClick</a><br /><a href='#eventEnter.md'>eventEnter</a><br /><a href='#eventKeyDown.md'>eventKeyDown</a><br /><a href='#eventKeyUp.md'>eventKeyUp</a><br /><a href='#eventLeave.md'>eventLeave</a><br /><a href='#eventMotion.md'>eventMotion</a><br /></td>
<td valign='top'>
<a href='#eventMouseDown.md'>eventMouseDown</a><br /><a href='#eventMouseUp.md'>eventMouseUp</a><br /><a href='#eventScroll.md'>eventScroll</a><br /><a href='#hitTest.md'>hitTest</a><br /><a href='#parent.md'>parent</a><br /><a href='#visible.md'>visible</a><br /></td>
<td valign='top'>
</td>
</tr></table>

**The BaseObject class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Destroy.md'>Destroy</a><br /><a href='#DestroyGl.md'>DestroyGl</a><br /><a href='#Draw.md'>Draw</a><br /><a href='#FindObjects.md'>FindObjects</a><br /></td>
<td valign='top'>
<a href='#GetFigure.md'>GetFigure</a><br /><a href='#GetWeakref.md'>GetWeakref</a><br /><a href='#OnDestroy.md'>OnDestroy</a><br /><a href='#OnDestroyGl.md'>OnDestroyGl</a><br /></td>
<td valign='top'>
<a href='#OnDraw.md'>OnDraw</a><br /><a href='#OnDrawFast.md'>OnDrawFast</a><br /><a href='#OnDrawScreen.md'>OnDrawScreen</a><br /><a href='#OnDrawShape.md'>OnDrawShape</a><br /></td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>children</font> ####
### <font color='#070'>BaseObject.children</font> ###

> Get a shallow copy of the list of children.


#### <font color='#FFF'>eventDoubleClick</font> ####
### <font color='#070'>BaseObject.eventDoubleClick</font> ###

> Fired when the mouse is double-clicked on this object.


#### <font color='#FFF'>eventEnter</font> ####
### <font color='#070'>BaseObject.eventEnter</font> ###

> Fired when the mouse enters this object or one of its children.


#### <font color='#FFF'>eventKeyDown</font> ####
### <font color='#070'>BaseObject.eventKeyDown</font> ###

> Fires when the mouse is moved over the object. Not fired when the mouse is over one of its children.


#### <font color='#FFF'>eventKeyUp</font> ####
### <font color='#070'>BaseObject.eventKeyUp</font> ###

> Fires when the mouse is moved over the object. Not fired when the mouse is over one of its children.


#### <font color='#FFF'>eventLeave</font> ####
### <font color='#070'>BaseObject.eventLeave</font> ###

> Fired when the mouse leaves this object (and is also not over any of it's children).


#### <font color='#FFF'>eventMotion</font> ####
### <font color='#070'>BaseObject.eventMotion</font> ###

> Fires when the mouse is moved over the object. Not fired when the mouse is over one of its children.


#### <font color='#FFF'>eventMouseDown</font> ####
### <font color='#070'>BaseObject.eventMouseDown</font> ###

> Fired when the mouse is pressed down on this object. (Also  fired the first click of a double click.)


#### <font color='#FFF'>eventMouseUp</font> ####
### <font color='#070'>BaseObject.eventMouseUp</font> ###

> Fired when the mouse is released after having been clicked down on this object (even if the mouse is now not over the object). (Also fired on the first click of a double click.)


#### <font color='#FFF'>eventScroll</font> ####
### <font color='#070'>BaseObject.eventScroll</font> ###

> Fires when the scroll wheel is used while over the object.  Not fired when the mouse is over one of its children.


#### <font color='#FFF'>hitTest</font> ####
### <font color='#070'>BaseObject.hitTest</font> ###

> Get/Set whether mouse events are generated for this object. From v1.7 this property is set automatically, and need not be set  to receive mouse events.


#### <font color='#FFF'>parent</font> ####
### <font color='#070'>BaseObject.parent</font> ###

> Get/Set the parent of this object. Use this to change the tree structure of your visualization objects (for example move a line from one axes to another).


#### <font color='#FFF'>visible</font> ####
### <font color='#070'>BaseObject.visible</font> ###

> Get/Set whether the object should be drawn or not.  If set to False, the hittest is also not performed.




---


## Methods ##

#### <font color='#FFF'>!Destroy</font> ####
### <font color='#066'>BaseObject.Destroy()</font> ###

> Destroy the object.
    * Removes itself from the parent's children
    * Calls Destroy() on all its children
    * Calls OnDestroyGl and OnDestroy on itself

> Note1: do not overload, overload OnDestroy().  Note2: it's best not to reuse destroyed objects. To temporary disable an object, better use "ob.parent=None", or "ob.visible=False".




#### <font color='#FFF'>DestroyGl</font> ####
### <font color='#066'>BaseObject.DestroyGl()</font> ###

> Destroy the OpenGl objects managed by this object.
    * Calls DestroyGl() on all its children.
    * Calls OnDestroyGl() on itself.

> Note: do not overload, overload OnDestroyGl().




#### <font color='#FFF'>!Draw</font> ####
### <font color='#066'>BaseObject.Draw(fast=False)</font> ###

> For wibjects: calls Draw() on the figure that contains this object. For wobjects: calls Draw() on the axes that contains this object.




#### <font color='#FFF'>FindObjects</font> ####
### <font color='#066'>BaseObject.FindObjects(pattern)</font> ###

> Find the objects in this objects' children, and its childrens children, etc, that correspond to the given pattern.

> The pattern can be a class or tuple of classes, an attribute name  (as a string) that the objects should have, or a callable that  returns True or False given an object. For example 'lambda x: ininstance(x, cls)' will do the same as giving a class.

> If 'self' is a wibject and has a `_`wobject property (like the Axes wibject) this method also performs the search in the list of wobjects.




#### <font color='#FFF'>GetFigure</font> ####
### <font color='#066'>BaseObject.GetFigure()</font> ###

> Get the figure that this object is part of. The figure represents the OpenGL context. Returns None if it has no figure.




#### <font color='#FFF'>GetWeakref</font> ####
### <font color='#066'>BaseObject.GetWeakref()</font> ###

> Get a weak reference to this object.  Call the weakref to obtain the real reference (or None if it's dead).




#### <font color='#FFF'>OnDestroy</font> ####
### <font color='#066'>BaseObject.OnDestroy()</font> ###

> Overload this to clean up any resources other than the GL objects.




#### <font color='#FFF'>OnDestroyGl</font> ####
### <font color='#066'>BaseObject.OnDestroyGl()</font> ###

> Overload this to clean up any OpenGl resources.




#### <font color='#FFF'>OnDraw</font> ####
### <font color='#066'>BaseObject.OnDraw()</font> ###

> Perform the opengl commands to draw this wibject/wobject.  Objects should overload this method to draw themselves.


#### <font color='#FFF'>OnDrawFast</font> ####
### <font color='#066'>BaseObject.OnDrawFast()</font> ###

> Overload this to provide a faster version to draw (but less pretty), which is called when the scene is zoomed/translated. By default, this calls OnDraw()




#### <font color='#FFF'>OnDrawScreen</font> ####
### <font color='#066'>BaseObject.OnDrawScreen()</font> ###

> Draw in screen coordinates. To be used for wobjects that need drawing in screen coordinates (like text). Wibjects are  always drawn in screen coordinates (using OnDraw).




#### <font color='#FFF'>OnDrawShape</font> ####
### <font color='#066'>BaseObject.OnDrawShape(color)</font> ###

> Perform  the opengl commands to draw the shape of the object in the given color.          If not implemented, the object cannot be picked.





---

