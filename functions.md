
---


# The functions of Visvis #

Visvis is object oriented by nature. However,
to facilitate creating the visualizing objects and performing other common
tasks, a set of functions is available.

Certain functions that you might be used to from Matlab
or Matplotlib are not listed here; they are availabe as properties of the
wibjects and wobjects (mostly the Axes and Axis objects).

As a rule of thumb, a function
is available if it creates something (as with xlabel, title, or colorbar)
and not if it changes a property (such as showGrid or xTicks). Of course,
there are also functions that do something that cannot be done in an
object oriented way (such as getframe or imwrite).

The functions are defined in the visvis/functions directory.
Anyone can make their own functions by creating a module in that
directory that defines a function with the same name as the module.

**Here's a list of all the functions currently available:**<br />
<table cellpadding='10px'><tr>
<td valign='top'>
<a href='#aVolume.md'>aVolume</a><br /><a href='#axis.md'>axis</a><br /><a href='#bar.md'>bar</a><br /><a href='#bar3.md'>bar3</a><br /><a href='#boxplot.md'>boxplot</a><br /><a href='#callLater.md'>callLater</a><br /><a href='#cla.md'>cla</a><br /><a href='#clf.md'>clf</a><br /><a href='#close.md'>close</a><br /><a href='#closeAll.md'>closeAll</a><br /><a href='#colorbar.md'>colorbar</a><br /><a href='#draw.md'>draw</a><br /><a href='#figure.md'>figure</a><br /><a href='#gca.md'>gca</a><br /><a href='#gcf.md'>gcf</a><br /><a href='#getOpenGlInfo.md'>getOpenGlInfo</a><br /><a href='#getframe.md'>getframe</a><br /><a href='#ginput.md'>ginput</a><br /><a href='#grid.md'>grid</a><br /></td>
<td valign='top'>
<a href='#help.md'>help</a><br /><a href='#hist.md'>hist</a><br /><a href='#imread.md'>imread</a><br /><a href='#imshow.md'>imshow</a><br /><a href='#imwrite.md'>imwrite</a><br /><a href='#kde.md'>kde</a><br /><a href='#legend.md'>legend</a><br /><a href='#mesh.md'>mesh</a><br /><a href='#meshRead.md'>meshRead</a><br /><a href='#meshWrite.md'>meshWrite</a><br /><a href='#movieRead.md'>movieRead</a><br /><a href='#movieShow.md'>movieShow</a><br /><a href='#movieWrite.md'>movieWrite</a><br /><a href='#peaks.md'>peaks</a><br /><a href='#plot.md'>plot</a><br /><a href='#polarplot.md'>polarplot</a><br /><a href='#processEvents.md'>processEvents</a><br /><a href='#record.md'>record</a><br /><a href='#reportIssue.md'>reportIssue</a><br /></td>
<td valign='top'>
<a href='#screenshot.md'>screenshot</a><br /><a href='#solidBox.md'>solidBox</a><br /><a href='#solidCone.md'>solidCone</a><br /><a href='#solidCylinder.md'>solidCylinder</a><br /><a href='#solidLine.md'>solidLine</a><br /><a href='#solidRing.md'>solidRing</a><br /><a href='#solidSphere.md'>solidSphere</a><br /><a href='#solidTeapot.md'>solidTeapot</a><br /><a href='#subplot.md'>subplot</a><br /><a href='#surf.md'>surf</a><br /><a href='#title.md'>title</a><br /><a href='#use.md'>use</a><br /><a href='#view.md'>view</a><br /><a href='#volshow.md'>volshow</a><br /><a href='#volshow2.md'>volshow2</a><br /><a href='#volshow3.md'>volshow3</a><br /><a href='#xlabel.md'>xlabel</a><br /><a href='#ylabel.md'>ylabel</a><br /><a href='#zlabel.md'>zlabel</a><br /></td>
</tr></table>


---


#### <font color='#FFF'>aVolume</font> ####
### <font color='#066'>aVolume(N=5, size=64)</font> ###

> Creates a volume (3D image) with random bars.  The returned numpy array has values between 0 and 1. Intended for quick illustration and test purposes.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>N : int</u><br /><font color='#020'> The number of bars for each dimension.<br /></font><u>size : int</u><br /><font color='#020'> The size of the volume (for each dimension).</font>




#### <font color='#FFF'>axis</font> ####
### <font color='#066'>axis(command, axes=None)</font> ###

> Convenience function to set axis properties. Note that all functionality can also be applied via the properties of the Axis object.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>command : string</u><br /><font color='#020'> The setting command to apply. See below.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> The axes to apply the setting to. Uses the current axes by default. </font>

> <b><u><font color='#A50'>Possible string commands</font></u></b><br />
    * off: hide the axis (Axes.axis.visible = False)
    * on: show the axis (Axes.axis.visible = True)
    * equal: make a circle be displayed circular (Axes.daspectAuto = False)
    * auto: change the range for each dimension indepdently (Axes.daspectAuto = True)
    * tight: show all data (Axes.SetLimits())
    * ij: flip the y-axis (make second element of Axes.daspect negative)
    * xy: (make all elements of Axes.daspect positive)  If you want to set an Axes' limits, use Axes.SetLimits(xlim, ylim, zlim).




#### <font color='#FFF'>bar</font> ####
### <font color='#066'>bar(<code>*</code>args, width=0.75, axesAdjust=True, axes=None, <code>*</code><code>*</code>kwargs)</font> ###

> Create a bar chart and returns a Bars2D instance that can be used to change the appearance of the bars (such as color).

> <b><u><font color='#A50'>Usage</font></u></b><br />
    * bar(H, ...) creates bars of specified height.
    * bar(X, H, ...) also supply their x-coordinates

> <b><u><font color='#A50'>Keyword arguments</font></u></b><br /><br /><u>width : scalar</u><br /><font color='#020'> The width of the bars.<br /></font><u>color : {3-element tuple, color-char}</u><br /><font color='#020'> The color of the bars<br /></font><u>colors : {3-element tuple, color-char}</u><br /><font color='#020'> A color value for each bar.<br /></font><u>lc : {3-element tuple, color-char}</u><br /><font color='#020'> The color for the bar lines (i.e. edges).<br /></font><u>lw : scalar</u><br /><font color='#020'> The width of the bar lines (i.e. edges).<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>




#### <font color='#FFF'>bar3</font> ####
### <font color='#066'>bar3(<code>*</code>args, width=0.75, axesAdjust=True, axes=None)</font> ###

> Create a 3D bar chart and returns a Bars3D instance that can be used to change the appearance of the bars (such as lighting properties and color).

> <b><u><font color='#A50'>Usage</font></u></b><br />
    * bar3(H, ...) creates bars of specified height.
    * bar3(X, H, ...) also supply their x-coordinates
    * bar3(X, Y, H, ...) supply both x- and y-coordinates

> <b><u><font color='#A50'>Keyword arguments</font></u></b><br /><br /><u>width : scalar</u><br /><font color='#020'> The width of the bars.<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>




#### <font color='#FFF'>boxplot</font> ####
### <font color='#066'>boxplot(<code>*</code>args, width=0.75, whiskers=1.5, axesAdjust=True, axes=None)</font> ###

> Create a box and whisker plot and returns a BoxPlot wobject that can be used to change the appearance of the boxes (such as color).

> If whiskers=='violin' creates a violin plot, which displays the kernel density estimate (kde) of each data.

> <b><u><font color='#A50'>Usage</font></u></b><br />
    * boxplot(data, ...) creates boxplots for the given list of data
    * boxplot(X, data, ...) also supply x-coordinates for each data

> <b><u><font color='#A50'>Arguments</font></u></b><br /><br /><u>X : iterable (optional)</u><br /><font color='#020'> Specify x position of the boxes.<br /></font><u>data : list</u><br /><font color='#020'> List of data, where each data is a sequence (something that can be passed to numpy.array()).<br /></font><u>width : scalar</u><br /><font color='#020'> The width of the boxes.<br /></font><u>whiskers : scalar or string</u><br /><font color='#020'> How to draw the whiskers. If a scalar is given, it defines the  length of the whiskers as a function of the IQR. In this case any points lying beyond the whiskers are drawn as outliers. If 'minmax', the whiskers simply extend to the maximal data range. If 'std', the whiskers indicate the mean +/- the standard deviation. If 'violin', a violin plot is drawn, which shows the probability  density function completely.<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>




#### <font color='#FFF'>callLater</font> ####
### <font color='#066'>callLater(delay, callable, <code>*</code>args, <code>*</code><code>*</code>kwargs)</font> ###

> Call a callable after a specified delay (in seconds),  with the specified arguments and keyword-arguments.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>delay : scalar</u><br /><font color='#020'> The delay in seconds. If zero, the callable is called right  after the current processing has returned to the main loop,  before any other visvis events are processed.<br /></font><u>callable : a callable object</u><br /><font color='#020'> The callback that is called when the delay has passed.</font>

> See also vv.Event




#### <font color='#FFF'>cla</font> ####
### <font color='#066'>cla()</font> ###

> Clear the current axes.




#### <font color='#FFF'>clf</font> ####
### <font color='#066'>clf()</font> ###

> Clear current figure.




#### <font color='#FFF'>close</font> ####
### <font color='#066'>close(fig)</font> ###

> Close a figure.

> fig can be a Figure object or an integer representing the id of the figure to close. Note that for the first case, you migh also call fig.Destroy().




#### <font color='#FFF'>closeAll</font> ####
### <font color='#066'>closeAll()</font> ###

> Closes all figures.




#### <font color='#FFF'>colorbar</font> ####
### <font color='#066'>colorbar(axes=None)</font> ###

> Attach a colorbar to the given axes (or the current axes if  not given). The reference to the colorbar instance is returned. Also see the vv.ColormapEditor wibject.




#### <font color='#FFF'>draw</font> ####
### <font color='#066'>draw(figure=None, fast=False)</font> ###

> Makes the given figure (or the current figure if None) draw itself. If fast is True, some wobjects can draw itself faster at reduced quality.

> This function is now more or less deprecated; visvis is designed to  invoke a draw whenever necessary.




#### <font color='#FFF'>figure</font> ####
### <font color='#066'>figure(fig=None)</font> ###

> Set the specified figure to be the current figure, creating it if necessary.  fig may be a Figure object, a figure number (a positive integer), or None.  Returns the specified or created figure.




#### <font color='#FFF'>gca</font> ####
### <font color='#066'>gca()</font> ###

> Get the current axes in the current figure. If there is no axes, an Axes instance is created. To make an axes current,  use Axes.MakeCurrent().

> See also gcf(), Figure.MakeCurrent(), Figure.currentAxes




#### <font color='#FFF'>gcf</font> ####
### <font color='#066'>gcf()</font> ###

> Get the current figure. If there is no figure yet, figure() is called to create one. To make a figure current,  use Figure.MakeCurrent().

> See also gca()




#### <font color='#FFF'>getOpenGlInfo</font> ####
### <font color='#066'>getOpenGlInfo()</font> ###

> Get information about the OpenGl version on this system.  Returned is a tuple (version, vendor, renderer, extensions)

> A figure is created and removed to create an openGl context if this is necessary.




#### <font color='#FFF'>getframe</font> ####
### <font color='#066'>getframe(object)</font> ###

> Get a snapshot of the current figure or axes or axesContainer. It is retured as a numpy array (color image). Also see vv.screenshot().




#### <font color='#FFF'>ginput</font> ####
### <font color='#066'>ginput(N=0, axes=None, ms='+', <code>*</code><code>*</code>kwargs)</font> ###

> Graphical input: select N number of points with the mouse.  Returns a 2D pointset.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>N : int</u><br /><font color='#020'> The maximum number of points to capture. If N=0, will keep capturing until the user stops it. The capturing always stops when enter is pressed or the mouse is double clicked. In the latter case a final point is added.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> The axes to capture the points in, or the current axes if not given.<br /></font><u>ms : markerStyle</u><br /><font color='#020'> The marker style to use for the points. See plot.</font>

> Any other keyword arguments are passed to plot to show the selected points and the lines between them.




#### <font color='#FFF'>grid</font> ####
### <font color='#066'>grid(<code>*</code>args, axesAdjust=True, axes=None)</font> ###

> Create a wireframe parametric surface.

> <b><u><font color='#A50'>Usage</font></u></b><br />
    * grid(Z) - create a grid mesh using the given image with z coordinates.
    * grid(Z, C) - also supply a texture image to map.
    * grid(X, Y, Z) - give x, y and z coordinates.
    * grid(X, Y, Z, C) - also supply a texture image to map.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>Z : A MxN 2D array</u><br /><font color='#020'><br /></font><u>X : A length N 1D array, or a MxN 2D array</u><br /><font color='#020'><br /></font><u>Y : A length M 1D array, or a MxN 2D array</u><br /><font color='#020'><br /></font><u>C : A MxN 2D array, or a AxBx3 3D array</u><br /><font color='#020'> If 2D, C specifies a colormap index for each vertex of Z.  If 3D, C gives a RGB image to be mapped over Z.  In this case, the sizes of C and Z need not match.</font>

> <b><u><font color='#A50'>Keyword arguments</font></u></b><br /><br /><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>

> <b><u><font color='#A50'>Notes</font></u></b><br />
    * This function should not be confused with the axis grid, see the  Axis.showGrid property.
    * This function is know in Matlab as mesh(), but to avoid confusion with the vv.Mesh class, it is called grid() in visvis.

> Also see surf() and the solid`*`() methods.




#### <font color='#FFF'>help</font> ####
### <font color='#066'>help()</font> ###

> Open a webbrowser with the API documentation of visvis.

> Note that all visvis classes and functions have docstrings, so  typing for example "vv.Mesh?" in IPython or IEP gives you  documentation on the fly.




#### <font color='#FFF'>hist</font> ####
### <font color='#066'>hist(a, bins=None, range=None, normed=False, weights=None)</font> ###

> Make a histogram plot of the data. Uses np.histogram (new version)  internally. See its docs for more information.

> See the kde() function for a more accurate density estimate. See the vv.StatData for more statistics on data.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>a : array_like</u><br /><font color='#020'> The data to calculate the historgam of.<br /></font><u>bins : int or sequence of scalars, optional</u><br /><font color='#020'> If <code>bins</code> is an int, it defines the number of equal-width bins in the given range. If <code>bins</code> is a sequence, it defines the bin edges,  including the rightmost edge, allowing for non-uniform bin widths. If bins is not given, the best number of bins is determined automatically using the Freedman-Diaconis rule.<br /></font><u>range : (float, float)</u><br /><font color='#020'> The lower and upper range of the bins. If not provided, range is simply (a.min(), a.max()). Values outside the range are ignored. <br /></font><u>normed : bool</u><br /><font color='#020'> If False, the result will contain the number of samples in each bin.  If True, the result is the value of the probability <b>density</b>  function at the bin, normalized such that the <b>integral</b> over the  range is 1. Note that the sum of the histogram values will not be  equal to 1 unless bins of unity width are chosen; it is not a  probability <b>mass</b> function.<br /></font><u>weights : array_like</u><br /><font color='#020'> An array of weights, of the same shape as <code>a</code>. Each value in <code>a</code>  only contributes its associated weight towards the bin count  (instead of 1). If <code>normed</code> is True, the weights are normalized,  so that the integral of the density over the range remains 1.     </font>




#### <font color='#FFF'>imread</font> ####
### <font color='#066'>imread(filename)</font> ###

> Read image from a file, requires imageio or PIL.




#### <font color='#FFF'>imshow</font> ####
### <font color='#066'>imshow(im, clim=None, aa=2, interpolate=False, cm=CM_GRAY, axesAdjust=True, axes=None)</font> ###

> Display a 2D image and returns the Texture2D object.

> If the image is an anisotropic array (vv.Aaray), the appropriate scale and translate transformations are applied.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>im : numpy array</u><br /><font color='#020'> The image to visualize. Can be grayscale, RGB, or RGBA.<br /></font><u>clim : 2-element tuple</u><br /><font color='#020'> The color limits to scale the intensities of the image. If not given, the im.min() and im.max() are used (neglecting nan and inf).<br /></font><u>aa : 0, 1, 2 or 3</u><br /><font color='#020'> Anti aliasing. 0 means no anti-aliasing. The highee the number, the better quality the anti-aliasing is (Requires a GLSL compatible OpenGl implementation). Default 2.<br /></font><u>interpolation : bool</u><br /><font color='#020'> Use no interpolation (i.e. nearest neighbour) or linear interpolation.<br /></font><u>cm : Colormap</u><br /><font color='#020'> Set the colormap to apply in case the image is grayscale.<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If axesAdjust==True, this function will call axes.SetLimits(), set the camera type to 2D, and make axes.daspect<code>[</code>1<code>]</code> negative (i.e. flip  the y-axis). If daspectAuto has not been set yet, it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>

> <b><u><font color='#A50'>Notes</font></u></b><br /><br />
> New images are positioned on z=-0.1, such that lines and points are visible over the image. This z-pos of textures already in the axes are moved backwards if new images are displayed with imshow, such that  the new image is displayed over the older ones. (the changed value is `Texture2D._trafo_trans.dz`)

> Visvis does not use the "hold on / hold off" system. So if updating  an image, better use Texture2D.Refresh() or call Axes.Clear() first.




#### <font color='#FFF'>imwrite</font> ####
### <font color='#066'>imwrite(filename, image, format=None)</font> ###

> Write image (numpy array) to file, requires imageio or PIL.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>filename : string</u><br /><font color='#020'> The name of the file to store the screenshot to. If filename is None,  the interpolated image is returned as a numpy array.<br /></font><u>image : numpy array</u><br /><font color='#020'> The image to write.<br /></font><u>format : string</u><br /><font color='#020'> The format for the image to be saved in. If not given, the format is deduced from the filename.</font>

> <b><u><font color='#A50'>Notes</font></u></b><br />
    * For floating point images, 0 is considered black and 1 is white.
    * For integer types, 0 is considered black and 255 is white.




#### <font color='#FFF'>kde</font> ####
### <font color='#066'>kde(a, bins=None, range=None, <code>*</code><code>*</code>kwargs)</font> ###

> Make a kernerl density estimate plot of the data. This is like a  histogram, but produces a smoother result, thereby better represening the probability density function.

> See the vv.StatData for more statistics on data.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>a : array_like</u><br /><font color='#020'> The data to calculate the historgam of.<br /></font><u>bins : int (optional)</u><br /><font color='#020'> The number of bins. If not given, the best number of bins is  determined automatically using the Freedman-Diaconis rule.<br /></font><u>kernel : float or sequence (optional)</u><br /><font color='#020'> The kernel to use for distributing the values. If a scalar is given, a Gaussian kernel with a sigma equal to the given number is used. If not given, the best kernel is chosen baded on the number of bins.<br /></font><u>kwargs : keyword arguments</u><br /><font color='#020'> These are given to the plot function.</font>




#### <font color='#FFF'>legend</font> ####
### <font color='#066'>legend('name1', 'name2', 'name3', ..., axes=None)</font> ###

> Can also be called with a single argument being a tuple/list of strings.

> Set the string labels for the legend. If no string labels are given, the legend wibject is hidden again.

> See also the Axes.legend property.




#### <font color='#FFF'>mesh</font> ####
### <font color='#066'>mesh(vertices, faces=None, normals=None, values=None, verticesPerFace=3, colormap=None, clim=None, texture=None, axesAdjust=True, axes=None)</font> ###

> Display a mesh of polygons, either triangles or quads.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>vertices : Nx3 array</u><br /><font color='#020'> The positions of the vertices in 3D space.<br /></font><u>faces : array or list of indices</u><br /><font color='#020'> The faces given in terms of the vertex indices.  Should be 1D, in which case the indices are grouped into groups of verticesPerFace, or Mx3 or Mx4, in which case verticesPerFace is ignored. The front of the face is defined using the right-hand-rule.<br /></font><u>normals : Nx3</u><br /><font color='#020'> A list of vectors specifying the vertex normals.<br /></font><u>values : N, Nx2, Nx3, or Nx4 array</u><br /><font color='#020'> Sets the color of each vertex, using values from a colormap (1D), colors from a texture (Nx2), RGB values (Nx3), or RGBA value (Nx4).<br /></font><u>verticesPerFace : 3 or 4</u><br /><font color='#020'> Whether the faces are triangle or quads, if not specified in faces.<br /></font><u>colormap : a Colormap</u><br /><font color='#020'> If values is 1D, the vertex colors are set from this colormap.<br /></font><u>clim : 2 element array</u><br /><font color='#020'> If values is 1D, sets the values to be mapped to the limits of the  colormap.  If None, the min and max of values are used.<br /></font><u>texture : a Texture</u><br /><font color='#020'> If values is Nx2, the vertex colors are set from this texture.<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> Whether to adjust the view after the mesh is drawn.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> The axes into which the mesh will be added.  If None, the current axes will be used.</font>




#### <font color='#FFF'>meshRead</font> ####
### <font color='#066'>meshRead(fname, check=False)</font> ###

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>fname : string</u><br /><font color='#020'> The name of the file to read.<br /></font><u>check : bool</u><br /><font color='#020'> For the STL format: if check is True and the file is in ascii,  some checks to the integrity of the file are done (which is a  bit slower). </font>

> <b><u><font color='#A50'>Notes on formats</font></u></b><br />
    * The STL format (.stl) is rather limited in the definition of the faces; smooth shading is not possible on an STL mesh.
    * The Wavefront format (.obj) is widely available.
    * For the wavefront format, material, nurbs and other fancy stuff is ignored.
    * The SSDF format (.ssdf or .bsdf) is the most efficient in terms of memory and speed, but is not widely available.




#### <font color='#FFF'>meshWrite</font> ####
### <font color='#066'>meshWrite(fname, mesh, name='', bin=True)</font> ###

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>fname : string</u><br /><font color='#020'> The filename to write to. The extension should be one of the following: .obj .stl .ssdf .bsdf <br /></font><u>mesh : vv.BaseMesh</u><br /><font color='#020'> The mesh instance to write.<br /></font><u>name : string (optional)</u><br /><font color='#020'> The name of the object (e.g. 'teapot')<br /></font><u>bin : bool</u><br /><font color='#020'> For the STL format: whether to write binary, which is much  more compact then ascii.</font>

> <b><u><font color='#A50'>Notes on formats</font></u></b><br />
    * The STL format (.stl) is rather limited in the definition of the faces; smooth shading is not possible on an STL mesh.
    * The Wavefront format (.obj) is widely available.
    * The SSDF format (.ssdf or .bsdf) is the most efficient in terms of memory and speed, but is not widely available.




#### <font color='#FFF'>movieRead</font> ####
### <font color='#066'>movieRead(filename, asNumpy=True)</font> ###

> Read the movie from GIF, SWF, AVI (or MPG), or a series of images (PNG, JPG,TIF,BMP).

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>filename : string</u><br /><font color='#020'> The name of the file that contains the movie. For a series of images, the <code>`*</code>` wildcard can be used.<br /></font><u>asNumpy : bool</u><br /><font color='#020'> If True, returns a list of numpy arrays. Otherwise return  a list if PIL images.</font>

> <b><u><font color='#A50'>Notes</font></u></b><br /><br />
> Reading AVI requires the "ffmpeg" application:
    * Most linux users can install it using their package manager
    * There is a windows installer on the visvis website




#### <font color='#FFF'>movieShow</font> ####
### <font color='#066'>movieShow(images, duration=0.1)</font> ###

> Show the images in the given list as a movie.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>images : list</u><br /><font color='#020'> The 2D images (can be color images) that the movie consists of.<br /></font><u>clim : (min, max)</u><br /><font color='#020'> The color limits to apply. See imshow.<br /></font><u>duration : scalar</u><br /><font color='#020'> The duration (in seconds) of each frame. The real duration can differ from the given duration, depending on the performance of your system.<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If axesAdjust==True, this function will call axes.SetLimits(), set the camera type to 2D, and make axes.daspect<code>[</code>1<code>]</code> negative (i.e. flip  the y-axis). If daspectAuto has not been set yet, it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>




#### <font color='#FFF'>movieWrite</font> ####
### <font color='#066'>movieWrite(fname, images, duration=0.1, repeat=True, <code>*</code><code>*</code>kwargs)</font> ###

> Write the movie specified in images to GIF, SWF, AVI/MPEG, or a series of images (PNG,JPG,TIF,BMP).

> <b><u><font color='#A50'>General parameters</font></u></b><br /><br /><u>filename : string</u><br /><font color='#020'> The name of the file to write the image to. For a series of images, the <code>`*</code>` wildcard can be used.<br /></font><u>images : list</u><br /><font color='#020'> Should be a list consisting of PIL images or numpy arrays.  The latter should be between 0 and 255 for integer types,  and between 0 and 1 for float types.<br /></font><u>duration : scalar</u><br /><font color='#020'> The duration for all frames. For GIF and SWF this can also be a list that specifies the duration for each frame. (For swf the durations are rounded to integer amounts of the smallest duration.)<br /></font><u>repeat : bool or integer</u><br /><font color='#020'> Can be used in GIF and SWF to indicate that the movie should loop. For GIF, an integer can be given to specify the number of loops.  </font>

> <b><u><font color='#A50'>Special GIF parameters</font></u></b><br /><br /><u>dither : bool</u><br /><font color='#020'> Whether to apply dithering<br /></font><u>nq : integer</u><br /><font color='#020'> If nonzero, applies the NeuQuant quantization algorithm to create the color palette. This algorithm is superior, but slower than the standard PIL algorithm. The value of nq is the quality parameter. 1 represents the best quality. 10 is in general a good tradeoff between quality and speed. When using this option,  better results are usually obtained when subRectangles is False.<br /></font><u>subRectangles : False, True, or a list of 2-element tuples</u><br /><font color='#020'> Whether to use sub-rectangles. If True, the minimal rectangle that is required to update each frame is automatically detected. This can give significant reductions in file size, particularly if only a part of the image changes. One can also give a list of x-y  coordinates if you want to do the cropping yourself. The default is True.<br /></font><u>dispose : int</u><br /><font color='#020'> How to dispose each frame. 1 means that each frame is to be left in place. 2 means the background color should be restored after each frame. 3 means the decoder should restore the previous frame. If subRectangles==False, the default is 2, otherwise it is 1.</font>

> <b><u><font color='#A50'>Special AVI/MPEG parameters</font></u></b><br /><br /><u>encoding : {'mpeg4', 'msmpeg4v2', ...}</u><br /><font color='#020'> The encoding to use. Hint for Windows users: the 'msmpeg4v2' codec  is natively supported on Windows.<br /></font><u>inputOptions : string</u><br /><font color='#020'> See the documentation of ffmpeg<br /></font><u>outputOptions : string</u><br /><font color='#020'> See the documentation of ffmpeg</font>

> <b><u><font color='#A50'>Notes for writing a series of images</font></u></b><br /><br />
> If the filenenumber contains an asterix, a sequence number is introduced  at its location. Otherwise the sequence number is introduced right before the final dot. To enable easy creation of a new directory with image  files, it is made sure that the full path exists.

> <b><u><font color='#A50'>Notes for writing AVI/MPEG</font></u></b><br /><br />
> Writing AVI requires the "ffmpeg" application:
    * Most linux users can install it using their package manager.
    * There is a windows installer on the visvis website.

> <b><u><font color='#A50'>Notes on compression and limitations</font></u></b><br />
    * GIF: Requires PIL. Animated GIF applies a color-table of maximal 256 colors. It's widely applicable though. Reading back GIF images can be problematic due to the applied color reductions and because of problems with PIL.
    * SWF: Provides lossless storage of movie frames with good (ZLIB)  compression. Reading of SWF files is limited to images stored using ZLIB compression. Requires no external libraries.
    * AVI: Requires ffmpeg. Provides excelent mpeg4 (or any other supported by ffmpeg) compression. Not intended for reading very large movies.
    * IMS: Requires PIL. Quality depends on the used image type. Use png for   lossless compression and jpg otherwise.




#### <font color='#FFF'>peaks</font> ####
### <font color='#066'>peaks()</font> ###

> Returs a 2D map of z-values that represent an example landscape with Gaussian blobs.




#### <font color='#FFF'>plot</font> ####
### <font color='#066'>plot(<code>*</code>args, lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k', alpha=1, axesAdjust=True, axes=None)</font> ###

> Plot 1, 2 or 3 dimensional data and return the Line object.

> <b><u><font color='#A50'>Usage</font></u></b><br />
    * plot(Y, ...) plots a 1D signal, with the values plotted along the y-axis
    * plot(X, Y, ...) also supplies x coordinates
    * plot(X, Y, Z, ...) also supplies z coordinates
    * plot(P, ...) plots using a Point or Pointset instance

> <b><u><font color='#A50'>Keyword arguments</font></u></b><br /><br />
> (The longer names for the line properties can also be used)    <br /><u>lw : scalar</u><br /><font color='#020'> lineWidth. The width of the line. If zero, no line is drawn.<br /></font><u>mw : scalar</u><br /><font color='#020'> markerWidth. The width of the marker. If zero, no marker is drawn.<br /></font><u>mew : scalar</u><br /><font color='#020'> markerEdgeWidth. The width of the edge of the marker.    <br /></font><u>lc : 3-element tuple or char</u><br /><font color='#020'> lineColor. The color of the line. A tuple should represent the RGB values between 0 and 1. If a char is given it must be one of 'rgbmcywk', for reg, green, blue, magenta, cyan, yellow,  white, black, respectively.<br /></font><u>mc : 3-element tuple or char</u><br /><font color='#020'> markerColor. The color of the marker. See lineColor.<br /></font><u>mec : 3-element tuple or char</u><br /><font color='#020'> markerEdgeColor. The color of the edge of the marker.    <br /></font><u>ls : string</u><br /><font color='#020'> lineStyle. The style of the line. (See below)<br /></font><u>ms : string</u><br /><font color='#020'> markerStyle. The style of the marker. (See below)<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If axesAdjust==True, this function will call axes.SetLimits(), set the camera type to 2D when plotting 2D data and to 3D when plotting 3D data. If daspectAuto has not been set yet, it is set to True.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>

> <b><u><font color='#A50'>Line styles</font></u></b><br />
    * Solid line: '-'
    * Dotted line: ':'
    * Dashed line: '--'
    * Dash-dot line: '-.' or '.-'
    * A line that is drawn between each pair of points: '+'
    * No line: '' or None.

> <b><u><font color='#A50'>Marker styles</font></u></b><br />
    * Plus: '+'
    * Cross: 'x'
    * Square: 's'
    * Diamond: 'd'
    * Triangle (pointing up, down, left, right): '^', 'v', '<', '>'
    * Pentagram star: 'p' or '`*`'
    * Hexgram: 'h'
    * Point/cirle: 'o' or '.'
    * No marker: '' or None




#### <font color='#FFF'>polarplot</font> ####
### <font color='#066'>polarplot(<code>*</code>args, inRadians=False, lw=1, lc='b', ls="-", mw=7, mc='b', ms='', mew=1, mec='k', alpha=1, axesAdjust=True, axes=None)</font> ###

> Plot 2D polar data, using a polar axis to draw a polar grid.

> <b><u><font color='#A50'>Usage</font></u></b><br />
    * plot(Y, ...) plots a 1D polar signal.
    * plot(X, Y, ...) also supplies angular coordinates
    * plot(P, ...) plots using a Point or Pointset instance

> <b><u><font color='#A50'>Keyword arguments</font></u></b><br /><br />
> (The longer names for the line properties can also be used)    <br /><u>lw : scalar</u><br /><font color='#020'> lineWidth. The width of the line. If zero, no line is drawn.<br /></font><u>mw : scalar</u><br /><font color='#020'> markerWidth. The width of the marker. If zero, no marker is drawn.<br /></font><u>mew : scalar</u><br /><font color='#020'> markerEdgeWidth. The width of the edge of the marker.    <br /></font><u>lc : 3-element tuple or char</u><br /><font color='#020'> lineColor. The color of the line. A tuple should represent the RGB values between 0 and 1. If a char is given it must be one of 'rgbmcywk', for reg, green, blue, magenta, cyan, yellow,  white, black, respectively.<br /></font><u>mc : 3-element tuple or char</u><br /><font color='#020'> markerColor. The color of the marker. See lineColor.<br /></font><u>mec : 3-element tuple or char</u><br /><font color='#020'> markerEdgeColor. The color of the edge of the marker.    <br /></font><u>ls : string</u><br /><font color='#020'> lineStyle. The style of the line. (See below)<br /></font><u>ms : string</u><br /><font color='#020'> markerStyle. The style of the marker. (See below)<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If axesAdjust==True, this function will call axes.SetLimits(), and set the camera type to 2D. <br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>

> <b><u><font color='#A50'>Line styles</font></u></b><br />
    * Solid line: '-'
    * Dotted line: ':'
    * Dashed line: '--'
    * Dash-dot line: '-.' or '.-'
    * A line that is drawn between each pair of points: '+'
    * No line: '' or None.

> <b><u><font color='#A50'>Marker styles</font></u></b><br />
    * Plus: '+'
    * Cross: 'x'
    * Square: 's'
    * Diamond: 'd'
    * Triangle (pointing up, down, left, right): '^', 'v', '<', '>'
    * Pentagram star: 'p' or '`*`'
    * Hexgram: 'h'
    * Point/cirle: 'o' or '.'
    * No marker: '' or None

> <b><u><font color='#A50'>Polar axis</font></u></b><br /><br />
> This polar axis has a few specialized methods for adjusting the polar plot. Access these via vv.gca().axis.
    * SetLimits(thetaRange, radialRange)
    * thetaRange, radialRange = GetLimits()
    * angularRefPos: Get and Set methods for the relative screen angle of the 0 degree polar reference.  Default is 0 degs which corresponds to the positive x-axis (y =0)
    * isCW: Get and Set methods for the sense of rotation CCW or CW. This method takes/returns a bool (True if the default CW).

> <b><u><font color='#A50'>Interaction</font></u></b><br />
    * Drag mouse up/down to translate radial axis.
    * Drag mouse left/right to rotate angular ref position.
    * Drag mouse + shift key up/down to rescale radial axis (min R fixed).




#### <font color='#FFF'>processEvents</font> ####
### <font color='#066'>processEvents()</font> ###

> Processes all GUI events (and thereby all visvis events). Users can periodically call this function during running  an algorithm to keep the figures responsove.

> Note that IEP and IPython can integrate the GUI event loop to  periodically update the GUI events when idle.

> Also see Figure.DrawNow()




#### <font color='#FFF'>record</font> ####
### <font color='#066'>record(object)</font> ###

> Take a snapshot of the given figure or axes after each draw. A Recorder instance is returned, with which the recording can be stopped, continued, and exported to GIF, SWF or AVI.


#### <font color='#FFF'>reportIssue</font> ####
### <font color='#066'>reportIssue()</font> ###

> help()

> Open a webbrowser with the visvis website at the issue list.






#### <font color='#FFF'>screenshot</font> ####
### <font color='#066'>screenshot(filename, ob=None sf=2, bg=None, format=None)</font> ###

> Make a screenshot and store it to a file, using cubic interpolation to increase the resolution (and quality) of the image.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>filename : string</u><br /><font color='#020'> The name of the file to store the screenshot to. If filename is None,  the interpolated image is returned as a numpy array.<br /></font><u>ob : Axes, AxesContainer, or Figure</u><br /><font color='#020'> The object to take the screenshot of. The AxesContainer can be obtained using vv.gca().parent. It can be usefull to take a  screeshot of an axes including thickmarks and labels.<br /></font><u>sf : integer</u><br /><font color='#020'> The scale factor. The image is increased in size with this factor, using a high quality interpolation method. A factor of 2 or 3 is recommended; the image quality does not improve with higher factors. If using a sf larger than 1, the image is best saved in the jpg format.<br /></font><u>bg : 3-element tuple or char</u><br /><font color='#020'> The color of the background. If bg is given, ob.bgcolor is set to bg before the frame is captured.<br /></font><u>format : string</u><br /><font color='#020'> The format for the screenshot to be saved in. If not given, the format is deduced from the filename.</font>

> <b><u><font color='#A50'>Notes</font></u></b><br /><br />
> Uses vv.getframe(ob) to obtain the image in the figure or axes.  That image is interpolated with the given scale factor (sf) using  bicubic interpolation. Then  vv.imwrite(filename, ..) is used to  store the resulting image to a file.

> <b><u><font color='#A50'>Rationale</font></u></b><br /><br />
> We'd prefer storing screenshots of plots as vector (eps) images, but  the nature of OpenGl prevents this. By applying high quality  interpolation (using a cardinal spline), the resolution can be increased,  thereby significantly improving the visibility/smoothness for lines  and fonts. Use this to produce publication quality snapshots of your plots.




#### <font color='#FFF'>solidBox</font> ####
### <font color='#066'>solidBox(translation=None, scaling=None, direction=None, rotation=None, axesAdjust=True, axes=None)</font> ###

> Creates a solid cube (or box if you scale it) centered at the  origin. Returns an OrientableMesh.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br />
> Note that translation, scaling, and direction can also be given using a Point instance.<br /><u>translation : (dx, dy, dz), optional</u><br /><font color='#020'> The translation in world units of the created world object. scaling: (sx, sy, sz), optional The scaling in world units of the created world object. direction: (nx, ny, nz), optional Normal vector that indicates the direction of the created world object. rotation: scalar, optional The anle (in degrees) to rotate the created world object around its direction vector.<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>




#### <font color='#FFF'>solidCone</font> ####
### <font color='#066'>solidCone(translation=None, scaling=None, direction=None, rotation=None, N=16, M=16, axesAdjust=True, axes=None)</font> ###

> Creates a solid cone with quad faces and its base at the origin. Returns an OrientableMesh instance.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br />
> Note that translation, scaling, and direction can also be given using a Point instance.<br /><u>translation : (dx, dy, dz), optional</u><br /><font color='#020'> The translation in world units of the created world object. scaling: (sx, sy, sz), optional The scaling in world units of the created world object. direction: (nx, ny, nz), optional Normal vector that indicates the direction of the created world object. rotation: scalar, optional The anle (in degrees) to rotate the created world object around its direction vector.<br /></font><u>N : int</u><br /><font color='#020'> The number of subdivisions around its axis. If smaller than 8, flat shading is used instead of smooth shading.  With N=4, a pyramid is obtained.<br /></font><u>M : int</u><br /><font color='#020'> The number of subdivisions along its axis. If smaller than 8, flat shading is used instead of smooth shading. <br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>




#### <font color='#FFF'>solidCylinder</font> ####
### <font color='#066'>solidCylinder( translation=None, scaling=None, direction=None, rotation=None, N=16, M=16, axesAdjust=True, axes=None)</font> ###

> Creates a cylinder object with quad faces and its base at the origin. Returns an OrientableMesh instance.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br />
> Note that translation, scaling, and direction can also be given using a Point instance.<br /><u>translation : (dx, dy, dz), optional</u><br /><font color='#020'> The translation in world units of the created world object. scaling: (sx, sy, sz), optional The scaling in world units of the created world object. direction: (nx, ny, nz), optional Normal vector that indicates the direction of the created world object. rotation: scalar, optional The anle (in degrees) to rotate the created world object around its direction vector.<br /></font><u>N : int</u><br /><font color='#020'> The number of subdivisions around its axis. If smaller than 8, flat shading is used instead of smooth shading. <br /></font><u>M : int</u><br /><font color='#020'> The number of subdivisions along its axis. If smaller than 8, flat shading is used instead of smooth shading. <br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>




#### <font color='#FFF'>solidLine</font> ####
### <font color='#066'>solidLine(pp, radius=1.0, N=16, axesAdjust=True, axes=None)</font> ###

> Creates a solid line in 3D space.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br />
> Note that translation, scaling, and direction can also be given using a Point instance.<br /><u>pp : Pointset</u><br /><font color='#020'> The sequence of points of which the line consists.<br /></font><u>radius : scalar or sequence</u><br /><font color='#020'> The radius of the line to create. If a sequence if given, it  specifies the radius for each point in pp.<br /></font><u>N : int</u><br /><font color='#020'> The number of subdivisions around its centerline. If smaller than 8, flat shading is used instead of smooth shading. <br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>




#### <font color='#FFF'>solidRing</font> ####
### <font color='#066'>solidRing(translation=None, scaling=None, direction=None, rotation=None, thickness=0.25, N=16, M=16, axesAdjust=True, axes=None)</font> ###

> Creates a solid ring with quad faces oriented at the origin.  Returns an OrientableMesh instance.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br />
> Note that translation, scaling, and direction can also be given using a Point instance.<br /><u>translation : (dx, dy, dz), optional</u><br /><font color='#020'> The translation in world units of the created world object. scaling: (sx, sy, sz), optional The scaling in world units of the created world object. direction: (nx, ny, nz), optional Normal vector that indicates the direction of the created world object. rotation: scalar, optional The anle (in degrees) to rotate the created world object around its direction vector.<br /></font><u>thickness : scalar</u><br /><font color='#020'> The tickness of the ring, represented as a fraction of the radius.<br /></font><u>N : int</u><br /><font color='#020'> The number of subdivisions around its axis. If smaller than 8, flat shading is used instead of smooth shading. <br /></font><u>M : int</u><br /><font color='#020'> The number of subdivisions along its axis. If smaller than 8, flat shading is used instead of smooth shading. <br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>




#### <font color='#FFF'>solidSphere</font> ####
### <font color='#066'>solidSphere(translation=None, scaling=None, direction=None, rotation=None, N=16, M=16, axesAdjust=True, axes=None)</font> ###

> Creates a solid sphere with quad faces and centered at the origin.  Returns an OrientableMesh instance.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br />
> Note that translation, scaling, and direction can also be given using a Point instance.<br /><u>translation : (dx, dy, dz), optional</u><br /><font color='#020'> The translation in world units of the created world object. scaling: (sx, sy, sz), optional The scaling in world units of the created world object. direction: (nx, ny, nz), optional Normal vector that indicates the direction of the created world object. rotation: scalar, optional The anle (in degrees) to rotate the created world object around its direction vector.<br /></font><u>N : int</u><br /><font color='#020'> The number of subdivisions around the Z axis (similar to lines of longitude). If smaller than 8, flat shading is used instead  of smooth shading. <br /></font><u>M : int</u><br /><font color='#020'> The number of subdivisions along the Z axis (similar to lines of latitude). If smaller than 8, flat shading is used instead  of smooth shading. <br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>




#### <font color='#FFF'>solidTeapot</font> ####
### <font color='#066'>solidTeapot( translation=None, scaling=None, direction=None, rotation=None, axesAdjust=True, axes=None)</font> ###

> Create a model of a teapot (a teapotahedron) with its bottom at the origin. Returns an OrientableMesh instance.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br />
> Note that translation, scaling, and direction can also be given using a Point instance.<br /><u>translation : (dx, dy, dz), optional</u><br /><font color='#020'> The translation in world units of the created world object. scaling: (sx, sy, sz), optional The scaling in world units of the created world object. direction: (nx, ny, nz), optional Normal vector that indicates the direction of the created world object. rotation: scalar, optional The anle (in degrees) to rotate the created world object around its direction vector.<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet,  it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the bars in the given axes, or the current axes if not given.</font>




#### <font color='#FFF'>subplot</font> ####
### <font color='#066'>subplot(ncols, nrows, nr)</font> ###

> Create or return axes in current figure. Note that subplot(322) is the same as subplot(3,2,2).

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>ncols : int</u><br /><font color='#020'> The number of columns to devide the figure in.<br /></font><u>nrows : int</u><br /><font color='#020'> The number of rows to devide the figure in.<br /></font><u>nr : int</u><br /><font color='#020'> The subfigure number on the grid specified by ncols and nrows. Should be at least one. subplot(221) is the top left. subplot(222) is the top right. </font>

> <b><u><font color='#A50'>Notes</font></u></b><br /><br />
> It is checked whether (the center of) an axes is present at the  specified grid location. If so, that axes is returned. Otherwise a new axes is created at that location.




#### <font color='#FFF'>surf</font> ####
### <font color='#066'>surf(..., axesAdjust=True, axes=None)</font> ###

> Shaded surface plot.

> <b><u><font color='#A50'>Usage</font></u></b><br />
    * surf(Z) - create a surface using the given image with z coordinates.
    * surf(Z, C) - also supply a texture image to map.
    * surf(X, Y, Z) - give x, y and z coordinates.
    * surf(X, Y, Z, C) - also supply a texture image to map.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>Z : A MxN 2D array</u><br /><font color='#020'><br /></font><u>X : A length N 1D array, or a MxN 2D array</u><br /><font color='#020'><br /></font><u>Y : A length M 1D array, or a MxN 2D array</u><br /><font color='#020'><br /></font><u>C : A MxN 2D array, or a AxBx3 3D array</u><br /><font color='#020'> If 2D, C specifies a colormap index for each vertex of Z.  If 3D, C gives a RGB image to be mapped over Z.  In this case, the sizes of C and Z need not match.</font>

> <b><u><font color='#A50'>Keyword arguments</font></u></b><br /><br /><u>axesAdjust : bool</u><br /><font color='#020'> If axesAdjust==True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet, it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>

> Also see grid()




#### <font color='#FFF'>title</font> ####
### <font color='#066'>title(text, axes=None)</font> ###

> Show title above axes. Remove title by suplying an empty string.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>text : string</u><br /><font color='#020'> The text to display.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>




#### <font color='#FFF'>use</font> ####
### <font color='#066'>use(backendName=None)</font> ###

> Use the specified backend and return an App instance that has a Run() method to enter the GUI toolkit's mainloop, and a ProcessEvents() method to process any GUI events.

> This function is only required to explicitly choose a specific backend,  or to obtain the application object; when this function is not used, vv.figure() will select a backend automatically.

> <b><u><font color='#A50'>Backend selection</font></u></b><br /><br />
> If no backend is given, returns the previously selected backend. If no backend was yet selected, a suitable backend is selected automatically. This is done by detecting whether any of the backend toolkits is already loaded. If not, visvis tries to load the  vv.settings.preferredBackend first.

> Note: the backend can be changed even when figures are created with another backend, but this is not recommended.

> <b><u><font color='#A50'>Example embedding in Qt4</font></u></b><br />
```
  # Near the end of the script:
  
  # Get app instance and create native app
  app = vv.use('pyside')
  app.Create() 
  
  # Create window
  m = MainWindow()
  m.resize(560, 420)
  m.show()
  
  # Run main loop
  app.Run()
  
```

#### <font color='#FFF'>view</font> ####
### <font color='#066'>view(viewparams=None, axes=None, <code>*</code><code>*</code>kw)</font> ###

> Get or set the view parameters for the given axes.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>viewparams : dict</u><br /><font color='#020'> View parameters to set.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> The axes the view parameters are for.  Uses the current axes by default. keyword pairs View parameters to set.  These take precidence.</font>

> If neither viewparams or any keyword pairs are given, returns the current view parameters (as a dict).  Otherwise, sets the view parameters given.


#### <font color='#FFF'>volshow</font> ####
### <font color='#066'>volshow(vol, clim=None, cm=CM_GRAY, axesAdjust=True, axes=None)</font> ###

> Display a 3D image (a volume).

> This is a convenience function that calls either volshow3() or  volshow2(). If the current system supports it (OpenGL version >= 2.0),  displays a 3D  rendering (volshow3). Otherwise shows three slices  that can be moved interactively (volshow2).

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>vol : numpy array</u><br /><font color='#020'> The 3D image to visualize. Can be grayscale, RGB, or RGBA. If the volume is an anisotropic array (vv.Aaray), the appropriate scale and translate transformations are applied.<br /></font><u>clim : 2-element tuple</u><br /><font color='#020'> The color limits to scale the intensities of the image. If not given, the im.min() and im.max() are used (neglecting nan and inf).<br /></font><u>cm : Colormap</u><br /><font color='#020'> Set the colormap to apply in case the volume is grayscale.<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If axesAdjust==True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet, it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>

> Any other keyword arguments are passed to either volshow2() or volshow3().




#### <font color='#FFF'>volshow2</font> ####
### <font color='#066'>volshow2(vol, clim=None, renderStyle=None, cm=CM_GRAY, axesAdjust=True, axes=None)</font> ###

> Display a 3D image (a volume) using three slice textures that can be moved interactively. Returns a SliceTextureProxy instance that "wraps" the three SliceTexture instances.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>vol : numpy array</u><br /><font color='#020'> The 3D image to visualize. Can be grayscale, RGB, or RGBA. If the volume is an anisotropic array (vv.Aaray), the appropriate scale and translate transformations are applied.<br /></font><u>clim : 2-element tuple</u><br /><font color='#020'> The color limits to scale the intensities of the image. If not given, the im.min() and im.max() are used (neglecting nan and inf).<br /></font><u>renderStyle : not used</u><br /><font color='#020'> This parameter is included for compatibility with volshow3. Its value is ignored.<br /></font><u>cm : Colormap</u><br /><font color='#020'> Set the colormap to apply in case the volume is grayscale.<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If axesAdjust==True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet, it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>




#### <font color='#FFF'>volshow3</font> ####
### <font color='#066'>volshow3(vol, clim=None, renderStyle='mip', cm=CM_GRAY, axesAdjust=True, axes=None)</font> ###

> Display a 3D image (a volume) using volume rendering,  and returns the Texture3D object.

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>vol : numpy array</u><br /><font color='#020'> The 3D image to visualize. Can be grayscale, RGB, or RGBA. If the volume is an anisotropic array (vv.Aaray), the appropriate scale and translate transformations are applied.<br /></font><u>clim : 2-element tuple</u><br /><font color='#020'> The color limits to scale the intensities of the image. If not given, the im.min() and im.max() are used (neglecting nan and inf).<br /></font><u>renderStyle : {'mip', 'iso', 'ray'}</u><br /><font color='#020'> The render style to use. Maximum intensity projection (default),  isosurface rendering (using lighting), raycasting.<br /></font><u>cm : Colormap</u><br /><font color='#020'> Set the colormap to apply in case the volume is grayscale.<br /></font><u>axesAdjust : bool</u><br /><font color='#020'> If axesAdjust==True, this function will call axes.SetLimits(), and set the camera type to 3D. If daspectAuto has not been set yet, it is set to False.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>




#### <font color='#FFF'>xlabel</font> ####
### <font color='#066'>xlabel(text, axes=None)</font> ###

> Set the xlabel of an axes.  Note that you can also use "axes.axis.xLabel = text".

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>text : string</u><br /><font color='#020'> The text to display.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>




#### <font color='#FFF'>ylabel</font> ####
### <font color='#066'>ylabel(text, axes=None)</font> ###

> Set the ylabel of an axes.  Note that you can also use "axes.axis.yLabel = text".

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>text : string</u><br /><font color='#020'> The text to display.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>




#### <font color='#FFF'>zlabel</font> ####
### <font color='#066'>zlabel(text, axes=None)</font> ###

> Set the zlabel of an axes.  Note that you can also use "axes.axis.zLabel = text".

> <b><u><font color='#A50'>Parameters</font></u></b><br /><br /><u>text : string</u><br /><font color='#020'> The text to display.<br /></font><u>axes : Axes instance</u><br /><font color='#020'> Display the image in this axes, or the current axes if not given.</font>





---

