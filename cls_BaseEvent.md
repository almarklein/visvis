
---

#### <font color='#FFF'>baseevent</font> ####
# <font color='#00B'>class BaseEvent</font> #

Inherits from .

The BaseEvent is the simplest type of event.

The purpose of the event class is to provide a way to bind/unbind  to events and to fire them. At the same time, it is the place where the properties of the event are stored (such mouse location, key  being pressed, ...).

In Qt speak, an event is a combination of an event and a signal. Multiple callbacks can be registered to an event (signal-paradigm). A callback may chose to override previously registered callbacks by using setHandled(). If there are no handlers, or if the event is explicitly ignored (using the Ignore method) by **all** handlers, the event is propagated to the parent object (event paradigm).

To register or unregister a callback, use the Bind and Unbind methods When fired, all handlers that are bind to this event are called,  until the event is set as handled. The handlers are called with the  event object as an argument. The event.owner provides a reference of  what wobject/wibject fired the event.





**The BaseEvent class implements the following properties:**<br /><table cellpadding='10px'><tr>
<td valign='top'>
<a href='#eventName.md'>eventName</a><br /><a href='#hasHandlers.md'>hasHandlers</a><br /><a href='#modifiers.md'>modifiers</a><br /><a href='#owner.md'>owner</a><br /><a href='#type.md'>type</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>

**The BaseEvent class implements the following methods:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#Accept.md'>Accept</a><br /><a href='#Bind.md'>Bind</a><br /><a href='#Fire.md'>Fire</a><br /><a href='#Ignore.md'>Ignore</a><br /><a href='#Set.md'>Set</a><br /><a href='#SetHandled.md'>SetHandled</a><br /><a href='#Unbind.md'>Unbind</a><br /></td>
<td valign='top'>
</td>
<td valign='top'>
</td>
</tr></table>



---


## Properties ##

#### <font color='#FFF'>eventName</font> ####
### <font color='#070'>BaseEvent.eventName</font> ###

> The name of this event.


#### <font color='#FFF'>hasHandlers</font> ####
### <font color='#070'>BaseEvent.hasHandlers</font> ###

> Get whether this event has handlers registered to it.


#### <font color='#FFF'>modifiers</font> ####
### <font color='#070'>BaseEvent.modifiers</font> ###

> The modifier keys active when the event occurs.


#### <font color='#FFF'>owner</font> ####
### <font color='#070'>BaseEvent.owner</font> ###

> The object that this event belongs to.


#### <font color='#FFF'>type</font> ####
### <font color='#070'>BaseEvent.type</font> ###

> The type (class) of this event.




---


## Methods ##

#### <font color='#FFF'>!Accept</font> ####
### <font color='#066'>BaseEvent.Accept()</font> ###

> Accept the event, preventing it from being propagated to the parent object. When an event handler is called, the event is accepted by default.


#### <font color='#FFF'>!Bind</font> ####
### <font color='#066'>BaseEvent.Bind(func)</font> ###

> Add an eventhandler to this event.

> The callback/handler (func) must be a callable. It is called with one argument: the event instance, which contains the mouse  location for the mouse event and the keycode for the key event.




#### <font color='#FFF'>!Fire</font> ####
### <font color='#066'>BaseEvent.Fire(<code>*</code>eventArgs)</font> ###

> Fire the event, calling all functions that are bound to it, untill the event is handled (a handler returns True).

> If no handlers are present or if the event is explicitly ignored, the event is propagated to the owners parent. This only apples to events for which this is approprioate and only if eventArgs  are given.




#### <font color='#FFF'>!Ignore</font> ####
### <font color='#066'>BaseEvent.Ignore()</font> ###

> Clears the accept flag parameter of the event object. Clearing the  accept parameter indicates that the event receiver does not want  the event. If none of the handlers for this event do not want it, the event might be propagated to the parent object.


#### <font color='#FFF'>!Set</font> ####
### <font color='#066'>BaseEvent.Set(modifiers)</font> ###

> Set the event properties before firing it. In the base event the only property is the modifiers state, a tuple of the  modifier keys currently pressed.




#### <font color='#FFF'>SetHandled</font> ####
### <font color='#066'>BaseEvent.SetHandled(isHandled=True)</font> ###

> Mark the event as handled, preventing any subsequent handlers from being called. Use this in a custom handler to override the  existing  handler. The same behavior is obtained when the handler returns True.


#### <font color='#FFF'>!Unbind</font> ####
### <font color='#066'>BaseEvent.Unbind(func=None)</font> ###

> Unsubscribe a handler, If func is None, remove all handlers.





---

