Visvis supports the following world objects:

  * [plot()](functions#plot.md) creates a (lines+markers) in 2D and 3D ([Line](cls_Line.md) object).
  * [imshow()](functions#imshow.md) creates a 2D grayscale and color image ([Texture2D](cls_Texture2D.md) object).
  * [volshow()](functions#volshow.md) creates a rendered 3D volumes, which can be rendered using several different styles ([Texture3D](cls_Texture3D.md) object).
  * Several functions create polygonal meshes and surfaces ([Mesh](cls_Mesh.md) object).
  * [polarplot()](functions#polarplot.md) for log-polar plots.
  * [bar3()](functions#bar3.md) creates  a 3D bar chart.
  * The [MotionDataContainer](cls_MotionDataContainer.md) class can be used to visualize animated data.
  * The [Text](cls_Text.md) class displays text at a certain position in world coordinates. The font size is expressed in screen coordinates though.


Visvis ...

  * supports colormaps.
  * supports fast interaction with the mouse (zooming/panning, and rotating in 3D).
  * has a simple and effective event system, allowing picking of all objects, also in 3D.
  * has a simple structured object model. Objects can be nested to create more complex models. Transformations (scaling, translation, rotation) applied to an object are also applied to its children.
  * uses properties to change the appearance of objects.
  * has an easy to use (Matlab like) functional interface to create visualization objects.
  * supports full Unicode text (if FreeType is installed). Various escape sequences to support bold, italics, sub- and superscript, greek, and mathematical symbols are available.
  * has support for animated data.
  * can make screenshots of the figure or axes. This screenshot can be interpolated using bicubic interpolation before writing the image to a file, which significantly increases the smoothness of the fonts.
  * has support to record screenshots as a movie, which can be exported to swf-files (flash), animated gif, AVI, or a series of images.
  * supports easy reading and writing images as numpy arrays (if PIL is installed).

Visvis does not (yet) support:
  * Full Latex support as Matplotlib does. (And it probably never will.)
  * Pie plots and the like.