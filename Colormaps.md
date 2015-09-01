A colormap is a table to convert a scalar value to an RGB or RGBA value. Colormaps can be applied to 2D textures and 3D textures (using the colormap property), and maybe to other wobjects in the future. For 2D textures the colormap is neglected if the texture represents a color image. For 3D textures, it depends on the render style how the colormap is used exactly. For the 'raycasting' render style, for example, the alpha value in the colormap will influence how deep in the volume the rays will travel.

A colormap is a abstract idea; it can be represented by a 3xN or 4xN numpy array, or by a list of tuples. There is also no colormap class (well there is actually, but it's only used to get the colormap data to OpenGl).

Visvis defines some default colormaps:
CM\_AUTUMN, CM\_BONE, CM\_COOL, CM\_COPPER, CM\_GRAY, CM\_HOT, CM\_HSV, CM\_JET, CM\_PINK, CM\_SPRING, CM\_SUMMER, CM\_WINTER

A dictionary of these default colormaps is available as vv.cm.colormaps.

There is also a [ColormapEditor](cls_ColormapEditor.md) widget that can be used to manually change the colormap in use.

See also the [colormaps example](example_colormaps.md).