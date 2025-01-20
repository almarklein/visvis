# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv


def ssdfWrite(fname, mesh, name='', bin='unused'):
    """ Simple function that writes a mesh to the ssdf file format.
    """
    
    # Create structure
    s = vv.ssdf.new()
    
    # Populate structure
    s.name = name
    s.vertices = mesh._vertices
    s.normals = mesh._normals
    s.values = mesh._values
    s.faces = mesh._faces
    s.verticesPerFace = mesh._verticesPerFace
    
    # Write
    vv.ssdf.save(fname, s)


def meshWrite(fname, mesh, name='', bin=True):
    """ meshWrite(fname, mesh, name='', bin=True)
    
    Parameters
    ----------
    fname : string
        The filename to write to. The extension should be one of the
        following: .obj .stl .ssdf .bsdf
    mesh : vv.BaseMesh
        The mesh instance to write.
    name : string (optional)
        The name of the object (e.g. 'teapot')
    bin : bool
        For the STL format: whether to write binary, which is much
        more compact then ascii.
    
    Notes on formats
    ----------------
      * The STL format (.stl) is rather limited in the definition of the
        faces; smooth shading is not possible on an STL mesh.
      * The Wavefront format (.obj) is widely available.
      * The SSDF format (.ssdf or .bsdf) is the most efficient in terms
        of memory and speed, but is not widely available.
    
    """
    
    # Use file extension to read file
    if fname.lower().endswith('.stl'):
        import visvis.vvio
        writeFunc = visvis.vvio.stl.StlWriter.write
    elif fname.lower().endswith('.obj'):
        import visvis.vvio
        writeFunc = visvis.vvio.wavefront.WavefrontWriter.write
    elif fname.lower().endswith('.ssdf') or fname.lower().endswith('.bsdf'):
        writeFunc = ssdfWrite
    else:
        raise ValueError('meshWrite cannot determine file type.')
    
    # Read
    return writeFunc(fname, mesh, name, bin)


if __name__ == '__main__':
    bm = vv.meshRead('bunny.ssdf')
    vv.meshWrite('bunny.obj', bm)
