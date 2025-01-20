# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# SSDF is distributed under the terms of the (new) BSD License.
# See http://www.opensource.org/licenses/bsd-license.php

""" ssdf.ssdf_bin.py

Implements functionality to read/write binary ssdf (.bsdf) files.
"""

import struct
import zlib

from . import ClassManager
from .ssdf_base import Struct, VirtualArray, SSDFReader, SSDFWriter, Block, _CLASS_NAME
from .ssdf_base import np, binary_type, ascii_type


# Formatters for struct (un)packing
_SMALL_NUMBER_FMT = '<B'
_LARGE_NUMBER_FMT = '<Q'
_TYPE_FMT = '<B'
_PARTITION_LEN_FMT = '<I'
_PARTITION_SIZE = 2**20 # 1 MB

# Types for binary
_TYPE_NONE = ord('N')
_TYPE_INT = ord('I')
_TYPE_FLOAT = ord('F')
_TYPE_UNICODE = ord('U')
_TYPE_ARRAY = ord('A')
_TYPE_LIST = ord('L')
_TYPE_DICT = ord('D')


class BinarySSDFReader(SSDFReader):
    
   
    def read_binary_blocks(self, f):
        """ read_binary_blocks(f)
        
        Given a file, creates the block instances.
        This is a generator function.
        
        """
        count = 0
        while True:
            count += 1
            
            # Get type. If no bytes left, we're done
            try:
                type_id, = struct.unpack(_TYPE_FMT, f.read(1))
            except StopIteration:
                break
            
            # Get indentation
            indent = f.read_number()
            
            # Get name
            name_len = f.read_number()
            if name_len:
                name = f.read(name_len).decode('utf-8')
            else:
                name = None
            
            # Get data
            data_len = f.read_number()
            data = f.read(data_len)
            
            # Create block instance
            yield BinaryBlock(indent, count, name, type_id, data=data)
    
    
    def read(self, file_or_bytes):
        """ read(file_or_bytes)
        
        Given a file or bytes, convert it to a struct by reading the
        blocks, building the tree and converting each block to its
        Python object.
        
        """
        
        # Get file
        if isinstance(file_or_bytes, binary_type):
            f = _VirtualFile(file_or_bytes)
        else:
            f = file_or_bytes
        
        # Check header
        bb1 = "BSDF".encode('utf-8')
        try:
            bb2 = f.read(len(bb1))
        except Exception:
            raise ValueError('Could not read header of binary SSDF file.')
        if bb1 != bb2:
            raise ValueError('Given SSDF bytes/file does not have the right header.')
        
        # Create compressed file to read from
        fc = _CompressedFile(f)
        
        # Create blocks and build tree
        root = BinaryBlock(-1, -1, type=_TYPE_DICT)
        block_gen = self.read_binary_blocks(fc)
        self.build_tree(root, block_gen)
        
        # Convert to real objects and return
        return root.to_object()
    

class BinarySSDFWriter(SSDFWriter):
    
    
    def write_binary_blocks(self, blocks, f):
        """ write_binary_blocks(blocks, f)
        
        Writes the given blocks to a binary file.
        
        """
        
        # Skip first, it is the root object
        for block in blocks[1:]:
            
            # Write type.
            f.write(struct.pack(_TYPE_FMT, block._type))
            
            # Write indentation
            f.write_number(block._indent)
            
            # Write name
            if block._name:
                name = block._name.encode('utf-8')
                f.write_number(len(name))
                f.write(name)
            else:
                f.write_number(0)
            
            # Write data
            if isinstance(block._data, list):
                data_len = sum([len(d) for d in block._data])
                f.write_number(data_len)
                for part in block._data:
                    f.write(part)
            else:
                data_len = len(block._data)
                f.write_number(data_len)
                f.write(block._data)
    
    
    
    def write(self, object, f=None):
        """ write(object, f=None)
        
        Serializes the given struct. If a file is given, writes bytes
        to that file, otherwise returns a bytes instance.
        
        """
        
        # Check input
        if f is None:
            f = _VirtualFile()
            return_bytes = True
        else:
            return_bytes = False
        
        # Write header
        f.write('BSDF'.encode('utf-8'))
        
        # Make compressed file
        fc = _CompressedFile(f)
        
        # Create block object
        root = BinaryBlock.from_object(-1, binary_type(), object)
        
        # Collect blocks and write
        blocks = self.flatten_tree(root)
        self.write_binary_blocks(blocks, fc)
        fc.flush()
        
        # Return?
        if return_bytes:
            return f.get_bytes()
    


class BinaryBlock(Block):
    
    
    def to_object(self):
        # Determine what type of object we are dealing with using the
        # type id.
        type = self._type
        if type==_TYPE_INT: return self._to_int()
        elif type==_TYPE_FLOAT: return self._to_float()
        elif type==_TYPE_UNICODE: return self._to_unicode()
        elif type==_TYPE_ARRAY: return self._to_array()
        elif type==_TYPE_LIST: return self._to_list()
        elif type==_TYPE_DICT: return self._to_dict()
        elif type==_TYPE_NONE: return self._to_none()
        else:
            print("SSDF: invalid type %s in block %i." % (repr(type), self._blocknr))
            return None
    
    
    def _from_none(self, value=None):
        self._type = _TYPE_NONE
        self._data = binary_type()
    
    def _to_none(self):
        return None
    
    
    def _from_int(self, value):
        self._type = _TYPE_INT
        self._data = struct.pack('<q', int(value))
    
    def _to_int(self):
        return struct.unpack('<q', self._data)[0]
    
    
    def _from_float(self, value):
        self._type = _TYPE_FLOAT
        self._data = struct.pack('<d', float(value))
    
    def _to_float(self):
        return struct.unpack('<d', self._data)[0]
    
    
    def _from_unicode(self, value):
        self._type = _TYPE_UNICODE
        self._data = value.encode('utf-8')
    
    def _to_unicode(self):
        return self._data.decode('utf-8')
    
    
    def _from_array(self, value):
        self._type = _TYPE_ARRAY
        f =_VirtualFile()
        # Write shape and dtype
        f.write_number(value.ndim)
        for s in value.shape:
            f.write_number(s)
        f.write_string(str(value.dtype))
        # Write data
        # tostring() returns bytes, not a string on py3k
        self._data = [f.get_bytes(), value.tostring()]
    
    def _to_array(self):
        f = _VirtualFile(self._data)
        # Get shape and dtype
        ndim = f.read_number()
        shape = [f.read_number() for i in range(ndim)]
        dtypestr = ascii_type(f.read_string())
        # Create numpy array or Virtual array
        i = f._fp
        if not np:
            return VirtualArray(shape, dtypestr, self._data[i:])
        else:
            if i < len(self._data):
                value = np.frombuffer(self._data, dtype=dtypestr, offset=i)
            else:
                value = np.array([], dtype=dtypestr)
            if np.prod(shape) == value.size:
                value.shape = tuple(shape)
            else:
                print("SSDF: prod(shape)!=size on line %i."%self._blocknr)
            return value
    
    
    def _from_dict(self, value):
        self._type = _TYPE_DICT
        self._data = binary_type()
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
            subBlock = BinaryBlock.from_object(self._indent+1, key, val)
            self._children.append(subBlock)
    
    def _to_dict(self):
        value = Struct()
        for child in self._children:
            val = child.to_object()
            if child._name:
                value[child._name] = val
            else:
                print("SSDF: unnamed element in dict in block %i."%child._blocknr)
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
        self._type = _TYPE_LIST
        self._data = binary_type()
        
        # Process children
        for element in value:
            # Add element as subblock
            subBlock = BinaryBlock.from_object(self._indent+1, None, element)
            self._children.append(subBlock)
    
    def _to_list(self):
        value = []
    
        for child in self._children:
            val = child.to_object()
            if child._name:
                print("SSDF: named element in list in block %i."%child._blocknr)
            else:
                value.append(val)
        return value



class _FileWithExtraMethods:
    
    def write_number(self, n):
        if n < 255:
            self.write( struct.pack(_SMALL_NUMBER_FMT, n) )
        else:
            self.write( struct.pack(_SMALL_NUMBER_FMT, 255) )
            self.write( struct.pack(_LARGE_NUMBER_FMT, n) )
    
    def write_bytes(self, bb):
        self.write_number(len(bb))
        self.write(bb)
    
    def write_string(self, ss):
        self.write_bytes(ss.encode('utf-8'))
    
    def read_number(self):
        n, = struct.unpack(_SMALL_NUMBER_FMT, self.read(1))
        if n == 255:
            n, = struct.unpack(_LARGE_NUMBER_FMT, self.read(8))
        return n
    
    def read_bytes(self):
        n = self.read_number()
        return self.read(n)
    
    def read_string(self):
        return self.read_bytes().decode('utf-8')


class _VirtualFile(_FileWithExtraMethods):
    """ _VirtualFile(bb=None)
    
    Wraps a bytes instance to provide a file-like interface. Also
    represents a file like object to which bytes can be written, and
    the resulting bytes can be obtained using get_bytes().
    
    """
    def __init__(self, bb=None):
        # For reading
        self._bb = bb
        self._fp = 0
        # For writing
        self._parts = []
    
    def read(self, n):
        i1 = self._fp
        self._fp = i2 = self._fp + n
        return self._bb[i1:i2]
    
    def write(self, data):
        self._parts.append(data)
    
    def close(self):
        pass
    
    def get_bytes(self):
        return binary_type().join(self._parts)


class _CompressedFile(_FileWithExtraMethods):
    """ _CompressedFile(file)
    
    Wraps a file object to transparantly support reading and writing
    data from/to a compressed file.
    
    Data is compressed in partitions of say 1MB. A partition in the file
    consists of a small header and a body. The header consists of 4 bytes
    representing the body's length (little endian unsigned 32 bit int).
    The body consists of bytes compressed using DEFLATE (i.e. zip).
    
    """
    
    def __init__(self, f):
        
        # Store file
        self._file = f
        
        # For reading
        self._buffer = binary_type()
        self._bp = 0 # buffer pointer
        
        # For writing
        self._parts = []
        self._pp = 0 # parts pointer (is more like a counter)
    
    
    def _read_new_partition(self):
        """ _read_new_partition()
        
        Returns the data in the next partition.
        Returns false if no new partition is available.
        
        """
        
        # Get bytes and read partition length
        # If eof, return True
        bb = self._file.read(4)
        if not bb:
            self._buffer = binary_type()
            self._bp = 0
            return False
        n, = struct.unpack(_PARTITION_LEN_FMT, bb)
        
        # Read partition and decompress
        bb = self._file.read(n)
        data = zlib.decompress(bb)
        del bb
        
        # Done
        return data
    
    
    def _write_new_partition(self):
        """ _write_new_partition()
        
        Compress the buffered data and write to file. Reset buffer.
        
        """
        
        # Get data
        data = binary_type().join(self._parts)
        
        # Reset buffer
        self._parts = []
        self._pp = 0
        
        # Compress and write
        bb = zlib.compress(data)
        del data
        header = struct.pack(_PARTITION_LEN_FMT, len(bb))
        self._file.write(header)
        self._file.write(bb)
    
    
    def read(self, n):
        """ read(n)
        
        Read n bytes. Partitions are automatically decompressed on the fly.
        If the end of the file is reached, raises StopIteration.
        
        """
        
        # Get bytes in buffer
        bytes_in_buffer = len(self._buffer) - self._bp
        
        if bytes_in_buffer < n:
            # Read partitions untill we have enough
            
            # Prepare
            localBuffer = [self._buffer[self._bp:]]
            bufferCount = len(localBuffer[0])
            
            # Collect blocks of data
            while bufferCount < n:
                partition = self._read_new_partition()
                if partition:
                    localBuffer.append(partition)
                    bufferCount += len(partition)
                else:
                    raise StopIteration
            
            # Update buffer
            offset = len(partition) - (bufferCount - n)
            self._bp = offset
            self._buffer = partition
            
            # Truncate last block and get data
            localBuffer[-1] = partition[:offset]
            data = binary_type().join(localBuffer)
        
        else:
            # Get data from current partition
            i1 = self._bp
            self._bp = i2 = i1 + n
            data = self._buffer[i1:i2]
        
        return data
    
    
    def write(self, data):
        """ write(data)
        
        Write data. The data is buffered until the accumulated size
        exceeds the partition size. When this happens, the data is compressed
        and written to the real underlying file/data.
        
        """
        
        # Get how many bytes we have beyond _PARTITION_SIZE
        i = (self._pp + len(data)) - _PARTITION_SIZE
        
        if i > 0:
            # Add portion to buffer, store remainder
            self._parts.append(data[:i])
            data = data[i:]
            # Write the buffer away and reset buffer
            self._write_new_partition()
        
        # Add data to buffer
        self._parts.append(data)
        self._pp += len(data)
    
    
    def flush(self):
        """ flush()
        
        After the last write, use this to compress and write
        the last partition.
        
        """
        self._write_new_partition()
