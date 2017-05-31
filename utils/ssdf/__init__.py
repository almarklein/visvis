# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# SSDF is distributed under the terms of the (new) BSD License.
# See http://www.opensource.org/licenses/bsd-license.php

""" Package ssdf

Simple Structured Data Format
-----------------------------
Ssdf is a simple format for stroring structured data. It supports
seven data types, two of which are container elements:
None, int, float, (Unicode) string, numpy array, list/tuple, dict/Struct.

One spec, two formats
---------------------
Ssdf is actually two formats: the original text format is human readable,
and thus enables inspecting databases and data structures using a simple
text editor. The binary format is more efficient and uses compression on
the whole file (the text format only compresses arrays). It is more suited
for storing really large databases or structures containing large arrays.
Both formats are fully compatible.

Functions of interest
---------------------
  * save    - save a struct to a file
  * saves   - serialize a struct to a string
  * saveb   - serialize a struct to bytes
  * load    - load a struct from file
  * loads   - load a struct from a string
  * loadb   - load a struct from bytes
  * update  - update a struct on file with a given struct
  * copy    - create a deep copy of a struct
  * new     - create a new empty struct
  * clear   - clear a struct, removing all elements
  * count   - count the number of elements in a struct

Notes
-----
From version 2.1, ssdf is a package (instead of a single module). The package
uses relative imports and the repository is flat, which makes it easy
to include ssdf as a subrepository in an application or library. Pyzolib
includes the ssdf package in this manner.

"""

__version__ = '2.1'

import time

# Create/import claassManager and insert two of its functions in this namespace
from .classmanager import ClassManager
register_class = ClassManager.register_class
is_compatible_class = ClassManager.is_compatible_class

# Import the rest
from . import ssdf_base
from .ssdf_base import Struct, isstruct, VirtualArray, binary_type, string_types
from . import ssdf_text, ssdf_bin



def _get_mode(filename, mode):
    """ _get_mode(filename, mode)
    
    Given filename and mode returns the mode (as 1 or 2).
    
    """
    
    # Determine mode from extension
    mode_ext = 0
    if filename.lower().endswith('.ssdf'):
        mode_ext = 1
    elif filename.lower().endswith('.bsdf'):
        mode_ext = 2
    
    # Determine given mode
    if isinstance(mode, string_types):
        mode = mode.lower()
    if mode in [1, 'text', 'string', 'str']:
        mode = 1
    elif mode in [2, 'binary', 'bin', 'bytes']:
        mode = 2
    elif mode:
        ValueError("Unknown mode given '%s'." % repr(mode))
    
    # Determine mode
    if not mode:
        mode = mode_ext
    elif mode_ext and mode_ext != mode:
        raise ValueError('Given mode does not correspond with extension.')
    if not mode:
        raise ValueError('No mode specified (and no known extension used).')
    
    # Done
    return mode


def save(filename, struct, mode=None):
    """ save(filename, struct, mode=None)
    
    Save the given struct or dict to the filesystem using the given filename.
    
    Two modes are supported: text mode stores in a human readable format,
    and binary mode stores in a more efficient (compressed) binary format.
    
    Parameters
    ----------
    filename : str
        The location in the filesystem to save the file. Files with extension
        '.ssdf' are stored in text mode, and '.bsdf' files are stored in
        binary mode. If another extension is used, the mode should be
        specified explicitly.
    struct : {Struct, dict}
        The object to save.
    mode : optional {'text', 'str', 1, 'bin', 'bytes', 2}
        This parameter can be used to explicitly specify the mode. Note
        that it is an error to use binary mode on a '.ssdf' file or text
        mode on a '.bsdf' file.
    
    """
    
    # Check
    if not (isstruct(struct) or isinstance(struct, dict)):
        raise ValueError('ssdf.save() expects the second argument to be a struct.')
    
    # Open file
    f = open(filename, 'wb')
    try:
        
        # Get mode
        mode = _get_mode(filename, mode)
        
        # Write
        if mode==1:
            writer = ssdf_text.TextSSDFWriter()
            # Write code directive and header
            header =  '# This Simple Structured Data Format (SSDF) file was '
            header += 'created from Python on %s.\n' % time.asctime()
            f.write('# -*- coding: utf-8 -*-\n'.encode('utf-8'))
            f.write(header.encode('utf-8'))
            # Write lines
            writer.write(struct, f)
        elif mode==2:
            writer = ssdf_bin.BinarySSDFWriter()
            writer.write(struct, f)
    
    finally:
        f.close()


def saves(struct):
    """ saves(struct)
    
    Serialize the given struct or dict to a (Unicode) string.
    
    Parameters
    ----------
    struct : {Struct, dict}
        The object to save.
    
    """
    # Check
    if not (isstruct(struct) or isinstance(struct, dict)):
        raise ValueError('ssdf.saves() expects a struct.')
    
    # Write
    writer = ssdf_text.TextSSDFWriter()
    return writer.write(struct)


def saveb(struct):
    """ saveb(struct)
    
    Serialize the given struct or dict to (compressed) bytes.
    
    Parameters
    ----------
    struct : {Struct, dict}
        The object to save.
    
    """
    
    # Check
    if not (isstruct(struct) or isinstance(struct, dict)):
        raise ValueError('ssdf.saveb() expects a struct.')
    
    # Write
    writer = ssdf_bin.BinarySSDFWriter()
    return writer.write(struct)


def load(filename):
    """ load(filename)
    
    Load a struct from the filesystem using the given filename.
    
    Two modes are supported: text mode stores in a human readable format,
    and binary mode stores in a more efficient (compressed) binary format.
    
    Parameters
    ----------
    filename : str
        The location in the filesystem of the file to load.
    
    """
    
    # Open file
    f = open(filename, 'rb')
    try:
    
        # Get mode
        try:
            firstfour = f.read(4).decode('utf-8')
        except Exception:
            raise ValueError('Not a valid ssdf file.')
        if firstfour == 'BSDF':
            mode = 2
        else:
            mode = 1 # This is an assumption.
        
        # Read
        f.seek(0)
        if mode==1:
            reader = ssdf_text.TextSSDFReader()
            return reader.read(f)
        elif mode==2:
            reader = ssdf_bin.BinarySSDFReader()
            return reader.read(f)
    
    finally:
        f.close()


def loadb(bb):
    """ loadb(bb)
    
    Load a struct from the given bytes.
    
    Parameters
    ----------
    bb : bytes
        A serialized struct (obtained using ssdf.saveb()).
    
    """
    # Check
    if not isinstance(bb, binary_type):
        raise ValueError('ssdf.loadb() expects bytes.')
    
    # Read
    reader = ssdf_bin.BinarySSDFReader()
    return reader.read(bb)


def loads(ss):
    """ loads(ss)
    
    Load a struct from the given string.
    
    Parameters
    ----------
    ss : (Unicode) string
        A serialized struct (obtained using ssdf.saves()).
    
    """
    # Check
    if not isinstance(ss, string_types):
        raise ValueError('ssdf.loads() expects a string.')
    
    # Read
    reader = ssdf_text.TextSSDFReader()
    return reader.read(ss)


def update(filename, struct):
    """ update(filename, struct)
    
    Update an existing ssdf file with the given struct.
    
    For every dict in the data tree, the elements are updated.
    Note that any lists occuring in both data trees are simply replaced.
    
    """
    
    # Load existing struct
    s = load(filename)
    
    # Insert stuff
    def insert(ob1, ob2):
        for name in ob2:
            if ( name in ob1 and isstruct(ob1[name]) and
                                 isstruct(ob2[name]) ):
                insert(ob1[name], ob2[name])
            else:
                ob1[name] = ob2[name]
    insert(s, struct)
    
    # Save
    save(filename, s)


def new():
    """ new()
    
    Create a new Struct object. The same as "Struct()".
    
    """
    return Struct()


def clear(struct):
    """ clear(struct)
    
    Clear all elements of the given struct object.
    
    """
    for key in [key for key in struct]:
        del(struct.__dict__[key])


def count(object):
    """ count(object):
    
    Count the number of elements in the given object.
    
    An element is defined as one of the 7 datatypes supported by ssdf
    (dict/struct, tuple/list, array, string, int, float, None).
    
    """
    
    n = 1
    if isstruct(object) or isinstance(object, dict):
        for key in object:
            val = object[key]
            n += count(val)
    elif isinstance(object, (tuple, list)):
        for val in object:
            n += count(val)
    return n


def copy(object):
    """ copy(objec)
    
    Return a deep copy the given object. The object and its children
    should be ssdf-compatible data types.
    
    Note that dicts are converted to structs and tuples to lists.
    
    """
    if isstruct(object) or isinstance(object, dict):
        newObject = Struct()
        for key in object:
            val = object[key]
            newObject[key] = copy(val)
        return newObject
    elif isinstance(object, (tuple, list)):
        return [copy(ob) for ob in object]
    elif isinstance(object, VirtualArray):
        return VirtualArray(object.shape, object.dtype, object.data)
    elif ssdf_base.np and isinstance(object, ssdf_base.np.ndarray):
        return object.copy()
    else:
        # immutable
        return object
