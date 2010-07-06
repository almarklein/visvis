description = 'An object oriented approach to visualization of 1D to 4D data.'
long_description = """
Visvis is a pure Python library for visualization of 1D to 4D
data in an object oriented way. Essentially, visvis is an object
oriented layer of Python on top of OpenGl, thereby combining the
power of OpenGl with the usability of Python. A Matlab-like
interface in the form of a set of functions allows easy creation 
of objects (e.g. plot(), imshow(), volshow(), surf()). 

"""

from distutils.core import setup

# Get version
for line in file('__init__.py').readlines():
    if (line.startswith('__version__')):
        exec(line.strip())


setup(
    name = 'visvis',
    version = __version__,
    author = 'Almar Klein',
    author_email = 'almar.klein at gmail',
    license = 'LGPL',
    
    url = 'http://code.google.com/p/visvis/',
    download_url = 'http://code.google.com/p/visvis/downloads/list',    
    keywords = "visualization OpenGl medical imaging 3D plotting",
    description = description,
    long_description = long_description,
    
    platforms = 'any',
    provides = ['visvis'],
    requires = ['numpy', 'pyOpenGl'],
    
    packages = ['visvis', 'visvis.functions', 'visvis.backends', 
                'visvis.processing', 'visvis.points'],
    package_dir = {'visvis': '.'},
    package_data = {'visvis': [ 'examples/*.py', 'visvisResources/*']},
    zip_safe = False, # I want examples to work
    )

# Note that the dir in package_dir must NOT be an empty string! This
# would work for distutils, but not for setuptools...
# I found this on-line doc very helpful for creating a setup script:
# http://docs.python.org/distutils/examples.html

