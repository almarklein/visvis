import os, sys
import visvis as vv
import wikimaker

functionsDocstring = """Visvis is object oriented by nature. However, 
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
\n"""

classDocstring = """Visvis knows two kinds of visualization objects: 
wibjects (widget objects) which have a position in screen coordinates, 
and wobjects (world objects) which reside in a scene represented by an 
Axes object. 

Most of the time, the wobjects represent the stuff we want 
to visualize, and wibjects help doing that. Both the Wibject and Wobject 
class inherit from visvis.BaseObject.
"""


# Establish what classes to use: all default wibjects and wobjects
classes = set()
for cls in vv.wibjects.__dict__.values() + vv.wobjects.__dict__.values():
    if isinstance(cls, type) and issubclass(cls, vv.base.BaseObject):
        classes.add(cls)

# And more
moreClasses = ([vv.base.BaseObject, vv.Position,
    vv.axises.BaseAxis, vv.core.Legend, vv.core.AxesContainer,
    vv.textures.BaseTexture, vv.text.BaseText, vv.Range, 
    vv.MotionMixin,
    vv.Transform_Rotate, vv.Transform_Scale, vv.Transform_Translate,
    vv.utils.pypoints.BasePoints, vv.Point, vv.Pointset, vv.Aarray,
    vv.Quaternion, vv.BaseMesh, vv.Light,
    vv.OrientationForWobjects_mixClass, 
    vv.BaseSlider,
    vv.events.BaseEvent, vv.Timer, vv.events.MouseEvent, vv.events.EventMotion,
    vv.events.EventScroll, vv.events.EventMouseDown, vv.events.EventMouseUp,
    vv.events.EventDoubleClick, vv.events.EventEnter, vv.events.EventLeave,
    vv.events.EventPosition, vv.events.KeyEvent, vv.events.EventKeyDown, 
    vv.events.EventKeyUp,
    
    vv.cameras.BaseCamera, vv.FlyCamera, vv.TwoDCamera, vv.ThreeDCamera,
    ])
classes = classes.union(moreClasses)

# Sort the classes by name
classes = list(classes)
classes.sort(key=wikimaker.get_class_name)

# Sort the classes in bins
baseClasses, wibjectClasses, wobjectClasses, otherClasses = [], [], [], []
for cls in classes:
    if cls is vv.Wibject or cls is vv.Wobject or cls is vv.base.BaseObject:
        baseClasses.append(cls)
    elif issubclass(cls, vv.Wibject):
        wibjectClasses.append(cls)
    elif issubclass(cls, vv.Wobject):
        wobjectClasses.append(cls)
    else:
        otherClasses.append(cls)


# Create class API
if True:
    
    # Create a wiki file for each class
    for cls in classes:
        wikimaker.create_wiki_page('', cls)
    
    # Create a wiki file that gives an overview of all classes
    totaldocs = "----\n\n= The classes of Visvis =\n\n"
    totaldocs += classDocstring

    totaldocs += '<table width="100%"><tr>\n'
    classLists = [baseClasses, wibjectClasses, wobjectClasses, otherClasses]
    classTypes = ['Base classes', 'Wibject classes', 
                    'Wobject classes', 'Other classes']
    for i in range(4):
        totaldocs += '<td valign="top">\n'
        totaldocs += '*%s:*\n' % classTypes[i]
        for cls in classLists[i]:
            tmp = wikimaker.get_class_name(cls)
            totaldocs += '  * [cls_%s %s]\n' % (tmp, tmp)
        totaldocs += '</td>\n'

    totaldocs += '</tr></table>\n'

    # Store file
    f = open('classes.wiki', 'w')
    f.write(totaldocs)
    f.close()
    # Notify
    print 'Made class overview.'


# Create function API
if True:
    
    # Title and introduction
    totaldocs = "----\n\n= The functions of Visvis =\n\n"
    totaldocs += functionsDocstring
    
    # Insert links
    funcNames = sorted( vv.functions._functionNames )
    linkList = []
    for key in funcNames: 
        linkList.append( '[#%s %s]' % (key, key) )
    totaldocs += "*Here's a list of all the functions currently available:*<br/>\n"
    totaldocs += wikimaker.create_table_from_list(linkList) + '\n'
    
    totaldocs += '----\n\n'
    
    # Insert docs itself
    for name in funcNames:
        fun = vv.__dict__[name]
        docs = wikimaker.get_function_docs(fun)
        totaldocs += docs + '\n\n'
    
    totaldocs += '----\n\n'
    
    # Store in file
    f = open('functions.wiki', 'w')
    f.write(totaldocs)
    f.close()
    # Notify
    print 'Made docs for all functions.'

##

# Examples
if True:
    
    # Define groups
    groups = {  'Textures':['images', 'anisotropicData', 'anisotropicData2',
                            'colormaps',
                            'transparentTextures', 'volumes', 'volumeRenderStyles',
                            'slicesInVolume','fourDimensions',
                            'colorVolume', 'imageEdges', 'unsharpMasking',
                            ],
                'Meshes':  ['meshes', 'lightsAndShading', 'surfaceRender',
                            'bouncingBall', 'surfaceFromRandomPoints' ],
                'Plotting':['plotting', 'polarplots', 'pointCloud', 'statistics',],
                'Embedding':['embeddingInQt4', 'embeddingInWx',
                            'embeddingInGTK', 'embeddingInFLTK'],
            }
    overview_text = """    
The structure of the objects in the figure is illustrated by the image below. 
Note that the text objects for the axis and legend are also children of 
the respective objects, but have been left out of the image for clarity. World
objects are shown in blue.

http://wiki.visvis.googlecode.com/hg/images/graph_structure.png
    """


    # Select examples dir
    tmp = vv.misc.getResourceDir()
    path = os.path.join( os.path.split(tmp)[0], 'examples')
    
    # Get all files
    example_names = []
    for fname in os.listdir(path):
        
        # Get name and full filename
        name = os.path.splitext(fname)[0]
        fname = os.path.join(path, fname)
        
        # Store
        example_names.append(name)
        
        # Create wiki page
        text = '# Wiki page auto-generated from visvis examples\n\n'
        # Include images
        for ext in ['png', 'gif']:
            im_name = 'images/examples/example_%s.%s' % (name, ext)
            if os.path.isfile(im_name):
                text += 'http://wiki.visvis.googlecode.com/hg/' + im_name
                text += '\n\n'
        # Include code
        code = open(fname, 'rb').read().decode('utf-8')
        text += '{{{\n%s\n}}}\n' % code
        if name == 'overview':
            text += overview_text
        # Write wiki page
        fname_wiki = 'example_' + name + '.wiki'
        f = open(fname_wiki, 'wb')
        f.write(text.encode('utf-8'))
        f.close()
    
    # Create overview page ...
    text = ""
    example_names_processed = []
    
    # Collect examples per group
    for group in groups:
        text += '*%s*\n' % group            
        # Select examples
        for name in groups[group]:
            if name in example_names:
                text += '  * [%s %s]\n' % ('example_' + name, name)
                example_names_processed.append(name)
            else:
                print 'unknown example:', name
    
    # Collect misc examples
    if True:
        text += '*Misc*\n'
        for name in example_names:
            if name not in example_names_processed:
                text += '  * [%s %s]\n' % ('example_' + name, name)
    
    # Write overview page
    fname_wiki = 'Examples.wiki'
    f = open(fname_wiki, 'wb')
    f.write(text.encode('utf-8'))
    f.close()

    
if False: # todo: a list of all names...
    
    # Title and introduction
    totaldocs = "----\n\n= A list of the names in the visvis namespace  =\n\n"
    totaldocs += ''
