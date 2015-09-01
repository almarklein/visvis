
---

## Creating screenshots ##
The function `getframe()` can be used to obtain a screenshot from the figure or axes as a numpy array.
```
im = vv.getframe(vv.gcf())
```

It would be great if we could store screenshots of plots as vector (eps) images, but the nature of OpenGl prevents this. Screenshots taken with getframe are of screen resolution,
which can be too low for certain applications (for example publishing in a scientific journal). To (partially) solve these problems visvis also has the `screenshot()` function, which uses `getframe()` to obtain a screenshot, and then uses high quality bicubic interpolation to produce a higher resolution image in which the fonts and lines look
much better. It can also temporarily make the background another color (since on paper you'd usually want a white background rather than gray).
```
vv.screenshot('figure1.jpg', sf=3, bg='w') # sf: scale factor
```

Another feature (introduced in visvis 1.3) enables you to easily make all fonts in a figure larger. When using the default font size, the text in a figure is often quite tiny on paper. By using the `Figure.relativeFontSize` property, the text can be made larger.

In addition to the text, this property also scales the distance between the items in a legend. Because the property does not scale the margin for the axes, it can be necessary to correct these as well.
```
fig.relativeFontSize = 1.3
axes.position.Correct(dh=-5) # may be required to fit the x label on screen.
vv.screenshot('figure1.jpg', sf=3, bg='w') # sf: scale factor
```

Here's an example cut out from a screenshot obtained in this way (relativeFontSize=1.3,
sf=3).

![http://wiki.visvis.googlecode.com/hg/images/example_highRes.png](http://wiki.visvis.googlecode.com/hg/images/example_highRes.png)



---


## Creating movies ##

Movies can be created in visvis using the `record()` function. It returns a recorder object which captures a screenshot each time the figure is drawn. It has methods to stop and continue capturing and to export the captured images to swf (flash), animated gif, AVI or a series of images.
```
rec = vv.record(vv.gcf())
...
rec.Stop()
rec.Export('movie.swf', fps=12)
```