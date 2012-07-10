# Cython specific imports
import numpy as np
cimport numpy as np
import cython 

cdef double pi = 3.1415926535897931
cdef extern from "math.h":
    double sin(double val)

# Type defs, we support float32 and float64
ctypedef np.float32_t FLOAT32_T
ctypedef np.float64_t FLOAT64_T
ctypedef np.int32_t INT32_T
FLOAT32 = np.float32
FLOAT64 = np.float64
INT32 = np.float32


# Floor operator (deal with negative numbers)
cdef inline int floor(double a): return <int>a if a>=0.0 else (<int>a)-1

cdef inline double fabs(double a): return a if a>=0 else -a


@cython.boundscheck(False)
@cython.wraparound(False)
def marching_squares(im, isovalue, 
                        cellToEdge, edgeToRelativePosX, edgeToRelativePosY):
    
    # Create array for result
    edges = np.zeros((im.size,2), 'float32')
    
    # Define maps as array types
    cdef np.ndarray[INT32_T, ndim=2] edgeToRelativePosX_ = edgeToRelativePosX
    cdef np.ndarray[INT32_T, ndim=2] edgeToRelativePosY_ = edgeToRelativePosY
    cdef np.ndarray[INT32_T, ndim=2] cellToEdge_ = cellToEdge
    
    # Define other arrays
    cdef np.ndarray[FLOAT32_T, ndim=2] im_ = im
    cdef np.ndarray[FLOAT32_T, ndim=2] edges_ = edges
    
    cdef int x, y, z
    cdef int dx1, dy1, dz1, dx2, dy2, dz2
    cdef double fx, fy, fz, ff
    cdef int i, j, k
    cdef int index
    cdef double tmpf, tmpf1, tmpf2
    cdef double isovalue_ = isovalue
    
    cdef double edgeCount = 0
    
    for y in range(im.shape[0]-1):
        for x in range(im.shape[1]-1):
            
            # Calculate index.
            index = 0
            if im_[y, x] > isovalue_:
                index += 1
            if im_[y, x+1] > isovalue_:
                index += 2
            if im_[y+1, x+1] > isovalue_:
                index += 4
            if im_[y+1, x] > isovalue_:
                index += 8
            
            # Resolve ambiguity
            if index == 5 or index == 10:
                # Calculate value of cell center (i.e. average of corners)
                tmpf = 0.0
                for dy1 in range(2):
                    for dx1 in range(2):
                        tmpf += im_[y+dy1,x+dx1]
                tmpf /= 4
                # If below isovalue, swap
                if tmpf <= isovalue_:
                    if index == 5:
                        index = 10
                    else:
                        index = 5
            
            # For each edge ...
            for i in range(cellToEdge_[index,0]):
                # For both ends of the edge ...
                for j in range(2):
                    # Get edge index
                    k = cellToEdge_[index, 1+i*2+j]
                    # Use these to look up the relative positions of the pixels to interpolate
                    dx1, dy1 = edgeToRelativePosX_[k,0], edgeToRelativePosY_[k,0]
                    dx2, dy2 = edgeToRelativePosX_[k,1], edgeToRelativePosY_[k,1]
                    # Define "strength" of each corner of the cube that we need
                    tmpf1 = 1.0 / (0.0001 + fabs( im_[y+dy1,x+dx1] - isovalue_))
                    tmpf2 = 1.0 / (0.0001 + fabs( im_[y+dy2,x+dx2] - isovalue_))
                    # Apply a kind of center-of-mass method
                    fx, fy, ff = 0.0, 0.0, 0.0
                    fx += <double>dx1 * tmpf1;  fy += <double>dy1 * tmpf1;  ff += tmpf1
                    fx += <double>dx2 * tmpf2;  fy += <double>dy2 * tmpf2;  ff += tmpf2
                    #
                    fx /= ff
                    fy /= ff
                    # Append point
                    edges_[edgeCount,0] = <double>x + fx
                    edges_[edgeCount,1] = <double>y + fy
                    edgeCount += 1
    
    # Done
    return edges[:edgeCount,:]


# @cython.boundscheck(False)
# @cython.wraparound(False)
# cdef int correct_index(int index, int y, int x, float value, float isovalue_):
#     cdef float tmpf
#     cdef int dy1, dx1, dy2, dx2
#      
#     if index == 5 or index == 10:
#         # Calculate value of cell center (i.e. average of corners)
#         tmpf = 0.0
#         for dy1 in range(2):
#             for dx1 in range(2):
#                 tmpf += value
#         tmpf /= 4
#         # If below isovalue, swap
#         if tmpf <= isovalue_:
#             if index == 5:
#                 index = 10
#             else:
#                 index = 5
#     return index
