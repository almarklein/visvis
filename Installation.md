### Requirements ###
  * Numpy
  * A backend GUI toolkit (see below)
  * PyOpenGL (version 3.0.0 or higher, 3.0.2b2 or higher for py3k)

Windows users can get these requirements at [Christoph Gohlke's site](http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy).

### Optional requirements ###
  * The OpenGL driver on your system should be version 2.0 or higher in order to render volumes and apply colormaps.
  * For better rendering of text: FreeType libraries (Are usually already installed on Linux, Windows users can download it from the visvis download page.
  * An image read/write toolkit: imageio or PIL


### Supported backend GUI toolkits ###
  * PySide (since version 1.7)
  * PyQt4
  * wxPython
  * GTK
  * pyFLTK

### Installation ###

There are several ways to get visvis:
  * Run `pip install visvis`
  * Download the latest zip-file and run "python setup.py install".
  * Download the latest zip-file and put the directory contained within in a directory on your PYTHONPATH.
  * Check out the latest source from Mercurial in a directory on your PYTHONPATH.
  * Windows users can download the installer.