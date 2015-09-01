If you have a question that's not in the list, feel free to post a message in the discussion group or e-mail me.


---


**Why won't Visvis render 3D data on my system?**

Your system probably has an OpenGl version < 2.0. This means that shading code (GLSL) cannot be used, which is necessary to render volumes.

**Why does rendering 3D data on my system take so long?**

If rendering works, but takes a very long time, you probably do not have a suitable video card to render in hardware. In this case, it might be better to set "vv.settings.volsshowPreference" to 2, such that visvis will display volumes using slices.

**Why do the texture2D.colormap and texture2D.clim property have no effect?**

Your system probably has an OpenGl version < 2.0. This means that shading code (GLSL) cannot be used. This is necessary for the colormap and clim properties. You can use the setClim() method though.


**What if the difference with Matplotlib?**

The advantage of Visvis over Matplotlib is that it can plot 3D data such as 3D
lines and points, and 3D renderings of volumetric data (such as CT or MRI
data). Also, because it uses OpenGl, displaying images, and zooming/panning them is much
faster in Visvis. Visvis is also designed to be extendable. If you know a bit of OpenGl
you can easily create your own objects and place them in a scene with other objects.

I tried to make Visvis a relatively complete visualization library by
enabling easy plotting, with support for labels, title, legend, etc.
However, compared to Matplotlib, Visvis' 2D plotting capabilities are very limited. I
plan to extend these a bit, by for example providing support for bar plots, but I do not
intend to go much further than that.

So you might say that Visvis is more focused at 3D visualization, and
leaves the advanced 2D visualization to Matplotlib. But there is of course some
overlap.


**What is the difference with Mayavi?**

One major difference is the fact that Mayavi is build on top of VTK, while Visvis is directly build on top of OpenGl (which is also the base for VTK). This would make Visvis probably a bit more lightweight.

Since OpenGl allows more control, Visvis gives users more freedom to
create their own objects, and for example different volume renderers
can relatively easily be implemented (in GLSL). Mayavi, on the other
hand, can make use of a lot of fancy VTK features.

Another difference is that Visvis is designed using an object oriented approach, which
makes it transparent and easy to use; each object in the
scene has a number of properties that can be changed to influence the
behavior or appearance (for example interpolation or anti aliasing of a texture).
In contrast, VTK adopts an approach in which a visualization pipeline is set up.
Mayavi seems to handle this behind the scene nicely though.


---
