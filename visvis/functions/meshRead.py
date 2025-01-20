# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import os
import visvis as vv


def ssdfRead(fname, check=False):
    """ Simple function that reads a mesh in the ssdf file format.
    """
    
    # Read structure
    s = vv.ssdf.load(fname)
    
    # Check
    if 'vertices' not in s:
        raise RuntimeError('This ssdf file does not contain mesh data.')
    if 'normals' not in s:
        s.normals = None
    if 'values' not in s:
        s.values = None
    if 'faces' not in s:
        s.faces = None
    if 'verticesPerFace' not in s:
        s.verticesPerFace = 3
    
    # Return mesh object
    return vv.BaseMesh(s.vertices, s.faces, s.normals, s.values, s.verticesPerFace)


def meshRead(fname, check=False):
    """ meshRead(fname, check=False)
    
    Parameters
    ----------
    fname : string
        The name of the file to read.
    check : bool
        For the STL format: if check is True and the file is in ascii,
        some checks to the integrity of the file are done (which is a
        bit slower).
    
    Notes on formats
    ----------------
      * The STL format (.stl) is rather limited in the definition of the
        faces; smooth shading is not possible on an STL mesh.
      * The Wavefront format (.obj) is widely available.
      * For the wavefront format, material, nurbs and other fancy stuff
        is ignored.
      * The SSDF format (.ssdf or .bsdf) is the most efficient in terms
        of memory and speed, but is not widely available.
    
    """
    
    if not os.path.isfile(fname):
        # try loading from the resource dir
        path = vv.core.misc.getResourceDir()
        fname2 = os.path.join(path, fname)
        if os.path.isfile(fname2):
            fname = fname2
        else:
            raise IOError("Mesh file '%s' does not exist." % fname)
    
    # Use file extension to read file
    if fname.lower().endswith('.stl'):
        import visvis.vvio
        readFunc = visvis.vvio.stl.StlReader.read
    elif fname.lower().endswith('.obj'):
        import visvis.vvio
        readFunc = visvis.vvio.wavefront.WavefrontReader.read
    elif fname.lower().endswith('.ssdf') or fname.lower().endswith('.bsdf'):
        readFunc = ssdfRead
    else:
        raise ValueError('meshRead cannot determine file type.')
    
    # Read
    return readFunc(fname, check)

    
if __name__ == '__main__':
    # Create BaseMesh object (has no visualization props)
    bm = vv.meshRead('bunny.ssdf')
    # Show it, returning a Mesh object (which does have visualization props)
    m = vv.mesh(bm)
