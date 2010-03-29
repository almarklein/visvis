from distutils.core import setup

from __init__ import __version__

setup(
    name='visvis',
    version=__version__,
    author='Almar Klein',
    author_email = 'almar.klein at gmail',
    license='LGPL',
    url='http://code.google.com/p/visvis/',
    description='An object oriented approach to visualization of 1D to 4D data.',
    
    platform='any',
    provides=['visvis'],
    requires=['numpy', 'pyOpenGl'],
    
    packages=['visvis', 'visvis.functions', 'visvis.backends', 'visvis.points'],
    package_dir = {'': 'D:\\almar\\projects\\_p'},
    package_data={'visvis': ['visvisResources/*.*',
                            'examples/*.py'
                            ] },

    )
