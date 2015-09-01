Here's a listing of the limitations of lower OpenGl versions. You can check your version using openGlVersion.py in the examples directory. It might help to update the latest video drivers. If that doesn't help, you could buy a new video card. Note that Nvidia cards work much better with OpenGl than ATI cards.

From Visvis version 1.1, a warning is given when the user tries to use a feature that is not available (version 1.0 would simply crash).

### OpenGl version < 2.0 ###
Because GLSL (OpenGl Shading Language) is required for some tasks, the following features are disabled on systems with OpenGl version < 2.0:

  * anti-aliasing (for Texture2D objects)
  * the clim property (of Texture2D and Texture3D objects)
  * colormaps
  * 3D rendering

Because these versions cannot iterate texture coordinate across point sprites, markers other than circles and squares are disabled (see the Line object and  plot()). Note that ATI cards are infamous for not handling point sprites correctly, even for OpenGl versions >= 2.0.

Also, textures for such versions need to be shaped by a power of two. Visvis will pad zeros to images and volumes before loading them into OpenGl memory. Note that for 3D textures, ATI can also require power-of-two data, or it will render in software mode, which is incredibly slow.

### OpenGl version < 1.4 ###
  * transparant points and lines (in other words, the Line.alpha property is disabled)

### OpenGl version < 1.2 ###
  * 3D textures are disabled all together