# Cython specific imports
import numpy as np
cimport numpy as np
import cython 

# Enable low level memory management
# from libc.stdlib cimport malloc, free
cdef extern from "stdlib.h": # The cimport does not work on my Linux Laptop
   void free(void* ptr)
   void* malloc(size_t size)

# Type defs, we support float32 and float64
ctypedef np.float32_t FLOAT32_T
ctypedef np.float64_t FLOAT64_T
ctypedef np.int32_t INT32_T
FLOAT32 = np.float32
FLOAT64 = np.float64
INT32 = np.float32


# Define tiny winy number
cdef double FLT_EPSILON = 0.0000001

# Define abs function for doubles
cdef inline double dabs(double a): return a if a>=0 else -a



cdef class Cell:
    """ Class to keep track of some stuff during the whole cube marching
    procedure. 
    
    Also has methods to add triangles, etc.
    """
    
    # Reference to LUTS object
    cdef LutProvider luts
    
    # Location of cube
    cdef int x
    cdef int y
    cdef int z
    
    # Values of cube corners (isovalue subtracted)
    cdef double v0
    cdef double v1
    cdef double v2
    cdef double v3
    cdef double v4
    cdef double v5
    cdef double v6
    cdef double v7
    
    # Small array to store the above values in (allowing indexing)
    cdef double *vv
    
    # Vertex position of center of cube (only calculated if needed)
    cdef double v12_x
    cdef double v12_y
    cdef double v12_z
    
    # The index value, our magic 256 bit word
    cdef int index
    
    # Dimensions of the total volume
    cdef int nx
    cdef int ny
    cdef int nz
    
    # Arrays with face information
    cdef int *faceLayer # The current facelayer (reference-copy of one of the below)
    cdef int *faceLayer1 # The actual first face layer 
    cdef int *faceLayer2 # The actual second face layer 
    
    # Stuff to store the output vertices
    cdef float *_vertices
    cdef int _vertexCount
    cdef int _vertexMaxCount
    
    # Stuff to store the output faces
    cdef int *_faces
    cdef int _faceCount
    cdef int _faceMaxCount
    
    
    def __init__(self, LutProvider luts, int nx, int ny, int nz):
        self.luts = luts
        self.nx, self.ny, self.nz = nx, ny, nz
        
        # Allocate face layers
        self.faceLayer1 = <int *>malloc(self.nx*self.ny*4 * sizeof(int))
        self.faceLayer2 = <int *>malloc(self.nx*self.ny*4 * sizeof(int))
        cdef int i
        for i in range(self.nx*self.ny*4):
            self.faceLayer1[i] = -1
            self.faceLayer2[i] = -1
        self.faceLayer = self.faceLayer1
    
    
    def __cinit__(self):
        
        # Init tiny array
        self.vv = <double *>malloc(8 * sizeof(double))
        
        # Init face layers
        self.faceLayer1 = NULL
        self.faceLayer2 = NULL
        
        # Init vertices
        self._vertexCount = 0
        self._vertexMaxCount = 8
        self._vertices = <float *>malloc(self._vertexMaxCount*3 * sizeof(float))
        
        # Init faces
        self._faceCount = 0
        self._faceMaxCount = 8
        self._faces = <int *>malloc(self._faceMaxCount * sizeof(int))
    
    
    def __dealloc__(self):
        if self.vv is not NULL:
            free(self.vv)
        if self.faceLayer1 is not NULL:
            free(self.faceLayer1)
        if self.faceLayer2 is not NULL:
            free(self.faceLayer2)
        if self._vertices is not NULL:
            free(self._vertices)
        if self._faces is not NULL:
            free(self._faces)
    
    
    cdef void _increase_size_vertices(self):
        """ Increase the size of the vertices array by a factor two.
        """
        # Allocate new array
        cdef int newMaxCount = self._vertexMaxCount * 2
        cdef float *newVertices = <float *>malloc(newMaxCount*3 * sizeof(float))
        # Copy
        cdef int i
        for i in range(self._vertexCount*3):
            newVertices[i] = self._vertices[i]
        # Apply
        free(self._vertices)
        self._vertices = newVertices
        self._vertexMaxCount = newMaxCount
    
    
    cdef void _increase_size_faces(self):
        """ Increase the size of the faces array by a factor two.
        """
        # Allocate new array
        cdef int newMaxCount = self._faceMaxCount * 2
        cdef int *newFaces = <int *>malloc(newMaxCount * sizeof(int))
        # Copy
        cdef int i
        for i in range(self._faceCount):
            newFaces[i] = self._faces[i]
        # Apply
        free(self._faces)
        self._faces = newFaces
        self._faceMaxCount = newMaxCount
    
    
    cdef int add_vertex(self, float x, float y, float z):
        """ Add a vertex to the result. Return index in vertex array.
        """
        # Check if array is large enough
        if self._vertexCount >= self._vertexMaxCount:
            self._increase_size_vertices()
        # Add vertex
        self._vertices[self._vertexCount*3+0] = x
        self._vertices[self._vertexCount*3+1] = y
        self._vertices[self._vertexCount*3+2] = z
        self._vertexCount += 1
        return self._vertexCount -1 
    
    
    cdef add_face(self, int index):
        """ Add a face to the result.
        """
        # Check if array is large enough
        if self._faceCount >= self._faceMaxCount:
            self._increase_size_faces()
        # Add face
        self._faces[self._faceCount] = index
        self._faceCount += 1
    
    
    def get_vertices(self):
        """ Get the final vertex array.
        """
        vertices = np.empty((self._vertexCount,3),'float32')
        cdef np.ndarray[FLOAT32_T, ndim=2] vertices_ = vertices
        cdef int i, j
        for i in range(self._vertexCount):
            for j in range(3):
                vertices_[i,j] = self._vertices[i*3+j]
        return vertices
    
    def get_faces(self):
        faces = np.empty((self._faceCount),'int32')
        cdef np.ndarray[INT32_T, ndim=1] faces_ = faces
        cdef int i, j
        for i in range(self._faceCount):
            faces_[i] = self._faces[i]
        return faces
    
    
    cdef void new_z_value(self):
        """ This method should be called each time a new z layer is entered.
        We will swap the layers with face information and empty the second.
        """ 
        # Swap layers
        self.faceLayer1, self.faceLayer2 = self.faceLayer2, self.faceLayer1
        # Empty last
        cdef int i
        for i in range(self.nx*self.ny*4):
            self.faceLayer2[i] = -1
    
    
    cdef int get_index_in_facelayer(self, int vi):
        """ 
        Get the index of a vertex position, given the edge on which it lies.
        We keep a list of faces so we can reuse vertices. This improves
        speed because we need less interpolation, and the result is more
        compact and can be visualized better because normals can be 
        interpolated.
        
        For each cell, we store 4 vertex indices; all other edges can be 
        represented as the edge of another cell.  The fourth is the center vertex.
        
        This method returns -1 if no vertex has been defined yet.
        
        
              vertices              edes                edge-indices per cell
        *         7 ________ 6           _____6__             ________
        *         /|       /|         7/|       /|          /|       /|
        *       /  |     /  |        /  |     /5 |        /  |     /  |
        *   4 /_______ /    |      /__4____ /    10     /_______ /    |
        *    |     |  |5    |     |    11  |     |     |     |  |     |
        *    |    3|__|_____|2    |     |__|__2__|     |     |__|_____|
        *    |    /   |    /      8   3/   9    /      2    /   |    /
        *    |  /     |  /        |  /     |  /1       |  1     |  /
        *    |/_______|/          |/___0___|/          |/___0___|/
        *   0          1        0          1
        */
        """ 
        
        # Init indices, both are corrected below
        cdef int i = self.nx * self.y + self.x  # Index of cube to get vertex at
        cdef int j = 0 # Vertex number for that cell
        cdef int vi_ = vi
        
        cdef int *faceLayer
        
        if False:
            # Select either upper or lower half
            if vi < 8:
                #  8 horizontal edges
                if vi < 4:
                    faceLayer = self.faceLayer2
                else:
                    vi -= 4
                    faceLayer = self.faceLayer1
                
                # Calculate actual index based on edge 
                if vi == 0:
                    i += self.nx
                elif vi == 1:
                    j = 1
                elif vi == 2:
                    pass
                elif vi == 3: 
                    i += 1
                    j = 1  
            
            elif vi<12:
                # four vertical edges
                faceLayer = self.faceLayer1
                j = 2
                
                if vi == 8:
                    i += self.nx + 1
                elif vi == 9:   # step in x
                    i += self.nx
                elif vi == 10:   # step in x and y
                    pass
                elif vi == 11:  # step in y
                    i += 1
            
            else:
                # center vertex
                faceLayer = self.faceLayer1
                j = 3
        else:
            
            # Select either upper or lower half
            if vi < 8:
                #  8 horizontal edges
                if vi < 4:
                    faceLayer = self.faceLayer1
                else:
                    vi -= 4
                    faceLayer = self.faceLayer2
                
                # Calculate actual index based on edge 
                #if vi == 0: pass  # no step
                if vi == 1:  # step in x
                    i += 1
                    j = 1
                elif vi == 2:  # step in y
                    i += self.nx
                elif vi == 3:  # no step
                    j = 1  
            
            elif vi<12:
                # four vertical edges
                faceLayer = self.faceLayer1
                j = 2
                
                #if vi == 8: pass # no step
                if vi == 9:   # step in x
                    i += 1 
                elif vi == 10:   # step in x and y
                    i += self.nx + 1 
                elif vi == 11:  # step in y
                    i += self.nx 
            
            else:
                # center vertex
                faceLayer = self.faceLayer1
                j = 3
        
#         print(vi_, i, j)
#         if (4*i + j) >= self.nx*self.ny:
#             print('woops!', i, j, self.z, self.nx, self.ny)
#             i, j = 0,0
        
        # Store facelayer and return index
        self.faceLayer = faceLayer # Dirty way of returning a value
        return 4*i + j
    
    
    cdef void set_location(self, int x, int y, int z):
        """ Set the current location of the cell.
        Dont forget to also set v0-v7.
        """
        self.x = x
        self.y = y
        self.z = z
    
    
    cdef void set_cube(self,    double isovalue, 
                                double v0, double v1, double v2, double v3, 
                                double v4, double v5, double v6, double v7):
        """  Set the values of the cube corners. The isovalue is subtracted
        from them, such that in further calculations the isovalue can be 
        taken as zero.
        """ 
        self.v0 = v0 - isovalue
        self.v1 = v1 - isovalue
        self.v2 = v2 - isovalue
        self.v3 = v3 - isovalue
        self.v4 = v4 - isovalue
        self.v5 = v5 - isovalue
        self.v6 = v6 - isovalue
        self.v7 = v7 - isovalue
    
    
    def calculate_gradients(self):
        # todo: process this further to add normals to the result
        
        # Derivatives, selected to always point in same direction.
        # Note that many corners have the same components as other points,
        # by interpolating  and averaging the normals this is solved.
        self.dx0, self.dy0, self.dz0 = self.v0-self.v1, self.v0-self.v3, self.v0-self.v4
        self.dx1, self.dy1, self.dz1 = self.v0-self.v1, self.v1-self.v2, self.v1-self.v5
        self.dx2, self.dy2, self.dz2 = self.v3-self.v2, self.v1-self.v2, self.v2-self.v6
        self.dx3, self.dy3, self.dz3 = self.v3-self.v2, self.v0-self.v3, self.v3-self.v7
        self.dx4, self.dy4, self.dz4 = self.v4-self.v5, self.v4-self.v7, self.v0-self.v4
        self.dx5, self.dy5, self.dz5 = self.v4-self.v5, self.v5-self.v6, self.v1-self.v5
        self.dx6, self.dy6, self.dz6 = self.v7-self.v6, self.v5-self.v6, self.v2-self.v6
        self.dx7, self.dy7, self.dz7 = self.v7-self.v6, self.v4-self.v7, self.v3-self.v7
    
    
    cdef void calculate_index(self):
        """ Calculate the index value for the current cell.
        The values v0-v7 should be set.
        """
        cdef int index
        
        index = 0
        if self.v0 > 0.0:   index += 1
        if self.v1 > 0.0:   index += 2
        if self.v2 > 0.0:   index += 4
        if self.v3 > 0.0:   index += 8
        if self.v4 > 0.0:   index += 16
        if self.v5 > 0.0:   index += 32
        if self.v6 > 0.0:   index += 64
        if self.v7 > 0.0:   index += 128
        self.index = index
    
    
    cdef void calculate_center_vertex(self):
        cdef double v0, v1, v2, v3, v4, v5, v6, v7
        cdef double fx, fy, fz, ff
        fx, fy, fz, ff = 0.0, 0.0, 0.0, 0.0
        
        # Define "strength" of each corner of the cube that we need
        # todo: can we disable Cython from checking for zero division? Because it never happens!
        v0 = 1.0 / (FLT_EPSILON + dabs(self.v0))
        v1 = 1.0 / (FLT_EPSILON + dabs(self.v1))
        v2 = 1.0 / (FLT_EPSILON + dabs(self.v2))
        v3 = 1.0 / (FLT_EPSILON + dabs(self.v3))
        v4 = 1.0 / (FLT_EPSILON + dabs(self.v4))
        v5 = 1.0 / (FLT_EPSILON + dabs(self.v5))
        v6 = 1.0 / (FLT_EPSILON + dabs(self.v6))
        v7 = 1.0 / (FLT_EPSILON + dabs(self.v7))
        
        # Apply a kind of center-of-mass method
        fx += 0.0*v0;  fy += 0.0*v0;  fz += 0.0*v0;  ff += v0
        fx += 1.0*v1;  fy += 0.0*v1;  fz += 0.0*v1;  ff += v1
        fx += 1.0*v2;  fy += 1.0*v2;  fz += 0.0*v2;  ff += v2
        fx += 0.0*v3;  fy += 1.0*v3;  fz += 0.0*v3;  ff += v3
        fx += 0.0*v4;  fy += 0.0*v4;  fz += 1.0*v4;  ff += v4
        fx += 1.0*v5;  fy += 0.0*v5;  fz += 1.0*v5;  ff += v5
        fx += 1.0*v6;  fy += 1.0*v6;  fz += 1.0*v6;  ff += v6
        fx += 0.0*v7;  fy += 1.0*v7;  fz += 1.0*v7;  ff += v7
        
        # Store
        self.v12_x = self.x + fx / ff
        self.v12_y = self.y + fy / ff
        self.v12_z = self.z + fz / ff
    
    
    cdef void add_triangles(self, Lut lut, int lutIndex, int nt):
        """ Add triangles.
        
        The vertices for the triangles are specified in the given
        Lut at the specified index. There are nt triangles.
        
        The reason that nt should be given is because it is often known
        beforehand.
        
        """
        
        cdef int i, j
        cdef int vi#, nt
        
        # Copy values in array so we can index them. Note the misalignment
        # because the numbering does not correspond with bitwise OR of xyz.
        self.vv[0] =self.v0 
        self.vv[1] =self.v1
        self.vv[2] =self.v3#
        self.vv[3] =self.v2#
        self.vv[4] =self.v4
        self.vv[5] =self.v5
        self.vv[6] =self.v7#
        self.vv[7] =self.v6#
        
        for i in range(nt):
            for j in range(3):
                # Get two sides for each element in this vertex
                vi = lut.get2(lutIndex, i*3+j)
                self._add_triangle(vi)
    
    cdef void add_triangles2(self, Lut lut, int lutIndex, int lutIndex2, int nt):
        """ Same as add_triangles, except that now the geometry is in a LUT
        with 3 dimensions, and an extra index is provided.
        
        """
        cdef int i, j
        cdef int vi#, nt
        
        # Copy values in array so we can index them. Note the misalignment
        # because the numbering does not correspond with bitwise OR of xyz.
        self.vv[0] =self.v0 
        self.vv[1] =self.v1
        self.vv[2] =self.v3#
        self.vv[3] =self.v2#
        self.vv[4] =self.v4
        self.vv[5] =self.v5
        self.vv[6] =self.v7#
        self.vv[7] =self.v6#
        
        for i in range(nt):
            for j in range(3):
                # Get two sides for each element in this vertex
                vi = lut.get3(lutIndex, lutIndex2, i*3+j)
                self._add_triangle(vi)
    
        
    cdef void _add_face_from_edge_index(self, int vi):
        """ Add one face from an edge index. Only adds a face if the
        vertex already exists. Otherwise also adds a vertex and applies
        interpolation.
        """ 
        
        # typedefs
        cdef int indexInVertexArray, indexInFaceLayer
        cdef int dx1, dy1, dz1
        cdef int dx2, dy2, dz2
        cdef int index1, index2
        cdef double tmpf1, tmpf2
        cdef double fx, fy, fz, ff
        
        # Get index in the face layer and corresponding vertex number
        indexInFaceLayer = self.get_index_in_facelayer(vi)
        indexInVertexArray = self.faceLayer[indexInFaceLayer]
        if indexInVertexArray >= 0:
            # We're done quick!
            self.add_face(indexInVertexArray)
            return
        
        # Vertex not calculated before; calculate now ...
        
        if vi == 12:
            # Add precalculated center vertex position (is interpolated)
            indexInVertexArray = self.add_vertex( self.v12_x, self.v12_y, self.v12_z)
        else:
            # Get relative edge indices for x, y and z
            dx1, dx2 = self.luts.EDGESRELX.get2(vi,0), self.luts.EDGESRELX.get2(vi,1)
            dy1, dy2 = self.luts.EDGESRELY.get2(vi,0), self.luts.EDGESRELY.get2(vi,1)
            dz1, dz2 = self.luts.EDGESRELZ.get2(vi,0), self.luts.EDGESRELZ.get2(vi,1)
            # Make two vertex indices
            index1 = dz1*4 + dy1*2 + dx1
            index2 = dz2*4 + dy2*2 + dx2
            # Define strength of both corners
            tmpf1 = 1.0 / (FLT_EPSILON + dabs(self.vv[index1]))
            tmpf2 = 1.0 / (FLT_EPSILON + dabs(self.vv[index2]))
            # Apply a kind of center-of-mass method
            fx, fy, fz, ff = 0.0, 0.0, 0.0, 0.0
            fx += <double>dx1 * tmpf1;  fy += <double>dy1 * tmpf1;  fz += <double>dz1 * tmpf1;  ff += tmpf1
            fx += <double>dx2 * tmpf2;  fy += <double>dy2 * tmpf2;  fz += <double>dz2 * tmpf2;  ff += tmpf2
            indexInVertexArray = self.add_vertex( 
                            <double>self.x + fx/ff, # todo: * self.step
                            <double>self.y + fy/ff,
                            <double>self.z + fz/ff )
        
        # Store vertex
        self.faceLayer[indexInFaceLayer] = indexInVertexArray
        self.add_face(indexInVertexArray)
        
#         # Create vertex non-interpolated
#         self.add_vertex( self.x + 0.5* dx1 + 0.5 * dx2,
#                         self.y + 0.5* dy1 + 0.5 * dy2,
#                         self.z + 0.5* dz1 + 0.5 * dz2 )

    



cdef class Lut:
    """ Representation of a lookup table.
    The tables are initially defined as numpy arrays. On initialization,
    this class converts them to a C array for fast access.
    This class defines functions to look up values using 1, 2 or 3 indices.
    """ 
    
    cdef char* VALUES
    cdef int L0 # Length
    cdef int L1 # size of tuple
    cdef int L2 # size of tuple in tuple (if any)
    
    def __init__(self, array):
        
        # Get the shape of the LUT
        self.L1 = 1
        self.L2 = 1
        #
        self.L0 = array.shape[0]
        if array.ndim > 1:
            self.L1 = array.shape[1]
        if array.ndim > 2:
            self.L2 = array.shape[2]
        
        # Copy the contents
        array = array.ravel()
        cdef int n, N
        N = self.L0 * self.L1 * self.L2
        self.VALUES = <char *> malloc(N * sizeof(char)) 
        for n in range(N):
            self.VALUES[n] = array[n]
    
    def __cinit__(self):
        self.VALUES = NULL
    
    def __dealloc__(self):
        if self.VALUES is not NULL:
            free(self.VALUES)
    
    cdef int get1(self, int i0):
        return self.VALUES[i0]
    
    cdef int get2(self, int i0, int i1):
        return self.VALUES[i0*self.L1 + i1]
    
    cdef int get3(self, int i0, int i1, int i2):
        return self.VALUES[i0*self.L1*self.L2 + i1*self.L2 + i2]

    

cdef class LutProvider:
    """ Class that provides a common interface to the many lookup tables
    used by the algorithm.
    All the lists of lut names are autogenerated to prevent human error.
    """
    
    cdef Lut CASESCLASSIC
    cdef Lut EDGESRELX # Edges relative X
    cdef Lut EDGESRELY
    cdef Lut EDGESRELZ
    
    cdef Lut CASES
    
    cdef Lut TILING1
    cdef Lut TILING2
    cdef Lut TILING3_1
    cdef Lut TILING3_2
    cdef Lut TILING4_1
    cdef Lut TILING4_2
    cdef Lut TILING5
    cdef Lut TILING6_1_1
    cdef Lut TILING6_1_2
    cdef Lut TILING6_2
    cdef Lut TILING7_1
    cdef Lut TILING7_2
    cdef Lut TILING7_3
    cdef Lut TILING7_4_1
    cdef Lut TILING7_4_2
    cdef Lut TILING8
    cdef Lut TILING9
    cdef Lut TILING10_1_1
    cdef Lut TILING10_1_1_
    cdef Lut TILING10_1_2
    cdef Lut TILING10_2
    cdef Lut TILING10_2_
    cdef Lut TILING11
    cdef Lut TILING12_1_1
    cdef Lut TILING12_1_1_
    cdef Lut TILING12_1_2
    cdef Lut TILING12_2
    cdef Lut TILING12_2_
    cdef Lut TILING13_1
    cdef Lut TILING13_1_
    cdef Lut TILING13_2
    cdef Lut TILING13_2_
    cdef Lut TILING13_3
    cdef Lut TILING13_3_
    cdef Lut TILING13_4
    cdef Lut TILING13_5_1
    cdef Lut TILING13_5_2
    cdef Lut TILING14
    
    cdef Lut TEST3
    cdef Lut TEST4
    cdef Lut TEST6
    cdef Lut TEST7
    cdef Lut TEST10
    cdef Lut TEST12
    cdef Lut TEST13
    
    cdef Lut SUBCONFIG13
    
    
    def __init__(self, CASESCLASSIC, EDGESRELX, EDGESRELY, EDGESRELZ, CASES,
            
            TILING1, TILING2, TILING3_1, TILING3_2, TILING4_1, TILING4_2, 
            TILING5, TILING6_1_1, TILING6_1_2, TILING6_2, TILING7_1, TILING7_2, 
            TILING7_3, TILING7_4_1, TILING7_4_2, TILING8, TILING9, 
            TILING10_1_1, TILING10_1_1_, TILING10_1_2, TILING10_2, TILING10_2_, 
            TILING11, TILING12_1_1, TILING12_1_1_, TILING12_1_2, TILING12_2, 
            TILING12_2_, TILING13_1, TILING13_1_, TILING13_2, TILING13_2_, 
            TILING13_3, TILING13_3_, TILING13_4, TILING13_5_1, TILING13_5_2, 
            TILING14,
            
            TEST3, TEST4, TEST6, TEST7, TEST10, TEST12, TEST13,
            SUBCONFIG13,
            ):
        
        self.CASESCLASSIC = Lut(CASESCLASSIC)
        self.EDGESRELX = Lut(EDGESRELX)
        self.EDGESRELY = Lut(EDGESRELY)
        self.EDGESRELZ = Lut(EDGESRELZ)
        
        self.CASES = Lut(CASES)
        
        self.TILING1 = Lut(TILING1)
        self.TILING2 = Lut(TILING2)
        self.TILING3_1 = Lut(TILING3_1)
        self.TILING3_2 = Lut(TILING3_2)
        self.TILING4_1 = Lut(TILING4_1)
        self.TILING4_2 = Lut(TILING4_2)
        self.TILING5 = Lut(TILING5)
        self.TILING6_1_1 = Lut(TILING6_1_1)
        self.TILING6_1_2 = Lut(TILING6_1_2)
        self.TILING6_2 = Lut(TILING6_2)
        self.TILING7_1 = Lut(TILING7_1)
        self.TILING7_2 = Lut(TILING7_2)
        self.TILING7_3 = Lut(TILING7_3)
        self.TILING7_4_1 = Lut(TILING7_4_1)
        self.TILING7_4_2 = Lut(TILING7_4_2)
        self.TILING8 = Lut(TILING8)
        self.TILING9 = Lut(TILING9)
        self.TILING10_1_1 = Lut(TILING10_1_1)
        self.TILING10_1_1_ = Lut(TILING10_1_1_)
        self.TILING10_1_2 = Lut(TILING10_1_2)
        self.TILING10_2 = Lut(TILING10_2)
        self.TILING10_2_ = Lut(TILING10_2_)
        self.TILING11 = Lut(TILING11)
        self.TILING12_1_1 = Lut(TILING12_1_1)
        self.TILING12_1_1_ = Lut(TILING12_1_1_)
        self.TILING12_1_2 = Lut(TILING12_1_2)
        self.TILING12_2 = Lut(TILING12_2)
        self.TILING12_2_ = Lut(TILING12_2_)
        self.TILING13_1 = Lut(TILING13_1)
        self.TILING13_1_ = Lut(TILING13_1_)
        self.TILING13_2 = Lut(TILING13_2)
        self.TILING13_2_ = Lut(TILING13_2_)
        self.TILING13_3 = Lut(TILING13_3)
        self.TILING13_3_ = Lut(TILING13_3_)
        self.TILING13_4 = Lut(TILING13_4)
        self.TILING13_5_1 = Lut(TILING13_5_1)
        self.TILING13_5_2 = Lut(TILING13_5_2)
        self.TILING14 = Lut(TILING14)
        
        self.TEST3 = Lut(TEST3)
        self.TEST4 = Lut(TEST4)
        self.TEST6 = Lut(TEST6)
        self.TEST7 = Lut(TEST7)
        self.TEST10 = Lut(TEST10)
        self.TEST12 = Lut(TEST12)
        self.TEST13 = Lut(TEST13)
        
        self.SUBCONFIG13 = Lut(SUBCONFIG13)


@cython.boundscheck(False)
@cython.wraparound(False)
def marching_cubes(im, isovalue, LutProvider luts):
    
    # Define image as numpy array
    cdef np.ndarray[FLOAT32_T, ndim=3] im_ = im
    
    # Get dimemsnions
    cdef int Nx, Ny, Nz
    Nx, Ny, Nz = im.shape[2], im.shape[1], im.shape[0]
    
    # Create cell to use throughout
    cdef Cell cell = Cell(luts, Nx, Ny, Nz)
    
    cdef int x, y, z
    cdef int dx1, dy1, dz1, dx2, dy2, dz2
    cdef int i, j, k
    cdef int index
    cdef double tmpf, tmpf1, tmpf2
    cdef double isovalue_ = isovalue
    
    cdef int nt
    cdef int case, config, subconfig
    
    cdef double edgeCount = 0
    
    # todo: allow a stepsize, this algorithm should work with that
    # todo: allow using original alg
    # todo: allow dynamic isovalue?
    # todo: return gradient or something so we can color the mesh too
    
    for z in range(Nz-1):
        cell.new_z_value() # Indicate that we enter a new layer
#         print('Z: ', z)
#         import time
#         time.sleep(0.1)
        for y in range(Ny-1):
            for x in range(Nx-1):
                
                # Initialize cell
                cell.set_location(x, y, z)
                cell.set_cube(isovalue_,
                    im_[z  ,y  , x  ], im_[z  ,y  , x+1], im_[z  ,y+1, x+1], im_[z  ,y+1, x  ],
                    im_[z+1,y  , x  ], im_[z+1,y  , x+1], im_[z+1,y+1, x+1], im_[z+1,y+1, x  ] )
                cell.calculate_index()
                
                # Do classic!
                if False:
                    # Determine number of vertices
                    nt = 0
                    while luts.CASESCLASSIC.get2(cell.index, 3*nt) != -1:
                        nt += 1
                    # Add triangles
                    cell.add_triangles(luts.CASESCLASSIC, cell.index, nt)
                else:
                    # Get case and config
                    case = luts.CASES.get2(cell.index, 0)
                    config = luts.CASES.get2(cell.index, 1)
                    subconfig = 0
                    
                    # Sinatures for tests
                    #test_face(cell, luts.TESTX.get1(config)):
                    #test_internal(cell, luts, case, config, subconfig, luts.TESTX.get1(config)):
                    #cell.add_triangles(luts.TILINGX, config, N)
                    
                    # The big switch
                    if case == 0:
                        pass
                    
                    elif case == 1:
                        cell.add_triangles(luts.TILING1, config, 1)
                    
                    elif case == 2:
                        cell.add_triangles(luts.TILING2, config, 2)
                    
                    elif case == 3:
                        if test_face(cell, luts.TEST3.get1(config)):
                            cell.add_triangles(luts.TILING3_2, config, 4)
                        else:
                            cell.add_triangles(luts.TILING3_1, config, 2)
                    
                    elif case == 4 :
                        if test_internal(cell, luts, case, config, subconfig, luts.TEST4.get1(config)):
                            cell.add_triangles(luts.TILING4_1, config, 2)
                        else:
                            cell.add_triangles(luts.TILING4_2, config, 6)
                    
                    elif case == 5 :
                        cell.add_triangles(luts.TILING5, config, 3)
                    
                    elif case == 6 :
                        if test_face(cell, luts.TEST6.get2(config,0)):
                            cell.add_triangles(luts.TILING6_2, config, 5)
                        else:
                            if test_internal(cell, luts, case, config, subconfig, luts.TEST6.get2(config,1)):
                                cell.add_triangles(luts.TILING6_1_1, config, 3)
                            else:
                                cell.calculate_center_vertex() # v12 needed
                                cell.add_triangles(luts.TILING6_1_2, config, 9)
                    
                    elif case == 7 :
                        # Get subconfig
                        if test_face(cell, luts.TEST7.get2(config,0)): subconfig += 1
                        if test_face(cell, luts.TEST7.get2(config,1)): subconfig += 2
                        if test_face(cell, luts.TEST7.get2(config,2)): subconfig += 4
                        # Behavior depends on subconfig
                        if subconfig == 0: cell.add_triangles(luts.TILING7_1, config, 3)
                        elif subconfig == 1: cell.add_triangles2(luts.TILING7_2, config, 0, 5)
                        elif subconfig == 2: cell.add_triangles2(luts.TILING7_2, config, 1, 5)
                        elif subconfig == 3: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING7_3, config, 0, 9)
                        elif subconfig == 4: cell.add_triangles2(luts.TILING7_2, config, 2, 5)
                        elif subconfig == 5: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING7_3, config, 1, 9)
                        elif subconfig == 6: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING7_3, config, 2, 9)
                        elif subconfig == 7: 
                            if test_internal(cell, luts, case, config, subconfig, luts.TEST7.get2(config,3)):
                                cell.add_triangles(luts.TILING7_4_2, config, 9)
                            else:
                                cell.add_triangles(luts.TILING7_4_1, config, 5)
                    
                    elif case == 8 :
                        cell.add_triangles(luts.TILING8, config, 2)
                    
                    elif case == 9 :
                        cell.add_triangles(luts.TILING9, config, 4)
                    
                    elif case == 10 :
                        if test_face(cell, luts.TEST10.get2(config,0)):
                            if test_face(cell, luts.TEST10.get2(config,1)):
                                cell.add_triangles(luts.TILING10_1_1_, config, 4)
                            else:
                                cell.calculate_center_vertex() # v12 needed
                                cell.add_triangles(luts.TILING10_2, config, 8)
                        else:
                            if test_face(cell, luts.TEST10.get2(config,1)):
                                cell.calculate_center_vertex() # v12 needed
                                cell.add_triangles(luts.TILING10_2_, config, 8)
                            else:
                                if test_internal(cell, luts, case, config, subconfig, luts.TEST10.get2(config,2)):
                                    cell.add_triangles(luts.TILING10_1_1, config, 4)
                                else:
                                    cell.add_triangles(luts.TILING10_1_2, config, 8)
                    
                    elif case == 11 :
                        cell.add_triangles(luts.TILING11, config, 4)
                    
                    elif case == 12 :
                        if test_face(cell, luts.TEST12.get2(config,0)):
                            if test_face(cell, luts.TEST12.get2(config,1)):
                                cell.add_triangles(luts.TILING12_1_1_, config, 4)
                            else:
                                cell.calculate_center_vertex() # v12 needed
                                cell.add_triangles(luts.TILING12_2, config, 8)
                        else:
                            if test_face(cell, luts.TEST12.get2(config,1)):
                                cell.calculate_center_vertex() # v12 needed
                                cell.add_triangles(luts.TILING12_2_, config, 8)
                            else:
                                if test_internal(cell, luts, case, config, subconfig, luts.TEST12.get2(config,2)):
                                    cell.add_triangles(luts.TILING12_1_1, config, 4)
                                else:
                                    cell.add_triangles(luts.TILING12_1_2, config, 8)
                    
                    elif case == 13 :
                        # Calculate subconfig
                        if test_face(cell, luts.TEST13.get2(config,0)): subconfig += 1
                        if test_face(cell, luts.TEST13.get2(config,1)): subconfig += 2
                        if test_face(cell, luts.TEST13.get2(config,2)): subconfig += 4
                        if test_face(cell, luts.TEST13.get2(config,3)): subconfig += 8
                        if test_face(cell, luts.TEST13.get2(config,4)): subconfig += 16
                        if test_face(cell, luts.TEST13.get2(config,5)): subconfig += 32
                        
                        # Map via LUT
                        subconfig = luts.SUBCONFIG13.get1(subconfig)
                        
                        # Behavior depends on subconfig
                        if subconfig==0:    cell.add_triangles(luts.TILING13_1, config, 4)
                        elif subconfig==1:  cell.add_triangles2(luts.TILING13_2, config, 0, 6)
                        elif subconfig==2:  cell.add_triangles2(luts.TILING13_2, config, 1, 6)
                        elif subconfig==3:  cell.add_triangles2(luts.TILING13_2, config, 2, 6)
                        elif subconfig==4:  cell.add_triangles2(luts.TILING13_2, config, 3, 6)
                        elif subconfig==5:  cell.add_triangles2(luts.TILING13_2, config, 4, 6)
                        elif subconfig==6:  cell.add_triangles2(luts.TILING13_2, config, 5, 6)
                        #
                        elif subconfig==7: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 0, 10)
                        elif subconfig==8: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 1, 10)
                        elif subconfig==9:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 2, 10)
                        elif subconfig==10: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 3, 10)
                        elif subconfig==11: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 4, 10)
                        elif subconfig==12: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 5, 10)
                        elif subconfig==13: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 6, 10)
                        elif subconfig==14: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 7, 10)
                        elif subconfig==15:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 8, 10)
                        elif subconfig==16: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 9, 10)
                        elif subconfig==17: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 10, 10)
                        elif subconfig==18: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3, config, 11, 10)
                        #
                        elif subconfig==19: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_4, config, 0, 12)
                        elif subconfig==20: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_4, config, 1, 12)
                        elif subconfig==21:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_4, config, 2, 12)
                        elif subconfig==22:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_4, config, 3, 12)
                        #
                        elif subconfig==23: 
                            subconfig = 0 # Note: the original source code sets the subconfig, without apparent reason
                            if test_internal(cell, luts, case, config, subconfig, luts.TEST13.get2(config,6)):
                                cell.add_triangles2(luts.TILING13_5_1, config, 0, 6)
                            else:
                                cell.add_triangles2(luts.TILING13_5_2, config, 0, 10)
                        elif subconfig==24: 
                            subconfig = 1
                            if test_internal(cell, luts, case, config, subconfig, luts.TEST13.get2(config,6)):
                                cell.add_triangles2(luts.TILING13_5_1, config, 1, 6)
                            else:
                                cell.add_triangles2(luts.TILING13_5_2, config, 1, 10)
                        elif subconfig==25: 
                            subconfig = 2 ;
                            if test_internal(cell, luts, case, config, subconfig, luts.TEST13.get2(config,6)):
                                cell.add_triangles2(luts.TILING13_5_1, config, 2, 6)
                            else:
                                cell.add_triangles2(luts.TILING13_5_2, config, 2, 10)
                        elif subconfig==26: 
                            subconfig = 3 ;
                            if test_internal(cell, luts, case, config, subconfig, luts.TEST13.get2(config,6)):
                                cell.add_triangles2(luts.TILING13_5_1, config, 3, 6)
                            else:
                                cell.add_triangles2(luts.TILING13_5_2, config, 3, 10)
                        #
                        elif subconfig==27: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 0, 10)
                        elif subconfig==28: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 1, 10)
                        elif subconfig==29:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 2, 10)
                        elif subconfig==30:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 3, 10)
                        elif subconfig==31:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 4, 10)
                        elif subconfig==32:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 5, 10)
                        elif subconfig==33: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config,6, 10)
                        elif subconfig==34: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 7, 10)
                        elif subconfig==35:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 8, 10)
                        elif subconfig==36: 
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 9, 10)
                        elif subconfig==37:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 10, 10)
                        elif subconfig==38:
                            cell.calculate_center_vertex() # v12 needed
                            cell.add_triangles2(luts.TILING13_3_, config, 11, 10)
                        #
                        elif subconfig==39: 
                            cell.add_triangles2(luts.TILING13_2_, config, 0, 6)
                        elif subconfig==40: 
                            cell.add_triangles2(luts.TILING13_2_, config, 1, 6)
                        elif subconfig==41: 
                            cell.add_triangles2(luts.TILING13_2_, config, 2, 6)
                        elif subconfig==42: 
                            cell.add_triangles2(luts.TILING13_2_, config, 3, 6)
                        elif subconfig==43: 
                            cell.add_triangles2(luts.TILING13_2_, config, 4, 6)
                        elif subconfig==44: 
                            cell.add_triangles2(luts.TILING13_2_, config, 5, 6)
                        #
                        elif subconfig==45: 
                            cell.add_triangles(luts.TILING13_1_, config, 4)
                        #
                        else:
                            print("Marching Cubes: Impossible case 13?" )
                    
                    elif case == 14 :
                        cell.add_triangles(luts.TILING14, config, 4)
    
    # Done
    return cell.get_vertices(), cell.get_faces()
#     return edges[:edgeCount,:]


cdef int test_face(Cell cell, int face):
    """ Return True of the face contains part of the surface.
    """
    
    # Get face absolute value
    cdef int absFace = face
    if face < 0:
        absFace *= -1
    
    # Get values of corners A B C D
    cdef double A, B, C, D
    if absFace == 1:
        A, B, C, D = cell.v0, cell.v4, cell.v5, cell.v1
    elif absFace == 2:
        A, B, C, D = cell.v1, cell.v5, cell.v6, cell.v2
    elif absFace == 3:
        A, B, C, D = cell.v2, cell.v6, cell.v7, cell.v3
    elif absFace == 4:
        A, B, C, D = cell.v3, cell.v7, cell.v4, cell.v0
    elif absFace == 5:
        A, B, C, D = cell.v0, cell.v3, cell.v2, cell.v1 
    elif absFace == 6:
        A, B, C, D = cell.v4, cell.v7, cell.v6, cell.v5
    
    # Return sign
    cdef double AC_BD = A*C - B*D
    if AC_BD > - FLT_EPSILON and AC_BD < FLT_EPSILON:
        return face >= 0
    else:
        return face * A * AC_BD >= 0;  # face and A invert signs


cdef int test_internal(Cell cell, LutProvider luts, int case, int config, int subconfig, int s):
    """ Return True of the face contains part of the surface.
    """
    
    # Typedefs
    cdef double t, At, Bt, Ct, Dt, a, b
    cdef int test = 0
    cdef int edge = -1 # reference edge of the triangulation
    
    
    # Calculate At Bt Ct Dt a b
    # Select case 4, 10,  7, 12, 13
    At, Bt, Ct, Dt = 0.0, 0.0, 0.0, 0.0
    
    if case==4 or case==10:
        a = ( cell.v4 - cell.v0 ) * ( cell.v6 - cell.v2 ) - ( cell.v7 - cell.v3 ) * ( cell.v5 - cell.v1 )
        b =  cell.v2 * ( cell.v4 - cell.v0 ) + cell.v0 * ( cell.v6 - cell.v2 ) - cell.v1 * ( cell.v7 - cell.v3 ) - cell.v3 * ( cell.v5 - cell.v1 )
        t = - b / (2*a)
        if t<0 or t>1:  return s>0 ;
    
        At = cell.v0 + ( cell.v4 - cell.v0 ) * t
        Bt = cell.v3 + ( cell.v7 - cell.v3 ) * t
        Ct = cell.v2 + ( cell.v6 - cell.v2 ) * t
        Dt = cell.v1 + ( cell.v5 - cell.v1 ) * t
    
    elif case==6 or case==7 or case==12 or case==13:
        # Define edge
        if case == 6:  edge = luts.TEST6.get2(config, 2)
        elif case == 7: edge = luts.TEST7.get2(config, 4)
        elif case == 12: edge = luts.TEST12.get2(config, 3)
        elif case == 13: edge = luts.TILING13_5_1.get3(config, subconfig, 0)
        
        if edge==0:
            t  = cell.v0 / ( cell.v0 - cell.v1 )
            At = 0
            Bt = cell.v3 + ( cell.v2 - cell.v3 ) * t
            Ct = cell.v7 + ( cell.v6 - cell.v7 ) * t
            Dt = cell.v4 + ( cell.v5 - cell.v4 ) * t
        elif edge==1:
            t  = cell.v1 / ( cell.v1 - cell.v2 )
            At = 0
            Bt = cell.v0 + ( cell.v3 - cell.v0 ) * t
            Ct = cell.v4 + ( cell.v7 - cell.v4 ) * t
            Dt = cell.v5 + ( cell.v6 - cell.v5 ) * t
        elif edge==2:
            t  = cell.v2 / ( cell.v2 - cell.v3 )
            At = 0
            Bt = cell.v1 + ( cell.v0 - cell.v1 ) * t
            Ct = cell.v5 + ( cell.v4 - cell.v5 ) * t
            Dt = cell.v6 + ( cell.v7 - cell.v6 ) * t
        elif edge==3:
            t  = cell.v3 / ( cell.v3 - cell.v0 )
            At = 0
            Bt = cell.v2 + ( cell.v1 - cell.v2 ) * t
            Ct = cell.v6 + ( cell.v5 - cell.v6 ) * t
            Dt = cell.v7 + ( cell.v4 - cell.v7 ) * t
        elif edge==4:
            t  = cell.v4 / ( cell.v4 - cell.v5 )
            At = 0
            Bt = cell.v7 + ( cell.v6 - cell.v7 ) * t
            Ct = cell.v3 + ( cell.v2 - cell.v3 ) * t
            Dt = cell.v0 + ( cell.v1 - cell.v0 ) * t
        elif edge==5:
            t  = cell.v5 / ( cell.v5 - cell.v6 )
            At = 0
            Bt = cell.v4 + ( cell.v7 - cell.v4 ) * t
            Ct = cell.v0 + ( cell.v3 - cell.v0 ) * t
            Dt = cell.v1 + ( cell.v2 - cell.v1 ) * t
        elif edge==6:
            t  = cell.v6 / ( cell.v6 - cell.v7 )
            At = 0
            Bt = cell.v5 + ( cell.v4 - cell.v5 ) * t
            Ct = cell.v1 + ( cell.v0 - cell.v1 ) * t
            Dt = cell.v2 + ( cell.v3 - cell.v2 ) * t
        elif edge==7:
            t  = cell.v7 / ( cell.v7 - cell.v4 )
            At = 0
            Bt = cell.v6 + ( cell.v5 - cell.v6 ) * t
            Ct = cell.v2 + ( cell.v1 - cell.v2 ) * t
            Dt = cell.v3 + ( cell.v0 - cell.v3 ) * t
        elif edge==8:
            t  = cell.v0 / ( cell.v0 - cell.v4 )
            At = 0
            Bt = cell.v3 + ( cell.v7 - cell.v3 ) * t
            Ct = cell.v2 + ( cell.v6 - cell.v2 ) * t
            Dt = cell.v1 + ( cell.v5 - cell.v1 ) * t
        elif edge==9:
            t  = cell.v1 / ( cell.v1 - cell.v5 )
            At = 0
            Bt = cell.v0 + ( cell.v4 - cell.v0 ) * t
            Ct = cell.v3 + ( cell.v7 - cell.v3 ) * t
            Dt = cell.v2 + ( cell.v6 - cell.v2 ) * t
        elif edge==10:
            t  = cell.v2 / ( cell.v2 - cell.v6 )
            At = 0
            Bt = cell.v1 + ( cell.v5 - cell.v1 ) * t
            Ct = cell.v0 + ( cell.v4 - cell.v0 ) * t
            Dt = cell.v3 + ( cell.v7 - cell.v3 ) * t
        elif edge==11:
            t  = cell.v3 / ( cell.v3 - cell.v7 )
            At = 0
            Bt = cell.v2 + ( cell.v6 - cell.v2 ) * t
            Ct = cell.v1 + ( cell.v5 - cell.v1 ) * t
            Dt = cell.v0 + ( cell.v4 - cell.v0 ) * t
        else:
             print( "Invalid edge %i." % edge )
    else:
        print( "Invalid ambiguous case %i." % case )
    
    # Process results
    if At >= 0: test += 1
    if Bt >= 0: test += 2
    if Ct >= 0: test += 4
    if Dt >= 0: test += 8
    
    # Determine what to return
    if test==0: return s>0
    elif test==1: return s>0
    elif test==2: return s>0
    elif test==3: return s>0
    elif test==4: return s>0
    elif test==5: 
        if At * Ct - Bt * Dt <  FLT_EPSILON: return s>0
    elif test==6: return s>0
    elif test==7: return s<0
    elif test==8: return s>0
    elif test==9: return s>0
    elif test==10: 
        if At * Ct - Bt * Dt >= FLT_EPSILON: return s>0
    elif test==11: return s<0
    elif test==12: return s>0
    elif test==13: return s<0
    elif test==14: return s<0
    elif test==15: return s<0
    else: return s<0
