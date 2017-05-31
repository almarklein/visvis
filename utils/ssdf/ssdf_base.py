# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# SSDF is distributed under the terms of the (new) BSD License.
# See http://www.opensource.org/licenses/bsd-license.php

""" ssdf.ssdf_base.py

Implements the base functionality for ssdf:
    * The Struct class
    * Some constants and small functions
    * The VirtualArray class
    * The base classes for SSDFReader, SSDFWriter anf Block
"""

import sys
from . import ClassManager

# Try importing numpy
try:
    import numpy as np
except ImportError:
    np = None

# From six.py
PY3 = sys.version_info[0] == 3
if PY3:
    string_types = str,
    integer_types = int,
    text_type = str
    binary_type = bytes
    ascii_type = str # Simple string
    from functools import reduce
else:
    string_types = basestring,  # noqa
    integer_types = (int, long)  # noqa
    text_type = unicode  # noqa
    binary_type = str
    ascii_type = str # Simple string
    reduce = reduce
    
# To store other classes
_CLASS_NAME = '_CLASS_NAME_'

# Same as in ssdf_bin (we only need the dict type id.
_TYPE_DICT = ord('D')

# Determine float and int types
if True:
    _FLOAT_TYPES = set([float])
    _INT_TYPES = set(integer_types)
if np:
    _FLOAT_TYPES.update([np.float32, np.float64])
    _INT_TYPES.update([   np.int8,  np.int16,  np.int32,  np.int64,
                        np.uint8, np.uint16, np.uint32, np.uint64 ])
_FLOAT_TYPES = tuple(_FLOAT_TYPES)
_INT_TYPES = tuple(_INT_TYPES)



def isstruct(ob):
    """ isstruct(ob)
    
    Returns whether the given object is an SSDF struct.
    
    """
    if hasattr(ob, '__is_ssdf_struct__'):
        return bool(ob.__is_ssdf_struct__)
    else:
        return False


def _not_equal(ob1, ob2):
    """ _not_equal(ob1, ob2)
    
    Returns None if the objects are equal. Otherwise returns a string
    indicating how the objects are inequal.
    
    """
    
    if isstruct(ob1) or isinstance(ob1, dict):
        if not ( isstruct(ob2) or isinstance(ob2, dict) ):
            return '<type does not match>'
        # Test number of elements
        keys1 = [key for key in ob1]
        keys2 = [key for key in ob2]
        if len(keys1) != len(keys2):
            return '<lengths do not match>'
        # Test all elements
        for key in keys1:
            if key not in keys2:
                return '<key not present in other struct/dict>'
            not_equal = _not_equal(ob1[key], ob2[key])
            if not_equal:
                return '.' + key + not_equal
    
    elif isinstance(ob1, (tuple, list)):
        if not isinstance(ob2, (tuple, list)):
            return '<type does not match>'
        if len(ob1) != len(ob2):
            return '<lengths do not match>'
        # Test all elements
        for i in range(len(ob1)):
            not_equal = _not_equal(ob1[i], ob2[i])
            if not_equal:
                return ('[%i]' % i) + not_equal
    
    elif isinstance(ob1, VirtualArray):
        if not isinstance(ob2, VirtualArray):
            return '<type does not match>'
        # Test properties
        if not (    ob1.shape==ob2.shape and
                    ob1.dtype==ob2.dtype and
                    ob1.data==ob2.data ):
            return '<array does not match>'
    
    elif np and isinstance(ob1, np.ndarray):
        if not isinstance(ob2, np.ndarray):
            return '<type does not match>'
        # Test properties
        if not (    ob1.shape==ob2.shape and
                    ob1.dtype==ob2.dtype and
                    (ob1==ob2).sum()==ob1.size ):
            return '<array does not match>'
    
    else:
        # Use default equality operator
        if not (ob1 == ob2):
            return '<objects not equal>'


def _isvalidname(name):
    """ _isvalidname(name)
    
    Returns attribute name, or None, if not valid
    
    """
    
    # Is it a string?
    if not ( name and isinstance(name, string_types) ):
        return None
    
    # Check name
    namechars = str('abcdefghijklmnopqrstuvwxyz_0123456789')
    name2 = name.lower()
    if name2[0] not in namechars[0:-10]:
        return None
    tmp = list(map(lambda x: x not in namechars, name2[2:]))
    
    # Return
    if sum(tmp)==0:
        return name


def _shapeString(ob):
    """ _shapeString(ob)
    
    Returns a string that represents the shape of the given array.
    
    """
    ss = str()
    for n in ob.shape:
        ss += '%ix' % n
    return ss[:-1]



class Struct(object):
    """ Struct(dictionary=None)
    
    Object to holds named data (syntactic sugar for a dictionary).
    
    Attributes can be any of the seven SSDF supported types:
    struct/dict, tuple/list, numpy array, (Unicode) string, int, float, None.
    
    Elements can be added in two ways:
        * s.foo = 'bar'       # the object way
        * s['foo'] = 'bar'    # the dictionary way
    
    Supported features
    ------------------
    * Iteration - yields the keys/names in the struct
    * len() - returns the number of elements in the struct
    * del statement can be used to remove elements
    * two structs can be added, yielding a new struct with combined elements
    * testing for equality with other structs
    
    Notes
    -----
      * The keys in the given dict should be valid names (invalid
        keys are ignoired).
      * On saving, names starting with two underscores are ignored.
      * This class does not inherit from dict to keep its namespace clean,
        avoid nameclashes, and to enable autocompletion of its items in
        most IDE's.
      * To get the underlying dict, simply use s.__dict__.
    
    """
    
    # Indentifier
    __is_ssdf_struct__ = True
    
        
    def __init__(self, a_dict=None):
        
        # Plain struct?
        if a_dict is None:
            return
        
        if not isinstance(a_dict, dict) and not isstruct(a_dict):
            tmp = "Struct can only be initialized with a Struct or a dict."
            raise ValueError(tmp)
        else:
            # Try loading from object
            
            def _getValue(val):
                """ Get the value, as suitable for Struct. """
                if isinstance(val, (string_types,) + _FLOAT_TYPES + _INT_TYPES ):
                    return val
                if np and isinstance(val, np.ndarray):
                    return val
                elif isinstance(val,(tuple,list)):
                    L = list()
                    for element in val:
                        L.append( _getValue(element) )
                    return L
                elif isinstance(val, dict):
                    return Struct(val)
                else:
                    pass # leave it
            
            # Copy all keys in the dict that are not methods
            for key in a_dict:
                if not _isvalidname(key):
                    print("Ignoring invalid key-name '%s'." % key)
                    continue
                val = a_dict[key]
                self[key] = _getValue(val)
    
    
    def __getitem__(self, key):
        # Name ok?
        key2 = _isvalidname(key)
        if not key2:
            raise KeyError("Trying to get invalid name '%s'." % key)
        # Name exists?
        if not key in self.__dict__:
            raise KeyError(str(key))
        # Return
        return self.__dict__[key]
    
    
    def __setitem__(self, key, value):
        # Name ok?
        key2 = _isvalidname(key)
        if not key2:
            raise KeyError("Trying to set invalid name '%s'." % key)
        # Set
        self.__dict__[key] = value
    
    
    def __iter__(self):
        """ Returns iterator over keys. """
        return self.__dict__.__iter__()
   
    
    def __delitem__(self, key):
        return self.__dict__.__delitem__(key)
    
    
    def __len__(self):
        """ Return amount of fields in the Struct object. """
        return len(self.__dict__)
    
    def __add__(self, other):
        """ Enable adding two structs by combining their elemens. """
        s = Struct()
        s.__dict__.update(self.__dict__)
        s.__dict__.update(other.__dict__)
        return s
    
    def __eq__(self, other):
        return not _not_equal(self, other)
    
    def __repr__(self):
        """ Short string representation. """
        return "<SSDF struct instance with %i elements>" % len(self)
    
    def __str__(self):
        """ Long string representation. """
        
        # Get alignment value
        c = 0
        for key in self:
            c = max(c, len(key))
        
        # How many chars left (to display on less than 80 lines)
        charsLeft = 79 - (c+4) # 2 spaces and ': '
        
        s = 'Elements in SSDF struct:\n'
        for key in self:
            if key.startswith("__"):
                continue
            tmp = "%s" % (key)
            value = self[key]
            valuestr = repr(value)
            if len(valuestr)>charsLeft or '\n' in valuestr:
                typestr = str(type(value))[7:-2]
                if np and isinstance(value,np.ndarray):
                    shapestr = _shapeString(value)
                    valuestr = "<array %s %s>" %(shapestr,str(value.dtype))
                elif isinstance(value, string_types):
                    valuestr = valuestr[:charsLeft-3] + '...'
                    #valuestr = "<string with length %i>" % (typestr, len(value))
                else:
                    valuestr = "<%s with length %i>" % (typestr, len(value))
            s += tmp.rjust(c+2) + ": %s\n" % (valuestr)
        return s


class VirtualArray(object):
    """ VirtualArray
    
    A VirtualArray represents an array when numpy is not available.
    This enables preserving the array when saving back a loaded dataset.
    
    """
    def __init__(self, shape, dtype, data):
        self.shape = tuple(shape)
        self.dtype = dtype
        self.data = data
    
    def tostring(self):
        return self.data
    
    @property
    def size(self):
        if self.shape:
            return reduce( lambda a,b:a*b, self.shape)
        else:
            return 1


class SSDFReader:
    
    def build_tree(self, root, blocks):
        """ build_tree(root, blocks)
        
        Build up the tree using the indentation information in the blocks.
        The tree is build up from the given root.
        
        """
        tree = [root]
        for block in blocks:
            # Select leaf in tree
            while block._indent <= tree[-1]._indent:
                tree.pop()
            # Append (to object and to simple tree structure)
            tree[-1]._children.append(block)
            tree.append(block)

    def serialize_struct(self, object, f=None):
        raise NotImplementedError()
    
    def read(self, file_or_string):
        raise NotImplementedError()


class SSDFWriter:
 
    def flatten_tree(self, block, sort=False):
        """ flatten_tree(block, sort=False)
        
        Returns a flat list containing the given block and
        all its children.
        
        If sort is True, packs blocks such that the data
        structures consisting of less blocks appear first.
        
        """
        
        # Get list of strings for each child
        listOfLists = []
        for child in block._children:
            childList = self.flatten_tree(child, sort)
            listOfLists.append( childList )
        
        # Sort by length
        if sort and listOfLists and block._type == _TYPE_DICT:
            listOfLists.sort(key=len)
        
        # Produce flat list
        flatList = [block]
        for childList in listOfLists:
            flatList.extend(childList)
        
        # Done
        return flatList

    def write(self, object, f=None):
        raise NotImplementedError()



class Block:
    """ Block
    
    A block represents a data element. This is where the conversion from
    Python objects to text/bytes and vice versa occurs.
    
    A block is a line in a text file or a piece of data in a binary file.
    A block contains all information about indentation, name, and value
    of the data element that it represents. The raw representation of its
    value is refered to as 'data'.
    
    """
    
    def __init__(self, indent, blocknr, name=None, type=None, data=None):
        self._indent = indent
        self._blocknr = blocknr # for producing usefull read error messages
        
        self._name = name
        self._type = type # used by binary only (and text-dict)
        self._data = data # the raw data, bytes or string
        
        self._children = [] # used only by dicts and lists
    
    
    @classmethod
    def from_object(cls, indent, name, value):
        
        # Instantiate a block
        self = cls(indent, -1, name)
        
        # Set object's data
        if value is None:
            self._from_none()
        elif ClassManager.is_registered_class(value.__class__):
            s = value.__to_ssdf__()
            s[_CLASS_NAME] = value.__class__.__name__
            self._from_dict(s)
        elif isinstance(value, _INT_TYPES):
            self._from_int(value)
        elif isinstance(value, _FLOAT_TYPES):
            self._from_float(value)
        elif isinstance(value, bool):
            self._from_int(int(value))
        elif isinstance(value, string_types):
            self._from_unicode(value)
        elif np and isinstance(value, np.ndarray):
            self._from_array(value)
        elif isinstance(value, VirtualArray):
            self._from_array(value)
        elif isinstance(value, dict) or isstruct(value):
            self._from_dict(value)
        elif isinstance(value, (list, tuple)):
            self._from_list(value)
        else:
            # We do not know
            self._from_none()
            tmp = repr(value)
            if len(tmp) > 64:
                tmp = tmp[:64] + '...'
            if name is not None:
                print("SSDF: %s is unknown object: %s %s" %
                                    (name, tmp, repr(type(value)) ))
            else:
                print("SSDF: unknown object: %s %s" %
                                    (tmp, repr(type(value)) ))
        
        # Done
        return self
