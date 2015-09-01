Visvis can run on different backends. Currently supported are PySide, PyQt4, WX, GTK and FLTK.

Visvis will automatically try to select a backend for you. If you want to explicitly
chose one, you can use `vv.use(backendName)`. If you are building an application, you might want to call the backend mainloop function at the end of your program. To facilitate this, `vv.use()` returns an application object, which provides a common `Run()` method that enters the mainloop of the backend's GUI toolkit:
```
import visvis as vv
app = vv.use('qt4')  # create application object for the specified backend
app.Create() # Instantiate the underlying GUI app

# setup the application
...

# enter the mainloop
app.Run()
```


Visvis is designed to be easily embeddable in an application. See the examples directory how to do this.

Visvis was set up such that implementing a backend can be done as easily as possible. More information can be found [here](Creating_a_backend.md). Do you want your favorite backend to be supported? Please go ahead and write it yourself! In case of any questions don't hesitate to ask, I'd like to see Visvis be supported on as many backends as possible.