
---


## Events ##

Visvis has a simple yet powerful event system. Each wobject and wibject
has a number of event properties, all starting with "event", for example
`eventMouseDown`.

Each event object has the following methods:
  * **Bind(callable)** - Register a callback for the event.
  * **Unbind(callable)** - Unregister a callback for the event. If callable is None, unregister all callbacks.
  * **Fire(...)** - Fires the event (this should usually be left to visvis' internal event handling system). Optionally, a set of arguments can be given, which are then used to call `Set()` automatically.
  * **Set(...)** - Depending on the event class, sets the properties such as mouse position or key being pressed.

For the event handler there are a couple of other methods:
  * **Accept()** - To explicitly accept the event so that it does not propagate to the parent. When an event handler is called, the event is accepted by default.
  * **Ignore()** - Clears the accept flag parameter of the event object, allowing the event to propagate to the parent object.
  * **SetHandled(isHandled=True)** - Mark the event as handled, preventing any subsequent handlers from being called.

When fired, all handlers that are bound to the event are called,
until the event is handled (SetHandled() is called, or a handler returns True). The handlers
are called with the event object as an argument, the last added handlers are called first.

There are three base event classes, which each have different properties. See the documentation of the [BaseEvent](cls_BaseEvent.md), [MouseEvent](cls_MouseEvent.md) and [KeyEvent](cls_KeyEvent.md) for more information.


## Types of events ##

All wibjects and wobjects have the following events:
  * [eventMouseDown](cls_EventMouseDown.md) `*`
  * [eventMouseUp](cls_EventMouseUp.md)
  * [eventDoubleClick](cls_EventDoubleClick.md) `*`
  * [eventEnter](cls_EventEnter.md)
  * [eventLeave](cls_EventLeave.md)
  * [eventMotion](cls_EventMotion.md)
  * [eventKeyDown](cls_EventKeyDown.md) `*`
  * [eventKeyUp](cls_EventKeyUp.md) `*`
  * [eventScroll](cls_EventScroll.md) `*`


All Wibjects also have [eventPosition](cls_EventPosition.md) which is fired when its position changes. Some classes, such as the Figure and PushButton implement more events. See their documentation for more information.

The events marked with a `*` are propagated to the parent object if necessary.

The EventMouseUp is fired when the user clicked down on the object and now releases the mouse (even if the mouse is not over the object anymore).

The enter event is fired when the mouse enters the object or any of its
children. The leave event is fired when the mouse was previously over the object or any of its children, and is now not.

The EventMotion is fired for all objects that have handlers registered to it, where-ever the mouse is moving.

Key events are fired only on the object that is under the mouse, and the event is propagated if not handled. The figure, however, is guaranteed to always get each key event.


## Picking ##

Picking of wobjects can be done easily, even when using a 3D camera. This is realized by having an additional render pass in which each item draws in a color specific to its ID. That way, the item under the mouse can be retrieved fast and easily.

See [the picking example](example_picking.md).

## Timers ##

The [Timer](cls_Timer.md) class inherits from the [BaseEvent](cls_BaseEvent.md) class, and thus also has the Bind, Unbind(), and Fire() methods.

The Timer class, however, is fired automatically at a certain interval. It has the following methods:
  * init(owner, interval=1000, oneshot=True)
  * Start(interval=None, oneshot=None) - Uses the interval and oneshot set at initialization by default.
  * Stop()

Furthermore it has a (readonly) property to determine whether the timer is running:
`isRunning`.

The Timer class is used in the MotionDataContainer class to redraw at a regular interval.


---
