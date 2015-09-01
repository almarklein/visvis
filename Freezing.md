Visvis is designed to be embedded in applications, and provides functionality to help
the freezing process. This functionality can be obtained via the module `freezeHelp`.
This module provides two functions:

  * `copyResources(destPath)` Copies the visvis resources (such as the GLSL source code and the lena image) to the destination path, which should be the path containing the executable.
  * `getIncludes(backendName)` Returns a list of includes to give to cx\_freeze or py2exe or whatever freeze program in use. This list depends on the backend that is used in the frozen application.

Note that if different versions of Numpy or PyOpenGL are used, there might be additional dependencies if their (new) API's so require.

For help on embedding visvis in a WX or QT4 application, see the examples in the visvis/examples directory.