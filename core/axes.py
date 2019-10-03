# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module baseFigure

Defines the AxisContainer and Axes classes, as well as the Legend class used
by the Axes.

"""

import OpenGL.GL as gl

from visvis.utils.pypoints import Pointset
#
import visvis as vv
from visvis.core import base
from visvis.core.base import DRAW_NORMAL, DRAW_FAST, DRAW_SHAPE, DRAW_SCREEN
from visvis.core.misc import Property, PropWithDraw, DrawAfter
from visvis.core.misc import Range, getColor, basestring
#
from visvis.core.baseWibjects import Box, DraggableBox
from visvis.core import cameras
from visvis.core.cameras import ortho
from visvis.text import Label
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
                
        # screenshot buffer and variable to indicate whether we can use it
        self._screenshot = None
        self._isdirty = True
        self._motionBlur = 0.0
        self._useBuffer = True
        
        # varialble to keep track of the position correction to fit labels
        self._xCorr, self._yCorr = 0, 0
        
        # create cameras and select 3D as the defaule
        self._cameras = {}
        self.camera = cameras.TwoDCamera()
        self.camera = cameras.ThreeDCamera()
        self.camera = cameras.FlyCamera()
        self.camera = '3D' # Select
        
        # init the background color of this axes
        self.bgcolor = 1,1,1  # remember that bgcolor is a property
        self.bgcolors = None
        
        # bind to event (no need to unbind because it's our own)
        self.eventMouseDown.Bind(self._OnMouseDown)
        self.eventKeyDown.Bind(self._OnKeyDown)
        self.eventScroll.Bind(self._OnScroll)
        
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
        
        Get the limits of the axes as currently displayed. This can differ
        from what was set by SetLimits if the daspectAuto is False.  With
        a 2D camera, this returns the limits for x and y determined by the
        view.  With a 3D camera, this returns the x, y, and z extents of
        the coordinate axes.
        
        """
        return self.camera.GetLimits()
    
    
    def GetView(self):
        """ GetView()
        
        Get a dictionary with the camera parameters. The parameters are
        named so they can be changed in a natural way and fed back using
        SetView(). Note that the parameters can differ for different camera
        types.
        
        """
        return self.camera.GetViewParams()
    
    
    @DrawAfter
    def SetView(self, s=None, **kw):
        """ SetView(s=None, **kw)
        
        Set the camera view using the given dictionary with camera parameters.
        Camera parameters can also be passed as keyword/value pairs; these will
        supersede the values of the same key in s.  If neither s nor any keywords
        are set, the camera is reset to its initial state.
        
        """
        if s or kw:
            self.camera.SetViewParams(s, **kw)
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
        if isinstance(self.camera, cameras.TwoDCamera):
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
    
    
    @PropWithDraw
    def bgcolors():
        """ Get/Set the colors for the axes background gradient. If used, this
        value overrides the normal bgcolor property. Notes:
          * Set to None to disable the gradient
          * Setting two colors defines a gradient from top to bottom.
          * Setting four colors sets the colors at the four corners.
          * The value must be an iterable (2 or 4 elements) in which each
            element can be converted to a color.
        """
        def fget(self):
            return self._bgcolors
        def fset(self, value):
            # None?
            if value is None:
                self._bgcolors = None
                return
            # Check
            try:
                if len(value) not in [2,4]:
                    raise ValueError('bgcolors must have 2 or 4 elements.')
            except Exception:
                # not an iterable
                raise ValueError('bgcolors must be None, or tuple/list/string.')
            # Apply
            colors = [getColor(val, 'setting bgcolors') for val in value]
            self._bgcolors = tuple(colors)
        return locals()
    
    
    @property
    def axis(self):
        """ Get the axis object associated with this axes.
        A new instance is created if it does not yet exist. This object
        can be used to change the appearance of the axis (tickmarks, labels,
        grid, etc.).
        
        See also the [[cls_BaseAxis Axis class]].
        
        """
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
        return locals()
    
    
    @PropWithDraw
    def camera():
        """ Get/Set the current camera.
        
        Setting can be done using:
          * The index of the camera; 1,2,3 for fly, 2d and 3d respectively.
          * A value as in the 'cameraType' property.
          * A new camera instance. This will replace any existing camera
            of the same type. To have multiple 3D cameras at the same axes,
            one needs to subclass cameras.ThreeDCamera.
        
        Shared cameras
        --------------
        One can set the camera to the camera of another Axes, so that they
        share the same camera. A camera that is shared uses daspectAuto
        property of the first axes it was attached to.
        
        Interactively changing a camera
        -------------------------------
        By default, the camera can be changed using the keyboard using the
        shortcut ALT+i, where i is the camera number. Similarly
        the daspectAuto propert can be switched with ALT+d.
        """
        def fget(self):
            return self._camera
        def fset(self, value):
            if isinstance(value, (basestring, int)):
                # Type
                self.cameraType = value
            else:
                # It must be a camera
                camera = value
                # Check
                if not isinstance(camera, cameras.BaseCamera):
                    raise ValueError('Given argument is not a camera.')
                # Store camera
                camType = camera.__class__.__name__
                oldCamera = self._cameras.get(camType, None)
                self._cameras[camType] = camera
                # Register at camera, unregister at old one
                camera._RegisterAxes(self)
                if oldCamera and oldCamera is not camera:
                    oldCamera._UnregisterAxes(self)
                # Make current and set limits
                self._camera = camera
                self.SetLimits()
        return locals()
    
    
    @PropWithDraw
    def cameraType():
        """ Get/Set the camera type to use.
        
        Currently supported are:
          * '2d' or 2  - two dimensional camera that looks down the z-dimension.
          * '3d' or 3  - three dimensional camera.
          * 'fly' or 1 - a camera like a flight sim.
        
        """
        def fget(self):
            return self._camera._NAMES[0]
        def fset(self, name):
            # Case insensitive
            if isinstance(name, basestring):
                name = name.lower()
            # Get camera with that name
            theCamera = None
            for camera in self._cameras.values():
                if name in camera._NAMES:
                    theCamera = camera
                    break
            # Set or raise error
            if theCamera:
                self._camera = theCamera
            else:
                raise ValueError("Unknown camera type!")
        return locals()
    
    
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
        """ Get/set the data aspect ratio of the current camera. Setting will
        also update daspect for the other cameras.
        
        The daspect is a 3-element tuple (x,y,z). If a 2-element tuple is
        given, z is assumed 1. Note that only the ratio between the values
        matters (i.e. (1,1,1) equals (2,2,2)). When a value is negative, the
        corresponding dimension is flipped.
        
        Note that if daspectAuto is True, the camera automatically changes
        its daspect to nicely scale the data to fit the screen (but the sign
        is preserved).
        """
        def fget(self):
            return self.camera.daspect
        def fset(self, value):
            # Set on all cameras
            camera = None
            for camera in self._cameras.values():
                camera.daspect = value
            # Set on self so new cameras can see what the user set.
            # Use camera's daspect, in case a 2-element tuple was used.
            if camera is not None:
                self._daspect = camera.daspect
        return locals()
    
    @property
    def daspectNormalized(self):
        """ Get the data aspect ratio, normalized such that the x scaling
        is +/- 1.
        """
        return self.camera.daspectNormalized
    
    @PropWithDraw
    def daspectAuto():
        """ Get/Set whether to scale the dimensions independently.
        
        If True, the camera changes the value of its daspect to nicely fit
        the data on screen (but the sign is preserved). This can happen
        (depending on the type of camera) during resetting, zooming, and
        resizing of the axes.
        
        If set to False, the daspect of all cameras is reverted to
        the user-set daspect.
        """
        def fget(self):
            return self._daspectAuto
        def fset(self, value):
            # Set dastecpAuto
            self._daspectAuto = bool(value)
            # Update daspect if False
            if not value:
                self.daspect = self._daspect
        return locals()
    
    
    @PropWithDraw
    def legend():
        """ Get/Set the string labels for the legend. Upon setting,
        a legend wibject is automatically shown.
        """
        def fget(self):
            return self.legendWibject._stringList
        def fset(self, value):
            self.legendWibject.SetStrings(value)
        return locals()
    
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
        return locals()
    
    
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
        return locals()
    
    ## Implement methods
    
    def OnDestroy(self):
        # Clean up.
        base.Wibject.OnDestroy(self)
        self.Clear(True)
        self._camera = None
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
        fig._dpi_aware_viewport(pos.absLeft, h-pos.absBottom, pos.w, pos.h)
        
        self._OnDrawContent(DRAW_SHAPE, clr, pos, pickerHelper)
        
        # Prepare for wibject children (draw in full viewport)
        fig._dpi_aware_viewport(0, 0, w, h)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        fig._normal_ortho(0, w, h, 0)
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
            
            # Correction of size for labels is normally done in OnDrawShape,
            # but this is not called if user interaction is disabled ...
            if not fig.enableUserInteraction:
                self._CorrectPositionForLabels()
            
            # Find actual position in pixels, do not allow negative values
            pos = self.position.InPixels()
            pos._w, pos._h = max(pos.w, 1), max(pos.h, 1)
            pos.h_fig = h
            pos._Update()
            
            # Set viewport (note that OpenGL has origin in lower-left, visvis
            # in upper-left)
            fig._dpi_aware_viewport(pos.absLeft, h-pos.absBottom, pos.w, pos.h)
            
            # Select screenshot
            sshot = self._screenshot
        
        
        # Perform tests
        # Only if enabled on axes and if user interaction is enabled for the figure
        if self._useBuffer and fig.enableUserInteraction:
            
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
            if self._useBuffer and fig.enableUserInteraction:
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
            fig._dpi_aware_viewport(0, 0, w, h)
            gl.glDisable(gl.GL_DEPTH_TEST)
        
        
        # Draw axis if using the 2D camera
        if isinstance(self.camera, cameras.TwoDCamera):
            # Let axis object for 2D-camera draw in screen coordinates
            # in the full viewport.
            # Note that if the buffered screenshot is used and the content
            # is not drawn, the axis' OnDraw method is not called, and the
            # ticks are therefore not re-calculated (which is time-consuming).
            
            # Set view
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            fig._dpi_aware_ortho( 0, w, 0, h)  # Note that 0 and h are swapped
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
            fig._normal_ortho(0, w, h, 0)
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
            
            # Maybe this would be better (set initial alpha to 0). But things
            # work without it and I'm too afraid to break things.
            # gl.glBlendFuncSeparate(gl.GL_ONE, gl.GL_ZERO, gl.GL_ZERO, gl.GL_ZERO)
            
            # Define colors, use gradient?
            bgcolor1 = bgcolor2 = bgcolor3 = bgcolor4 = bgcolor
            if mode != DRAW_SHAPE and self.bgcolors:
                gl.glShadeModel(gl.GL_SMOOTH)
                if len(self.bgcolors) == 2:
                    bgcolor1 = bgcolor2 = self.bgcolors[0]
                    bgcolor3 = bgcolor4 = self.bgcolors[1]
                elif len(self.bgcolors) == 4:
                    bgcolor1, bgcolor2, bgcolor3, bgcolor4 = self.bgcolors
            
            # Draw
            gl.glBegin(gl.GL_POLYGON)
            gl.glColor3f(bgcolor3[0], bgcolor3[1], bgcolor3[2])
            gl.glVertex2f(0,0)
            gl.glColor3f(bgcolor1[0], bgcolor1[1], bgcolor1[2])
            gl.glVertex2f(0,1)
            gl.glColor3f(bgcolor2[0], bgcolor2[1], bgcolor2[2])
            gl.glVertex2f(1,1)
            gl.glColor3f(bgcolor4[0], bgcolor4[1], bgcolor4[2])
            gl.glVertex2f(1,0)
            gl.glEnd()
            
            # Reset
            gl.glEnable(gl.GL_DEPTH_TEST)
            # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            
        # Draw items in world coordinates
        if True:
            
            # Setup the camera
            self.camera.SetView()
            
            # Draw stuff, but wait with lines
            lines2draw = []
            for item in self._wobjects:
                if isinstance(item, (Line, BaseAxis)):
                    lines2draw.append(item)
                else:
                    item._DrawTree(mode, pickerHelper)
            
            # Lines (and the axis) are a special case. In order to blend
            # them well, we should draw textures, meshes etc, first.
            # Note that this does not work if lines textures are children
            # of each-other. in that case they should be added to the scene
            # in the correct order.
            for item in lines2draw:
                item._DrawTree(mode, pickerHelper)
        
        # Draw items in screen coordinates
        if mode != DRAW_SHAPE:
            
            pixelRatio = self.GetFigure()._devicePixelRatio
            
            # Set camera to screen coordinates.
            gl.glMatrixMode(gl.GL_PROJECTION)
            gl.glLoadIdentity()
            h = pos.h_fig
            ortho(pos.absLeft * pixelRatio,
                  pos.absRight * pixelRatio,
                  (h - pos.absBottom) * pixelRatio,
                  (h - pos.absTop) * pixelRatio,
            )
            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glLoadIdentity()
            
            # Allow wobjects to draw in screen coordinates
            # Note that the axis for the 2d camera needs to draw beyond
            # the viewport of the axes, and is therefore drawn later.
            gl.glEnable(gl.GL_DEPTH_TEST)
            is2dcam = isinstance(self.camera, cameras.TwoDCamera)
            for item in self._wobjects:
                if is2dcam and isinstance(item, BaseAxis):
                    continue
                item._DrawTree(DRAW_SCREEN)
    
    
    def _OnMouseDown(self, event):
        self.MakeCurrent()
    
    def _OnScroll(self, event):
        SCROLL_ZOOM_FACTOR = 1.1
        self.camera.zoom *= SCROLL_ZOOM_FACTOR**event.verticalSteps
    
    def _OnKeyDown(self, event):
        """ Give user a lot of control via special keyboard input.
        Kind of a secret function, as not all keys are not documented.
        """
        
        # Only do this if this is the current axes
        f = self.GetFigure()
        if not (f and self is f.currentAxes):
            return False
        
        if vv.KEY_ALT in event.modifiers and len(event.modifiers)==1:
            
            numbers = [ord(i) for i in '0123456789']
            
            if event.key in numbers:
                self.cameraType = int(chr(event.key))
            elif event.key == ord('d'):
                self.daspectAuto = not self.daspectAuto
            elif event.key == ord('a'):
                self.axis.visible = not self.axis.visible
            elif event.key == ord('g'):
                self.axis.showGrid = not any(self.axis.showGrid)
            elif event.key == ord('b'):
                if self.bgcolor == (1,1,1):
                    self.bgcolor = 'k'
                    self.axis.axisColor = 'w'
                else:
                    self.bgcolor = 'w'
                    self.axis.axisColor = 'k'
            else:
                return False
        else:
            return False
    
    
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
        deltax, deltay = label.GetVertexLimits()
        #y2 = label.position.h / 2
        y2 = (deltay[1] + deltay[0]) / 2
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
            deltax, deltay = label.GetVertexLimits()
            label.position.w = (deltax[1]-deltax[0])+2
            maxWidth = max([maxWidth, label.position.w ])
        
        # make own size ok
        if self._wobjects:
            pos = label.position
            self.position.w = maxWidth + pos.x + self._xoffset
            #self.position.h = pos.bottom + self._yoffset
            deltax, deltay = label.GetVertexLimits()
            labelHeight = deltay[1]# - deltay[0]
            self.position.h = pos.top + labelHeight + self._yoffset + 2
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
