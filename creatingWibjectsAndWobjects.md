[Wibjects](api_wibjectAndWobject.md) and [Wobjects](api_wibjectAndWobject.md) have a few methods you'll probably want to overload when implementing one. These are automatically called.

  * `OnDraw()` - To draw the object.
  * `OnDrawFast()` - To draw the object faster, when a normal draw would take relatively long.
  * `OnDrawShape(color)` - To draw the shape of the object in the specified color. To enable picking of the object.
  * `OnDrawScreen()` - Draw in screen coordinates. Used for example by the Text class. (Wibjects are always drawn in screen coordinates (using OnDraw).)
  * `OnDestroyGl()` - Implement this to clean up the objects OpenGl resources (if any). This method is called for example when an object is removed from a figure (it's OpenGl context).
  * `OnDestroy()` - Implement this to clean up any other resources. This is called when Destroy() is called on the object or any of its parents.

World objects can also implement the following methods:
  * `_GetLimits()` - To allow an axes to automatically determine its limits based on the objects in the scene.

I encourage the use of lazy programming: if your object
requires some sort of OpenGl objects such as textures display lists etc., verify on each `Ondraw()` that the objects exist, if not, create them (preferably
by calling a specific method for that). In `OnDestroyGl()` remove the objects from
OpenGL memory. This will transparently enable transferring objects from one
figure to another (which is another OpenGL context).

Destroying wibjects and wobjects happens by calling their `Destroy()` method.
This first destroys all its children and then calls `OnDestroy()` on itself.

Drawing happens by calling the `Draw()` method on the figure or axes. This
method prepares OpenGL and then calls `_DrawTree()` on each object (but you
don't need to know that) which calls `OnDraw()` on the object and then `_DrawTree` on all its children, thus the drawing tree unfolds.