# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module stl

This module produces functionality to read and write STL files
(binary and ascii).

http://en.wikipedia.org/wiki/STL_%28file_format%29

STL is intended to describe solids; the mesh represents the outer boundary.
Therefore it is important that the faces face the right way (to the outside).

The format specifies a normal for each face, therefore the normal is
actually redundant information. We do not use the normal when reading,
and write a dummy normal on writing. The format also unly supports triangular
faces.

The classes are written with compatibility of Python3 in mind.

"""

import visvis as vv
import numpy as np
import struct


class StlReader(object):
    
    def __init__(self, f):
        self._f = f
    
    @classmethod
    def read(cls, fname, check=False):
        """ read(fname, check=False)
        
        This classmethod is the entry point for reading STL files.
        
        Parameters
        ----------
        fname : string
            The name of the file to read.
        check : bool
            If check is True and the file is in ascii, some checks to the
            integrity of the file are done (which is a bit slower).
        
        """
        
        # Open file
        f = open(fname, 'rb')
        try:
            
            # Read whitespace
            while not f.read(1).strip():
                pass
            # Go one back
            f.seek(-1,1)
            
            # Determine ascii or binary
            data = f.read(5).decode('ascii', 'ignore')
            if data == 'solid':
                # Pop rest of line (i.e. the name) and get reader object
                f.readline()
                reader = StlAsciiReader(f)
            else:
                # Pop rest if header (header has 80 chars) and get reader object
                f.read(75)
                reader = StlBinReader(f)
            
            # Read all
            vertices = vv.Pointset(3)
            while True:
                reader.readFace(vertices, check)
            
        except EOFError:
            pass
        finally:
            f.close()
        
        # Done
        return vv.BaseMesh(vertices)


class StlWriter(object):
    
    def __init__(self, f):
        self._f = f
    
    
    @classmethod
    def _convertQuadsToTriangles(cls, mesh):
        """ STL only allows triangles, therefore we need a method
        to convert triangles to quads.
        """
        if mesh._faces is not None:
            faces = mesh._GetFaces()
            vertices = mesh._vertices
            vv1 = vertices[faces[:,0]]
            vv2 = vertices[faces[:,1]]
            vv3 = vertices[faces[:,2]]
            vv4 = vertices[faces[:,3]]
        else:
            vv1 = mesh._vertices[0::4]
            vv2 = mesh._vertices[1::4]
            vv3 = mesh._vertices[2::4]
            vv4 = mesh._vertices[3::4]
        
        tri1 = vv.Pointset(vv1)
        tri2 = vv.Pointset(vv2)
        tri3 = vv.Pointset(vv3)
        #
        tri1.extend(vv.Pointset(vv3))
        tri2.extend(vv.Pointset(vv4))
        tri3.extend(vv.Pointset(vv1))
        
        return tri1, tri2, tri3
    
    
    @classmethod
    def write(cls, fname, mesh, name='', bin=True):
        """ write(fname, mesh, name='', bin=True)
        
        This classmethod is the entry point for writing mesh data to STL.
        
        Parameters
        ----------
        fname : string
            The filename to write to.
        mesh : Mesh data
            Can be vv.BaseMesh, vv.Pointset, or np.ndarray.
        name : string
            The name of the object (e.g. 'teapot')
        bin : bool
            Whether to write binary, which is much more compact then ascii.
        
        """
        
        if isinstance(mesh, vv.BaseMesh):
            if mesh._verticesPerFace != 3:
                vv1, vv2, vv3 = cls._convertQuadsToTriangles(mesh)
            elif mesh._faces is not None:
                faces = mesh._GetFaces()
                vertices = mesh._vertices
                # Get vertex per faces index (for all faces)
                vv1 = vertices[faces[:,0]]
                vv2 = vertices[faces[:,1]]
                vv3 = vertices[faces[:,2]]
            else:
                vv1 = mesh._vertices[0::3]
                vv2 = mesh._vertices[1::3]
                vv3 = mesh._vertices[2::3]
        elif vv.utils.pypoints.is_Pointset(mesh):
            if mesh.ndim != 3:
                raise ValueError('Mesh vertices must be 3D.')
            vv1 = mesh[0::3]
            vv2 = mesh[1::3]
            vv3 = mesh[2::3]
        elif isinstance(mesh, np.ndarray):
            if mesh.shape[1] != 3:
                raise ValueError('Mesh vertices must be 3D.')
            vv1 = mesh[0::3]
            vv2 = mesh[1::3]
            vv3 = mesh[2::3]
        else:
            raise ValueError('Unknown type for mesh vertices.')
        
        
        # Open file
        f = open(fname, 'wb')
        try:
            # Get writer and write head
            if bin:
                writer = StlBinWriter(f)
                f.write(struct.pack('<B', 0)*80)
                f.write(struct.pack('<I', len(vv1)))
            else:
                writer = StlAsciiWriter(f)
                writer.writeLine('solid %s' % name)
            # Write vertices
            for i in range(len(vv1)):
                writer.writeFace(vv1[i], vv2[i], vv3[i])
            # Write end
            if not bin:
                writer.writeLine('endsolid %s' % name)
        except EOFError:
            pass
        finally:
            f.close()


class StlAsciiReader(StlReader):
        
    def readline(self):
        """ Simple readLine method that strips whitespace and skips
        empty lines.
        """
        line = ''
        while not line:
            line = self._f.readline().decode('ascii', 'ignore').strip()
        return line
    
    
    def readFace(self, vertices, check=False):
        """ readFace(vertices, check=False)
        
        Read a face (three vertices) from the file. The normal is ignored;
        we will calculate it ourselves.
        
        Info: http://en.wikipedia.org/wiki/STL_%28file_format%29
        
        What a face in a file looks like
        --------------------------------
        facet normal ni nj nk
        outer loop
        vertex v1x v1y v1z
        vertex v2x v2y v2z
        vertex v3x v3y v3z
        endloop
        endfacet
        
        """
        
        # Read normal and identifier
        line_normal = self.readline()
        if line_normal.startswith('endsolid'):
            raise EOFError() # Finished
        line_begin_loop = self.readline()
        
        # Read 3 vertices
        for i in range(3):
            line_vertex = self.readline()
            numbers = [num for num in line_vertex.split(' ')]
            numbers = [float(num) for num in numbers[1:] if num]
            vertices.append(*numbers)
        
        # Read two more identifiers
        line_end_loop = self.readline()
        line_end_facet = self.readline()
        
        # Test?
        if check:
            if not line_normal.startswith('facet normal'):
                print('Warning: expected facet normal.')
            if line_begin_loop != "outer loop":
                print('Warning: expected outer loop.')
            if line_end_loop != "endloop":
                print('Warning: expected endloop.')
            if line_end_facet != "endfacet":
                print('Warning: expected endfacet.')


class StlAsciiWriter(StlWriter):
    
    def writeLine(self, text):
        """ Simple writeLine function to write a line of code to the file.
        The encoding is done here, and a newline character is added.
        """
        text += '\n'
        self._f.write(text.encode('ascii'))
    
    
    def writeFace(self, v1, v2, v3):
        """ writeFace(v1, v2, v3)
        
        Write the three vertices that make up a face.
        
        """
        
        # Write dummy normal and start-of-3-vertices-tag
        self.writeLine('facet normal 0.0E+00 0.0E+00 0.0E+00')
        self.writeLine('outer loop')
        
        # Write three vertices
        for v in [v1, v2, v3]:
            self.writeLine('vertex %E %E %E' % (v[0], v[1], v[2]))
        
        # Finish facet
        self.writeLine('endloop')
        self.writeLine('endfacet')


class StlBinReader(StlReader):
    
    def __init__(self, f):
        StlReader.__init__(self, f)
        
        # Get number of faces in this file
        self._n, = struct.unpack('<I', f.read(4))
        self._count = 0
    
    
    def readFace(self, vertices, check=False):
        """ readFace(vertices, check=False)
        
        Read a face (three vertices) from the file. The normal is ignored;
        we will calculate it ourselves.
        
        Info: http://en.wikipedia.org/wiki/STL_%28file_format%29
        
        A face consists of 12 32bit float numbers and a short int.
        The 12 numbers are the 3 vertices and the normal.
        
        """
        
        # Reached last face?
        if self._count >= self._n:
            raise EOFError()
        
        # Read data.
        # 12 32bit floating point numbers + short int used by some apps
        n = 12*4+2
        data = self._f.read(n)
        if len(data) < n:
            raise EOFError()
        
        # Convert numbers
        numbers = [struct.unpack('<f', data[i*4:(i+1)*4]) for i in range(12)]
        #attribute_byte_count = struct.unpack('<H', data[12*4:12*4+2]
        
        # Add vertices, ignore normal
        vertices.append(*numbers[3:6])
        vertices.append(*numbers[6:9])
        vertices.append(*numbers[9:12])
        
        # Increase counter
        self._count += 1
    

class StlBinWriter(StlWriter):
    
    def writeFace(self, v1, v2, v3):
        """ writeFace(v1, v2, v3)
        
        Write the three vertices that make up a face.
        
        """
        
        # Construct data
        dataList = []
        for i in range(3):
            dataList.append( struct.pack('<f', 0.0) )
        for p in v1:
            dataList.append( struct.pack('<f', p) )
        for p in v2:
            dataList.append( struct.pack('<f', p) )
        for p in v3:
            dataList.append( struct.pack('<f', p) )
        if True:
            dataList.append( struct.pack('<H', 0) )
        
        # Write data
        data = ''.encode('ascii').join(dataList)
        self._f.write(data)
