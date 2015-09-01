
---


## Future work ##

I am now focusing my energy on [Vispy](http://vispy.org), and leave work
on Visvis limited to maintenance such as fixing bugs and implementing small
features. Vispy will eventually replace Visvis, but at this time it is still
in development and can not yet replace Visvis.


## Release 1.9 (26-12-2012) ##

  * [issue 65](https://code.google.com/p/visvis/issues/detail?id=65): Line.Set\*data does not accept a list, neither a np.array of integers
  * Can now render text in xkcd font
  * Simplified lighting in volume rendering, thereby making it work on more systems

  * Added medical image volume: vv.volread('stent')
  * Fixes related to freezing: [issue 67](https://code.google.com/p/visvis/issues/detail?id=67), [issue 68](https://code.google.com/p/visvis/issues/detail?id=68)
  * Textures support more numpy types: [issue 69](https://code.google.com/p/visvis/issues/detail?id=69), [issue 70](https://code.google.com/p/visvis/issues/detail?id=70)
  * Can use imageio library for reading/saving images
  * Better handling of invalid values in Line class (plotting)
  * Fixed error in surf()
  * If an NxM ndarray is given to vv.plot(), and M is in (2,3), it is shown as x-y(-z) plot.
  * Support for wx Phoenix (by Keith Smith)



## Release 1.8 (17-12-2012) ##

  * [issue 52](https://code.google.com/p/visvis/issues/detail?id=52): Better separation of widget and figure creation, making it easier to embed visvis in threaded applications.
  * [issue 61](https://code.google.com/p/visvis/issues/detail?id=61): Better handling of NaN, Inf in line objects, barplots, boxplots, and calculation of axes limits.
  * [issue 63](https://code.google.com/p/visvis/issues/detail?id=63): Fixed potential memory leak in case many textures/meshes are created and destroyed.
  * Fixes issues related to fig.enableUserInteraction = False ([issue 57](https://code.google.com/p/visvis/issues/detail?id=57))
  * [issue 60](https://code.google.com/p/visvis/issues/detail?id=60): Improved the (api of) the surf function
  * The bar plot now supports the `bottom` keyword, allowing for stacked bar charts.
  * Fixed that imwrite() did not accept RGBA
  * Meshes can now be made (semi)transparent by giving RGBA values to mesh.faceColor.
  * Better alignment of rotated x-ticks.
  * Integration with Pyzo. In particular, visvis now looks in Pyzo's shared directory when looking for the freetype lib.
  * Visvis now stores its config file locally if running in a portable distribution (see https://code.google.com/p/iep/issues/detail?id=99)


## Release 1.7 (22-08-2012) ##

  * Support for Python 3 (see comment below) ([issue 35](https://code.google.com/p/visvis/issues/detail?id=35))
  * PySide backend ([issue 31](https://code.google.com/p/visvis/issues/detail?id=31))
  * Full Unicode support (see comment below) ([issue 25](https://code.google.com/p/visvis/issues/detail?id=25))
  * Much more beautiful text, particularly at large font sizes ([issue 25](https://code.google.com/p/visvis/issues/detail?id=25))
  * Introduction of eventScroll, which is used to zoom an axes (isue 34)
  * Improvements to the event system (see comment below)
  * Wobject class has new `TransformPoint` method.
  * Line class has new readonly `points` property.
  * Figure class has new `enableUserInteraction` property.
  * Added a 'utils' subackage for code related to, but not part of visvis.
  * The utils subpackage contains a Cython based Marching Cubes algorithm
  * 2D camera also applies lighting.
  * Visvis is now installable using pip ([issue 37](https://code.google.com/p/visvis/issues/detail?id=37))
  * Reading and writing images via imageio ([issue 38](https://code.google.com/p/visvis/issues/detail?id=38))
  * All functions have an example at the bottom of the script.
  * Added gif image that can be used as an example ('newtonscradle.gif')
  * io package is renamed to vvio (because a name conflict broke the pip installation), and is now lazy-loaded (only when needed).
  * Fixed an issue with sprites not working (revision e868aeb399d2)
  * [issue 39](https://code.google.com/p/visvis/issues/detail?id=39), [issue 50](https://code.google.com/p/visvis/issues/detail?id=50), [issue 43](https://code.google.com/p/visvis/issues/detail?id=43), [issue 48](https://code.google.com/p/visvis/issues/detail?id=48)


**Notes on Python 3:**
At the time of writing the latest PyOpenGl release does not yet support Python3. Python3 users should therefore install the 'bleeding edge' version of PyOpenGl from its repository. _edit: PyOpenGl 3.0.2b2 was released on August 22._

**Notes on text rendering:**
Visvis now renders text using the FreeType library. If the library is not installed, visvis falls back to the old (pre-rendered font) approach. On Linux FreeType is usually already installed. Windows users can easily install it from the visvis download page.

**Notes on the improvements to the event system:**
  * An object does not need its hitTest property to be set; this is now done automatically
  * An event handler can explicitly `Ignore()` an event.
  * If an event has no registered handlers, or if the event is ignored by all handlers, the event is propagated to the parent object. This applies to a selection of events for which this makes sense.
  * An event handler can explicitly set an event as handled using  `SetHandled()`, which prevents any next handlers from receiving the event. This is equivalent to the existing behavior of the handler returning True.
  * These changes should make old code related to mouse events behave in exactly the same way, yet open possibilities for new code.
  * Key events are now explicitly send to the object that the mouse is currently over (and propagates as described above if necessary). The figure class is guaranteed to always receive a key event.
  * In rare circumstances this can change the behavior of old code related to key events; in previous versions all handlers bound to **any** object were called on each key event.


## Release 1.6 (24-04-2012) ##

The major changes in this release are related to the shading code, 3D rendering techniques and better support for motion data.

Changes to the use of shading code (GLSL):

Visvis now uses a very flexible system for its shading code, that allows replacing arbitrary parts with new pieces of code. This allows for much better code reuse between the different shaders (which have a significant part that is the same). In addition, it allows users to easily embed pieces of GLSL code to implement certain specific visualization techniques. See the [unsharp masking example](example_unsharpMasking.md) and the [image edges example](example_imageEdges.md). Further ...

  * There are now five well-defined render styles: 'mip', 'iso', 'edgeray', 'ray' and 'litray'. See the [Texture3D.renderStyle](cls_Texture3D#Texture3D.renderStyle.md) property and the [example](example_volumeRenderStyles.md).
  * Improvements to isosurface volume rendering (smoother surfaces).
  * Volume rendering now works correctly in projective view.
  * Shader code for lighting is now shared between Texture3D and Mesh classes. Both classes now use the blinn-phong light model and can handle multiple light sources.
  * Errors in compiling and linking of shader code are handled more gracefully.
  * Anti-aliasing for 2D textures now uses a Lanczos kernel instead of a Gaussian, so the result is less blurred.

Motions:

  * Introducing the [MotionMixin](cls_MotionMixin.md) class, that defines a generic API for all Wobjects that have motion. The [MotionDataContainer](cls_MotionDataContainer.md) class uses this API.
  * There are new classes to specify moving textures: [MotionTexture2D and [cls\_MotionTexture3D MotionTexture3D](cls_MotionTexture2D.md).


Meshes:

  * Meshes now use the right-hand-rule to determine which side of the face is the front.
  * The vv.processing.lineToMesh function now supports specifying a value for each point.
  * New functions [meshRead](functions#meshRead.md) and [meshWrite](functions#meshWrite.md). Can read STL, Wavefront .obj files, and a format based on ssdf.
  * Added stanford bunny model: try `vv.mesh(vv.meshRead('bunny.ssdf'))`.
  * Replaced teapot model with a nicer version that does not show the ugly ridges.

Other changes:

  * Property decorators do not anymore use the evil `settrace` function.
  * Colorbars can now also have labels.
  * More intuitive usage of daspect; it is now a property of the camera (but still accessible via the Axes.daspect property.
  * Support for boxplot and violin plot (kde), see the [boxplot function](functions#boxplot.md) and the [example](example_statistics.md).
  * Axes can have a gradient as a background (see the [Axes.bgcolors](cls_Axes#Axes.bgcolors.md) property).
  * Removed lots of unnecessary imports detected by pyflakes.
  * Lots of other fixes ...




## Release 1.5 (21-06-2011) ##

This release contains many changes suggested and implemented by Robert. His fresh look on things has already helped improving visvis as lot. Most notably are the GTK backend and improvements to the backends in general, changes to the Mesh class, and improvements of the camera classes.


Here's a list of the most notable changes in this release:
  * Cameras are much better exposed to the user and the axes.daspect property is used more natural now. See below for a complete list.
  * IMPORTANT: the signature of the Mesh class was changed to make it more intuitive. The old signature if still supported but may be removed in future versions.
  * Added convenience functions mesh(), help(), reportIssue()
  * Visvis now has a Colormapable mix class. All classes inheriting from it can be 'colormapped' using the colormap editor (and the colorbar shows their current colormap). These classes have a `clim` propery and a SetClim() method. The Mesh class and texture classes are color-mappable.
  * Did some major refactoring to better organize the growing amount of modules.
  * Visvis now also has a GTK backend. Thanks Robert!
  * General improvements to all backends.
  * Visvis now has a settings object, which can be used to change user-specific defaults, such as the preferred backend and the size of new figures.
  * Added test in imshow and volshow to test if array has zero elements.
  * New ssdf module, which now also features a binary file format.
  * The GIF writer now supports sub-rectangles (contributed by Alex Robinson), which enables much more efficient files if only part of the scene changes.
  * 3D color data can now be rendered (requested by Asmi).
  * Visvis now has the notion of the DELETE key.
  * the screenshot() function now has a format specifier so the file extension can be user-defined.
  * The 3D camera now also has a perspective view. Use shift+RMB to interactively change the field of view. Great work by Robert.
  * Implemented volshow2(), which displays a volume using three 2D slices, which can be moved interactively through the volume. Visvis automatically falls back to this way of visualization if 3D volume rendering is not possible on the client hardware.
  * Made MIP and isosurface renderer set the depth value for the fragment. This means that the renders can much easier be combined with for example a SliceTexture instance.
  * Added a couple of examples.


Changes to camera system:
  * The cameras are now more explicitly exposed to the user, and are listed on the wiki API page.
  * Reimplemented the [FlyCamera](cls_FlyCamera.md) so it is much easier to control. Some gaming experience will still help though :) see the [meshes example](http://code.google.com/p/visvis/wiki/example_meshes) for a movie.
  * Changed camera behavior of axes.daspectAuto. Previously it meant that axes.daspect was ignored. Now it means that axes.daspect is automatically modified by the camera to nicely fit the data on screen.
  * By default, cameras can now be selected using the keyboard by holding ALT and pressing any of the number keys (1,2,3 for Fly, 2D and 3D camera respectively).
  * Made it easier for the user to set a new camera, for example to use a single camera for multiple axes. See the new axes.camera property. This also makes it easier to create a whole new camera class and use that.


Some of the many fixed issues:
  * The "key" value of key events now always corresponds to the lowercase version of a letter, regardless whether SHIFT is down.
  * Fixed that the lower right border of a widget was drawn one pixel too far.
  * Mouse-driven translation now occurs in plane perpendicular to the camera.
  * Fixed bug in calculating normals for mesh objects.
  * Fixed bug that prevented the user from given RGBA colors to mesh objects.
  * Fixed [issue 19](https://code.google.com/p/visvis/issues/detail?id=19) (Key events no longer work on wx).
  * Fixed [issue 20](https://code.google.com/p/visvis/issues/detail?id=20).
  * Fixed wx backend (in newer versions there is no Parent property).
  * Fixed downsampling of texture data (made it also more lightweight).


## Release 1.4 (16-12-2010) ##

Much work has been done since the previous release. Visvis has made a few important steps towards maturity. Also, Visvis is now BSD-licensed.

The scenes are now automatically redrawn when an object's property is changed, and the Axes objects buffer their contents so they can redraw much faster when nothing has changed (for example when using multiple subplots).

Using new functions movieRead and movieWrite, movies can be imported and exported to/from animated GIF, SWF (flash), AVI (needs ffmpeg), and a series of images. Visvis now uses guisupport.py, enabling seamless integration in the IEP and IPython interactive event loops.

Furthermore, many docstrings have been improved and so has the script that creates the online API documentation from them. Several examples have been added and all examples are now available via the website (including images and animation).

  * Visvis is now BSD-licensed.
  * Visvis now uses the new pypoints module see [here](points_pypoints.md) for conversion tips.
  * Figure windows show icons for the wx and qt4 backends.
  * Setting a property now automatically invokes a redraw. The same goes for methods that change the appearance of an object.
  * The contents of axes is buffered, such that if nothing has changed, it can be redrawn much faster.
  * Axes.axis.xTicks, yTicks, zTicks now also accept dictionaries that map scalars to strings, enabling advanced personalization of the tickmarks.
  * The axis instance of an Axes is not removed when using Axes.Clear(), so that any applied settings to the axis are maintained.
  * Added Slider and RangeSlider wibjects.
  * Added ClimEditor tool.
  * Enabled taking a screenshot of axes.parent (an AxesContainer instance), so that tickmarks are included.
  * New functions: movieRead, movieWrite, movieShow.
  * Support reading and writing movies (SWF, GIF, AVI, and series of images, previously visvis only supported writing SWF and GIF).
  * Significantly improved the quality of exported animated GIF (thanks to Ant1).
  * GIF can now also be exported to the superior NeuQuant quantisation algorithm (thanks to Marius).
  * The Recorder object (see vv.record) now uses vv.movieWrite().
  * Fixed in issue were textures would not work on some older ATI cards.
  * Visvis uses guisupport.py, which enables seamless integration in the IEP and IPython interactive event loops.
  * Improved all docstrings and the wikimaker to produce the on-line API reference.
  * Fixed issue when data was plotted that had a very large range.
  * imshow() and volshow() now correctly chose a color range (`clim`) even if the data contains NAN's and INF's.
  * Created several new examples. The examples are now also shown on the website (with resulting images/animations).
  * Loads of bug fixes ...


---


## Release 1.3.1 (06-07-2010) ##
Bug fix release.

  * Fixes [issue 10](https://code.google.com/p/visvis/issues/detail?id=10)
  * Fixes [issue 11](https://code.google.com/p/visvis/issues/detail?id=11)


## Release 1.3 (29-06-2010) ##

The main changes involved the implementation of lights and the Mesh class. Other notable
new features are polar plots (thanks Curt) and the introduction of the Axis class. Since the release of v1.2 I've also switched
from using SVN to Mercurial because it just seems more "right" and makes it easier
to merge code from other contributers.

### API changes ###
  * Introduced the Axis class (and derivatives) that handle the drawing of lines and ticks. Previously this functionality was contained in the Axes class. The separation makes for cleaner code and enables new features, such as the polar plot.
  * All properties that do something to the axis have been moved from the Axes to the Axis class. These can be easily accessed using the new Axes.axis property.

### New features ###
  * Implementation of lighting using the Light class. The Axes.light0 and Axes.lights properties can be used to control lighting.
  * Implementation of the BaseMesh and Mesh classes to manage quad and triangular meshes is a generic way. The mesh colors and lighting/reflection properties can be easily changed, as well as the shading of the faces and edges. Textures can be applied to meshes, as well as colormaps, or colors can be explicitly specified for each vertex.
  * Introduced a subpackage called "processing" to contain processing algorithms, mainly intended for the generation of and calculation on meshes, such as automatically generating the normals.
  * Several functions were added to easily create basic shapes: boxes, spheres, cylinders, cones, rings (donuts), lines (from a list of points) and, of course, teapots.
  * A mixin class was introduced to easily orient Wobjects. An OrientableMesh class is now also available (this is what most of the above functions return).
  * A surf function was created to create lit surface plots.
  * Curt implemented polar plots.
  * Implemented 3D bar charts.
  * User defined axis ticks can now also be strings.
  * Introduced the Figure.relativeFontSize property to increase font size to produce better looking screenshots for publication.

### Other changes ###
  * The 3D camera is now the default.
  * daspectAuto is now False by default.
  * All functions will set the camera to the correct type, set the daspectAuto, and set the limits of the axes, unless the keyword arg 'axesAdjust' is set to False. This technique is applied uniformly for all wobject generating functions.
  * Axes.SetLimits() does not apply a margin for the ranges given as an argument.
  * The backend is auto-selected in a better way (looks for any loaded backends).
  * The display of italics is now artifact free. Italics can now be mixed with bold and sub/super script.
  * Several issue/bug fixes ...


---


## Release 1.2 (30-03-2010) ##

Some significant changes in code for the backends to make visvis work on Linux. Also some api changes with regard to the events. I planned to implement lighting for version 1.2, but I wanted to solve the Linux problems first and release asap.

### Bug fixes ###
  * Changed time.clock() usage to time.time(), solving [issue 2](https://code.google.com/p/visvis/issues/detail?id=2).
  * Did a redesign on how visvis interacts with the backend GUI toolkit. This made visvis work on Linux a lot better.
  * As a consequence of the above changes, the fltk backend is now stable as well.
  * Visvis now also works in IPython (with wx and qt4 backend).


### Api changes ###
  * Modified signature of FindObjects() to make it easier to use and more flexible.
  * The mouseUp event is available for all BaseObject's. It fires when the mouse was first pressed down on the object and is now released (which does not have to be over the same object).
  * The mouseUp event is available for all BaseObject's. It fires when the mouse moves while the figure is active.
  * Each BaseObject has a Draw() method now, which currently tries to obtain the figure instance and call its Draw() method. In the future this behavior might be changed. For example not all axes objects need redrawing each round.

### Other changes ###
  * A button changes its appearance when hovering over it.
  * A button fires an eventPress event when released after pressing down.
  * The ColorBar does not use the colormap's alpha value to draw, because it prevented seeing the colors.
  * Visvis now has a setup script and can be obtained using easy\_install.
  * ... many other small bugs, issues and improvements ...


---


## Release 1.1 (10-02-2010) ##

Several improvements, better documentation and a more consistent api.
Also much care was taken to make visvis work on older systems that do not have the newest version of OpenGl.


### New features ###
  * Colormaps (as a property of the Texture2D and Texture3D classes), the colorbar and the ColormapEditor wibject. Also created several standard colormaps (vv.gray, vv.hot, etc.).
  * Self-made shader programs can be used by creating a shader file in the visvis/resources directory. Use Texture2d.aa or Texture3d.renderStyle to select your shader.
  * Raycast render method to render 3D volumes. Use the ColormapEditor wibject to control the transparancy and colors.
  * Visvis works for all OpenGl versions from OpenGl 1.1! Some functionality is turned off when not available, and a warning message is produced.
  * The Polar camera (or '3d' camera) resets better (better initial field of view), and can also roll by holding control.
  * Made ginput function to let the user select a number of points.
  * Made function vv.screenshot() to capture the screen and interpolate the image before writing it to disk. This enables making high quality snapshots of your visualized data.
  * Made a few other convenience functions such as vv.axis() and vv.legend().


### Bug fixes ###
  * Calling vv.use() is not necessary anymore; a suitable backend is selected automatically.
  * The wx backend now always creates a front AND a back buffer. (thanks to David Baddeley)
  * The linking of shader code happens at compile time (instead of draw-time). This about doubled the speed at which volumes can be rendered.
  * Transformations for textures representing anisotropic data are applied only when setting the data.
  * Destroy() calls OnDestroy() on the leaf objects first, so that an object can still reference its parent when cleaning up.
  * The wx backend stays responsive when periodically calling Figure.DrawNow() during a running program.
  * And many more...


### API changes ###
  * All wobjects have a `_`GetLimits method that can be overloaded to specify its limits. For all current wobjects, the transformations are taken into account now.
  * Each wobject now has a DestroyGl and an Destroy method and their accompanying OnDestroyGl and Ondestroy. The first should only be used to clean up OpenGl resources, the latter to clean up any other resources. By making this difference, it's easy to for example move an object from one figure (i.e. OpenGl context) to another.
  * GetAxes() replaces the Axes property with the same name. This makes it more consistent with the GetFigure() method. Note that both methods can return None, which would make them a bit awkward as a property.
  * Removed Wibject.GetSize, use Wibject.position.size instead.
  * Figures can be closes programatically using the method Destroy().
  * Removed relativeToAbsolute and absoluteToRelative methods of the Wibjects class. This functionality is now handled by the Position object.
  * Solved bug where many tickmarks would be created if they got the same text.
  * Fixed bug that volumes were not rendered correctly when the Axes.daspect was changed.
  * Used weakrefs in many places and modified some code such that objects can be deleted by the gc when they are destroyed.
  * Use a smaller depth range on systems with <24 bits depth buffer, so that the objects are still drawn in the correct order (lines above 2D textures, etc.).
  * Added GetView() and SetView() methods to the Axes object to get more control over the cameras.
  * Removed App() factory function, because vv.use() does the same. vv.use() can also be called without an argument, in which case a backend is chosen automatically. The returned application instance has a Run() method instead of a run() method.


### Other changes ###
  * Refactored the textures module.
  * Interpolation is True by default for 3D textures. For 2D textures it's still false.
  * Improved the way 3D volumes are rendered (specifically the way the ray directions are calculated). This made the pre-draw rendering pass unnecessary, so it was removed.
  * Data for textures is automatically down-sampled if too large to fit in OpenGl.
  * Added the '+' lineStyle for Line objects (plot). It draws a line between each pair of points, which can be handy for vector plots and the like.
  * Fonts are rendered more smoothly and faster.
  * Reworked the position property for wibjects.
  * Negative x/y values for widget's position now simply represent negative locations.
  * Tickmarks at the bottom right that would stick out of the figure are not drawn.
  * Tickmarks are wider apart for the x-axis in 2D cam if they are represented using an exponent.



---


## Release 1.0 ##
The first official release.


---
