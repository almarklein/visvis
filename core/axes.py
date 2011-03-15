# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module baseFigure

Defines the AxisContainer and Axes classes, as well as the Legend class used
by the Axes.

"""

import OpenGL.GL as gl
import OpenGL.GLU as glu

import time
import numpy as np

from visvis.pypoints import Point, Pointset
#
from visvis.core import base
from visvis.core.base import DRAW_NORMAL, DRAW_FAST, DRAW_SHAPE, DRAW_SCREEN
from visvis.core.misc import Property, PropWithDraw, DrawAfter 
from visvis.core.misc import Range, getColor
from visvis.core import events
#
from visvis.core.baseWibjects import Box, DraggableBox
from visvis.core.cameras import (ortho, depthToZ, TwoDCamera, ThreeDCamera, FlyCamera)
from visvis.core.textRender import BaseText, Text, Label
from visvis.core.line import Line 
from visvis.core.axises import BaseAxis, CartesianAxis, PolarAxis2D
from visvis.core.light import Light


def _Screenshot():
    """ _Screenshot()
    
    Capture the screen as a numpy array to use it later.
    Used by the object picker helper to determine which item is
    under the mouse, and by the axes to buffer its content. 
    
    """
    gl.glReadBuffer(gl.GL_BACK)
    xywh = gl.glGetIntegerv(gl.GL_VIEWPORT)
    x,y,w,h = xywh[0], xywh[1], xywh[2], xywh[3]
    # use floats to prevent strides etc. uint8 caused crash on qt backend.
    im = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_FLOAT)
    # reshape, flip, and store
    im.shape = h,w,3
    return im


class _BaseFigure(base.Wibject):
    """ Abstract class that the BaseFigure inherits from. It solves
    the mutual dependence of the Axes and BaseFigure classes.
    """
    pass  


class AxesContainer(Box):
    """ AxesContainer(parent)
    
    A simple container wibject class to contain one Axes instance.
    Each Axes in contained in an AxesContainer instance. By default
    the axes position is expressed in pixel coordinates, while the
    container's position is expressed in unit coordinates. This 
    enables advanced positioning of the Axes.
    
    When there is one axes in a figure, the container position will
    be "0,0,1,1". For subplots however, the containers are positioned
    to devide the figure in equal parts. The Axes instances themselves
    are positioned in pixels, such that when resizing, the margins for
    the tickmarks and labels remains equal.
    
    The only correct way to create (and obtain a reference to) 
    an AxesContainer instance is to use:
      * axes = vv.Axes(figure)
      * container = axes.parent
    
    This container is automatically destroyed once the axes is removed. 
    You can attach wibjects to an instance of this class, but note that
    the container object is destroyed as soon as the axes is gone.
    
    """
    
    def __init__(self, parent, *args, **kwargs):
        
        # check that the parent is a Figure 
        if not isinstance(parent, _BaseFigure):
            raise Exception("The given parent for an AxesContainer " +
                            "should be a Figure.")
        
        # Init box
        Box.__init__(self, parent, *args, **kwargs)
        
        # Init position
        self.position = 0,0,1,1
        
        # Set properties
        self.edgeWidth = 0
        self.bgcolor = None
    
    def GetAxes(self):
        """ GetAxes()
        
        Get the axes. Creates a new axes object if it has none. 
        
        """
        if self._children:
            child = self._children[0]
            if isinstance(child, Axes):
                return child
        return None
    
    
    def _DrawTree(self, mode, *args, **kwargs):
        """ _DrawTree(mode, *args, **kwargs)
        
        Pass on, but Destroy itself if axes is gone. 
        
        """
        axes = self.GetAxes()
        if axes:
            # Draw normally
            base.Wibject._DrawTree(self, mode, *args, **kwargs)
        else:
            self.Destroy()
    

class Axes(base.Wibject):
    """ Axes(parent, axisClass=None)
    
    An Axes instance represents the scene with a local coordinate system 
    in which wobjects can be drawn. It has various properties to influence 
    the appearance of the scene, such as aspect ratio and lighting. 
    
    To set the appearance of the axis (the thing that indicates x, y and z), 
    use the properties of the Axis instance. For example:
    Axes.axis.showGrid = True
    
    The cameraType determines how the data is visualized and how the user 
    can interact with the data.
    
    The daspect property represents the aspect ratio of the data as a
    three element tuple. The sign of the elements indicate dimensions 
    being flipped. (The function imshow() for example flips the 
    y-dimension). If daspectAuto is False, all dimensions are always
    equally zoomed (The function imshow() sets this to False).
    
    An Axes can be created with the function vv.subplot() or vv.gca().
    
    """ 
    
    def __init__(self, parent, axisClass=None):
        
        # check that the parent is a Figure or AxesContainer
        if isinstance(parent, AxesContainer):
            figure = parent.parent 
        elif isinstance(parent, _BaseFigure):            
            figure = parent
            parent = AxesContainer(figure)
        else:
            raise Exception("The given parent for an Axes " +
                            "should be a Figure or AxesContainer.")
        
        # call base __init__
        base.Wibject.__init__(self, parent)
        
        # objects in the scene. The Axes is the only wibject that
        # can contain wobjects. Basically, the Axes is the root
        # for all the wobjects in it.    
        self._wobjects = []
        
        # data aspect ratio. If daspectAuto is True, the values
        # of daspect are ignored (only the sign is taken into account)
        self._daspect = (1.0,1.0,1.0)
        self._daspectAuto = None # None is like False, but means not being set
        
        # make clickable
        self.hitTest = True
        
        # screenshot buffer and variable to indicate whether we can use it
        self._screenshot = None
        self._isdirty = True
        self._motionBlur = 0.0
        self._useBuffer = True
        
        # varialble to keep track of the position correction to fit labels
        self._xCorr, self._yCorr = 0, 0
        
        # create cameras and select one
        self._cameras = {   '2d': TwoDCamera(self), 
                            '3d': ThreeDCamera(self),                            
                            'fly': FlyCamera(self)}
        self.camera = self._cameras['3d']
        
        # init the background color of this axes
        self.bgcolor = 1,1,1  # remember that bgcolor is a property
        
        # bind to event (no need to unbind because it's our own)
        self.eventMouseDown.Bind(self._OnMouseDown)
        
        # Store axis class and instantiate it
        if axisClass is None or not isinstance(axisClass, BaseAxis):
            axisClass = CartesianAxis
        self._axisClass = axisClass
        axisClass(self) # is a wobject
        
        # Let there be lights
        self._lights = []
        for i in range(8):
            self._lights.append(Light(self, i))
        # Init default light
        self.light0.On()
        
        # make current
        figure.currentAxes = self
    
    
    ## Define more methods
    
    @DrawAfter
    def SetLimits(self, rangeX=None, rangeY=None, rangeZ=None, margin=0.02):
        """ SetLimits(rangeX=None, rangeY=None, rangeZ=None, margin=0.02)
        
        Set the limits of the scene. For the 2D camera, these are taken 
        as hints to set the camera view. For the 3D camear, they determine
        where the axis is drawn.
        
        Returns a 3-element tuple of visvis.Range objects.
        
        Parameters
        ----------
        rangeX : (min, max), optional
            The range for the x dimension.
        rangeY : (min, max), optional
            The range for the y dimension.
        rangeZ : (min, max), optional
            The range for the z dimension.
        margin : scalar
            Represents the fraction of the range to add for the
            ranges that are automatically obtained (default 2%).
        
        Notes
        -----
        Each range can be None, a 2 element iterable, or a visvis.Range 
        object. If a range is None, the range is automatically obtained
        from the wobjects currently in the scene. To set the range that
        will fit all wobjects, simply use "SetLimits()"
        
        """
        
        # Check margin
        if margin and not isinstance(margin, float):
            raise ValueError('In SetLimits(): margin should be a float.')
        
        # if tuples, convert to ranges
        if rangeX is None or isinstance(rangeX, Range):
            pass # ok
        elif hasattr(rangeX,'__len__') and len(rangeX)==2:            
            rangeX = Range(rangeX[0], rangeX[1])
        else:
            raise ValueError("Limits should be Ranges or two-element iterables.")
        if rangeY is None or isinstance(rangeY, Range):
            pass # ok
        elif hasattr(rangeY,'__len__') and len(rangeY)==2:            
            rangeY = Range(rangeY[0], rangeY[1])
        else:
            raise ValueError("Limits should be Ranges or two-element iterables.")
        if rangeZ is None or isinstance(rangeZ, Range):
            pass # ok
        elif hasattr(rangeZ,'__len__') and len(rangeZ)==2:            
            rangeZ = Range(rangeZ[0], rangeZ[1])
        else:
            raise ValueError("Limits should be Ranges or two-element iterables.")
        
        rX, rY, rZ = rangeX, rangeY, rangeZ
        
        if None in [rX, rY, rZ]:
            
            # find outmost range
            wobjects = self.FindObjects(base.Wobject)
            for ob in wobjects:
                
                # Ask object what it's limits are
                tmp = ob._GetLimits()
                if not tmp:
                    continue                
                tmpX, tmpY, tmpZ = tmp
                
                # Check for NaNs
                if tmpX.min*0 != 0 or tmpX.max*0 != 0:
                    tmpX = None
                if tmpY.min*0 != 0 or tmpY.max*0 != 0:
                    tmpY = None
                if tmpZ.min*0 != 0 or tmpZ.max*0 != 0:
                    tmpZ = None
                
                # update min/max
                if rangeX:
                    pass
                elif tmpX and rX:
                    rX = Range( min(rX.min, tmpX.min), max(rX.max, tmpX.max) )
                elif tmpX:
                    rX = tmpX
                if rangeY:
                    pass
                elif tmpY and rY:
                    rY = Range( min(rY.min, tmpY.min), max(rY.max, tmpY.max) )
                elif tmpY:
                    rY = tmpY
                if rangeZ:
                    pass
                elif tmpZ and rZ:
                    rZ = Range( min(rZ.min, tmpZ.min), max(rZ.max, tmpZ.max) )
                elif tmpX:
                    rZ = tmpZ
        
        # default values
        if rX is None:
            rX = Range(-1,1)
        if rY is None:
            rY = Range(0,1)
        if rZ is None:
            rZ = Range(0,1)
        
        # apply margins
        if margin:
            if rangeX is None:
                tmp = rX.range * margin
                if tmp == 0: tmp = margin
                rX = Range( rX.min-tmp, rX.max+tmp )            
            if rangeY is None:
                tmp = rY.range * margin
                if tmp == 0: tmp = margin
                rY = Range( rY.min-tmp, rY.max+tmp )
            if rangeZ is None:
                tmp = rZ.range * margin
                if tmp == 0: tmp = margin
                rZ = Range( rZ.min-tmp, rZ.max+tmp )
        
        # apply to each camera
        for cam in self._cameras.values():
            cam.SetLimits(rX, rY, rZ)
        
        # return
        return rX, rY, rZ 
    
    
    def GetLimits(self):
        """ GetLimits()
        
        Get the limits of the 2D axes as currently displayed. This can differ
        from what was set by SetLimits if the daspectAuto is False. 
        Returns a tuple of limits for x and y, respectively.
        
        Note: the limits are queried from the twod camera model, even 
        if this is not the currently used camera.
        
        """
        # get camera
        cam = self._cameras['2d']
        
        # calculate limits
        tmp = cam._fx/2 / self.daspect[0]
        xlim = Range( cam.view_loc[0] - tmp, cam.view_loc[0] + tmp )
        tmp = cam._fy/2 / self.daspect[1]
        ylim = Range( cam.view_loc[1] - tmp, cam.view_loc[1] + tmp )
        
        # return
        return xlim, ylim
    
    
    def GetView(self):
        """ GetView()
        
        Get a structure with the camera parameters. The parameters are
        named so they can be changed in a natural way and fed back using
        SetView(). Note that the parameters can differ for different camera
        types.
        
        """
        return self.camera.GetViewParams()
    
    
    @DrawAfter
    def SetView(self, s=None):
        """ SetView(s=None)
        
        Set the camera view using the given structure with camera parameters.
        If s is None, the camera is reset to its initial state.
        
        """
        if s:
            self.camera.SetViewParams(s)
        else:
            self.camera.Reset()
    
    
    def Draw(self, fast=False):
        """ Draw(fast=False)
        
        Calls Draw(fast) on its figure, as the total opengl canvas 
        has to be redrawn. This might change in the future though. 
        
        """
        
        if self._isbeingdrawn:
            return False
        else:
            # Make dirty
            self._isdirty = True
            
            # Draw figure
            figure = self.GetFigure()
            if figure:
                figure.Draw(fast)
            
            # Done
            return True
    
    
    @DrawAfter
    def Clear(self, clearForDestruction=False):
        """ Clear()
        
        Clear the axes. Removing all wobjects in the scene.
        
        """
        # Remove wobjects
        for w in self.wobjects:
            if isinstance(w, BaseAxis) and not clearForDestruction:
                continue
            elif hasattr(w,'Destroy'):
                w.Destroy()
    
    @property
    def wobjects(self):
        """ Get a shallow copy of the list of wobjects in the scene. 
        """
        return [child for child in self._wobjects]
    
    
    def _CorrectPositionForLabels(self):
        """ _CorrectPositionForLabels()
        
        Correct the position for the labels and title etc. 
        
        """
        
        # init correction
        xCorr, yCorr = 0, 0
        
        # correction should be applied for 2D camera and a valid label
        if isinstance(self.camera, TwoDCamera):
            axis = self.axis
            if isinstance(axis, PolarAxis2D):
                if axis.visible and axis.xLabel:
                    yCorr += 25
            else:
                if axis.visible:
                    yCorr += 20
                    xCorr += 60 # there's already a margin of 10 by default
                    if axis.xLabel:
                        yCorr += 20
                    if axis.yLabel:
                        xCorr += 20
        
        # check the difference
        if xCorr != self._xCorr or yCorr != self._yCorr:
            dx = self._xCorr - xCorr
            dy = self._yCorr - yCorr
            self._xCorr, self._yCorr = xCorr, yCorr
            # apply
            self.position.Correct(-dx, 0, dx, dy)
    
    ## Define more properties
    
    
    @property
    def axis(self):
        """ Get the axis object associated with this axes. 
        A new instance is created if it does not yet exist. This object
        can be used to change the appearance of the axis (tickmarks, labels,
        grid, etc.).
        
        See also the [[cls_BaseAxis Axis class]].
        
        """
        axis = None
        # Find object in root
        for object in self._wobjects:
            if isinstance(object, BaseAxis):
                return object
        else:
            # Create new and return
            return self._axisClass(self)
    
    
    @PropWithDraw
    def axisType():
        """ Get/Set the axis type to use. 
        
        Currently supported are:
          * 'cartesian' - a normal axis (default)
          * 'polar' - a polar axis.
        """        
        def fget(self):
            D = {PolarAxis2D:'polar', CartesianAxis:'cartesian'}
            if self._axisClass in D:
                return D[self._axisClass]
            else:
                return ''
        def fset(self, axisClass):
            # Handle string argument
            if not isinstance(axisClass, BaseAxis):
                D = {'polar':PolarAxis2D, 'cartesian':CartesianAxis}
                if axisClass not in D:
                    raise ValueError('Invalid axis class.')
                axisClass = D[axisClass.lower()]
            if axisClass is not self._axisClass:
                # Store class            
                self._axisClass = axisClass
                # Remove previous
                axisList = self.FindObjects(BaseAxis)
                for axis in axisList:
                    axis.Destroy()
                # Add new
                axisClass(self)
    
    @PropWithDraw
    def cameraType():
        """ Get/Set the camera type to use. 
        
        Currently supported are:
          * '2d' - a two dimensional camera that looks down the z-dimension.
          * '3d' - a three dimensional camera.
          * 'fly' - a camera like a flight sim. Not recommended.
        """
        def fget(self):
            for key in self._cameras:
                if self._cameras[key] is self.camera:
                    return key
            else:
                return ''
        def fset(self, cameraName):        
            MAP = {'twod': '2d', 'threed':'3d'}
            cameraName = cameraName.lower()
            if cameraName in MAP.keys():
                cameraName = MAP[cameraName]
            if not self._cameras.has_key(cameraName):
                raise Exception("Unknown camera type!")
            self.camera = self._cameras[cameraName]
    
    @property
    def mousepos(self):
        """ Get position of mouse in screen pixels, relative to this axes. 
        """
        figure = self.GetFigure()
        if not figure:
            return 0,0
        x,y = figure.mousepos
        pos = self.position
        return x-pos.absLeft, y-pos.absTop
    
    
    @PropWithDraw
    def daspect():
        """ Get/Set the data aspect ratio as a three element tuple. 
        
        A two element tuple can also be given (then z is assumed 1).
        Values can be negative, in which case the corresponding dimension
        is flipped. 
        
        Note that if daspectAuto is True, only the sign of the
        daspect is taken into account.
        """
        def fget(self):            
            return self._daspect
        def fset(self, value):        
            if not value:
                self._daspect = 0
                return
            try:
                l = len(value)
            except TypeError:
                raise Exception("You can only set daspect with a sequence!")
            if 0 in value:
                raise Exception("The given daspect contained a zero!")
            if l==2:            
                self._daspect = (float(value[0]), float(value[1]), 1.0)
            elif l==3:
                self._daspect = (float(value[0]), 
                    float(value[1]), float(value[2]))
            else:            
                raise Exception("daspect should be a length 2 or 3 sequence!")
    
    @PropWithDraw
    def daspectAuto():
        """ Get/Set whether to scale the dimensions independently.
        
        If True, the dimensions are scaled independently, and only the sign
        of the axpect ratio is taken into account. If False, the dimensions
        have the scale specified by the daspect property.
        """
        def fget(self):
            return self._daspectAuto
        def fset(self, value):
            self._daspectAuto = bool(value)
    
    @PropWithDraw
    def legend():
        """ Get/Set the string labels for the legend. Upon setting,
        a legend wibject is automatically shown. 
        """
        def fget(self):
            return self.legendWibject._stringList
        def fset(self, value):            
            self.legendWibject.SetStrings(value)
    
    @property
    def legendWibject(self):
        """ Get the legend wibject, so for exampe its position
        can be changed programatically. 
        """
        legendWibjects = self.FindObjects(Legend)
        if not legendWibjects:
            legendWibjects = [Legend(self)] # create legend object
        return legendWibjects[-1]
    
    
    @property
    def light0(self):
        """ Get the default light source in the scene. 
        """
        return self._lights[0]
    
    @property
    def lights(self):
        """ Get a list of all available lights in the scene. Only light0 is
        enabeled by default. 
        """
        return [light for light in self._lights]
        
    
    @PropWithDraw
    def useBuffer():
        """ Get/Set whether to use a buffer; after drawing, a screenshot
        of the result is obtained and stored. When the axes needs to
        be redrawn, but has not changed, the buffer can be used to 
        draw the contents at great speed (default True).
        """
        def fget(self):
            return self._useBuffer
        def fset(self, value): 
            self._useBuffer = bool(value)
    
    
    @Property
    def motionBlur():
        """ Get/Set the amount of motion blur when interacting with
        this axes. The value should be a number between 0 and 1. 
        Note: this is a rather useless feature :) 
        """
        def fget(self):
            return self._motionBlur
        def fset(self, value): 
            tmp = float(value)
            self._motionBlur = min(max(tmp,0.0),1.0)
    
    ## Implement methods
    
    def OnDestroy(self):
        # Clean up.
        base.Wibject.OnDestroy(self)
        self.Clear(True)
        self.camera = None
        self._cameras = {}
        # container is destroyed as soon as it notices the axes is gone
        # any wibjects are destoyed automatically by the Destroy command.
    
    
    def OnDrawShape(self, clr):
        
        # Correct size for labels (shape is the first draw pass)
        self._CorrectPositionForLabels()
        
        # Get picker helper and draw
        pickerHelper = self.GetFigure()._pickerHelper
        
        # Size of figure ...
        fig = self.GetFigure()
        w,h = fig.position.size
        
        # Find actual position in pixels, do not allow negative values
        pos = self.position.InPixels()
        pos._w, pos._h = max(pos.w, 1), max(pos.h, 1)
        pos.h_fig = h
        pos._Update()
        
        # Set viewport (note that OpenGL has origin in lower-left, visvis
        # in upper-left)
        gl.glViewport(pos.absLeft, h-pos.absBottom, pos.w, pos.h)
        
        self._OnDrawContent(DRAW_SHAPE, clr, pos, pickerHelper)
        
        # Prepare for wibject children (draw in full viewport)
        gl.glViewport(0,0,w,h)
        gl.glDisable(gl.GL_DEPTH_TEST)                
        gl.glMatrixMode(gl.GL_PROJECTION)        
        gl.glLoadIdentity()
        ortho( 0, w, h, 0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # Transform
        self.parent._Transform() # Container
        self._Transform() # Self
    
    
    def OnDrawFast(self):
        self._OnDrawInMode(DRAW_FAST, self.bgcolor)
    
    def OnDraw(self):
        self._OnDrawInMode(DRAW_NORMAL, self.bgcolor)
    
    
    def _OnDrawInMode(self, mode, bgcolor, pickerHelper=None):
        # Draw the background of the axes and the wobjects in it.
        
        # Prepare
        if True:
            
            # Get size of figure ...
            fig = self.GetFigure()
            w,h = fig.position.size
            
            # Find actual position in pixels, do not allow negative values
            pos = self.position.InPixels()
            pos._w, pos._h = max(pos.w, 1), max(pos.h, 1)
            pos.h_fig = h
            pos._Update()
            
            # Set viewport (note that OpenGL has origin in lower-left, visvis
            # in upper-left)
            gl.glViewport(pos.absLeft, h-pos.absBottom, pos.w, pos.h)        
            
            # Select screenshot
            sshot = self._screenshot
        
        
        # Perform tests
        if self._useBuffer:
            
            # Test if we can use the screenshot
            canUseScreenshot = (    (sshot is not None) and 
                                    sshot.shape[0] == pos.h and 
                                    sshot.shape[1] == pos.w )
            
            # Test if we want to blur with the screenshot
            blurWithScreenshot = (  bool(self._motionBlur) and 
                                    self._isdirty and
                                    mode==DRAW_FAST )
            
            # Test whether we should use the screenshot
            shouldUseScreenshot = ( canUseScreenshot and 
                                    (not self._isdirty or blurWithScreenshot) )
        
        else:
            # Old school mode
            shouldUseScreenshot = False
            blurWithScreenshot = False
        
        
        # Draw content of axes (if we need to)
        if (not shouldUseScreenshot) or blurWithScreenshot:
            
            # Draw fresh
            self._OnDrawContent(mode, bgcolor, pos, pickerHelper)
            
            # Make screenshot and store/combine
            tmp = _Screenshot()
            shapesMatch = (sshot is not None) and tmp.shape == sshot.shape
            if blurWithScreenshot and shapesMatch:
                f = self._motionBlur
                sshot[:] = f*sshot + (1.0-f)*tmp
            else:
                self._screenshot = tmp
        
        
        # Draw screenshot (if we should)
        if shouldUseScreenshot:
            
            # Set view
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()        
            ortho( 0, 1, 0, 1)             
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            # Apply bitmap directly
            sshot = self._screenshot
            gl.glRasterPos(0,0)
            gl.glDrawPixels(pos.w, pos.h, gl.GL_RGB, gl.GL_FLOAT, sshot)
        
        
        # # Set viewport to the full figure and disable depth test
        if True:
            gl.glViewport(0,0,w,h)
            gl.glDisable(gl.GL_DEPTH_TEST)
        
        
        # Draw axis if using the 2D camera
        if isinstance(self.camera, TwoDCamera):
            # Let axis object for 2D-camera draw in screen coordinates 
            # in the full viewport.
            # Note that if the buffered screenshot is used and the content
            # is not drawn, the axis' OnDraw method is not called, and the
            # ticks are therefore not re-calculated (which is time-consuming).
            
            # Set view            
            gl.glMatrixMode(gl.GL_PROJECTION)        
            gl.glLoadIdentity()
            ortho( 0, w, 0, h)  # Note that 0 and h are swapped
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            # Draw
            for item in self._wobjects:
                if isinstance(item, BaseAxis):
                    item._DrawTree(DRAW_SCREEN)      
        
        
        # Prepare for drawing child wibjects in screen coordinates 
        if True:
            
            # Set view            
            gl.glMatrixMode(gl.GL_PROJECTION)        
            gl.glLoadIdentity()
            ortho( 0, w, h, 0)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            # Transform
            self.parent._Transform() # Container
            self._Transform() # Self
        
        
        # We're clean now ...
        if mode != DRAW_SHAPE:
            self._isdirty = False
    
    
    def _OnDrawContent(self, mode, bgcolor, pos, pickerHelper=None):
        
        # Draw background
        if bgcolor:
            
            # Set view
            gl.glMatrixMode(gl.GL_PROJECTION)        
            gl.glLoadIdentity()        
            ortho( 0, 1, 0, 1)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            # Overwrite all
            gl.glDisable(gl.GL_DEPTH_TEST)
            
            # Draw
            gl.glColor3f(bgcolor[0], bgcolor[1], bgcolor[2])
            gl.glBegin(gl.GL_POLYGON)
            gl.glVertex2f(0,0)
            gl.glVertex2f(0,1)
            gl.glVertex2f(1,1)
            gl.glVertex2f(1,0)
            gl.glEnd()
            
            # Reset
            gl.glEnable(gl.GL_DEPTH_TEST)
        
        
        # Draw items in world coordinates
        if True:
            
            # Setup the camera
            self.camera.SetView()
            
            # Draw stuff, but wait with lines     
            lines2draw = []
            for item in self._wobjects:
                if isinstance(item, (Line,)):
                    lines2draw.append(item)
                else:
                    item._DrawTree(mode, pickerHelper)
            
            # Lines are special case. In order to blend them well, we should
            # draw textures, meshes etc, first.
            # Note that this does not work if lines textures are children
            # of each-other. in that case they should be added to the scene
            # in the correct order.
            for item in lines2draw:
                item._DrawTree(mode, pickerHelper)
        
        # Draw items in screen coordinates
        if mode != DRAW_SHAPE:
            
            # Set camera to screen coordinates.
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            h = pos.h_fig
            ortho( pos.absLeft, pos.absRight, h-pos.absBottom, h-pos.absTop)
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            # Allow wobjects to draw in screen coordinates
            # Note that the axis for the 2d camera needs to draw beyond
            # the viewport of the axes, and is therefore drawn later.
            gl.glEnable(gl.GL_DEPTH_TEST)
            is2dcam = isinstance(self.camera, TwoDCamera)
            for item in self._wobjects:
                if is2dcam and isinstance(item, BaseAxis):
                    continue
                item._DrawTree(DRAW_SCREEN)
    
    
    def _OnMouseDown(self, event):
        self.MakeCurrent()
    
    def MakeCurrent(self):
        """ MakeCurrent()
        
        Make this the current axes. Also makes the containing figure
        the current figure.
        
        """
        f = self.GetFigure()
        if f:
            f.currentAxes = self
            f.MakeCurrent()


class Legend(DraggableBox):
    """ Legend(parent)
    
    A legend is a wibject that should be a child (does not have
    to be the direct child) of an axes. It displays a description for 
    each line in the axes, and is draggable.
    
    A Legend can be shown with the function vv.legend(), or using the
    Axes.legend property.
    
    """
    
    def __init__(self, parent):
        DraggableBox.__init__(self, parent)
        
        # params for the layout
        self._linelen = 40
        self._xoffset = 10        
        self._yoffset = 3        
        self._yspacing = 16
        
        # position in upper left by default
        self.position = 10, 10
        self.bgcolor = 'w'
        
        # start with nothing
        self._stringList = []
        self.visible = False
        
        # by creating a _wobjects attribute, we are allowed to hold
        # wobjects, but our ourselves responsible for drawing them
        self._wobjects = []
    
    
    def _AddLineAndLabel(self, text, yspacing=1.0, twoPoints=True):
        """ Add a line and label to our pool. """
        # get y position
        index = len(self._wobjects)
        y = self._yoffset + yspacing * (index)        
        # create label
        label = Label(self, text)
        label.bgcolor = ''        
        label.position = self._xoffset*2 + twoPoints*self._linelen, y
        label._Compile()
        label._PositionText()
        #y2 = label.position.h / 2
        y2 = (label._deltay[1] - label._deltay[0]) / 2 
        # create 2-element pointset
        pp = Pointset(2)        
        pp.append(self._xoffset, y + y2)
        if twoPoints:
            pp.append(self._xoffset + self._linelen, y + y2)
        # create line
        line = Line(self, pp) # line has no parent        
        # return
        return line, label
    
    
    def SetStrings(self, *stringList):
        """ SetStrings(*stringList)
        
        Set the strings of the legend labels.
        
        """
        # Note that setting the .visible property will invoke a draw
        
        # test
        if len(stringList)==1 and isinstance(stringList[0],(tuple,list)):
            stringList = stringList[0]
        for value in stringList:
            if not isinstance(value, basestring):
                raise ValueError("Legend string list should only contain strings.")
        
        # store
        self._stringList = stringList
        
        # clean up labels and lines
        for line in [line for line in self._wobjects]:
            line.Destroy()
        for label in self.children:
            label.Destroy()
        
        # find axes and figure
        axes = self.parent
        while axes and not isinstance(axes, Axes):
            axes = axes.parent
        if not axes:
            return
        fig = axes.GetFigure()
        
        # collect line objects
        lines = []
        twoPoints = False
        for ob in axes._wobjects:
            if len(self._wobjects) >= len(stringList):
                break
            if isinstance(ob, Line):
                # Add line props
                tmp = ob.ls, ob.lc, ob.lw, ob.ms, ob.mc, ob.mw, ob.mec, ob.mew
                lines.append(tmp)
                # Set whether to use two points
                twoPoints = twoPoints or bool(ob.ls and ob.lc and ob.lw)
        
        # create new lines and labels
        maxWidth = 0
        nr = -1
        for lineProps in lines:            
            nr += 1
            if nr >= len(stringList):
                break
            # get new line and label                
            text = stringList[nr]
            yspacing = self._yspacing * fig._relativeFontSize
            line, label = self._AddLineAndLabel(text, yspacing, twoPoints)
            # apply line properties
            line.ls, line.lc, line.lw = lineProps[0:3]
            line.ms, line.mc, line.mw = lineProps[3:6]
            line.mec, line.mew = lineProps[6:8]
            # correct label size and store max
            label.position.w = (label._deltax[1]-label._deltax[0])+2
            maxWidth = max([maxWidth, label.position.w ])
        
        # make own size ok
        if self._wobjects:
            pos = label.position
            self.position.w = maxWidth + pos.x + self._xoffset
            #self.position.h = pos.bottom + self._yoffset
            labelHeight = label._deltay[1] - label._deltay[0]
            self.position.h = pos.top + labelHeight + self._yoffset
            self.visible = True
        else:
            self.visible = False
    
    
    def OnDraw(self):
        
        # draw box 
        DraggableBox.OnDraw(self)
        
        # draw lines        
        for line in self._wobjects:
            line.OnDraw()
        
        # reset some stuff that was set because it was thinking it was drawing
        # in world coordinates.
        gl.glDisable(gl.GL_DEPTH_TEST)
    
    
    def OnDestroy(self):
        DraggableBox.OnDestroy(self)
        
        # clear lines and such
        for ob in [ob for ob in self._wobjects]:
            ob.Destroy()

