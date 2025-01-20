# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module cameras

A camera represents both the camera model and the interaction style.

A lot of blood sweat and tears went into this module to get the
OpenGL transformations right and calculate screen to world coordinates
etc. Please be carefull when changing stuff here.

The models were designed such that the order of transformations makes
sense, and that as much as possible "just works". Also the diffent
models were designed to be as consistent as possible.

"""

import OpenGL.GL as gl
import OpenGL.GLU as glu

import math

import visvis as vv
from visvis.core.misc import Property, Range, basestring
from visvis.core import constants
from visvis.utils.pypoints import Quaternion, Point

# Global to store depth Bits
depthBits = [0]
# Trig functions in degrees
sind = lambda q: math.sin(q*math.pi/180)
cosd = lambda q: math.cos(q*math.pi/180)

# The cmp function is gone in Py3k
cmp = lambda a,b: (a > b) - (a < b)


def getDepthValue():
    """ Get the depth value.
    
    for glOrto(x1,y1,x2,y2,n,f) and s the depth buffer depth:
    def calcPrecision(z=0, n=1000, bits=16): # approximates precision
        z+=n
        return z * z / ( n * float(1<<bits) - z )
        
    For 24 bits and more, we're fine with 100.000, but for 16 bits we
    need 3000 or so. The criterion is that at the center, we should be
    able to distinguish between 0.1, 0.0 and -0.1 etc. So we can draw lines
    on top (0.1) then the gridlines (0.0) and then 2d textures
    (0.1, 0.2, etc.).
    
    """
    if not depthBits[0]:
        bits = gl.glGetInteger(gl.GL_DEPTH_BITS)
        if bits:
            depthBits[0] = bits
    # Process
    if depthBits[0] < 24:
        return 3000
    else:
        return 100000


def ortho(x1, x2, y1,y2):
    """ ortho(x1, x2, y1, y2)
    
    Like gl.glOrtho() but the z-values are automatically determined
    dependent on the amount of bits in the depth buffer.
    
    """
    val = getDepthValue()
    gl.glOrtho(x1, x2, y1, y2, -val, val)


def depthToZ(depth):
    """ depthToZ(depth)
    
    Get the z-coord, given the depth value.
    
    """
    val = getDepthValue()
    return val - depth * 2 * val


class BaseCamera(object):
    """ BaseCamera()
    
    Abstract camera class. A camera represents both the camera model
    and the interaction style.
    
    """
    
    # The names by which this camera type is known
    _NAMES = ()
    
    # Subclasses should set viewparams; the list if attributes that define
    # the view of the camera.
    _viewparams = ('daspect', 'loc', 'zoom')
    
    def __init__(self):
        
        # Init list of axeses that this camera applies to
        self._axeses = []
        
        # Init limits of what to visualize
        self._xlim = Range(0,1)
        self._ylim = Range(0,1)
        self._zlim = Range(0,1)
        
        # Init view location
        self._view_loc = 0,0,0
        
        # Init zoom factor
        self._zoom = 1.0
        
        # Init daspect
        self._daspect = 1.0, 1.0, 1.0
        
        # Variable to keep track of window size during resizing
        self._windowSizeFactor = 0
    
    
    def _RegisterAxes(self, axes):
        """ _RegisterAxes(axes)
        
        Method used by the axes to register itself at this camera.
        
        """
        
        # Make sure it not currently registered
        self._UnregisterAxes(axes)
        
        # Append to list
        self._axeses.append(axes)
        
        # Bind to events
        axes.eventPosition.Bind(self.OnResize)
        axes.eventKeyDown.Bind(self.OnKeyDown)
        axes.eventKeyUp.Bind(self.OnKeyUp)
        #
        axes.eventMouseDown.Bind(self.OnMouseDown)
        axes.eventMouseUp.Bind(self.OnMouseUp)
        axes.eventMotion.Bind(self.OnMotion)
        axes.eventDoubleClick.Bind(self.OnDoubleClick)
    
    
    def _UnregisterAxes(self, axes):
        """ _UnregisterAxes(axes)
        
        Method used by the axes to unregister itself at this camera.
        
        """
        
        # Remove from list
        while axes in self._axeses:
            self._axeses.remove(axes)
        
        # Unbind events
        axes.eventPosition.Unbind(self.OnResize)
        axes.eventKeyDown.Unbind(self.OnKeyDown)
        axes.eventKeyUp.Unbind(self.OnKeyUp)
        #
        axes.eventMouseDown.Unbind(self.OnMouseDown)
        axes.eventMouseUp.Unbind(self.OnMouseUp)
        axes.eventMotion.Unbind(self.OnMotion)
        axes.eventDoubleClick.Unbind(self.OnDoubleClick)
    
    
    def OnResize(self, event):
        pass
    def OnKeyDown(self, event):
        pass
    def OnKeyUp(self, event):
        pass
    def OnMouseDown(self, event):
        pass
    def OnMouseUp(self, event):
        pass
    def OnMotion(self, event):
        pass
    
    def OnDoubleClick(self, event):
        # Reset view if this is the current camera.
        if self is self.axes.camera:
            return self.Reset()
    
    @property
    def axes(self):
        """ Get the axes that this camera applies to (or the first axes if
        it applies to multiple axes).
        """
        if self._axeses:
            return self._axeses[0]
        else:
            return None
    
    @property
    def axeses(self):
        """ Get a tuple with the axeses that this camera applies to.
        """
        return tuple(self._axeses)
    
    
    @Property
    def daspect():
        """ Get/Set the data aspect ratio as a three element tuple.
        
        The daspect is a 3-element tuple (x,y,z). If a 2-element tuple is
        given, z is assumed 1. Note that only the ratio between the values
        matters (i.e. (1,1,1) equals (2,2,2)). When a value is negative, the
        corresponding dimension is flipped.
        
        Note that if axes.daspectAuto is True, the daspect is changed by the
        camera to nicely scale the data to fit the screen (but the sign
        is preserved).
        """
        def fget(self):
            return self._daspect
        def fset(self, value):
            try:
                l = len(value)
            except TypeError:
                raise Exception("You can only set daspect with a sequence.")
            if 0 in value:
                raise Exception("The given daspect should not contain zeros.")
            if l==2:
                self._daspect = (float(value[0]), float(value[1]), 1.0)
            elif l==3:
                self._daspect = tuple([float(v) for v in value])
            else:
                raise Exception("daspect should be a length 2 or 3 sequence!")
        return locals()
    
    
    @property
    def daspectNormalized(self):
        """ Get the data aspect ratio, normalized such that the x scaling
        is +/- 1.
        """
        return tuple(d/abs(self._daspect[0]) for d in self._daspect)
    
    @Property
    def zoom():
        """ Get/set the current zoom factor.
        """
        def fget(self):
            return self._zoom
        def fset(self, value):
            self._zoom = float(value)
            for ax in self.axeses:
                ax.Draw()
        return locals()
    
    @Property
    def loc():
        """ Get/set the current viewing location.
        """
        def fget(self):
            return tuple(self._view_loc)
        def fset(self, value):
            # Check
            if isinstance(value, (tuple, list)) and len(value)==3:
                value = [float(v) for v in value]
            else:
                raise ValueError('loc must be a 3-element tuple.')
            # Set
            self._view_loc = tuple(value)
            for ax in self.axeses:
                ax.Draw()
        return locals()
    
    
    def GetLimits(self):
        """ GetLimits()
        
        Return the extent of the axes, which is determined by the camera
        in the 2D case.
        
        """
        return self._xlim, self._ylim, self._zlim
    
    def SetLimits(self, xlim, ylim, zlim=None):
        """ SetLimits(xlim, ylim, zlim=None)
        
        Set the data limits of the camera.
        Always set this before rendering!
        This also calls reset to reset the view.
        
        """
        if zlim is None:
            zlim = Range(-1,1)
        self._xlim = xlim
        self._ylim = ylim
        self._zlim = zlim
        
        # reset
        self.Reset()
    
    
    def GetViewParams(self):
        """ GetViewParams()
        
        Get a dictionary with view parameters.
        
        """
        return dict([(key, getattr(self, key))
                     for key in self.__class__._viewparams])
    
    def SetViewParams(self, s=None, **kw):
        """ SetViewParams(s=None, **kw)
        
        Set the view, given a dictionary with view parameters.  View parameters
        may also be passed as keyword/value pairs; these will supersede the same
        keys in s.
        
        """
        if s is None:
            s = {}
        if kw:
            # Updating with an empty dict is okay, but this way we can take
            # arguments that don't have an update method (like ssdf objects).
            s.update(kw)
        for key in self.__class__._viewparams:
            try:
                setattr(self, key, s[key])
            except KeyError:
                pass
    
    def Reset(self):
        """ Reset()
        
        Reset the view.
        Overload this in the actual camera models.
        
        """
        
        # set centre
        rx,ry,rz = self._xlim.range, self._ylim.range, self._zlim.range
        dx,dy,dz = self._xlim.min, self._ylim.min, self._zlim.min
        self._view_loc = rx/2.0 + dx, ry/2.0 + dy, rz/2.0 + dz
        # refresh
        for axes in self.axeses:
            axes.Draw()
    
    
    def SetView(self):
        """ SetView()
        
        Set the view, thus simulating a camera.
        Overload this in the actual camera models.
        
        """
        pass
    
    
    def ScreenToWorld(self, x_y=None):
        """ ScreenToWorld(x_y=None)
        
        Given a tuple of screen coordinates,
        calculate the world coordinates.
        If not given, the current mouse position is used.
        
        This basically simulates the actions performed in SetView
        but then for a single location.
        
        """
        
        # use current mouse position if none given
        if x_y is None:
            x,y = self.axes.mousepos
        else:
            x, y = x_y[0], x_y[1] # in case the input is 3d
        
        # get window size
        w, h = self.axes.position.size
        w, h = float(w), float(h)
        
        # Calculate viewing range for x and y
        fx = abs( 1.0 / self._zoom )
        fy = abs( 1.0 / self._zoom )
        
        # correct zoom factor for window size
        if w > h:
            fx *= w/h
        else:
            fy *= h/w
        
        # determine position in projection. Here is a conversion
        # of the coordinate system... (flip y)
        x, y = (x/w-0.5) * fx, (0.5-y/h) * fy
        
        # scale
        daspect = self.daspectNormalized
        x, y = x / daspect[0], y / daspect[1]
        
        # translate it
        x, y = x + self._view_loc[0], y + self._view_loc[1]
        
        #print(x, y)
        return x,y
    
    
    def _SetDaspect(self, ratio, i, j, refDaspect=None):
        """ _SetDaspect(ratio,  i, j, refDaspect=None)
        
        Change the value of the given refDaspect (or use self.daspect)
        and set that as the new daspect. The new daspect is also returned.
        
        Sets daspect[i] to daspect[j] * ratio, but preserves the sign
        of the original reference daspect.
        
        """
        
        # Make sure that the ratio is absolute
        ratio = abs(ratio)
        
        # Get daspect from reference daspect
        if refDaspect is None:
            refDaspect = self.daspect
        
        # Get absolute version
        daspect = [abs(d) for d in refDaspect]
        
        # Modify x value using the ratio. Preserve sign
        daspect[i] = daspect[j] * ratio
        
        # Preserve sign
        daspect2 = []
        for i in range(3):
            if refDaspect[i] < 0:
                daspect2.append(-daspect[i])
            else:
                daspect2.append(daspect[i])
        
        # Done
        self.daspect = daspect2
        return daspect2


class TwoDCamera(BaseCamera):
    """ TwoDCamera()
    
    The default camera for viewing 2D data.
    
    This camera uses orthografic projection and looks
    down the z-axis from inifinitly far away.
    
    Interaction
    -----------
      * Hold down the LMB and then move the mouse to pan.
      * Hold down the RMB and then move the mouse to zoom.
    
    """
    
    _NAMES = ('2d', 2, '2', 'twod')
    ndim = 2
    
    def __init__(self):
        BaseCamera.__init__(self)
        
        # reference stuff for interaction
        self._ref_loc = 0,0,0    # view_loc when clicked
        self._ref_mloc = 0,0     # mouse location when clicked
        self._ref_but = 0        # mouse button when clicked
        self._ref_axes = None
        #
        self._ref_zoom = 1.0
        self._ref_daspect = 1,1,1
    
    
    def OnResize(self, event):
        """ OnResize(event)
        
        Callback that adjusts the daspect (if axes.daspectAuto is True)
        when the window dimensions change.
        
        """
        
        # Get new size factor
        w,h = self.axes.position.size
        sizeFactor1 = float(h) / w
        
        # Get old size factor
        sizeFactor2 = self._windowSizeFactor
        
        # Make it quick if daspect is not in auto-mode
        if not self.axes.daspectAuto:
            self._windowSizeFactor = sizeFactor1
            return
        
        # Get daspect factor
        daspectFactor = sizeFactor1
        if sizeFactor2:
            daspectFactor /= sizeFactor2
        
        # Get zoom factor
        zoomFactor = 1.0
        if sizeFactor1 < 1:
            zoomFactor /= sizeFactor1
        if sizeFactor2 and sizeFactor2 < 1:
            zoomFactor *= sizeFactor2
        
        # Set size factor for next time
        self._windowSizeFactor = sizeFactor1
        
        # Change daspect and zoom
        self._SetDaspect(daspectFactor, 1, 1)
        self._zoom *= zoomFactor
    
    
    def Reset(self, event=None):
        """ Reset()
        
        Reset the view.
        
        """
        
        # Reset daspect from user-given daspect
        if self.axes:
            self._daspect = self.axes._daspect
        
        # Get window size (and store factor now to sync with resizing)
        w,h = self.axes.position.size
        w,h = float(w), float(h)
        self._windowSizeFactor = h / w
        
        # Get range and translation for x and y
        rx, ry = self._xlim.range, self._ylim.range
        
        # Correct ranges for window size.
        if w / h > 1:
            rx /= w/h
        else:
            ry /= h/w
        
        # If auto-scale is on, change daspect, x is the reference
        if self.axes.daspectAuto:
            self._SetDaspect(rx/ry, 1, 0)
        
        # Correct for normalized daspect
        ndaspect = self.daspectNormalized
        rx, ry = abs(rx*ndaspect[0]), abs(ry*ndaspect[1])
        
        # Convert to screen coordinates. (just for clarity and to be
        # consistent with the 3D camera)
        rxs = rx
        rys = ry
        
        # Set zoom
        self._zoom = min(1.0/rxs, 1.0/rys)
        
        # Set center location -> calls refresh
        BaseCamera.Reset(self)
    
    
    def GetLimits(self):
        # Calculate viewing range for x and y from camera view
        fx = abs( 1.0 / self._zoom )
        fy = abs( 1.0 / self._zoom )
        # correct for window size
        w, h = map(float, self.axes.position.size)
        if w / h > 1:
            fx *= w/h
        else:
            fy *= h/w
        
        # calculate limits
        tmp = fx/2 / self.axes.daspectNormalized[0]
        xlim = Range( self._view_loc[0] - tmp, self._view_loc[0] + tmp )
        tmp = fy/2 / self.axes.daspectNormalized[1]
        ylim = Range( self._view_loc[1] - tmp, self._view_loc[1] + tmp )
        
        # return
        return xlim, ylim

    
    
    def OnMouseDown(self, event):
        
        # store mouse position and button
        self._ref_mloc = event.x, event.y
        self._ref_but = event.button
        self._ref_axes = event.owner
        
        # store current view parameters
        self._ref_loc = self._view_loc
        self._ref_zoom = self._zoom
        self._ref_daspect = self.daspect
        
        #self.ScreenToWorld() # for debugging


    def OnMouseUp(self, event):
        self._ref_but = 0
        # Draw without the fast flag
        for axes in self.axeses:
            axes.Draw()


    def OnMotion(self, event):
        
        if not self._ref_but:
            return
        if self._ref_axes is not event.owner:
            return
        if self.axes.camera is not self:
            return False
        
        # get loc (as the event comes from the figure, not the axes)
        mloc = event.owner.mousepos
        
        if self._ref_but==1:
            # translate
            
            # get distance and convert to world coordinates
            refloc = self.ScreenToWorld(self._ref_mloc)
            loc = self.ScreenToWorld(mloc)
            
            # calculate translation
            dx = loc[0] - refloc[0]
            dy = loc[1] - refloc[1]
            
            # apply
            self._view_loc = (  self._ref_loc[0] - dx,
                                self._ref_loc[1] - dy,
                                self._ref_loc[2])
        
        elif self._ref_but==2:
            # zoom
            
            # get movement in x (in pixels) and normalize
            factorx = float(self._ref_mloc[0] - mloc[0])
            factorx /= self.axes.position.width
            
            # get movement in y (in pixels) and normalize
            factory = float(self._ref_mloc[1] - mloc[1])
            factory /= self.axes.position.height
            
            # apply
            if self.axes.daspectAuto:
                # Zooming in pure x goes via daspect.
                # Zooming in pure y goes via zoom factor.
                dzoom_x, dzoom_y = math.exp(-factorx), math.exp(factory)
                self._SetDaspect(dzoom_y/dzoom_x, 1, 1, self._ref_daspect)
                self._zoom = self._ref_zoom * dzoom_x
            
            else:
                self._zoom = self._ref_zoom * math.exp(factory)
        
        # refresh
        for axes in self.axeses:
            axes.Draw(True)


    def SetView(self):
        """ SetView()
        
        Prepare the view for drawing
        This applies the camera model.
        
        """
        
        # Calculate viewing range for x and y
        fx = abs( 1.0 / self._zoom )
        fy = abs( 1.0 / self._zoom )
        
        # correct for window size
        if True:
            w, h = self.axes.position.size
            w, h = float(w), float(h)
            if w / h > 1:
                fx *= w/h
            else:
                fy *= h/w
        
        # Init projection view. It will define the whole camera model,
        # so the modelview matrix is really for models only.
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        
        # Remember, in terms of a global coordinate system,
        # the transformations are done backwards... (See the Red Book ch. 3)
        
        # 3. Define part that we view. Remember, we're looking down the
        # z-axis. We zoom here.
        ortho( -0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy)
        
        # Prepare for models ...
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # Set camera lights
        for light in self.axes._lights:
            if light.isCamLight:
                light._Apply()
        
        # 2. Set aspect ratio (scale the whole world), and flip any axis...
        ndaspect = self.daspectNormalized
        gl.glScale( ndaspect[0], ndaspect[1], ndaspect[2] )
        
        # 1. Translate to view location (coordinate where we look at).
        # Do this first because otherwise the translation is not in world
        # coordinates.
        gl.glTranslate(-self._view_loc[0], -self._view_loc[1], 0.0)
        
        # Set non-camera lights
        for light in self.axes._lights:
            if not light.isCamLight:
                light._Apply()


# todo: FOV: properly setting which axis has ticks, the tick spacing,
# and which axes to show when showBox is False.

class ThreeDCamera(BaseCamera):
    """ ThreeDCamera()
    
    The ThreeDCamera camera is a camera to visualise 3D data.
    
    In contrast to the 2D camera, this camera can be rotated around
    the data to look at it from different angles. By default the
    field of view of this camera is set to 0, corresponding to an
    orthografic projection. If the field of view is larger than 0,
    projective projection is applied.
    
    
    Interaction
    -----------
      * Hold down the LMB and then move the mouse to change the azimuth
        and elivation (i.e. rotate around the scene).
      * Hold down the RMB and then move the mouse to zoom.
      * Hold down SHIFT + LMB and then move to pan.
      * Hold down SHIFT + RMB and then move to change the vield of view.
      * Hold down CONTROL + LMB and then move to rotate the whole scene
        around the axis of the camera.
    
    """
    
    _NAMES = ('3d', 3, '3', 'threed')
    ndim = 3
    _viewparams = BaseCamera._viewparams + ('azimuth', 'elevation', 'roll', 'fov')
    
    def __init__(self):
        BaseCamera.__init__(self)
        
        # camera view params
        self._view_az = -10.0 # azimuth
        self._view_el = 30.0 # elevation
        self._view_ro = 0.0 # roll
        self._fov = 0.0 # field of view - if 0, use ortho view
        
        # reference variables for when dragging
        self._ref_loc = 0,0,0    # view_loc when clicked
        self._ref_mloc = 0,0     # mouse location when clicked
        self._ref_but = 0        # mouse button clicked
        self._ref_axes = None
        #
        self._ref_az = 0         # angles when clicked
        self._ref_el = 0
        self._ref_ro = 0
        #
        self._ref_fov = 0
        self._ref_zoom = 0
        self._ref_daspect = 1,1,1
    
    
    @Property
    def azimuth():
        """ Get/set the current azimuth angle (rotation around z-axis).
        This angle is between -180 and 180 degrees.
        """
        def fget(self):
            return self._view_az
        def fset(self, value):
            # Set
            self._view_az = float(value)
            # keep within bounds
            while self._view_az < -180:
                self._view_az += 360
            while self._view_az >180:
                self._view_az -= 360
            # Draw
            for ax in self.axeses:
                ax.Draw()
        return locals()
    
    @Property
    def elevation():
        """ Get/set the current elevation angle (rotation with respect to
        the x-y plane). This angle is between -90 and 90 degrees.
        """
        def fget(self):
            return self._view_el
        def fset(self, value):
            # Set
            self._view_el = float(value)
            # keep within bounds
            if self._view_el < -90:
                self._view_el = -90
            if self._view_el > 90:
                self._view_el = 90
            # Draw
            for ax in self.axeses:
                ax.Draw()
        return locals()
    
    @Property
    def roll():
        """ Get/set the current roll angle (rotation around the camera's
        viewing axis). This angle is between -90 and 90 degrees.
        """
        def fget(self):
            return self._view_ro
        def fset(self, value):
            # Set
            self._view_ro = float(value)
            # keep within bounds
            if self._view_ro < -90:
                self._view_ro = -90
            if self._view_ro > 90:
                self._view_ro = 90
            # Draw
            for ax in self.axeses:
                ax.Draw()
        return locals()
    
    @Property
    def fov():
        """ Get/set the current field of view (i.e. camera aperture).
        This value is between 0 (orthographic projection) and 180.
        """
        def fget(self):
            return self._fov
        def fset(self, value):
            # Set
            self._fov = float(value)
            # keep within bounds
            if self._fov > 179:
                self._fov = 179
            if self._fov < 0:
                self._fov = 0
            # Draw
            for ax in self.axeses:
                ax.Draw()
        return locals()
    
    
    def OnResize(self, event):
        """ OnResize(event)
        
        Callback that adjusts the daspect (if axes.daspectAuto is True)
        when the window dimensions change.
        
        """
        
        # Get new size factor
        w,h = self.axes.position.size
        sizeFactor1 = float(h) / w
        
        # Get old size factor
        sizeFactor2 = self._windowSizeFactor
        
        # Make it quick if daspect is not in auto-mode
        if not self.axes.daspectAuto:
            self._windowSizeFactor = sizeFactor1
            return
        
        # Get daspect factor
        daspectFactor = sizeFactor1
        if sizeFactor2:
            daspectFactor /= sizeFactor2
        
        # Set size factor for next time
        self._windowSizeFactor = sizeFactor1
        
        # Change daspect. Zoom is never changed
        self._SetDaspect(daspectFactor, 2, 2)
    
    
    def Reset(self, event=None):
        """ Reset()
        
        Reset the view.
        
        """
        
        # Reset daspect from user-given daspect
        if self.axes:
            self._daspect = self.axes._daspect
        
        # Set angles
        self._view_az = -10.0
        self._view_el = 30.0
        self._view_ro = 0.0
        self._fov = 0.0
        
        # Get window size (and store factor now to sync with resizing)
        w,h = self.axes.position.size
        w,h = float(w), float(h)
        self._windowSizeFactor = h / w
        
        # Get range and translation for x and y
        rx, ry, rz = self._xlim.range, self._ylim.range, self._zlim.range
        
        # Correct ranges for window size. Note that the window width
        # influences the x and y data range, while the height influences
        # the z data range.
        if w / h > 1:
            rx /= w/h
            ry /= w/h
        else:
            rz /= h/w
        
        # If auto-scale is on, change daspect, x is the reference
        if self.axes.daspectAuto:
            self._SetDaspect(rx/ry, 1, 0)
            self._SetDaspect(rx/rz, 2, 0)
        
        # Correct for normalized daspect
        ndaspect = self.daspectNormalized
        rx, ry, rz = abs(rx*ndaspect[0]), abs(ry*ndaspect[1]), abs(rz*ndaspect[2])
        
        # Convert to screen coordinates. In screen x, only x and y have effect.
        # In screen y, all three dimensions have effect. The idea of the lines
        # below is to calculate the range on screen when that will fit the
        # data under any rotation.
        rxs = ( rx**2 + ry**2 )**0.5
        rys = ( rx**2 + ry**2 + rz**2 )**0.5
        
        # Set zoom, depending on screen dimensions
        if w / h > 1:
            rxs *= w/h
            self._zoom = (1/rxs) / 1.04  # 4% extra space
        else:
            self._zoom = (1/rys) / 1.08 # 8% extra space
        
        # set center location -> calls refresh
        BaseCamera.Reset(self)
    
    
    def SetRef(self):
        # store current view parameters
        self._ref_az = self._view_az
        self._ref_el = self._view_el
        self._ref_ro = self._view_ro
        self._ref_fov = self._fov
        #
        self._ref_loc = self._view_loc
        #
        self._ref_zoom = self._zoom
        self._ref_daspect = self.daspect
    
    
    def OnKeyDown(self, event):
        # store mouse position and button
        self._ref_mloc = event.owner.mousepos
        self.SetRef()

    def OnKeyUp(self, event):
        self._ref_mloc = event.owner.mousepos
        self.SetRef()
    
    
    def OnMouseDown(self, event):
        
        # store mouse position and button
        self._ref_mloc = event.x, event.y
        self._ref_but = event.button
        self._ref_axes = event.owner
        
        self.SetRef()

   
    def OnMouseUp(self, event):
        self._ref_but = 0
        for axes in self.axeses:
            axes.Draw()

    
    def OnMotion(self, event):
        
        if not self._ref_but:
            return
        if self._ref_axes is not event.owner:
            return
        if self.axes.camera is not self:
            return False
        
        # get loc (as the event comes from the figure, not the axes)
        mloc = event.owner.mousepos
            
        if constants.KEY_SHIFT in event.modifiers and self._ref_but==1:
            # translate
            
            # get locations and convert to world coordinates
            refloc = self.ScreenToWorld(self._ref_mloc)
            loc = self.ScreenToWorld(mloc)
            
            # calculate distance and undo aspect ratio adjustment from ScreenToWorld
            ar = self.daspect
            distx = (refloc[0] - loc[0]) * ar[0]
            distz = (refloc[1]-loc[1]) * ar[1]
            
            # calculate translation
            sro, saz, sel = list(map(sind, (self._view_ro, self._view_az, self._view_el)))
            cro, caz, cel = list(map(cosd, (self._view_ro, self._view_az, self._view_el)))
            dx = (  distx * (cro * caz + sro * sel * saz) +
                    distz * (sro * caz - cro * sel * saz) ) / ar[0]
            dy = (  distx * (cro * saz - sro * sel * caz) +
                    distz * (sro * saz + cro * sel * caz) ) / ar[1]
            dz = ( -distx * sro * cel + distz * cro * cel) / ar[2]
            
            # apply
            self._view_loc = (  self._ref_loc[0] + dx,
                                self._ref_loc[1] + dy,
                                self._ref_loc[2] + dz )
        
        elif constants.KEY_CONTROL in event.modifiers and self._ref_but==1:
            # Roll
            
            # get normalized delta values
            sze = self.axes.position.size
            d_ro = float( self._ref_mloc[0] - mloc[0] ) / sze[0]
            
            # change az and el accordingly
            self._view_ro = self._ref_ro + d_ro * 90.0
            
            # keep within bounds
            if self._view_ro < -90:
                self._view_ro = -90
            if self._view_ro > 90:
                self._view_ro = 90
        
        elif self._ref_but==1:
            # rotate
            
            # get normalized delta values
            sze = self.axes.position.size
            d_az = float( self._ref_mloc[0] - mloc[0] ) / sze[0]
            d_el = -float( self._ref_mloc[1] - mloc[1] ) / sze[1]
            
            # change az and el accordingly
            self._view_az = self._ref_az + d_az * 90.0
            self._view_el = self._ref_el + d_el * 90.0
            
            # keep within bounds
            while self._view_az < -180:
                self._view_az += 360
            while self._view_az >180:
                self._view_az -= 360
            if self._view_el < -90:
                self._view_el = -90
            if self._view_el > 90:
                self._view_el = 90
            #print(self._view_az, self._view_el)
        
        elif constants.KEY_SHIFT in event.modifiers and self._ref_but==2:
            # Change FoV
            
            # get normailized delta value
            d_fov = float(self._ref_mloc[1] - mloc[1]) / self.axes.position.height
            
            # apply
            self._fov = self._ref_fov + d_fov * 90
            
            # keep from being too big or negative
            if self._fov > 179:
                self._fov = 179
            elif self._fov < 0:
                self._fov = 0
        
        elif self._ref_but==2:
            # zoom
            
            # get movement in x (in pixels) and normalize
            factorx = float(self._ref_mloc[0] - mloc[0])
            factorx /= self.axes.position.width
            
            # get movement in y (in pixels) and normalize
            factory = float(self._ref_mloc[1] - mloc[1])
            factory /= self.axes.position.height
            
            # apply
            if self.axes.daspectAuto:
                # Zooming in x and y goes via daspect.
                # Zooming in z goes via zoom factor.
                
                # Motion to right or top should always zoom in, regardless of rotation
                sro, saz, sel = list(map(sind, (self._view_ro, self._view_az, self._view_el)))
                cro, caz, cel = list(map(cosd, (self._view_ro, self._view_az, self._view_el)))
                dx = ( -factorx * abs(cro * caz + sro * sel * saz) +
                        factory * abs(sro * caz - cro * sel * saz) )
                dy = ( -factorx * abs(cro * saz - sro * sel * caz) +
                        factory * abs(sro * saz + cro * sel * caz) )
                dz =    factorx * abs(sro * cel) + factory * abs(cro * cel)
                
                # Set sata aspect
                daspect = self._ref_daspect
                daspect = self._SetDaspect(math.exp(dy-dx), 1, 1, daspect)
                daspect = self._SetDaspect(math.exp(dz-dx), 2, 2, daspect)
                
                # Set zoom
                self._zoom = self._ref_zoom * math.exp(dx)
            
            else:
                self._zoom = self._ref_zoom * math.exp(factory)
        
        # refresh (fast)
        for axes in self.axeses:
            axes.Draw(True)
    
    
    def SetView(self):
        """ SetView()
        
        Prepare the view for drawing
        This applies the camera model.
        
        """
        
        # Calculate viewing range for x and y
        fx = abs( 1.0 / self._zoom )
        fy = abs( 1.0 / self._zoom )
        
        # Correct for window size
        if True:
            w, h = self.axes.position.size
            w, h = float(w), float(h)
            if w / h > 1:
                fx *= w/h
            else:
                fy *= h/w
        
        # Init projection view
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        
        # Remember, in terms of a global coordinate system,
        # the transformations are done backwards... (See the Red Book ch. 3)
        
        # 4. Define part that we view. Remember, we're looking down the
        # z-axis. We zoom here.
        if self._fov == 0:
            ortho( -0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy)
        else:
            # Figure distance to center in order to have correct FoV and fy.
            d = fy / (2 * math.tan(math.radians(self._fov)/2))
            val = math.sqrt(getDepthValue())
            glu.gluPerspective(self._fov, fx/fy, d/val, d*val)
            gl.glTranslate(0, 0, -d)
        
        # Prepare for models
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # Set camera lights
        for light in self.axes._lights:
            if light.isCamLight:
                light._Apply()
        
        # 3. Set viewing angle (this is the only difference with the 2D camera)
        gl.glRotate(self._view_ro, 0.0, 0.0, 1.0)
        gl.glRotate(270+self._view_el, 1.0, 0.0, 0.0)
        gl.glRotate(-self._view_az, 0.0, 0.0, 1.0)
        
        # 2. Set aspect ratio (scale the whole world), and flip any axis...
        ndaspect = self.daspectNormalized
        gl.glScale( ndaspect[0], ndaspect[1] , ndaspect[2] )
        
        # 1. Translate to view location. Do this first because otherwise
        # the translation is not in world coordinates.
        gl.glTranslate(-self._view_loc[0], -self._view_loc[1], -self._view_loc[2])
        
        # Set non-camera lights
        for light in self.axes._lights:
            if not light.isCamLight:
                light._Apply()
    

class FlyCamera(BaseCamera):
    """ FlyCamera()
    
    The fly camera provides a fun way to visualise 3D data using an
    interaction style that resembles a flight sim.
    
    Think of the fly camera as a remote controlled vessel with
    which you fly trough your data, much like in the classic game 'Descent'.
    
    Interaction
    -----------
    Notice: interacting with this camera might need a bit of practice.
    
    Moving:
      * w,a,s,d keys to move forward, backward, left and right
      * f and c keys move up and down
      * Using SHIFT+RMB, the scale factor can be changed, a lower scale
        means smaller motions (i.e. more fine-grained control).
    
    Viewing:
      * Use the mouse to control the pitch and yaw.
      * Alternatively, the pitch and yaw can be changed using the keys i,k,j,l.
      * The camera auto-rotates to make the bottom of the vessel point down,
        manual rolling can be performed using q and e.
      * Using the RMB, one can zoom in, like looking through binoculars.
        This will also make you move slightly faster.
    
    """
    _NAMES = ('fly', 1) # 1 for first person
    ndim = 3
    _viewparams = BaseCamera._viewparams + ('fov', 'rotation')
    
    def __init__(self):
        BaseCamera.__init__(self)
        
        # Here, view_loc is not the position you look at,
        # but the position you ARE at
        
        # Note that the zoom factor is the measure for scale, and the fov
        # is used for zooming.
        
        self._rotation1 = Quaternion() # The total totation
        self._rotation2 = Quaternion() # The delta yaw and pitch rotation
        
        # Set field of view: how zoomed in the view is
        self._fov = 90
        speed_angle = 0.5*self._fov*math.pi/180
        self._speed_rot = math.sin(speed_angle)
        self._speed_trans = math.cos(speed_angle)
        
        # Acceleration (by key press)
        # 2 means pressed, 1 means depressed, if 1 set to 0 in OnTimer().
        # That way, even a small tap always results in some motion.
        # Negative values for opposite directions.
        self._acc_forward = 0
        self._acc_right = 0
        self._acc_up = 0
        #
        self._acc_roll = 0
        self._acc_pitch = 0
        self._acc_yaw = 0
        
        # Motion speed in each direction.
        self._speed_forward = 0
        self._speed_right = 0
        self._speed_up = 0
        #
        self._speed_roll = 0
        self._speed_pitch = 0
        self._speed_yaw = 0
        
        # reference variables for when dragging
        self._ref_loc = 0,0,0    # view_loc when clicked
        self._ref_mloc = 0,0     # mouse location when clicked
        self._ref_but = 0        # mouse button clicked
        self._ref_axes = None
        #
        self._ref_fov = 0
        self._ref_zoom = 0
        
        # Key mapping for conrolling the camera
        self._keymap = {    'w':+1, 's':-1, 'd':+2, 'a':-2, 'f':+3, 'c':-3,
                            'i':-4, 'k':+4, 'l':+5, 'j':-5, 'q':+6, 'e':-6}
        # Make event.text -> event.key
        for k in [k for k in self._keymap]:
            if isinstance(k, basestring) and len(k)==1:
                self._keymap[ord(k)] = self._keymap[k]
                del self._keymap[k]
        
        # create timer and bind to it. This timer is started when clicked
        # and stopped when the mouse is released. This is to make a
        # smoother flying possible. 20 fps
        self._timer = vv.Timer(self, 50, False)
        self._timer.Bind(self.OnTimer)
    
        
    @Property
    def fov():
        """ Get/set the current field of view (i.e. camera aperture).
        This value is between 10 and 90.
        """
        def fget(self):
            return self._fov
        def fset(self, value):
            # Set
            self._fov = float(value)
            # keep within bounds
            if self._fov > 90:
                self._fov = 90
            if self._fov < 10:
                self._fov = 10
            # Draw
            for ax in self.axeses:
                ax.Draw()
        return locals()
    
    
    @Property
    def rotation():
        """ Get/set the current rotation quaternion.
        """
        def fget(self):
            return self._rotation1.copy()
        def fset(self, value):
            # Set
            self._rotation1 = value.normalize()
            # Draw
            for ax in self.axeses:
                ax.Draw()
        return locals()
    
    
    @property
    def _rotation(self):
        """ Get the full rotation for internal use. This rotation is composed
        of the normal rotation plus the extra rotation due to the current
        interaction of the user.
        """
        rotation = self._rotation2 * self._rotation1
        return rotation.normalize()
    
    
    def Reset(self, event=None):
        """ Reset()
        
        Reset the view.
        
        """
        # Reset daspect from user-given daspect
        if self.axes:
            self._daspect = self.axes._daspect
        
        # Stop moving
        self._acc_forward = 0
        self._acc_right = 0
        self._acc_up = 0
        #
        self._acc_pitch = 0
        self._acc_yaw = 0
        self._acc_roll = 0
        #
        self._speed_forward = 0
        self._speed_right = 0
        self._speed_up = 0
        #
        self._speed_pitch = 0
        self._speed_yaw = 0
        self._speed_roll = 0
        
        # Set orientation
        q_ro = Quaternion.create_from_axis_angle(200*math.pi/180, 0,0,1)
        q_az = Quaternion.create_from_axis_angle(130*math.pi/180, 0,1,0)
        q_el = Quaternion.create_from_axis_angle(120*math.pi/180, 1,0,0)
        #
        self._rotation1 = ( q_ro * q_az * q_el).normalize()
        self._rotation2 = Quaternion()
        self._fov = 90.0
        speed_angle = 0.5*self._fov*math.pi/180
        self._speed_rot = math.sin(speed_angle)
        self._speed_trans = math.cos(speed_angle)
        
        # Get window size (and store factor now to sync with resizing)
        w,h = self.axes.position.size
        w,h = float(w), float(h)
        self._windowSizeFactor = h / w
        
        # Get range and translation for x and y
        rx, ry, rz = self._xlim.range, self._ylim.range, self._zlim.range
        
        # Correct ranges for window size. Note that the window width
        # influences the x and y data range, while the height influences
        # the z data range.
        if w / h > 1:
            rx /= w/h
            ry /= w/h
        else:
            rz /= h/w
        
        # If auto-scale is on, change daspect, x is the reference
        if self.axes.daspectAuto:
            self._SetDaspect(rx/ry, 1, 0)
            self._SetDaspect(rx/rz, 2, 0)
        
        # Correct for normalized daspect
        ndaspect = self.daspectNormalized
        rx, ry, rz = abs(rx*ndaspect[0]), abs(ry*ndaspect[1]), abs(rz*ndaspect[2])
        
        # Do not convert to screen coordinates. This camera does not need
        # to fit everything on screen, but we need to estimate the scale
        # of the data in the scene.
        
        # Set zoom, depending on data range
        self._zoom = min(1/rx, 1/ry, 1/rz)
        
        # Set initial position to a corner of the scene
        dx,dy,dz = self._xlim.min, self._ylim.min, self._zlim.max
        #dd = (rx**2 + ry**2 + rz**2 )**0.5
        self._view_loc = dx, dy, dz
        
        # Refreshw
        for axes in self.axeses:
            axes.Draw()
    
    
    def OnKeyDown(self, event):
        
        if self.axes.camera is not self:
            return
        elif not self._timer.isRunning:
            # Make sure the timer runs
            self._timer.Start()
        
        # Only listen to plain keys.
        if event.modifiers:
            return False
        
        # Get action (or None)
        action = self._keymap.get(event.key, None)
        
        # Decide
        if not action:
            return False
        # Translation in-plane
        elif abs(action) == 1:
            self._acc_forward = 2 * cmp(action,0)
        elif abs(action) == 2:
            self._acc_right = 2 * cmp(action,0)
        elif abs(action) == 3:
            self._acc_up = 2 * cmp(action,0)
        # Rotation
        elif abs(action) == 4:
            self._acc_pitch = 2 * cmp(action,0)
        elif abs(action) == 5:
            self._acc_yaw = 2 * cmp(action,0)
        elif abs(action) == 6:
            self._acc_roll = 2 * cmp(action,0)
    
    
    def OnKeyUp(self, event):
        
        if self.axes.camera is not self:
            return
        
        # Get action (or None)
        action = self._keymap.get(event.key, None)
        
        # Decide
        if not action:
            return False
        # Translation in-plane
        elif abs(action) == 1:
            self._acc_forward = 1 * cmp(action,0)
        elif abs(action) == 2:
            self._acc_right = 1 * cmp(action,0)
        elif abs(action) == 3:
            self._acc_up = 1 * cmp(action,0)
        # Rotation
        elif abs(action) == 4:
            self._acc_pitch = 1 * cmp(action,0)
        elif abs(action) == 5:
            self._acc_yaw = 1 * cmp(action,0)
        elif abs(action) == 6:
            self._acc_roll = 1 * cmp(action,0)
    
    
    def OnMouseDown(self, event):
        
        # store mouse position and button
        self._ref_mloc = event.x, event.y
        self._ref_but = event.button
        self._ref_axes = event.owner
        
        # store current view parameters
        self._ref_loc = self._view_loc
        self._ref_zoom = self._zoom
        self._ref_fov = self._fov
    
    
    def OnMouseUp(self, event):
        
        # Apply rotation
        self._rotation1 = ( self._rotation2 * self._rotation1 ).normalize()
        self._rotation2 = Quaternion()
        
        # Set not-motion
        self._ref_but = 0
        for axes in self.axeses:
            axes.Draw()
    
    
    def OnMotion(self, event):
       
        if self.axes.camera is not self:
            return
        elif not self._timer.isRunning:
            # Make sure the timer runs
            self._timer.Start()
        
        if not self._ref_but:
            return
        if self._ref_axes is not event.owner:
            return
        
        
        # get loc (as the event comes from the figure, not the axes)
        mloc = self.axes.mousepos
        
        if self._ref_but==1:
            # rotate
            
            # get normalized delta values
            sze = self.axes.position.size
            d_az = float( self._ref_mloc[0] - mloc[0] ) / sze[0]
            d_el = -float( self._ref_mloc[1] - mloc[1] ) / sze[1]
            
            # Apply gain
            d_az *= - 0.5 * math.pi# * self._speed_rot
            d_el *=   0.5 * math.pi#  * self._speed_rot
            
            # Create temporary quaternions
            q_az = Quaternion.create_from_axis_angle(d_az, 0,1,0)
            q_el = Quaternion.create_from_axis_angle(d_el, 1,0,0)
            
            # Apply to global quaternion
            self._rotation2 = ( q_el.normalize() * q_az ).normalize()
        
        elif not event.modifiers and self._ref_but==2:
            # zoom --> fov
            
            # get normailized delta value
            d_fov = float(self._ref_mloc[1] - mloc[1]) / self.axes.position.height
            
            # apply
            self._fov = self._ref_fov - d_fov * 90
            
            # keep from being too big or negative
            if self._fov > 90:
                self._fov = 90 # fully "zoomed out"
            elif self._fov < 10:
                self._fov = 10 # fully "zoomed in"
            
            # Determine relative speed
            speed_angle = 0.5*self._fov*math.pi/180
            self._speed_rot = math.sin(speed_angle)
            self._speed_trans = math.cos(speed_angle)
            
        elif constants.KEY_SHIFT in event.modifiers and self._ref_but==2:
            # scale / relative speed --> zoom
            
            # get movement in x (in pixels) and normalize
            factorx = float(self._ref_mloc[0] - mloc[0])
            factorx /= self.axes.position.width
            
            # get movement in y (in pixels) and normalize
            factory = float(self._ref_mloc[1] - mloc[1])
            factory /= self.axes.position.height
            
            # apply
            self._zoom = self._ref_zoom * math.exp(factory)
        
        
        # Refresh
        for axes in self.axeses:
            axes.Draw(True)
    
    
    def _GetDirections(self):
        # Get reference points in reference coordinates
        #p0 = Point(0,0,0)
        pf = Point(0,0,-1) # front
        pr = Point(1,0,0)  # right
        pl = Point(-1,0,0)  # left
        pu = Point(0,1,0)  # up
        
        # Get total rotation
        rotation = self._rotation.inverse()
        
        # Transform to real coordinates
        pf = rotation.rotate_point(pf).normalize()
        pr = rotation.rotate_point(pr).normalize()
        pl = rotation.rotate_point(pl).normalize()
        pu = rotation.rotate_point(pu).normalize()
        
        return pf, pr, pl, pu
    
    
    def OnTimer(self, event):
        
        # Stop running?
        if self.axes.camera is not self:
            self._timer.Stop()
            return
        
        # Get direction vectors for forwatd, right, left, and up
        pf, pr, pl, pu = self._GetDirections()
        
        # Initial relative speed
        rel_speed = 0.02
        
        # Create speed vectors, use zoom to scale
        # Create the space in 100 "units"
        ndaspect = self.daspectNormalized
        dv = Point([1.0/d for d in ndaspect])
        #
        vf = pf * dv * rel_speed * self._speed_trans / self._zoom
        vr = pr * dv * rel_speed * self._speed_trans / self._zoom
        vu = pu * dv * rel_speed * self._speed_trans / self._zoom
        
        
        # Determine speed from acceleration
        if True:
            acc = 0.2
            #
            if self._acc_forward > 0:       self._speed_forward += acc
            elif self._speed_forward > 0:   self._speed_forward -= acc * 0.5
            if self._acc_forward < 0:       self._speed_forward -= acc
            elif self._speed_forward < 0:   self._speed_forward += acc * 0.5
            #
            if self._acc_right > 0:       self._speed_right += acc
            elif self._speed_right > 0:   self._speed_right -= acc * 0.5
            if self._acc_right < 0:       self._speed_right -= acc
            elif self._speed_right < 0:   self._speed_right += acc * 0.5
            #
            if self._acc_up > 0:       self._speed_up += acc
            elif self._speed_up > 0:   self._speed_up -= acc * 0.5
            if self._acc_up < 0:       self._speed_up -= acc
            elif self._speed_up < 0:   self._speed_up += acc * 0.5
            #
            if self._acc_pitch > 0:       self._speed_pitch += acc
            elif self._speed_pitch > 0:   self._speed_pitch -= acc * 0.5
            if self._acc_pitch < 0:       self._speed_pitch -= acc
            elif self._speed_pitch < 0:   self._speed_pitch += acc * 0.5
            #
            if self._acc_yaw > 0:       self._speed_yaw += acc
            elif self._speed_yaw > 0:   self._speed_yaw -= acc * 0.5
            if self._acc_yaw < 0:       self._speed_yaw -= acc
            elif self._speed_yaw < 0:   self._speed_yaw += acc * 0.5
            #
            if self._acc_roll > 0:       self._speed_roll += acc
            elif self._speed_roll > 0:   self._speed_roll -= acc * 0.5
            if self._acc_roll < 0:       self._speed_roll -= acc
            elif self._speed_roll < 0:   self._speed_roll += acc * 0.5
            
            # Set speed to 0 in a reliable way (no accumulating round errors)
            if abs(self._speed_forward) < acc: self._speed_forward = 0
            if abs(self._speed_right) < acc: self._speed_right = 0
            if abs(self._speed_up) < acc: self._speed_up = 0
            if abs(self._speed_pitch) < acc: self._speed_pitch = 0
            if abs(self._speed_yaw) < acc: self._speed_yaw = 0
            if abs(self._speed_roll) < acc: self._speed_roll = 0
            
            # Limit speed
            self._speed_forward = min(1.2, max(-1.2, self._speed_forward))
            self._speed_right = min(1.0, max(-1.0, self._speed_right))
            self._speed_up = min(1.0, max(-1.0, self._speed_up))
            self._speed_pitch = min(1.0, max(-1.0, self._speed_pitch))
            self._speed_yaw = min(1.0, max(-1.0, self._speed_yaw))
            self._speed_roll = min(1.0, max(-1.0, self._speed_roll))
        
        
        # Disable accelerations?
        if True:
            if abs(self._acc_forward) == 1: self._acc_forward = 0
            if abs(self._acc_right) == 1: self._acc_right = 0
            if abs(self._acc_up) == 1: self._acc_up = 0
            if abs(self._acc_pitch) == 1: self._acc_pitch = 0
            if abs(self._acc_yaw) == 1: self._acc_yaw = 0
            if abs(self._acc_roll) == 1: self._acc_roll = 0
        
        
        # Determine new position from translation speed
        if True:
            pos = Point(self._view_loc)
            #
            if self._speed_forward:
                pos =  pos + self._speed_forward * vf
            if self._speed_right:
                pos = pos + self._speed_right * vr
            if self._speed_up:
                pos = pos + self._speed_up * vu
            # Apply position
            self._view_loc = (pos.x, pos.y, pos.z)
        
        # Determine new orientation from rotation speed
        if True:
            angleGain = 3 * math.pi/180
            if self._speed_pitch:
                angle = self._speed_pitch * angleGain
                q = Quaternion.create_from_axis_angle(angle, -1,0,0)
                self._rotation1 = ( q * self._rotation1 ).normalize()
            if self._speed_yaw:
                angle = 1.5 * self._speed_yaw * angleGain
                q = Quaternion.create_from_axis_angle(angle, 0,1,0)
                self._rotation1 = ( q * self._rotation1 ).normalize()
            if self._speed_roll:
                # Manual roll
                angle = self._speed_roll * angleGain
                q = Quaternion.create_from_axis_angle(angle, 0,0,-1)
                self._rotation1 = ( q * self._rotation1 ).normalize()
            else:
                # Calculate auto-roll
                #au = pu.angle(Point(0,0,1))
                ar = pr.angle(Point(0,0,1))
                al = pl.angle(Point(0,0,1))
                af = pf.angle(Point(0,0,1))
                #
                magnitude =  abs(math.sin(af)) # abs(math.sin(au))
                magnitude *= math.sin(0.5*(al - ar))
                if abs(magnitude) < 0.01:
                    magnitude = 0
                #
                angle = 10 * magnitude * math.pi/180
                q = Quaternion.create_from_axis_angle(angle, 0,0,1)
                self._rotation1 = ( q * self._rotation1 ).normalize()
        
        # Break if there is no motion
        if not (self._speed_forward or self._speed_right or self._speed_up
                or self._speed_pitch or self._speed_yaw or self._speed_roll
                or magnitude):
            return
        
        # Refresh
        for axes in self.axeses:
            axes.Draw(True)
    
    
    def SetView(self):
        """ SetView()
        
        Prepare the view for drawing
        This applies the camera model.
        
        """
        # Note that this method is almost identical to the 3D
        # camera's implementation. The only difference is that
        # this implementation uses gluPerspective rather than
        # glOrtho, and some signs for the angles are changed.
        
        # Calculate viewing range for x and y
        fx = abs( 1.0 / self._zoom )
        fy = abs( 1.0 / self._zoom )
        
        # Correct for window size
        if True:
            w, h = self.axes.position.size
            w, h = float(w), float(h)
            if w / h > 1:
                fx *= w/h
            else:
                fy *= h/w
        
        # Init projection view. It will define the whole camera model,
        # so the modelview matrix is really for models only.
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        
        # Remember, in terms of a global coordinate system,
        # the transformations are done backwards... (See the Red Book ch. 3)
        
        # 4. Define part that we view. Remember, we're looking down the
        # z-axis. We zoom here.
        # Figure distance to center in order to have correct FoV and fy.
        d = fy / (2 * math.tan(math.radians(self._fov)/2))
        val = math.sqrt(getDepthValue())
        glu.gluPerspective(self._fov, fx/fy, d/val, d*val)
        #ortho( -0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy)
        
        # Prepare for models
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # Set camera lights
        for light in self.axes._lights:
            if light.isCamLight:
                light._Apply()
        
        # 3. Set viewing angle from the quaternion
        # This bit needs to be in the Modelview matrix so that the light
        # is from the camera; in the 3D camera, we move the scene, here
        # we move the camera.
        axis_angle = self._rotation.get_axis_angle()
        angle = axis_angle[0]*180/math.pi
        gl.glRotate(angle, *axis_angle[1:])
        
        # 2. Set aspect ratio (scale the whole world), and flip any axis...
        ndaspect = self.daspectNormalized
        gl.glScale( ndaspect[0], ndaspect[1] , ndaspect[2] )
        
        # 1. Translate to view location. Do this first because otherwise
        # the translation is not in world coordinates.
        gl.glTranslate(-self._view_loc[0], -self._view_loc[1], -self._view_loc[2])
        
        # Set non-camera lights
        for light in self.axes._lights:
            if not light.isCamLight:
                light._Apply()
