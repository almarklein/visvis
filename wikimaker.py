""" wikimaker.py
Module to create wiki pages (for google code) from docstrings.

Copyright (c) 2010, Almar Klein
All rights reserved. BSD licensed.
"""

import re

COLOR_FUNC = '#066' #'#E50'
COLOR_PROP = '#070' #'#900'
COLOR_CLASS = '#00B' #'#080' 
COLOR_PARAM = '#020'
COLOR_HEAD = '#A50'

def smart_format( text):
    
    class Line:
        def __init__(self, text):
            self.text = text
            self.sText = text.lstrip()
            self.indent = len(self.text) - len(self.sText)
            self.needNL = False
            self.isParameter = False
    
    # Get lines
    lines = text.splitlines()
    
    # Test minimal indentation
    minIndent = 9999
    for line in lines[1:]:
        tmp = line.lstrip()
        indent = len(line) - len(tmp)
        if tmp:
            minIndent = min(minIndent, indent)
    
    # Remove minimal indentation
    lines2 = [ Line(lines[0].lstrip()) ]
    for line in lines[1:]:            
        lines2.append( Line(line[minIndent:]) )
    
    # Prepare state variables   
    prevLine = Line('')     
    inExample = False
    inCode = False
    inParameter = False
    
    # Format line by line
    lines3 = []
    for line in lines2:
        
        if not line.sText:
            if inParameter:
                lines3.append("</font>\n\n")
                inParameter = False
            elif inCode or inExample:
                lines3.append("\n")
            else:
                lines3.append("\n\n")
            prevLine = Line('')
            continue
        
        # Detect special cases
        if line.indent == prevLine.indent and ( "---" in line.text or 
                                                "===" in line.text):
            underCount = line.text.count('-') + line.text.count('=')
            len1, len2 = len(line.text.strip()), len(prevLine.text.strip())
            if underCount == len1 and len2 and  len1 >= len2:
                # Header
                if True:
                    head = "<b><u><font color='%s'>%s</font></u></b><br />"
                    lines3[-1] = head % (COLOR_HEAD, prevLine.sText)
                    line.text = line.sText = ''
                    line.needNL = True
                # Close example?
                if inExample:
                    lines3.insert(-1, '\n}}}\n')
                # Start example?
                inExample = False
                if prevLine.sText.lower().startswith('example'):
                    inExample = True
                    line.text = '\n{{{' 
                    line.needNL = False
        elif ' : ' in line.text:
            # Parameter (numpy style)
            tmp = line.text.split(' : ',1)
            line.text = '<u>' + tmp[0] + ' : ' + tmp[1] + '</u>' #+ tmp[1]
            line.text += "<br /><font color='%s'>" % COLOR_PARAM
            # Handle parameter
            if inParameter:
                line.text = '</font>' + line.text
            inParameter = True
            line.isParameter = True
            prevLine.needNL = True
        elif line.sText[:2] in ['* ', '# '] and not (inExample or inCode):
            # Bullet or enumeration, wiki makes newline for bullets
            prevLine.needNL = False
            line.text = '\n' + line.text
        elif line.sText[:3] in ['{{{', '}}}']:
            # Code block
            if line.sText[0] == '{':
                inCode = True
            else:
                inCode = False
            line.text = '\n' + line.text + '\n'
        elif prevLine.needNL:
            line.text = '\n' + line.sText
        elif inExample or inCode:
            line.text = '\n' + line.text
        elif prevLine.sText:
            line.text = " " + line.sText
            line.isParameter = prevLine.isParameter
        else:
            line.text = line.text
        
        # Prepend html newline tag?
        if prevLine.needNL:
            line.text = '<br />' + line.text
        
        # Prepend font closing tag?
        if inParameter and not line.isParameter:
            line.text = '</font>' + line.text
            inParameter = False
        
        # Done with line
        prevLine = line
        lines3.append(line.text)
    
    # Finish parameter
    if inParameter:
        lines3.append('</font>\n')
        
    # Finish example
    if inExample:
        lines3.append('}}}\n')
    
    # Done line by line formatting
    docs = ''.join(lines3)
    
    # "Pack" underscores and asterix that are not intended as markup
    # Mark all asterixes that surround a word or bullet
    docs = re.sub('(\s)\*(\w+)\*(\s)', '\g<1>\0\g<2>\0\g<3>', docs)
    docs = re.sub( re.compile('^(\s+)\* ',re.MULTILINE), '\g<1>\0 ', docs)
    # Pack all remaining asterixes
    docs = docs.replace('*',"`*`").replace('\0','*')
    # Do the same for underscores (but no need to look for bullets)
    # Underscores within a word do not need esacping.
    docs = re.sub('(\s)_(\w+)_(\s)', '\g<1>\0\g<2>\0\g<3>', docs)
    docs = docs.replace(' _'," `_`").replace('_ ', '`_` ').replace('\0','_')
    # Pack square brackets
    docs = docs.replace("[[","<BRACKL>").replace("]]","<BRACKR>")
    docs = docs.replace("[","`[`").replace("]","`]`")
    docs = docs.replace("<BRACKL>", "[").replace("<BRACKR>", "]")
    
    return docs


def split_docs(ob, name, base_name=''):
    """ split_docs(ob, name, base_name='')
    
    Get the docstring of the given object as a two element tuple:
    (header, body)
    
    The header contains the name and signature (if available) of the class
    or function. 
    
    Uses smart_format() internally.
    
    """
    
    def searchEndBrace(text, i0):
        """ Start on opening brace. """
        i = i0
        level = int(text[i0]=='(')
        while level and (i <len(text)-1):
            i+=1
            if text[i] == '(':
                level += 1
            elif text[i] == ')':
                level -= 1
        
        if level:
            return i0+1
        else:
            return i
    
    
    # Get docs using smart_format()
    docs = smart_format(ob.__doc__)
    
    # Depending on class, analyse signature, or use a default signature.
    
    if 'function' in str(type(ob)):
        header = name + '()'
        
        # Is the signature in the docstring?
        if docs.startswith(name+'('):
            docs2 = docs.replace('\r','|').replace('\n','|')
            tmp = re.search(name+'(\(.*?\))', docs2)
            if True:
                i = searchEndBrace(docs, len(name)) + 1
                header = docs2[:i].replace('|', '') 
                docs = docs[i:].lstrip(':').lstrip()
            elif tmp:
                header = name + tmp.group(1)
                docs = docs[len(header):].lstrip(':').lstrip()
                #header = header.replace('*','`*`').replace('|','')
                header = header.replace('|','')
    
    elif 'property' in str(type(ob)): 
        header = name
        
        # Is the "signature in the header?
        if docs.startswith(name):
            header, sep, docs = docs.partition('\n')
    
    elif 'type' in str(type(ob)): 
        header = name
        
        # Is the signature in the docstring?
        if docs.startswith(name+'('):
            docs2 = docs.replace('\r','|').replace('\n','|')
            tmp = re.search(name+'(\(.*?\))', docs2)
            if True:
                i = searchEndBrace(docs, len(name)) + 1
                header = docs2[:i].replace('|', '') 
                docs = docs[i:].lstrip(':').lstrip()
            elif tmp:
                header = name + tmp.group(1)
                docs = docs[len(header):].lstrip(':').lstrip()
                #header = header.replace('*','`*`').replace('|','')
                header = header.replace('|','')
        elif docs.startswith(name):
            header, sep, docs = docs.partition('\n')
    
    # Remove spaces from header
    for i in range(10):
        header = header.replace('  ',' ')
    
    # Add class name to header
    if base_name:
        header = base_name + '.' + header
    
    # Done
    return header, docs


def get_property_docs(prop, name, class_name=''):
    """ get_property_docs(prop, name, class_name='')
    
    Get wiki content for the specified property. Makes a header from
    the property name (with an anchor) and indents the body of
    the documentation.
    
    (Need the name, since we cannot obtain it from the 
    property object. )
    """
    
    # Get docs
    header, docs = split_docs (prop, name, class_name)
    
    # Add indentation (so it is uniform)
    doclines = docs.splitlines()
    for i in range(len(doclines)):
        doclines[i] = "  " + doclines[i]
    docs = '\n'.join(doclines)
    
    # Return with markup
    anchor = '==== <font color="#FFF">%s</font> ====\n'
    contnt = '=== <font color="%s">%s</font> ===\n\n%s'
    return anchor % name + contnt % (COLOR_PROP, header, docs)
    
    
    
def get_function_docs(fun, name=None, class_name='', **kwargs):
    """ get_function_docs(fun, class_name='')
    
    Get wiki content for the specified function or method. Makes 
    a header from the property name (with an anchor) and indents 
    the body of the documentation.
    """
    
    # Get docs
    if name is None:
        name = fun.__name__
    header, docs = split_docs(fun, name, class_name)
    
    # Add indentation (so it is uniform)
    doclines = docs.splitlines()
    for i in range(len(doclines)):
        doclines[i] = "  " + doclines[i]
    docs = '\n'.join(doclines)
    
    # Return with markup. Also return an invisible header so that the
    # links will work. Use exclamation mark so it wont't be seen as Wiki link.
    if name[0].isupper():
        name = '!' + name
    anchor = '==== <font color="#FFF">%s</font> ====\n'
    contnt = '=== <font color="%s">%s</font> ===\n\n%s'
    return anchor % name + contnt % (COLOR_FUNC, header, docs)


def get_class_docs(cls, package_name='', include_inherited=False):
    """ get_class_docs(package_name='', include_inherited=False)
    
    Get wiki content for the specified class. Writes the formatted
    docstring of the class, lists all methods and properties and
    gives the docs for all methods and properties (as given by 
    get_function_docs() and get_property_docs()).
    
    If include_inherited is True, also include inherited properties
    and methods. 
    
    """
    
    # Get name
    class_name = get_class_name(cls)
    
    # containers for attributes
    methods = {}
    properties = {}
    
    # Collect attributes
    atts = {}
    def collect_attributes(cls):
        for att, val in cls.__dict__.items():
            atts[att] = val
        if include_inherited:
            for c in cls.__bases__:
                collect_attributes(c)
    collect_attributes(cls)
    
    # Collect docs for methods and properties
    for att in atts.keys():
        
        # Get value
        val = atts[att]
        
        # Don't do private attributes
        if att.startswith('_'):
            continue
        
        # Skip if attribute does not have a docstring
        if not val.__doc__:
            print('Skipping %s.%s: no docstring' % (class_name, att))
            continue
        
        # Get info
        if 'function' in str(type(val)):
            methods[att] = get_function_docs(val, att, class_name)
        elif 'property' in str(type(val)):
            properties[att] = get_property_docs(val, att, class_name )
    
    # Init the variable to hold the docs
    total_docs = '----\n'
    
    # Produce anchor
    total_docs += '==== <font color="#FFF">%s</font> ====\n' % class_name.lower()
    
    # Produce Title
    header, docs = split_docs(cls, class_name)
    tmp = '= <font color="%s">class %s</font> =\n\n'
    if package_name:
        total_docs += tmp % (COLOR_CLASS, package_name+'.'+header)
    else:
        total_docs += tmp % (COLOR_CLASS, header)
    
    # Show inheritance
    bases = []
    for base in cls.__bases__:
        tmp = get_class_name(base)
        bases.append( '[cls_%s %s]' % (tmp, tmp) )
    total_docs += 'Inherits from %s.\n\n' % ', '.join(bases)
    
    # Insert docs itself
    total_docs += docs + '\n\n'
    
    # Insert summary of properties with links
    if properties:
        propList = []
        for key in sorted( properties.keys() ):
            propList.append( '[#%s %s]' % (key, key) )
        tmp = '*The %s class implements the following properties:*<br/>'
        total_docs += tmp % class_name
        #propList = ['  * '+m for m in propList]
        #total_docs += '\n'.join(propList) + '\n\n'
        total_docs += create_table_from_list(propList) + '\n'
    
    # Insert summary of methods with links
    if methods:
        method_list = []
        for key in sorted( methods.keys() ):
            method_list.append( '[#%s %s]' % (key, key) )
        tmp = '*The %s class implements the following methods:*<br/>\n'
        total_docs += tmp % class_name
        #method_list = ['  * '+m for m in method_list]
        #total_docs += '\n'.join(method_list) + '\n\n'
        total_docs += create_table_from_list(method_list) + '\n'
    
    # Insert properties
    if properties:
        total_docs += '\n----\n\n== Properties ==\n\n'
        for key in sorted( properties.keys() ):
            total_docs += properties[key] + '\n\n'
    
    # Insert methods
    if methods:
        total_docs += '\n----\n\n== Methods ==\n\n'
        for key in sorted( methods.keys() ):
            total_docs += methods[key] + '\n\n'
    
    # End with line
    total_docs += '----\n\n'
    
    # Done
    return total_docs


def get_class_name(cls):
    """ get_class_name(cls)
    Get the name of the given type object.
    """
    name = str(cls)
    try:
        name = name.split("'")[1]
    except Exception:
        pass
    name = name.split(".")[-1]
    return name


def create_table_from_list(elements, columns=3):
    """ create_table_from_list(elements, columns=3)
    
    Create a table from a list, consisting of a specified number
    of columns.
    """
    
    import math
    
    # Check how many elements in each column
    n = len(elements)
    tmp = n / float(columns)
    rows = int( math.ceil(tmp) )
    
    # Correct rows in a smart way, so that each column has at least
    # three items
    ok = False  
    while not ok:
        cn = []
        for i in range(columns):
            tmp = n - rows*i
            if tmp <= 0:
                tmp = 9999999999 
            cn.append( min(rows, tmp) )
        #print cn
        if rows >= n:
            ok = True
        elif min(cn) <= 3:
            rows += 1
        else:
            ok = True
    
    
    # Open table
    text = "<table cellpadding='10px'><tr>\n"
    
    # Insert columns
    for col in range(columns):
        text += '<td valign="top">\n'
        for row in range(rows):
            i = col*rows + row
            if i < len(elements):
                text += elements[i] + '<br />'
        text += '</td>\n'
    
    # Close table and return
    text += '</tr></table>\n'
    return text
    
    
    

def isclass(object):
    return isinstance(object, type) or type(object).__name__ == 'classobj'


def get_docs(object, base_name='', **kwargs):
    """ get_docs(object, base_name='')
    
    Get the docs for the given string, class, function, or list with 
    any of the above items.
    
    """
    
    if isinstance(object, basestring):
        return smart_format(object, **kwargs)
    elif isinstance(object, list):
        tmp = [get_docs(ob, base_name, **kwargs) for ob in object]
        return '\n\n'.join(tmp)
    elif isclass(object):
        return get_class_docs(object, base_name, **kwargs)
    elif 'function' in str(type(object)):
        return get_function_docs(object, None, base_name, **kwargs)
    else:
        raise ValueError('Cannot determine how to generate docs from object.')


def create_wiki_page(fname, object, base_name='', **kwargs):
    """ create_wiki_page(fname, object, base_name='', **kwargs)
    
    Create a wiki page of the given object. If the object is a list, 
    creates a wiki page with documentation of all objects in that list.
    
    If fname evaluates to False, will auto-generate a filename (only 
    works for functions and classes).
    
    """
    
    # Auto-generate filename?
    if not fname:
        if isclass(object):
            fname = 'cls_%s.wiki' % get_class_name(object)
        elif 'function' in str(type(object)):
            fname = 'fun_%s.wiki' % object.__name__
    
    # Get docs
    docs = get_docs(object, base_name, **kwargs)
    
    # Write
    if fname:
        # Need extension?
        if not '.' in fname:
            fname += '.wiki'
        # Open file and write
        f = open(fname, 'w')
        f.write('#summary Docs generated by wikimaker.py\n\n')
        f.write(docs)
        f.close()
        # Notify
        print 'Wrote wiki page: ', fname
    else:
        raise ValueError('Need filename.')


# todo: function to document whole module.
