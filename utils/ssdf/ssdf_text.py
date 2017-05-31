# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# SSDF is distributed under the terms of the (new) BSD License.
# See http://www.opensource.org/licenses/bsd-license.php

""" ssdf.ssdf_text.py

Implements functionality to read/write text ssdf files.
"""

import sys
import struct
import base64
import zlib
import re

from . import ClassManager
from .ssdf_base import Struct, VirtualArray, SSDFReader, SSDFWriter, Block, _CLASS_NAME
from .ssdf_base import _shapeString, _FLOAT_TYPES, _INT_TYPES, _TYPE_DICT
from .ssdf_base import np, string_types, binary_type, ascii_type, reduce


# Get base64 encode/decode functions
PY3 = sys.version_info[0] == 3
if PY3:
    base64encode = base64.encodebytes
    base64decode = base64.decodebytes
else:
    base64encode = base64.encodestring
    base64decode = base64.decodestring


# The data types for arrays and how the struct (un)pack formatters.
_DTYPES = { 'uint8':'<B', 'int8':'<b',
            'uint16':'<H', 'int16':'<h',
            'uint32':'<L', 'int32':'<l',
            'float32':'<f', 'float64':'<d' }
    
    
class TextSSDFReader(SSDFReader):
    
    
    def read_text_blocks(self, lines):
        """ read_text_blocks(lines)
        
        Given a list of Unicode lines, create the block instances.
        This is a generator function.
        
        """
        for i in range(len(lines)):
            line = lines[i]
            count = i+1
            
            # Strip line
            line2 = line.lstrip()
            
            # Skip comments and empty lines
            if len(line2)==0 or line2[0] == '#':
                continue
            
            # Find the indentation
            indent = len(line) - len(line2)
            
            # Split name and value using a regular expression
            m = re.search("^\w+? *?=", line2)
            if m:
                i = m.end(0)
                name = line2[:i-1].strip()
                data = line2[i:].lstrip()
            else:
                name = None
                data = line2
            
            # Create block instance
            # Note that type is inferred from the raw data
            yield TextBlock(indent, count, name, data=data)
    
    
    def read(self, file_or_string):
        """ read(file_or_string)
        
        Given a file or string, convert it to a struct by reading the
        blocks, building the tree and converting each block to its
        Python object.
        
        """
        
        # Get lines
        if isinstance(file_or_string, string_types):
            lines = file_or_string.splitlines()
        else:
            lines = file_or_string.readlines()
            lines = [line.decode('utf-8') for line in lines]
        
        # Create blocks and build tree
        root = TextBlock(-1, -1, data='dict:')
        block_gen = self.read_text_blocks(lines)
        self.build_tree(root, block_gen)
        
        # Convert to real objects and return
        return root.to_object()



class TextSSDFWriter(SSDFWriter):
    
   
    def write_text_blocks(self, blocks):
        """ write_text_blocks(blocks)
        
        Converts the given blocks to a list of string lines.
        
        """
        # Skip first, it is the root object
        lines = []
        for block in blocks[1:]:
            
            # Write indent
            line = str(" ") * block._indent
            
            # Write name
            if block._name:
                line += "%s = " % block._name
            
            # Write data
            line += block._data
            lines.append(line)
        
        return lines
    
    
    def write(self, object, f=None):
        """ write(object, f=None)
        
        Serializes the given struct. If a file is given, writes
        (utf-8 encoded)text to that file, otherwise returns a string.
        
        """
        # Create block object
        root = TextBlock.from_object(-1, '', object)
        
        # Collect blocks and convert to lines
        blocks = self.flatten_tree(root, True)
        lines = self.write_text_blocks(blocks)
        
        # Write to file or return as a string
        if f is None:
            return '\n'.join(lines)
        else:
            NL = '\n'.encode('utf-8')
            for line in lines:
                f.write(line.encode('utf-8'))
                f.write(NL)


class TextBlock(Block):
    
    def to_object(self):
        
        # Determine what type of object we're dealing with by reading
        # like a human.
        data = self._data
        if not data:
            print('SSDF: no value specified at line %i.' % self._blocknr)
        elif data[0] in '-.0123456789':
            if '.' in data: return self._to_float()
            else: return self._to_int()
        elif data[0] == "'":
            return self._to_unicode()
        elif data.startswith('array'):
            return self._to_array()
        elif data.startswith('dict:'):
            return self._to_dict()
        elif data.startswith('list:') or data[0] == '[':
            return self._to_list()
        elif data.startswith('Null') or data.startswith('None'):
            return self._to_none()
        else:
            print("SSDF: invalid type on line %i." % self._blocknr)
            return None
    
    
    def _from_none(self, value=None):
        self._data = 'Null'
    
    def _to_none(self):
        return None
    
    
    def _from_int(self, value):
        self._data = '%i' % int(value)
    
    def _to_int(self):
        # First remove any comments
        line = self._data
        i = line.find('#')
        if i>0:
            line = line[:i].strip()
        try:
            return int(line)
        except Exception:
            print("SSDF: could not parse integer on line %i."%self._blocknr)
            return None
    
    
    def _from_float(self, value):
        # Use general specifier with a very high precision.
        # Any spurious zeros are automatically removed. The precision
        # should be sufficient such that any numbers saved and loaded
        # back will have the exact same value again. 20 seems plenty.
        self._data = '%0.20g' % value
    
    def _to_float(self):
        # First remove any comments
        line = self._data
        i = line.find('#')
        if i>0:
            line = line[:i].strip()
        try:
            return float(line)
        except Exception:
            print("SSDF: could not parse float on line %i."%self._blocknr)
            return None
    
    
    def _from_unicode(self, value):
        value = value.replace('\\', '\\\\')
        value = value.replace('\n','\\n')
        value = value.replace('\r','\\r')
        value = value.replace('\x0b', '\\x0b').replace('\x0c', '\\x0c')
        value = value.replace("'", "\\'")
        self._data = "'" + value + "'"
    
    def _to_unicode(self):
        # Encode double slashes
        line = self._data.replace('\\\\','0x07') # temp
        
        # Find string using a regular expression
        m = re.search("'.*?[^\\\\]'|''", line)
        if not m:
            print("SSDF: string not ended correctly on line %i."%self._blocknr)
            return None # return not-a-string
        else:
            line = m.group(0)[1:-1]
        
        # Decode stuff
        line = line.replace('\\n','\n')
        line = line.replace('\\r','\r')
        line = line.replace('\\x0b', '\x0b').replace('\\x0c', '\x0c')
        line = line.replace("\\'","'")
        line = line.replace('0x07','\\')
        return line
    
    
    def _from_dict(self, value):
        self._data = "dict:"
        self._type = _TYPE_DICT # Specify type, used by writer to sort
        # Get keys sorted by name
        keys = [key for key in value]
        keys.sort()
        # Process children
        for key in keys:
            # Skip all the buildin stuff
            if key.startswith("__"):
                continue
            # We have the key, go get the value!
            val = value[key]
            # Skip methods, or anything else we can call
            if hasattr(val,'__call__') and not hasattr(val, '__to_ssdf__'):
                # Note: py3.x does not have function callable
                continue
            # Add!
            subBlock = TextBlock.from_object(self._indent+1, key, val)
            self._children.append(subBlock)
    
    def _to_dict(self):
        value = Struct()
        for child in self._children:
            val = child.to_object()
            if child._name:
                value[child._name] = val
            else:
                print("SSDF: unnamed element in dict on line %i."%child._blocknr)
        # Make class instance?
        if _CLASS_NAME in value:
            className = value[_CLASS_NAME]
            if className in ClassManager._registered_classes:
                value = ClassManager._registered_classes[className].__from_ssdf__(value)
            else:
                print("SSDF: class %s not registered." % className)
        # Done
        return value
    
    
    def _from_list(self, value):
        # Check whether this is a "small list"
        isSmallList = True
        allowedTypes = _INT_TYPES+_FLOAT_TYPES+(string_types,)
        subBlocks = []
        for element in value:
            # Add element as subblock
            subBlock = TextBlock.from_object(self._indent+1, None, element)
            subBlocks.append(subBlock)
            # Check if ok type
            if not isinstance(element, allowedTypes):
                isSmallList = False
        
        # Store list
        if isSmallList:
            elements = [subBlock._data.strip() for subBlock in subBlocks]
            self._data = '[%s]' % (', '.join(elements))
        else:
            self._data = "list:"
            for subBlock in subBlocks:
                self._children.append(subBlock)
    
    def _to_list(self):
        value = []
        if self._data[0] == 'l': # list:
            
            for child in self._children:
                val = child.to_object()
                if child._name:
                    print("SSDF: named element in list on line %i."%child._blocknr)
                else:
                    value.append(val)
            return value
            
        else:
            # [ .., .., ..]
            return self._to_list2()
    
    
    def _to_list2(self):
        i0 = 1
        pieces = []
        inString = False
        escapeThis = False
        line = self._data
        for i in range(1,len(line)):
            if inString:
                # Detect how to get out
                if escapeThis:
                    escapeThis = False
                    continue
                elif line[i] == "\\":
                    escapeThis = True
                elif line[i] == "'":
                    inString = False
            else:
                # Detect going in a string, break, or end
                if line[i] == "'":
                    inString = True
                elif line[i] == ",":
                    pieces.append(line[i0:i])
                    i0 = i+1
                elif line[i] == "]":
                    piece = line[i0:i]
                    if piece.strip(): # Do not add if empty
                        pieces.append(piece)
                    break
        else:
            print("SSDF: one-line list not closed correctly on line %i." % self._blocknr)
        
        # Cut in pieces and process each piece
        value = []
        for piece in pieces:
            lo = TextBlock(self._indent, self._blocknr, data=piece.strip())
            value.append( lo.to_object() )
        return value
    
    
    def _from_array(self, value):
        shapestr = _shapeString(value)
        dtypestr = str(value.dtype)
            
        if value.size<33 and not isinstance(value, VirtualArray):
            # Small enough to print
            # Get values in list (we need to ravel)
            if 'int' in dtypestr:
                elements = ['%i' % v for v in value.ravel()]
            else:
                elements = ['%0.20g' % v for v in value.ravel()]
            if elements:
                elements.append('') # Make sure there's at least one komma
            # Build string
            self._data = "array %s %s %s" % (shapestr, dtypestr,
                ", ".join(elements) )
        
        else:
            # Store binary
            # Get raw data
            data = value.tostring()
            # In blocks of 1MB, compress and encode
            BS = 1024*1024
            texts = []
            i=0
            while i < len(data):
                block = data[i:i+BS]
                blockc = zlib.compress(block)
                text = base64encode(blockc).decode('utf-8')
                texts.append( text.replace("\n","") )
                i += BS
            text = ';'.join(texts)
            self._data = "array %s %s %s" % (shapestr, dtypestr, text)
    
    def _to_array(self):
        
        # Split
        tmp = self._data.split(' ',3)
        if len(tmp) < 4:
            print("SSDF: invalid array definition on line %i."%self._blocknr)
            return None
        # word1 = tmp[0] # says "array"
        word2 = tmp[1]
        word3 = tmp[2]
        word4 = tmp[3]
        
        # Determine shape and size
        try:
            shape = [int(i) for i in word2.split('x') if i]
        except Exception:
            print("SSDF: invalid array shape on line %i."%self._blocknr)
            return None
        if shape:
            size = reduce( lambda a,b:a*b, shape)
        else:
            size = 1 # Scalar
        
        # Determine datatype
        # Must use 1byte/char string in Py2.x, or numpy wont understand )
        dtypestr = ascii_type(word3)
        if dtypestr not in _DTYPES.keys():
            print("SSDF: invalid array data type on line %i."%self._blocknr)
            return None
        
        # Stored as ASCII?
        asAscii = ( word4.find(',', 0, 100) > 0 ) or ( word4.endswith(',') )
        
        # Get data
        if size==0:
            # Empty array
            data = binary_type()
        
        elif asAscii:
            # Stored in ascii
            dataparts = []
            fmt = _DTYPES[dtypestr]
            for val in word4.split(','):
                if not val.strip():
                    continue
                try:
                    if 'int' in dtypestr:
                        val = int(val)
                    else:
                        val = float(val)
                    dataparts.append(struct.pack(fmt, val))
                except Exception:
                    if 'int' in dtypestr:
                        dataparts.append(struct.pack(fmt, 0))
                    else:
                        dataparts.append(struct.pack(fmt, float('nan')))
                        
            data = binary_type().join(dataparts)
        
        else:
            # Stored binary
            # Get data: decode and decompress in blocks
            dataparts = []
            for blockt in word4.split(';'):
                blockc = base64decode(blockt.encode('utf-8'))
                block = zlib.decompress(blockc)
                dataparts.append(block)
            data = binary_type().join(dataparts)
        
        # Almost done ...
        if not np:
            # Make virtual array to allow saving it again
            return VirtualArray(shape, dtypestr, data)
        elif data:
            # Convert to numpy array
            value  = np.frombuffer(data, dtype=dtypestr )
            # Set and check shape
            if size == value.size:
                value.shape = tuple(shape)
            else:
                print("SSDF: prod(shape)!=size on line %i."%self._blocknr)
            return value
        else:
            # Empty numpy array
            return np.zeros(shape, dtype=dtypestr)
