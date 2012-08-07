# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.


""" SCRIPT
Pack all font data in a single ssdf file.

Use the free command line tool BMFontGenerator to generate a .png
file with the character data and an xml file with the space and size
information for each character.

To make this even easier, I made a .bat file on which you can drop a
text file with the options to pass to BMFontGenerator.exe.

Next, run this script to collect the data and store it in 
an ssdf file. All created fonts are recognized and packed
in a single file. Do make sure the font is distributed in a 
single png file (if multiple files appear, make the size larger).

The result is fonts.ssdf.

the fontfiles should be named 
"<fontname>_<type>.xml", 
"<fontname>_<type>-0.png",
"<fontname>_<type>-1.png"
etc.
for instance "mono_r.xml", "mono_i-0.png".

"""

# The info is in an xml file but I chose to parse it line by line, 
# and hope the xml file is always produced one line per char.

from visvis import ssdf
import Image
import numpy as np
import os

class Char:
    pass

# get the path where this file is located
path = __file__
path = os.path.dirname( os.path.abspath(path) )
if not path.endswith('/'):
    path+='/'
if not os.path.isfile(path + 'pack.py'):
    # running from editor, testing ...
    path = 'D:/almar/projects/_p/tools/visvis/fonts/'




def processFont(fontname):

    ## retrieve fontsize
    fontsize = 6 # default very small so we see the error
    for line in open(path+'tmp/temp_font'+'.txt'):
        if line.startswith('-size'):
            fontsize = int(line[6:])
            break
    
    ## info

    entries = {}
    for line in open(path + 'tmp/' + fontname + '.xml'):
        # find character code
        i = line.find('code=')
        if i<0: continue
        ch = line[i+6:i+10]    
        ch = int(ch,16)    
        # create char
        char = Char()
        # find location in texture
        i = line.find('origin=')
        i1 = line.find("\"",i)
        if i<0 or i1<0: continue
        i2 = line.find("\"",i1+1)
        if i2<0: continue
        tmp = line[i1+1:i2]
        tmp = tmp.split(',')    
        if len(tmp)!=2: continue
        char.origin = [int(i) for i in tmp]
        # find size
        i = line.find('size=')
        i1 = line.find("\"",i)
        if i<0 or i1<0: continue
        i2 = line.find("\"",i1+1)
        if i2<0: continue
        tmp = line[i1+1:i2]
        tmp = tmp.split('x')    
        if len(tmp)!=2: continue
        char.size = [int(float(i)+0.5) for i in tmp]
        # find width
        i = line.find('aw=')
        i1 = line.find("\"",i)
        if i<0 or i1<0: continue
        i2 = line.find("\"",i1+1)
        if i2<0: continue
        tmp = line[i1+1:i2]    
        char.aw = int(tmp)    
        # store char    
        entries[ch] = char

    ## make lists of the information

    # a list of all registered characters
    charcodes = list(entries.keys())

    L = max(charcodes)+1
    origin = np.zeros((L,2), dtype=np.uint16)
    size = np.zeros((L,2), dtype=np.uint8)
    width = np.zeros((L,), dtype=np.uint8)
    for code in entries:
        char = entries[code]
        origin[code,0] = char.origin[0]
        origin[code,1] = char.origin[1]
        size[code,0] = char.size[0]
        size[code,1] = char.size[1]
        width[code] = char.aw
    
    ## image
    tmp = Image.open(path+'tmp/'+fontname+'-0.png')
    im = np.asarray(tmp)
    im = im[:,:,0]
    h, w = im.shape


    ## store data    
    s = ssdf.new()
    s.charcodes = np.array(charcodes, dtype=np.uint16)
    s.origin = origin
    s.size = size
    s.width = width
    s.data = im.copy()
    s.fontsize = fontsize
    return s
    
## Scan available fonts and pack them

files = os.listdir(path)
base = ssdf.new()
for font in ['mono', 'sans', 'serif']:
    ss = []
    for fonttype in ['r', 'b', 'i']:  # regular, bold, italic
        fontname = font+'_'+fonttype        
        s = processFont(fontname)
        ss.append(s)
    
    # process to pack together
    sr, sb, si = ss[0], ss[1], ss[2]
    for fonttype in ['b', 'i']:
        s = ss[{'b':1,'i':2}[fonttype]]
        # cut interesting part of image in i or b
        [Iy,Ix] = np.where(s.data>0); y1 = Iy.max()
        data = s.data[0:y1+1,:]
        # paste that part in image of regular
        [Iy,Ix] = np.where(sr.data>0); y1 = Iy.max()
        y2 = y1 + data.shape[0]
        sr.data[y1:y2] = data
        # correct origin of chars
        for i in range(s.origin.shape[0]):
            s.origin[i,1] += y1
        # copy information to struct of sr
        sr['charcodes_'+fonttype] = s.charcodes
        sr['origin_'+fonttype] = s.origin
        sr['size_'+fonttype] = s.size
        sr['width_'+fonttype] = s.width
    
    # store
    base[font] = sr

ssdf.save(path+'fonts.ssdf', base)
ssdf.save(path+'../visvisResources/fonts.ssdf', base)


