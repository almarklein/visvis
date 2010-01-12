""" Get Docs in wiki format on a visvis class.

"""
import types

def getWikiDocs(cls):
    
    className = str(cls)
    
    methods = {}
    properties = {}
    
    for att in cls.__dict__.keys():
        if att.startswith('_'):
            continue
        
        # Get info
        val = cls.__dict__[att]
        if val.__doc__:
            doclines = val.__doc__.splitlines()
        else:
            doclines = []
        
        if 'function' in str(type(val)):
            # A method
            if att in doclines[0]:
                line = className + '.' + doclines[0].lstrip()
                line = "*" + line + "*<br/>"
                doclines[0] = line
            else:
                line = className + '.' + att + "()"
                line = "*" + line + "*<br/>"
                doclines.insert(0,line)
            # Store
            methods[att] = '\n'.join(doclines)
        
        elif 'property' in str(type(val)):
            line = className + '.' + att
            line = "*" + line + "*<br/>"
            doclines.insert(0,line)
            # Store
            properties[att] = '\n'.join(doclines)
    
    # Produce docs:
    docs = "=" + className + "=\n"
    docs += cls.__doc__
    docs += '\n\n\n'
    
    # Insert properties
    docs += '\n== Properties ==\n\n'
    for key in sorted( properties.keys() ):
        docs += properties[key] + '\n\n'
    
    # Insert methods
    docs += '\n== Methods ==\n\n'
    for key in sorted( methods.keys() ):
        docs += methods[key] + '\n\n'
    
    print docs

import visvis as vv
getWikiDocs(vv.base.BaseObject)