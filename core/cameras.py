# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
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

from visvis.core.misc import Property, PropWithDraw, DrawAfter 
from visvis.core.misc import Range
from visvis.core.events import Timer
import constants


# Global to store depth Bits
depthBits = [0]
# Trig functions in degrees
sind = lambda q: math.sin(q*math.pi/180)
cosd = lambda q: math.cos(q*math.pi/180)

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
    """ BaseCamera(*axes)
    
    Abstract camera class. A camera represents both the camera model
    and the interaction style.
    
    """
    _NAMES = ()
    
    # Subclasses should set viewparams, a set of (key, attribute_name) pairs
    # for the values returned by GetViewParams.
    viewparams = (('daspect', 'daspect'), ('loc', 'location'), ('zoom', 'zoom'))
    
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
        axes.eventDoubleClick.Bind(self.Reset)
    
    
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
        axes.eventDoubleClick.Unbind(self.Reset)
    
    
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
        """ This property mirrors the daspect property of the first axes. 
        Setting this propery will set the daspect of all axeses.
        """
        def fget(self):
            if self.axes:
                return self.axes.daspect
            else:
                return None
        def fset(self, value):
            for ax in self.axeses:
                ax.daspect = value # ax.daspect posts a draw
    
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
    
    @Property
    def location():
        """ Get/set the current viewing location.
        """
        def fget(self):
            return tuple(self._view_loc)
        def fset(self, value):
            # Check
            if isinstance(value, (tuple, list)) and len(value)==3:
                value = [float(v) for v in value]
            else:
                raise ValueError('location must be a 3-element tuple.')
            # Set
            self._view_loc = tuple(value)
            for ax in self.axeses:
                ax.Draw()
    
    
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
        return dict([(key, getattr(self, attr)) 
                     for key, attr in self.__class__.viewparams])
    
    def SetViewParams(self, s=None, **kw):
        """ SetViewParams(s=None, **kw)
        
        Set the view, given a dictionary with view parameters.  View parameters
        may also be passed as keyword/value pairs; these will supersede the same
        keys in s.
        
        """
        if s is None:
            s = {}
        if kw:  # Updating with an empty dict is okay, but this way we can take
                # arguments that don't have an update method (like ssdf objects).
            s.update(kw)
        for key, attr in self.__class__.viewparams:
            try:
                setattr(self, attr, s[key])
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
        daspect = self.axes.daspectNormalized
        x, y = x / daspect[0], y / daspect[1]
        
        # translate it
        x, y = x + self._view_loc[0], y + self._view_loc[1]
        
        #print x, y
        return x,y
    
    
    def _SetDaspect(self, ratio, i, j, refDaspect=None):
        """ _SetDaspect(ratio,  i, j, refDaspect=None)
        
        Change the value of the given refDaspect (or use axes.daspect)
        and set that as the new daspect. The new daspect is also returned.
        
        Sets daspect[i] to daspect[j] * ratio, but preserves the sign
        of the original reference daspect.
        
        Will change the daspect of all registered axeses that have this 
        camera as their current camera.
        
        """
        
        # Check if we are allowed to change the daspect
        if self is not self.axes.camera:
            return refDaspect
        
        # Make sure that the ratio is absolute        
        ratio = abs(ratio)
        
        # Get daspect from reference daspect
        if refDaspect is None:
            refDaspect = self.axes.daspect
        
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
        
        # Set for all axes for which this is the camera
        for a in self.axeses:
            if a.camera is self:
                a.daspect = tuple(daspect2)
        
        # Done
        return daspect2


class TwoDCamera(BaseCamera):
    """ TwoDCamera(*axes)
    
    The default camera for viewing 2D data. 
    
    This camera uses orthografic projection and basically looks
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
        
        # Get window size
        w,h = self.axes.position.size
        w,h = float(w), float(h)
        
        # Get range and translation for x and y   
        rx, ry = self._xlim.range, self._ylim.range
        
        # Correct ranges for window size.
        if w / h > 1:
            rx /= w/h
        else:
            ry /= h/w
        
        # If auto-scale is on, change daspect, x is the reference
        if self.axes.daspectAuto:
            daspect = self._SetDaspect(rx/ry, 1, 0)
        
        # Correct for normalized daspect
        ndaspect = self.axes.daspectNormalized
        rx, ry = abs(rx*ndaspect[0]), abs(ry*ndaspect[1])
        
        # Convert to screen coordinates. (just for clarity and to be 
        # consistent with the 3D camera)
        rxs = rx
        rys = ry
        
        # Set zoom
        self._zoom = min(1.0/rxs, 1.0/rys)
        
        # Set center location -> calls refresh
        BaseCamera.Reset(self)
    
    
    def OnMouseDown(self, event): 
        
        # store mouse position and button
        self._ref_mloc = event.x, event.y
        self._ref_but = event.button
        self._ref_axes = event.owner
        
        # store current view parameters        
        self._ref_loc = self._view_loc
        self._ref_zoom = self._zoom
        self._ref_daspect = self.axes.daspect
        
        #self.ScreenToWorld() # for debugging


    def OnMouseUp(self, event):
        self._ref_but = 0
        # Draw without the fast flag      
        for axes in self.axeses:
            axes.Draw()


    def OnMotion(self, event):
        
        if not self._ref_but:
            return
        if not self._ref_axes is event.owner:
            return
        if not self.axes.camera is self:
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
            self._view_loc = ( self._ref_loc[0] - dx ,  self._ref_loc[1] - dy )
        
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
        
        # 2. Set aspect ratio (scale the whole world), and flip any axis...
        ndaspect = self.axes.daspectNormalized
        gl.glScale( ndaspect[0], ndaspect[1], ndaspect[2] )
        
        # 1. Translate to view location (coordinate where we look at). 
        # Do this first because otherwise the translation is not in world 
        # coordinates.
        gl.glTranslate(-self._view_loc[0], -self._view_loc[1], 0.0)


# todo: FOV: properly setting which axis has ticks, the tick spacing, and which axes to show when showBox is False.

class ThreeDCamera(BaseCamera):
    """ ThreeDCamera(*axes)
    
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
    viewparams = BaseCamera.viewparams + (('azimuth', 'azimuth'), 
                  ('elevation', 'elevation'), ('roll', 'roll'), ('fov', 'fov'))
    
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
        
        # Set angles
        self._view_az = -10.0
        self._view_el = 30.0
        self._view_ro = 0.0 
        self._fov = 0.0
        
        # Get window size
        w,h = self.axes.position.size
        w,h = float(w), float(h)
        
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
        ndaspect = self.axes.daspectNormalized
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
        self._ref_daspect = self.axes.daspect
    
    
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
        if not self._ref_axes is event.owner:
            return
        if not self.axes.camera is self:
            return False
        
        # get loc (as the event comes from the figure, not the axes)
        mloc = event.owner.mousepos
            
        if constants.KEY_SHIFT in event.modifiers and self._ref_but==1:
            # translate
            
            # get locations and convert to world coordinates
            refloc = self.ScreenToWorld(self._ref_mloc)
            loc = self.ScreenToWorld(mloc)
            
            # calculate distance and undo aspect ratio adjustment from ScreenToWorld
            ar = self.axes.daspect
            distx = (refloc[0] - loc[0]) * ar[0]
            distz = (refloc[1]-loc[1]) * ar[1]
            
            # calculate translation
            sro, saz, sel = map(sind, (self._view_ro, self._view_az, self._view_el))
            cro, caz, cel = map(cosd, (self._view_ro, self._view_az, self._view_el))
            dx = (  distx * (cro * caz + sro * sel * saz) + 
                    distz * (sro * caz - cro * sel * saz) ) / ar[0]
            dy = (  distx * (cro * saz - sro * sel * caz) + 
                    distz * (sro * saz + cro * sel * caz) ) / ar[1]
            dz = ( -distx * sro * cel + distz * cro * cel) / ar[2]
            
            # apply
            self._view_loc = ( self._ref_loc[0] + dx ,  self._ref_loc[1] + dy , 
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
            #print self._view_az, self._view_el
        
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
                sro, saz, sel = map(sind, (self._view_ro, self._view_az, self._view_el))
                cro, caz, cel = map(cosd, (self._view_ro, self._view_az, self._view_el))
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
        ndaspect = self.axes.daspectNormalized    
        gl.glScale( ndaspect[0], ndaspect[1] , ndaspect[2] )
        
        # 1. Translate to view location. Do this first because otherwise
        # the translation is not in world coordinates.
        gl.glTranslate(-self._view_loc[0], -self._view_loc[1], -self._view_loc[2])
        
        # Set non-camera lights
        for light in self.axes._lights:
            if not light.isCamLight:
                light._Apply()
    

# todo: use quaternions to fly it?
# todo: better init
class FlyCamera(ThreeDCamera):
    """ FlyCamera(*axes)
    
    The fly camera is a funky camera to visualise 3D data.
    
    Think of the fly camera as a remote controlled vessel with
    which you fly trough your data, a bit like a flight sim.
    It uses a perspective projection, by zooming you can change
    your "lens" from very wide to zoom.
    
    Interacting with this camera might need a bit of practice. While 
    holding the mouse the camera is controllable. Now you can rotate 
    the camera, zoom, and fly! Pressing W increases the forward speed, 
    S reduces it. A increases the strafing speed to the left, and D to 
    the right...
    
    """
    
    _NAMES = ('fly', 4)
    ndim = 3
    
    # Note that this camera does not use the MouseMove event but uses
    # a timer to update itself, this is to get the motion smooth.
    
    def __init__(self):
        ThreeDCamera.__init__(self)
        
        # camera view params
        # view_loc is not the position you look at,
        # but the position you ARE at
        self._view_az = 10.0
        self._view_el = 30.0
        self._view_zoomx = 100.0
        self._view_zoomy = 100.0
        
        # reference variables for when dragging
        self._ref_loc = 0,0      # view_loc when clicked
        self._ref_mloc = 0,0     # mouse location clicked
        self._ref_but = 0        # button clicked
        self._ref_speed1 = 0     # direction forward
        self._ref_speed2 = 0     # direction rigth        
        self._ref_az = 0         # angles when clicked
        self._ref_el = 0
        self._ref_zoomx = 0      # zoom factors when clicked
        self._ref_zoomy = 0
        
        # create timer and bind to it. This timer is started when clicked
        # and stopped when the mouse is released. This is to make a 
        # smoother flying possible.
        self._timer = Timer(self, 50, False)
        self._timer.Bind(self.OnTimer)


    def Reset(self, event=None):
        """ Reset()
        
        Position the camera at a suitable position from the scene.
        
        """
        
        # Only reset if this is currently the camera
        #if self.axes.camera is not self:
        #    return
        
        # call the 3D camera reset... It calls Draw(), which is thus called
        # unnecesary, but hell, you dont reset that often...
        ThreeDCamera.Reset(self)
        
        # get aspect ratio
        ar = self.axes.daspect
        
        # change centre, we move at the minimum x and y, but at a higher z.
        rx,ry,rz = self._xlim.range, self._ylim.range, self._zlim.range
        dx,dy,dz = self._xlim.min, self._ylim.min, self._zlim.min        
        dd = (rx**2 + ry**2 + rz**2 )**0.5        
        dd *= ar[2]
        #self._view_loc = rx/2.0+dx+500, ry/2.0+dy+500, rz/2.0/rz-dd
        self._view_loc = dx, dy, dz + rz/2.0 + dd
        
        # set angles        
        self._view_az = -math.atan2(ar[0],ar[1])*180/math.pi
        self._view_el = 80 # look down
        
        # refresh
        for axes in self.axeses:
            axes.Draw()
        
        
    def OnKeyDown(self, event):
        # Detect whether the used wants to set things in motion.
        if event.text == 'w':
            self._ref_speed1 += 1
        elif event.text == 's':
            self._ref_speed1 -= 1
        elif event.text == 'd':
            self._ref_speed2 += 1
        elif event.text == 'a':
            self._ref_speed2 -= 1
   
     
    def Move(self, event=None):
        # Move the fly -> change its position.
        
        # get aspect ratio, we need to normalize with it...
        ar = self.axes.daspect
        # calculate distance to travel            
        rx,ry,rz = self._xlim.range, self._ylim.range, self._zlim.range
        distance = dd = (rx**2 + ry**2 + rz**2 )**0.5/200.0
        # express angles in radians
        rad_az = self._view_az * math.pi / 180.0
        rad_el = self._view_el * math.pi / 180.0
        
        # init
        dx=dy=dz = 0.0
        sp1, sp2 = self._ref_speed1, self._ref_speed2
        
        if sp1:
            f = math.cos( -rad_el )
            dx += sp1 * distance * math.sin( -rad_az ) * f / ar[0]
            dy += sp1 * distance * math.cos( -rad_az ) * f / ar[1] 
            dz += sp1 * distance * math.sin( -rad_el ) / ar[2]
        if sp2:
            dx +=   sp2 * distance * math.cos( -rad_az ) / ar[0]
            dy += - sp2 * distance * math.sin( -rad_az ) / ar[1] 
        
        # update location
        self._view_loc = ( self._view_loc[0] + dx ,  self._view_loc[1] + dy , 
            self._view_loc[2] + dz )
        
        # refresh is performed by the caller
        
    
    
    def OnMouseDown(self, event):
        
        # store mouse position and button
        self._ref_mloc = event.x, event.y
        self._ref_but = event.button
        self._ref_axes = event.owner
        
        # store current view parameters
        self._ref_az = self._view_az
        self._ref_el = self._view_el
        self._ref_loc = self._view_loc
        self._ref_zoomx = self._view_zoomx 
        self._ref_zoomy = self._view_zoomy 
        
        # start moving!
        self._ref_speed1 = 0
        self._ref_speed2 = 0
        self._timer.Start()
   
    
    def OnMouseUp(self, event):        
        self._ref_but = 0
        for axes in self.axeses:
            axes.Draw()
        self._timer.Stop()
    
    
    def OnTimer(self, event):
       
        if not self._ref_but:
            return
        if not self.axes.camera is self:
            return False
        
        # get loc (as the event comes from the figure, not the axes)
        mloc = self.axes.mousepos
        
        if self._ref_but==1:
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
            #print self._view_az, self._view_el
        
        elif self._ref_but==2:
            # zoom
            
            # get movement in x (in pixels) and normalize
            factorx = float(self._ref_mloc[0] - mloc[0])
            factorx /= self.axes.position.width
            
            # get movement in y (in pixels) and normalize
            factory = float(self._ref_mloc[1] - mloc[1])
            factory /= self.axes.position.height
            
            # apply (use only y-factor if daspect is valid.
            if self.axes.daspectAuto:
                self._view_zoomx = self._ref_zoomx * math.exp(factorx)
                self._view_zoomy = self._ref_zoomy * math.exp(-factory)
            else:
                self._view_zoomy = self._ref_zoomy * math.exp(-factory)
                self._view_zoomx = self._view_zoomy
        
        # Move and refresh
        self.Move()
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
        
        # test zoomfactors
        if not self.axes.daspectAuto:
            if self._view_zoomx != self._view_zoomy:
                # apply average zoom
                tmp = self._view_zoomx + self._view_zoomy
                self._view_zoomx = self._view_zoomy = tmp / 2.0
#         if self._view_zoomx < 2:
#             self._view_zoomx = 2.0
#         if self._view_zoomy < 2:
#             self._view_zoomy = 2.0
        
        # get zoom
        fx, fy = self._view_zoomx, self._view_zoomy
        
        # correct for window size        
        if not self.axes.daspectAuto:
            w, h = self.axes.position.size
            w, h = float(w), float(h)        
            if w / h > 1:#self._ylim.range / self._xlim.range:
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
        glu.gluPerspective(fy/50, fx/fy, 1.0, 100000.0)
        #gl.glOrtho( -0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy,
        #            -100000.0, 100000.0 )
        
        # 3. Set viewing angle (this is the only difference with 2D camera)
        gl.glRotate(self._view_el-90, 1.0, 0.0, 0.0)        
        gl.glRotate(-self._view_az, 0.0, 0.0, 1.0)
        
        # Prepare for models ...
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # 2. Set aspect ratio (scale the whole world), and flip any axis...
        daspect = self.axes.daspect        
        gl.glScale( daspect[0], daspect[1] , daspect[2] )
        
        # 1. Translate to view location. Do this first because otherwise
        # the translation is not in world coordinates.
        gl.glTranslate(-self._view_loc[0], -self._view_loc[1], -self._view_loc[2])


