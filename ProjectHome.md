## Introduction ##

Visvis is a pure Python library for visualization of 1D to 4D data in an object oriented way. Essentially, visvis is an object oriented layer of Python on top of OpenGl, thereby combining the power of OpenGl with the usability of Python. A Matlab-like interface in the form of a set of functions allows easy creation of objects (e.g. plot(), imshow(), volshow(), surf()).

Visvis ...
  * is easy to use
  * is cross-platform
  * is lightweight
  * is designed to be easily extendable
  * can be used in scripts
  * can be used in interactive sessions (like in [IPython](http://ipython.scipy.org/) or [IEP](http://iep-project.org))
  * can be embedded in (commercial) GUI applications
  * runs on Python 2.x and Python 3.x
  * requires [Numpy](http://numpy.scipy.org/), [pyOpenGl](http://pyopengl.sourceforge.net/) and a [GUI backend](Installation#Supported_backend_GUI_toolkits.md).

Notice: Vispy will eventually replace Visvis, see [roadmap](http://code.google.com/p/visvis/wiki/releaseNotes).

## How visvis works ##

With visvis a range of different data can be visualized by simply adding [world objects](cls_Wobject.md) to a scene (i.e. an [axes](cls_Axes.md)). These world objects can be anything from plots ([lines](example_plotting.md) with markers), to [images](example_images.md), 3D rendered [volumes](example_volumes.md), shaded [meshes](example_meshes.md), or you can program your own world object class. If required, these data can also be [moved](example_fourDimensions.md) in time.

Online **documentation** is available for all [classes](classes.md) and [functions](functions.md). Any questions can be asked in the [visvis discussion group](http://groups.google.com/group/visvis).

At EuroScipy 2012, I gave a talk about Visvis. The long version of the presentation can be seen [here](https://docs.google.com/presentation/pub?id=17J5IVIoh2zQk49ycYh__CYpi33aWi0oSljI_MnYByeg&start=false&loop=false&delayms=3000) and there is also a [PDF](https://dl.dropbox.com/u/1463853/docs/Talk%20on%20Visvis%20at%20Euroscipy%202012.pdf).

## Example ##
[![](http://wiki.visvis.googlecode.com/hg/images/overviewScreen.png)](http://code.google.com/p/visvis/wiki/example_overview)

Click on the figure to see the **code** and how the user can interact with the figure.


### Support Visvis ###
You can support the development of Visvis by:
  * Reporting issues and bugs or propose improvements.
  * Let me know if you like Visvis. Positive feedback is very motivating for any open-source developer.
