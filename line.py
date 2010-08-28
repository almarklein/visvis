#   This file is part of VISVIS.
#
#   VISVIS is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as
#   published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   VISVIS is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with this program.  If not, see
#   <http://www.gnu.org/licenses/>.
#
#   Copyright (C) 2010 Almar Klein

""" Module line

Defines the Line class, which represents a line connected (optionally)
with markers. It is the object created with the plot() function.

The lines are drawn simply with OpenGL lines. The markers are drawn
with OpenGl points if possible, and using sprites otherwise.


"""

import OpenGL.GL as gl
import OpenGL.GL.ARB.shader_objects as gla
import OpenGL.GLU as glu

import numpy as np
import math, time, os

from points import Point, Pointset

from misc import Property, Range, OpenGLError, getColor, getOpenGlCapable
from base import Wobject


# int('1010101010101010',2)  int('1100110011001100',2)
lineStyles = {  ':':int('1010101010101010',2),  '--':int('1111000011110000',2),
                '-.':int('1110010011100100',2), '.-':int('1110010011100100',2),
                '-':False, '+':False}


class Sprite:
    """ Represents an OpenGL sprite object. """

    def __init__(self, data):
        """ Supply the data, which must be uint8 alpha data,
        preferably shaped with a power of two. """
        self._texId = 0
        self._data = data
        self._canUse = False # set to True if OpenGl version high enough

    def Create(self):
        """ Create an OpenGL texture from the data. """

        # gl.glEnable(gl.GL_TEXTURE_2D)

        # make texture
        self._texId = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._texId)

        # set interpolation and extrapolation parameters
        tmp = gl.GL_NEAREST # gl.GL_NEAREST | gl.GL_LINEAR
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, tmp)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, tmp)

        # upload data
        shape = self._data.shape
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_ALPHA, shape[0], shape[1],
            0, gl.GL_ALPHA, gl.GL_UNSIGNED_BYTE, self._data)

        # detemine now if we can use point sprites
        self._canUse = getOpenGlCapable('2.0',
            'point sprites (for advanced markers)')


    def Enable(self):
        """ Enable the sprite, drawing points after calling this
        draws this sprite at each point. """

        if not self._texId:
            self.Create()

        if not self._canUse:
            return # canUse is assigned in Create()

        # bind to texture
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self._texId)

        # get allowed point size
        sizeRange = gl.glGetFloatv(gl.GL_ALIASED_POINT_SIZE_RANGE)
        gl.glPointParameterf( gl.GL_POINT_SIZE_MIN, sizeRange[0] );
        gl.glPointParameterf( gl.GL_POINT_SIZE_MAX, sizeRange[1] );

        # enable sprites and set params
        gl.glEnable(gl.GL_POINT_SPRITE)

        # tell opengl to iterate over the texture
        gl.glTexEnvf( gl.GL_POINT_SPRITE, gl.GL_COORD_REPLACE, gl.GL_TRUE )


    def Disable(self):
        """ Return to normal points. """
        if self._canUse:
            gl.glDisable(gl.GL_TEXTURE_2D)
            gl.glDisable(gl.GL_POINT_SPRITE)


    def Destroy(self):
        """ Destroy the sprite, removing the texture from opengl. """
        if self._texId > 0:
            try:
                gl.glDeleteTextures([self._texId])
                self._texId = 0
            except:
                pass

    def __del__(self):
        """ Delete when GC cleans up. """
        self.Destroy()


class MarkerManager:
    """ The markermanager manages sprites to draw the markers. It
    creates the sprite textures on the fly when they are needed.
    Already created sprites are reused.

    Given the markerStyle, markerWidth and markerEdgeWidth a marker
    can be requested.
    """

    def __init__(self):
        # a dict of 3 element tuples (size, sprite1, sprite2)
        # where the first is for the face, the second for the edge.
        self.sprites = {}

    def GetSprites(self, ms, mw, mew):
        """ Get the sprites for drawing the edge and the face, given
        the ms, mw and mew.
        This will create the appropriate sprites or reuse a previously
        created set of sprites if available.
        Returns a tuple (size, faceSprite, edgeSprite)
        """
        # find the diameter which best fits, but which is a multiple of 4
        # such that 32 bits are always filled.
        mw, mew = int(mw), int(mew)

        # create key of these settings
        key = "%s_%i_%i" % (ms, mw, mew)

        # if it does not exist, create it!
        if not self.sprites.has_key(key):
            self.sprites[key] = self._CreateSprites(ms, mw, mew)
        else:
            # check if it is a valid texture ...
            id = self.sprites[key][1]._texId
            if not gl.glIsTexture(id):
                self.sprites[key] = self._CreateSprites(ms, mw, mew)

        # return
        return self.sprites[key]


    def _CreateSprites(self, ms, mw, mew):
        """ Create the sprites from scratch. """

        ## init
        # We'll make a 2D array of size d, which fits the marker completely.
        # Then we make a second array with the original eroded as many
        # times as the edge is wide.

        # find nearest multiple of four
        d = 4
        while d < mw+2*mew:
            d += 4
        # what is the offset for the face
        #dd = ( d-(mw+2*mew) ) / 2
        dd = (d-mw)/2

        # calc center
        c = mw/2.0

        # create patch
        data1 = np.zeros((d,d),dtype=np.uint8)

        # create subarray for face
        data2 = data1[dd:,dd:][:mw,:mw]

        ## define marker functions
        def square(xy):
            x, y = xy
            data2[y,x]=255
        def diamond(xy):
            x, y = xy
            if y > x-mw/2 and y<x+mw/2 and y > (mw-x)-c and y<(mw-x)+c:
                data2[y,x]=255
        def plus(xy):
            x, y = xy
            if y > mw/3 and y < 2*mw/3:
                data2[y,x]=255
            if x > mw/3 and x < 2*mw/3:
                data2[y,x]=255
        def cross(xy):
            x, y = xy
            if y > x-mw/4 and y < x+mw/4:
                data2[y,x]=255
            if y > (mw-x)-mw/4 and y < (mw-x)+mw/4:
                data2[y,x]=255
        def flower(xy):
            x, y = xy
            a = math.atan2(y-c,x-c)
            r = (x-c)**2 + (y-c)**2
            relAng = 5 * a / (2*math.pi)  # whole circle from 1 to 5
            subAng = (relAng % 1)       # get the non-integer bit
            if subAng>0.5: subAng = 1-subAng
            refRad1, refRad2 = c/4, c
            a = math.sin(subAng*math.pi)
            refRad = (1-a)*refRad1 + a*refRad2
            if r < refRad**2:
                data2[y,x]=255
        def star5(xy):
            x, y = xy
            a = math.atan2(y-c,x-c) - 0.5*math.pi
            r = (x-c)**2 + (y-c)**2
            relAng = 5 * a / (2*math.pi)  # whole circle from 1 to 5
            subAng = (relAng % 1)       # get the non-integer bit
            if subAng>0.5: subAng = 1-subAng
            refRad1, refRad2 = c/4, c
            a = math.asin(subAng*2) / (math.pi/2)
            refRad = (1-a)*refRad1 + a*refRad2
            if r < refRad**2:
                data2[y,x]=255
        def star6(xy):
            x, y = xy
            a = math.atan2(y-c,x-c)
            r = (x-c)**2 + (y-c)**2
            relAng = 6 * a / (2*math.pi)  # whole circle from 1 to 5
            subAng = (relAng % 1)       # get the non-integer bit
            if subAng>0.5: subAng = 1-subAng
            refRad1, refRad2 = c/3, c
            a = math.asin(subAng*2) / (math.pi/2)
            refRad = (1-a)*refRad1 + a*refRad2
            if r < refRad**2:
                data2[y,x]=255
        def circle(xy):
            x,y = xy
            r = (x-c)**2 + (y-c)**2
            if r < c**2:
                data2[y,x] = 255
        def triangleDown(xy):
            x,y = xy
            if x >= 0.5*y and x <= mw-0.5*(y+1):
                data2[y,x] = 255
        def triangleUp(xy):
            x,y = xy
            if x >= c-0.5*y and x <= c+0.5*y:
                data2[y,x] = 255
        def triangleLeft(xy):
            x,y = xy
            if y >= c-0.5*x and y <= c+0.5*x:
                data2[y,x] = 255
        def triangleRight(xy):
            x,y = xy
            if y >= 0.5*x and y <= mw-0.5*(x+1):
                data2[y,x] = 255

        # a dict ms to function
        funcs = {   's':square, 'd':diamond, '+':plus, 'x':cross,
                    '*':star5, 'p':star5, 'h':star6, 'f':flower,
                    '.':circle, 'o':circle, 'v':triangleDown,
                    '^':triangleUp, '<':triangleLeft, '>':triangleRight}

        # select function
        try:
            func = funcs[ms]
        except KeyError:
            func = circle

        ## Create face
        I,J = np.where(data2==0)
        xy = zip(I,J)
        map(func, xy)

        ## dilate x times to create edge
        # we add a border to the array to make the dilation possible
        data3 = np.zeros((d+4,d+4), dtype=np.uint8)
        data3[2:-2,2:-2] = 1
        # retrieve indices.
        I,J = np.where(data3==1)
        xy = zip(I,J)
        # copy face
        data3[2:-2,2:-2] = data1
        tmp = data3.copy()
        # apply
        def dilatePixel(xy):
            x,y = xy
            if tmp[y-1:y+2,x-1:x+2].max():
                data3[y,x] = 255
        for i in range(int(mew)):
            map(dilatePixel, xy)
            tmp = data3.copy()
        # remove border
        data3 = data3[2:-2,2:-2]

        ## create sprites and return

        sprite1 = Sprite(data1)
        sprite2 = Sprite(data3-data1)

        return d, sprite1, sprite2


class Line(Wobject):
    """ Line(parent, points)

    The line class represents a set of points (locations) in world coordinates.
    They are displayed by a line between these points and/or markers drawn
    at the point coordinates.

    Line objects can be created with the function vv.plot().

    There are several linestyles that can be used:
      * -  a solid line
      * :   a dotted line
      * --  a dashed line
      * -.  a dashdot line
      * .-  dito
      * +   draws a line between each pair of points (handy for visualizing
            for example vectore fields)
    If None, '' or False is given no line is drawn.

    There are several marker styles that can be used:
      * `+`  a plus
      * `x`  a cross
      * `s`  a square
      * `d`  a diamond
      * `^v<>` an up-, down-, left- or rightpointing triangle
      * `*` or `p`  a (pentagram star)
      * `h`  a hexagram
      * `o` or `.`  a point/circle
    If None, '', or False is given, no marker is drawn.

    Performance tip:
    The s, o (and .) styles can be drawn using standard
    OpenGL points if alpha is 1 or if no markeredge is drawn.
    Otherwise point sprites are used, which can be slower
    on some cards (like ATI, Nvidia performs quite ok with with
    sprites)
    """

    def __init__(self, parent, points):
        Wobject.__init__(self, parent)

        # make a copy
        points = points.Copy()

        # add z dimension to points if not available
        if points.ndim == 2:
            # a bit dirty...
            tmp = points._data, 0.1*np.ones((len(points._data),1), dtype='float32')
            points._data = np.concatenate(tmp,1)
        self._points = points

        # init line properties
        self._lw, self._ls, self._lc = 1, '-', 'b'
        # init marker properties
        self._mw, self._ms, self._mc = 7, '', 'b'
        # init marker edge properties
        self._mew, self._mec = 1, 'k'

        # alpha values
        self._alpha1 = 1


    def _AsFloat(self, value, descr):
        """ Make sure a value is a float. """
        try:
            value = float(value)
            if value<0:
                raise ValueError()
        except ValueError:
            tmp = "the value must be a number equal or larger than zero!"
            raise Exception("Error in %s: %s" % (descr, tmp) )
        return value


    def _GetLimits(self):
        """ _GetLimits()
        Get the limits in world coordinates between which the object exists.
        """
        
        # Obtain untransformed coords (if not an empty set)
        if not self._points:
            return None
        else:
            x1, x2 = self._points[:,0].min(), self._points[:,0].max()
            y1, y2 = self._points[:,1].min(), self._points[:,1].max()
            z1, z2 = self._points[:,2].min(), self._points[:,2].max()
        
        # There we are
        return Wobject._GetLimits(self, x1, x2, y1, y2, z1, z2)


    ## Create properties


    @Property
    def lw():
        """ Get/Set the lineWidth: the width of the line in pixels.
        If zero, the line is not drawn. """
        def fget(self):
            return self._lw
        def fset(self, value):
            self._lw = self._AsFloat(value, 'lineWidth')

    @Property
    def ls():
        """ Get/Set the lineStyle: the style of the line.
          * -   a solid line
          * :   a dotted line
          * --  a dashed line
          * -.  a dashdot line
          * .-  dito
          * +   draws a line between each pair of points
        If None, '' or False is given no line is drawn. """
        def fget(self):
            return self._ls
        def fset(self, value):
            if not value:
                value = None
            elif not isinstance(value, (str,unicode)):
                raise Exception("Error in lineStyle: style must be a string!")
            elif value not in ['-', '--', ':', '-.', '.-', '+']:
                raise Exception("Error in lineStyle: unknown line style!")
            self._ls = value

    @Property
    def lc():
        """ Get/Set the lineColor: the color of the line, as a 3-element
        tuple or as a single character string (shown in uppercase):
        Red, Green, Blue, Yellow, Cyan, Magenta, blacK, White. """
        def fget(self):
            return self._lc
        def fset(self, value):
            value = getColor(value, 'lineColor')
            self._lc = value


    @Property
    def mw():
        """ Get/Set the markerWidth: the width (bounding box) of the marker
        in (screen) pixels. If zero no marker is drawn."""
        def fget(self):
            return self._mw
        def fset(self, value):
            self._mw = self._AsFloat(value, 'markerWidth')

    @Property
    def ms():
        """ Get/Set the markerStyle: the style of the marker.
          * +       : a plus
          * x       : a cross
          * s       : a square
          * d       : a diamond
          * ^v<>    : an up-, down-, left- or rightpointing triangle
          * * or p  : a (pentagram star)
          * h       : a hexagram
          * o or .  : a point/circle
        If None, '', or False is given, no marker is drawn.
        """
        def fget(self):
            return self._ms
        def fset(self, value):
            if not value:
                value = None
            elif not isinstance(value,(str,unicode)):
                raise Exception("markerstyle (ms) should be a string!")
            elif value not in 'sd+x*phfv^><.o':
                raise Exception("Error in markerStyle: unknown line style!")
            self._ms = value

    @Property
    def mc():
        """ Get/Set the markerColor: The color of the face of the marker
        If None, '', or False, the marker face is not drawn (but the edge is).
        """
        def fget(self):
            return self._mc
        def fset(self, value):
            value = getColor(value, 'markerColor')
            self._mc = value

    @Property
    def mew():
        """ Get/Set the markerEdgeWidth: the width of the edge of the marker.
        If zero no edge is drawn. """
        def fget(self):
            return self._mew
        def fset(self, value):
            self._mew = self._AsFloat(value, 'markerEdgeWidth')

    @Property
    def mec():
        """ Get/Set the markerEdgeColor: the color of the edge of the marker.
        """
        def fget(self):
            return self._mec
        def fset(self, value):
            tmp = getColor(value, 'markerEdgeColor')
            self._mec = value

#     # create aliases
#     lineWidth = lw
#     lineStyle = ls
#     lineColor = lc
#     markerWidth = mw
#     markerStyle = ms
#     markerColor = mc
#     markerEdgeWidth = mew
#     markerEdgeColor = mec

    @Property
    def alpha():
        """ Get/Set the alpha (transparancy) of the line and markers.
        When this is < 1, the line cannot be anti-aliased, and it
        is drawn on top of any other wobjects.
        """
        def fget(self):
            return self._alpha1
        def fset(self, value):
            self._alpha1 = self._AsFloat(value, 'alpha')

    ## Set methods

    def SetXdata(self, data):
        """ SetXdata(data)
        Set the x coordinates of the points of the line.
        """
        self._points[0,:] = data

    def SetYdata(self, data):
        """ SetYdata(data)
        Set the y coordinates of the points of the line.
        """
        self._points[1,:] = data

    def SetZdata(self, data):
        """ SetZdata(data)
        Set the z coordinates of the points of the line.
        """
        self._points[2,:] = data

    def SetPoints(self, points):
        """ SetPoints(points)
        Set x,y (and optionally z) data at once
        using a Pointset object. The data is copied, so changes to the given
        points object will not affect the visualized points.
        If you do want this, use the ._points attribute, but note that it
        should always have three dimensions.
        """
        self._points = points.Copy()


    ## Draw methods

    def OnDrawFast(self):
        self.OnDraw(True)

    def OnDraw(self, fast=False):

        # add z dimension to points if not available
        pp = self._points
        if pp.ndim == 2:
            # a bit dirty this
            tmp = pp._data, 0.1*np.ones((len(pp._data),1),dtype='float32')
            pp._data = np.concatenate(tmp,1)

        # can I draw this data?
        if pp.ndim != 3:
            raise Exception("Can only draw 3D data!")

        # no need to draw if no points
        if len(self._points) == 0:
            return

        # enable anti aliasing and blending
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glEnable(gl.GL_BLEND)

        # lines
        if self.lw and self.ls:
            self._DrawLines()

        # points
        if self.mw and self.ms:
            self._DrawPoints()

        # clean up
        #gl.glDisable(gl.GL_BLEND)


    def _DrawLines(self):

        # set stipple style
        if not self.ls in lineStyles:
            stipple = False
        else:
            stipple = lineStyles[self.ls]
        #
        if stipple and self.lw:
            gl.glEnable(gl.GL_LINE_STIPPLE)
            gl.glLineStipple(int(round(self.lw)), stipple)
        else:
            gl.glDisable(gl.GL_LINE_STIPPLE)

        # init vertex array
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(self._points.data)

        # init blending. Only use constant blendfactor when alpha<1
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        if self._alpha1<1:
            if getOpenGlCapable('1.4','transparant points and lines'):
                gl.glBlendFunc(gl.GL_CONSTANT_ALPHA,
                    gl.GL_ONE_MINUS_CONSTANT_ALPHA)
                gl.glBlendColor(0.0,0.0,0.0, self._alpha1)
            gl.glDisable(gl.GL_DEPTH_TEST)

        # get color
        clr = getColor( self.lc )

        if clr and self._alpha1>0:

            # set width and color
            gl.glLineWidth(self.lw)
            gl.glColor3f(clr[0], clr[1], clr[2])

            # draw
            method = gl.GL_LINE_STRIP
            if self.ls == '+':
                method = gl.GL_LINES
            gl.glDrawArrays(method, 0, len(self._points))
            # flush!
            gl.glFlush()

        # clean up
        gl.glDisable(gl.GL_LINE_STIPPLE)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)


    def _DrawPoints(self):

        # get colors (use color from edge or face if not present)
        clr1 = getColor(self.mc)
        clr2 = getColor(self.mec)

        # draw face or edge?
        drawFace = bool(self.mc) # if not ms or mw we would not get here
        drawEdge = self.mec and self.mew
        if not drawFace and not drawEdge:
            return

        # get figure
        f = self.GetFigure()
        if not f:
            return

        # init blending. Only use constant blendfactor when alpha<1
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        if self._alpha1<1:
            if getOpenGlCapable('1.4','transparant points and lines'):
                gl.glBlendFunc(gl.GL_CONSTANT_ALPHA,
                    gl.GL_ONE_MINUS_CONSTANT_ALPHA)
                gl.glBlendColor(0.0,0.0,0.0, self._alpha1)
            gl.glDisable(gl.GL_DEPTH_TEST)

        # init vertex array
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(self._points.data)

        # points drawn on top of points should draw (because we draw
        # the face and edge seperately)
        gl.glDepthFunc(gl.GL_LEQUAL)

        # Enable alpha test, such that fragments with 0 alpha
        # will not update the z-buffer.
        gl.glEnable(gl.GL_ALPHA_TEST)
        gl.glAlphaFunc(gl.GL_GREATER, 0.01)

        if self.ms in ['o','.','s'] and not drawEdge:
            # Use standard OpenGL points, faster and anti-aliased
            # Pure filled points or squares always work.

            # choose style
            if self.ms == 's':
                gl.glDisable(gl.GL_POINT_SMOOTH)
            else:
                gl.glEnable(gl.GL_POINT_SMOOTH)

            # draw faces only
            if drawFace:
                gl.glColor3f(clr1[0],clr1[1],clr1[2])
                gl.glPointSize(self.mw)
                gl.glDrawArrays(gl.GL_POINTS, 0, len(self._points))

        elif self.ms in ['o','.','s'] and drawFace and self.alpha==1:
            # Use standard OpenGL points, faster and anti-aliased
            # If alpha=1 and we have a filled marker, we can draw in two steps.

            # choose style
            if self.ms == 's':
                gl.glDisable(gl.GL_POINT_SMOOTH)
            else:
                gl.glEnable(gl.GL_POINT_SMOOTH)

            # draw edges
            if drawEdge:
                gl.glColor3f(clr2[0],clr2[1],clr2[2])
                gl.glPointSize(self.mw+self.mew*2)
                gl.glDrawArrays(gl.GL_POINTS, 0, len(self._points))
            # draw faces
            if drawFace:
                gl.glColor3f(clr1[0],clr1[1],clr1[2])
                gl.glPointSize(self.mw)
                gl.glDrawArrays(gl.GL_POINTS, 0, len(self._points))

        #elif self.alpha>0:
        else:
            # Use sprites

            # get sprites
            tmp = f._markerManager.GetSprites(self.ms, self.mw, self.mew)
            pSize, sprite1, sprite2 = tmp
            gl.glPointSize(pSize)

            # draw points for the faces
            if drawFace:
                sprite1.Enable()
                gl.glColor3f(clr1[0],clr1[1],clr1[2])
                gl.glDrawArrays(gl.GL_POINTS, 0, len(self._points))
            # draw points for the edges
            if drawEdge:
                sprite2.Enable()
                gl.glColor3f(clr2[0],clr2[1],clr2[2])
                gl.glDrawArrays(gl.GL_POINTS, 0, len(self._points))
            # disable sprites
            sprite2.Disable()

        # clean up
        gl.glDisable(gl.GL_ALPHA_TEST)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


    def OnDrawShape(self, clr):
        # Draw the shape of the line so we can detect mouse actions

        # disable anti aliasing and blending
        gl.glDisable(gl.GL_LINE_SMOOTH)
        gl.glDisable(gl.GL_BLEND)

        # no stippling, square points
        gl.glDisable(gl.GL_LINE_STIPPLE)
        gl.glDisable(gl.GL_POINT_SMOOTH)

        # init vertex array
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(self._points.data)

        # detect which parts to draw
        drawLine, drawMarker = False, False
        if self.lw and self.ls and getColor(self.lc):
            drawLine = True
        if self.mw and self.ms:
            drawMarker = True

        if drawLine:
            # set width and color
            gl.glLineWidth(self.lw)
            gl.glColor3f(clr[0], clr[1], clr[2])
            # draw
            gl.glDrawArrays(gl.GL_LINE_STRIP, 0, len(self._points))
            gl.glFlush()

        if drawMarker:
            w = self.mw
            if self.mec:
                w += self.mew
            # set width and color
            gl.glColor3f(clr[0],clr[1],clr[2])
            gl.glPointSize(w)
            # draw
            gl.glDrawArrays(gl.GL_POINTS, 0, len(self._points))
            gl.glFlush()

        # clean up
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)


    def OnDestroy(self):
        # clean up some memory
        self._points.Clear()


# This is a new type of wobject called PolarLine which encapsulates
# polar plot data.
class PolarLine(Line):
    """ PolarLine(parent, angle(radians), mag)

    The Polarline class represents a set of points (locations) in world
    coordinates.
    They are displayed by a line between these points and/or markers drawn
    at the point coordinates.

    There are several linestyles that can be used:
      * -  a solid line
      * :   a dotted line
      * --  a dashed line
      * -.  a dashdot line
      * .-  dito
      * +   draws a line between each pair of points (handy for visualizing
            for example vectore fields)
    If None, '' or False is given no line is drawn.

    There are several marker styles that can be used:
      * `+`  a plus
      * `x`  a cross
      * `s`  a square
      * `d`  a diamond
      * `^v<>` an up-, down-, left- or rightpointing triangle
      * `*` or `p`  a (pentagram star)
      * `h`  a hexagram
      * `o` or `.`  a point/circle
    If None, '', or False is given, no marker is drawn.

    Performance tip:
    The s, o (and .) styles can be drawn using standard
    OpenGL points if alpha is 1 or if no markeredge is drawn.
    Otherwise point sprites are used, which can be slower
    on some cards (like ATI, Nvidia performs quite ok with with
    sprites)
    """
    def __init__(self, parent, angs, mags):
        self._angs = angs
        self._mags = mags
        x = mags * np.cos(angs)
        y = mags * np.sin(angs)
        z = np.zeros((np.size(x), 1))
        tmp = x, y, z
        pp = Pointset(np.concatenate(tmp, 1))
        Line.__init__(self, parent, pp)

    def TransformPolar(self, radialRange, angRefPos, sense):
        offsetMags = self._mags - radialRange.min
        rangeMags = radialRange.range
        offsetMags[offsetMags > rangeMags] = rangeMags
        tmpang = angRefPos + sense * self._angs
        x = offsetMags * np.cos(tmpang)
        y = offsetMags * np.sin(tmpang)
        z = np.zeros((np.size(x), 1)) + 0.2
        x[offsetMags < 0] = 0
        y[offsetMags < 0] = 0
        tmp = x, y, z
        self._points = Pointset(np.concatenate(tmp, 1))

    def _GetPolarLimits(self):
        if not self._points:
            return None
        else:
            return Range(self._angs.min(), self._angs.max()), \
                   Range(self._mags.min(), self._mags.max())
