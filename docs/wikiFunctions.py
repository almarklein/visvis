""" This script checks all functions and gives a 
documentation text in wiki format to paste on the web. 
"""
import os, sys, re

# get files
path = 'd:/almar/projects/_p/tools/visvis/functions'
files = os.listdir(path)

# extract all functions
names = []
text = ""
for file in files:
    # not this file
    if file.startswith('__'):
        continue
    # only python files
    if file.endswith('.pyc'):
        if file[:-1] in files:
            continue # only try import once
    elif not file.endswith('.py'):
        continue    
    # build names
    fullfile = os.path.join(path, file)
    funname = os.path.splitext(file)[0]
    # load file and extract function signature
    f = open(fullfile,'r')
    text = f.read()
    f.close()
    tmp = re.search('def '+funname+'(.*):', text)    
    if tmp:
        sig = '*'+funname+'*' + tmp.group(1).replace('*','`*`')
    else:
        sig = '*'+funname+'*'
    # import module
    mod = __import__("visvis.functions."+funname, fromlist=[funname])
    if not hasattr(mod,funname):
        print "module %s does not have a function with the same name!" % (
            funname)
    else:
        # get doc and take first line
        #doc = mod.__dict__[funname].__doc__
        doc = mod.__doc__
        if doc:
            doc = doc#doc.splitlines()[0]
        else:
            doc = ''
        print '  *',sig, '-', doc
        # insert into THIS namespace
#         g = globals()
#         g[funname] = mod.__dict__[funname]
#         names.append(funname)

