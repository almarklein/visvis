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
    
    def __init__(self, *axes):
        
        # store scenes to render in
        if len(axes)==1 and isinstance(axes[0], (list,tuple)):
            axes = axes[0]
        self.axeses = axes
        
        # flag for axis
        self.isTwoD = False
        
        # init limits of what to visualize        
        self.xlim = Range(0,1)
        self.ylim = Range(0,1)
        self.zlim = Range(0,1)
        self.view_loc = 0,0,0
        self.OnInit()
    
    @property
    def axes(self):
        """ Get the axes that this camera applies to (or the first axes if
        it applies to multiple axes).
        """
        return self.axeses[0]
    
    def OnInit(self):
        """ OnInit()
        
        Override this to do more initializing.
        
        """
        pass
    
    def SetLimits(self, xlim, ylim, zlim=None):
        """ SetLimits(xlim, ylim, zlim=None)
        
        Set the limits to visualize  
        Always set this before rendering!
        This also calls reset to reset the view.
        
        """
        if zlim is None:
            zlim = Range(-1,1)        
        self.xlim = xlim
        self.ylim = ylim
        self.zlim = zlim
        
        # reset
        self.Reset()
    
    # Subclasses should set viewparams, a set of (key, attribute_name) pairs
    # for the values returned by GetViewParams.
    viewparams = None
    
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
        rx,ry,rz = self.xlim.range, self.ylim.range, self.zlim.range
        dx,dy,dz = self.xlim.min, self.ylim.min, self.zlim.min
        self.view_loc = rx/2.0 + dx, ry/2.0 + dy, rz/2.0 + dz
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
        
        # Get data aspect ratio
        daspect = self.axes.daspect
        
        # use current mouse position if none given
        if x_y is None:
            x,y = self.axes.mousepos
        else:
            x, y = x_y[0], x_y[1] # in case the input is 3d
        
        # get window size
        w, h = self.axes.position.size
        w, h = float(w), float(h) 
        
        # get zoom factor
        fx, fy = 1.0 / self.zoom, 1.0 / self.zoom
        
        # correct zoom factor for window size      
        if not self.axes.daspectAuto:
            if w > h:
                fx *= w/h
            else:
                fy *= h/w                
        
        # determine position in projection. Here is a conversion
        # of the coordinate system... (flip y)
        x, y = (x/w-0.5) * fx, (0.5-y/h) * fy
        
        # scale
        x, y = x / daspect[0], y / daspect[1]
        
        # translate it
        x, y = x + self.view_loc[0], y + self.view_loc[1]
        
        #print x, y
        return x,y
    
    
    def _SetDaspect(self, ratio, i, j, refDaspect=None):
        """ _SetDaspect(ratio,  i, j, refDaspect=None)
        
        Change the value of the given refDaspect (or use axes.daspect)
        and set that as the new daspect. The new daspect is also returned.
        
        Sets daspect[i] to daspect[j] * ratio, bur preserves the sign
        of the original reference daspect.
        
        """
        
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
        
        # Set for all axes
        for a in self.axeses:
            a.daspect = tuple(daspect2)
        # todo: set for all axeses, or make daspect a camera property?
        
        return daspect2
    
    
    def _GetNormalizedDaspect(self):
        
        daspect = self.axes.daspect
        length = float(daspect[0]**2 + daspect[1]**2 + daspect[2]**2)**0.5
        return [d/length for d in daspect]


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
    
    ndim = 2
    
    def OnInit(self):
        
        # Set flag
        self.isTwoD = True
        
        # indicate part that we view.
        # view_loc is the coordinate that we center on
        self.view_loc = 0,0,0 # we only use the 2D part
        self._fx, self._fy = 0,0
        self.zoom = 1.0
        
        # reference stuff for interaction
        self.ref_loc = 0,0,0    # view_loc when clicked
        self.ref_mloc = 0,0     # mouse location when clicked
        self.ref_but = 0        # mouse button when clicked   
        self.ref_axes = None
        
        self.ref_zoom = 1.0
        self.ref_daspect = [1,1,1]
        
        # bind events
        for axes in self.axeses:
            axes.eventMouseDown.Bind( self.OnMouseDown)        
            axes.eventMouseUp.Bind( self.OnMouseUp)        
            axes.eventMotion.Bind( self.OnMotion)
            axes.eventDoubleClick.Bind( self.Reset)
    
    
    viewparams = (('loc', 'view_loc'), ('zoom', 'zoom'))
    
    
    def Reset(self, event=None):
        """ Reset()
        
        Reset the view.        
        
        """
        
        # Only reset if this is currently the camera
        if self.axes.camera is not self:
            return
        
        # get window size
        w,h = self.axes.position.size
        w,h = float(w), float(h)
        
        # get range and translation for x and y   
        rx, ry = self.xlim.range, self.ylim.range
        
        if not self.axes.daspectAuto:
            # simulate what SetView will do to correct for window size
            # make fx smaller if SetView will make it larger...
            if w / h > 1:
                rx /= w/h
            else:
                ry /= h/w
        else:
            # Modify daspect, y is the reference
            daspect = self._SetDaspect(ry/rx, 0, 1)
        
        # set zoom factor
        daspect = self.axes.daspect
        zoomx = 1.0 / abs(daspect[0] * rx)
        zoomy = 1.0 / abs(daspect[1] * ry)
        self.zoom = min(zoomx, zoomy)
        
        # set center location -> calls refresh
        BaseCamera.Reset(self)
    
    
    def OnMouseDown(self, event): 
        
        # store mouse position and button
        self.ref_mloc = event.x, event.y
        self.ref_but = event.button
        self.ref_axes = event.owner
        
        # store current view parameters        
        self.ref_loc = self.view_loc
        self.ref_zoom = self.zoom
        self.ref_daspect = self.axes.daspect
        
        #self.ScreenToWorld() # for debugging


    def OnMouseUp(self, event):
        self.ref_but = 0
        # Draw without the fast flag      
        for axes in self.axeses:
            axes.Draw()


    def OnMotion(self, event):
        
        if not self.ref_but:
            return
        if not self.ref_axes is event.owner:
            return
        if not self.axes.camera is self:
            return False
        
        # get loc (as the event comes from the figure, not the axes)
        mloc = event.owner.mousepos
        
        if self.ref_but==1:
            # translate
            
            # get distance and convert to world coordinates
            refloc = self.ScreenToWorld(self.ref_mloc)
            loc = self.ScreenToWorld(mloc)
            
            # calculate translation
            dx = loc[0] - refloc[0]
            dy = loc[1] - refloc[1]
            
            # apply
            self.view_loc = ( self.ref_loc[0] - dx ,  self.ref_loc[1] - dy )
        
        elif self.ref_but==2:
            # zoom
            
            # get movement in x (in pixels) and normalize
            factorx = float(self.ref_mloc[0] - mloc[0])
            factorx /= self.axes.position.width
            
            # get movement in y (in pixels) and normalize
            factory = float(self.ref_mloc[1] - mloc[1])
            factory /= self.axes.position.height
            
            # apply 
            if self.axes.daspectAuto:
                # Zooming in pure x goes via daspect.
                # Zooming in pure y goes via zoom factor.
                dzoom_x, dzoom_y = math.exp(-factorx), math.exp(factory)
                self._SetDaspect(dzoom_x/dzoom_y, 0, 0, self.ref_daspect)
                self.zoom = self.ref_zoom * dzoom_y
            
            else:
                self.zoom = self.ref_zoom * math.exp(factory)
        
        # refresh
        for axes in self.axeses:
            axes.Draw(True)


    def SetView(self):
        """ SetView()
        
        Prepare the view for drawing
        This applies the camera model.
        
        """
        
        # Calculate viewing range for x and y
        fx = abs( 1.0 / self.zoom )
        fy = abs( 1.0 / self.zoom )
        
        # correct for window size
        if not self.axes.daspectAuto:
            w, h = self.axes.position.size
            w, h = float(w), float(h)        
            if w / h > 1:#self.ylim.range / self.xlim.range:
                fx *= w/h
            else:
                fy *= h/w
        
        # store these values
        self._fx, self._fy = fx, fy
        
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
        daspect = self.axes.daspect
        gl.glScale( daspect[0], daspect[1], daspect[2] )
        
        # 1. Translate to view location (coordinate where we look at). 
        # Do this first because otherwise the translation is not in world 
        # coordinates.
        gl.glTranslate(-self.view_loc[0], -self.view_loc[1], 0.0)


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
    
    ndim = 3
    
    def OnInit(self):
        
        # camera view params
        self.view_az = -10.0 # azimuth
        self.view_el = 30.0 # elevation
        self.view_ro = 0.0 # roll
        self.view_fov = 0.0 # field of view - if 0, use ortho view
        self.view_loc = 0,0,0
        self.zoom = 1.0
        
        self._windowSizeFactor = None
        
        # reference variables for when dragging
        self.ref_loc = 0,0,0    # view_loc when clicked
        self.ref_mloc = 0,0     # mouse location when clicked
        self.ref_but = 0        # mouse button clicked
        self.ref_az = 0         # angles when clicked
        self.ref_el = 0
        self.ref_ro = 0
        self.ref_fov = 0
        self.ref_zoom = 0
        
        # Bind to events
        for axes in self.axeses:
            axes.eventPosition.Bind(self.OnResize)
            axes.eventKeyDown.Bind(self.OnKeyDown)
            axes.eventKeyUp.Bind(self.OnKeyUp)        
            # 
            axes.eventMouseDown.Bind(self.OnMouseDown)
            axes.eventMouseUp.Bind(self.OnMouseUp)        
            axes.eventMotion.Bind(self.OnMotion)
            axes.eventDoubleClick.Bind(self.Reset)
            # Some of these bindings can just as well be done in 
            # the base camera class
    
    
    viewparams = (('loc', 'view_loc'), ('zoom', 'zoom'),
                  ('azimuth', 'view_az'), ('elevation', 'view_el'), ('roll', 'view_ro'),
                  ('fov', 'view_fov'))
    
    
    def OnResize(self, event):
        
        # Get new size factor
        w,h = self.axes.position.size
        sizeFactor = float(h) / w
        
        # Make it quick if daspect is not in auto-mode
        if not self.axes.daspectAuto:
            self._windowSizeFactor = sizeFactor
            return
        
        # Get daspect factor
        if self._windowSizeFactor:
            daspectFactor = sizeFactor / self._windowSizeFactor
        else:
            daspectFactor = sizeFactor
        
        # Set size factor for next time
        self._windowSizeFactor = sizeFactor
        
        # Change daspect
        self._SetDaspect(daspectFactor, 2, 2)
    
    
    def Reset(self, event=None):
        """ Reset()
        
        Reset the view.
        
        """
        
        # Only reset if this is currently the camera
        if self.axes.camera is not self:
            return
        
        # Set angles
        self.view_az = -10.0
        self.view_el = 30.0
        self.view_ro = 0.0 
        self.view_fov = 0.0
        
        # get window size
        w,h = self.axes.position.size
        w,h = float(w), float(h)
        
        # get range and translation for x and y   
        rx, ry, rz = self.xlim.range, self.ylim.range, self.zlim.range
        
        if True:
            # Correct ranges for window size. Note that the window width
            # influences the x and y data range, while the height influences
            # the z data range.
            if w / h > 1:
                rx /= w/h
                ry /= w/h
            else:
                rz /= h/w
        
        if self.axes.daspectAuto:
            # Change daspect, x is the reference
            self._SetDaspect(rx/ry, 1, 0)
            self._SetDaspect(rx/rz, 2, 0)
        
        # Correct for normalized daspect
        ndaspect = self._GetNormalizedDaspect()
        rx, ry, rz = rx*ndaspect[0], ry*ndaspect[1], rz*ndaspect[2]
        
        # Below this line x and y represent screen coordinates. In screen x, 
        # only x and y have effect. In screen y, all three dimensions have 
        # effect, because of the elevation and azimuth.
        # The idea of the lines below is to calculate the range on screen
        # when the scene is in a 45 degrees rotated state.
        rxs = ( rx**2 + ry**2 )**0.5
        rys = ( rx**2 + ry**2 + rz**2 )**0.5
        
        # Correct again for screen coords
        if w / h > 1:
            rxs *= w/h
            self.zoom = (1/rxs) / 1.04  # 2% extra space
        else:
#             rys *= h/w
            self.zoom = (1/rys) / 1.08 # 10% extra space
        # set zoom factor
#         daspect = self.axes.daspect
#         zoomx = 1.0 / abs(daspect[0] * rx) 
#         zoomy = 1.0 / abs(daspect[1] * ry)
#         zoomz = 1.0 / abs(daspect[2] * rz)
#         self.zoom = min(1/rxs, 1/rys) / 1.05  # 5% extra space
        
        # set center location -> calls refresh
        BaseCamera.Reset(self)
    
    
    def SetRef(self):
        # store current view parameters
        self.ref_az = self.view_az
        self.ref_el = self.view_el
        self.ref_ro = self.view_ro
        self.ref_fov = self.view_fov
        #
        self.ref_loc = self.view_loc
        #
        self.ref_zoom = self.zoom
        self.ref_daspect = self.axes.daspect
    
    
    def OnKeyDown(self, event):
        # store mouse position and button
        self.ref_mloc = event.owner.mousepos
        self.SetRef()

    def OnKeyUp(self, event):
        self.ref_mloc = event.owner.mousepos
        self.SetRef()
    
    
    def OnMouseDown(self, event):
        
        # store mouse position and button
        self.ref_mloc = event.x, event.y
        self.ref_but = event.button
        self.ref_axes = event.owner
        
        self.SetRef()

   
    def OnMouseUp(self, event):        
        self.ref_but = 0
        for axes in self.axeses:
            axes.Draw()

    
    def OnMotion(self, event):
        
        if not self.ref_but:
            return
        if not self.ref_axes is event.owner:
            return
        if not self.axes.camera is self:
            return False
        
        # get loc (as the event comes from the figure, not the axes)
        mloc = event.owner.mousepos
            
        if constants.KEY_SHIFT in event.modifiers and self.ref_but==1:
            # translate
            
            # get locations and convert to world coordinates
            refloc = self.ScreenToWorld(self.ref_mloc)
            loc = self.ScreenToWorld(mloc)
            
            # calculate distance and undo aspect ratio adjustment from ScreenToWorld
            ar = self.axes.daspect
            distx = (refloc[0] - loc[0]) * ar[0]
            distz = (refloc[1]-loc[1]) * ar[1]
            
            # calculate translation
            sro, saz, sel = map(sind, (self.view_ro, self.view_az, self.view_el))
            cro, caz, cel = map(cosd, (self.view_ro, self.view_az, self.view_el))
            dx = (distx * (cro * caz + sro * sel * saz) + distz * (sro * caz - cro * sel * saz))/ar[0]
            dy = (distx * (cro * saz - sro * sel * caz) + distz * (sro * saz + cro * sel * caz))/ar[1]
            dz = (-distx * sro * cel + distz * cro * cel)/ar[2]
            
            # apply
            self.view_loc = ( self.ref_loc[0] + dx ,  self.ref_loc[1] + dy , 
                self.ref_loc[2] + dz )
        
        elif constants.KEY_CONTROL in event.modifiers and self.ref_but==1:
            # Roll
            
            # get normalized delta values
            sze = self.axes.position.size
            d_ro = float( self.ref_mloc[0] - mloc[0] ) / sze[0]
            
            # change az and el accordingly
            self.view_ro = self.ref_ro + d_ro * 90.0
            
            # keep within bounds    
            if self.view_ro < -90:
                self.view_ro = -90
            while self.view_ro > 90:
                self.view_ro = 90
        
        elif self.ref_but==1:
            # rotate
            
            # get normalized delta values
            sze = self.axes.position.size
            d_az = float( self.ref_mloc[0] - mloc[0] ) / sze[0]
            d_el = -float( self.ref_mloc[1] - mloc[1] ) / sze[1]
            
            # change az and el accordingly
            self.view_az = self.ref_az + d_az * 90.0
            self.view_el = self.ref_el + d_el * 90.0
            
            # keep within bounds            
            while self.view_az < -180:
                self.view_az += 360
            while self.view_az >180:
                self.view_az -= 360
            if self.view_el < -90:
                self.view_el = -90
            if self.view_el > 90:
                self.view_el = 90
            #print self.view_az, self.view_el
        
        elif constants.KEY_SHIFT in event.modifiers and self.ref_but==2:
            # Change FoV
            
            # get normailized delta value
            d_fov = float(self.ref_mloc[1] - mloc[1]) / self.axes.position.height
            
            # apply
            self.view_fov = self.ref_fov + d_fov * 90
            
            # keep from being too big or negative
            if self.view_fov > 179:
                self.view_fov = 179
            elif self.view_fov < 0:
                self.view_fov = 0
        
        elif self.ref_but==2:
            # zoom
            
            # get movement in x (in pixels) and normalize
            factorx = float(self.ref_mloc[0] - mloc[0])
            factorx /= self.axes.position.width
            
            # get movement in y (in pixels) and normalize
            factory = float(self.ref_mloc[1] - mloc[1])
            factory /= self.axes.position.height
            
            # apply 
            if self.axes.daspectAuto:
                # Zooming in x and y goes via daspect.
                # Zooming in z goes via zoom factor.
                dzoom_x, dzoom_y = math.exp(-factorx), math.exp(factory)
                daspect = self.ref_daspect
                ar = self.axes.daspect
                
                sro, saz, sel = map(sind, (self.view_ro, self.view_az, self.view_el))
                cro, caz, cel = map(cosd, (self.view_ro, self.view_az, self.view_el))
                # Motion to right or top should always zoom in, regardless of rotation
                dx = -factorx * abs(cro * caz + sro * sel * saz) + factory * abs(sro * caz - cro * sel * saz)
                dy = -factorx * abs(cro * saz - sro * sel * caz) + factory * abs(sro * saz + cro * sel * caz)
                dz = factorx * abs(sro * cel) + factory * abs(cro * cel)
                
                daspect = self._SetDaspect(math.exp(dy-dx), 1, 1, daspect)
                daspect = self._SetDaspect(math.exp(dz-dx), 2, 2, daspect)
                
                #factor = 1.0 / (3*2**0.5)
                self.zoom = self.ref_zoom * math.exp(factory) * math.exp(factory)
            else:
                self.zoom = self.ref_zoom * math.exp(factory)
        
        # refresh (fast)
        for axes in self.axeses:
            axes.Draw(True)
    
    
    def SetView(self):
        """ SetView()
        
        Prepare the view for drawing
        This applies the camera model.
        
        """
        
        # Calculate viewing range for x and y
        fx = abs( 1.0 / self.zoom )
        fy = abs( 1.0 / self.zoom )
        
        # Correct for window size        
        if True:
            w, h = self.axes.position.size
            w, h = float(w), float(h)        
            if w / h > 1:#self.ylim.range / self.xlim.range:
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
        if self.view_fov == 0:
            ortho( -0.5*fx, 0.5*fx, -0.5*fy, 0.5*fy)
        else:
            # Figure distance to center in order to have correct FoV and fy.
            d = fy / (2 * math.tan(math.radians(self.view_fov)/2))
            val = math.sqrt(getDepthValue())
            glu.gluPerspective(self.view_fov, fx/fy, d/val, d*val)
            gl.glTranslate(0, 0, -d)
        
        # Prepare for models
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # Set camera lights
        for light in self.axes._lights:
            if light.isCamLight:                
                light._Apply()
        
        # 3. Set viewing angle (this is the only difference with the 2D camera)
        gl.glRotate(self.view_ro, 0.0, 0.0, 1.0)
        gl.glRotate(270+self.view_el, 1.0, 0.0, 0.0)
        gl.glRotate(-self.view_az, 0.0, 0.0, 1.0)
        
        # 2. Set aspect ratio (scale the whole world), and flip any axis...
        ndaspect = self._GetNormalizedDaspect()    
        gl.glScale( ndaspect[0], ndaspect[1] , ndaspect[2] )
        
        # 1. Translate to view location. Do this first because otherwise
        # the translation is not in world coordinates.
        gl.glTranslate(-self.view_loc[0], -self.view_loc[1], -self.view_loc[2])
        
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
    
    ndim = 3
    
    # Note that this camera does not use the MouseMove event but uses
    # a timer to update itself, this is to get the motion smooth.
    
    def OnInit(self):
        
        # camera view params
        # view_loc is not the position you look at,
        # but the position you ARE at
        self.view_az = 10.0
        self.view_el = 30.0
        self.view_zoomx = 100.0
        self.view_zoomy = 100.0
        self.view_loc = 0,0,0 
        
        # reference variables for when dragging
        self.ref_loc = 0,0      # view_loc when clicked
        self.ref_mloc = 0,0     # mouse location clicked
        self.ref_but = 0        # button clicked
        self.ref_speed1 = 0     # direction forward
        self.ref_speed2 = 0     # direction rigth        
        self.ref_az = 0         # angles when clicked
        self.ref_el = 0
        self.ref_zoomx = 0      # zoom factors when clicked
        self.ref_zoomy = 0
        
        # create timer and bind to it. This timer is started when clicked
        # and stopped when the mouse is released. This is to make a 
        # smoother flying possible.
        self._timer = Timer(self, 50, False)
        self._timer.Bind(self.OnTimer)
        
        # Bind to events
        axes = self.axes
        axes.eventKeyDown.Bind(self.OnKeyDown)        
        # 
        axes.eventMouseDown.Bind(self.OnMouseDown)
        axes.eventMouseUp.Bind(self.OnMouseUp)
        axes.eventDoubleClick.Bind(self.Reset)


    def Reset(self, event=None):
        """ Reset()
        
        Position the camera at a suitable position from the scene.
        
        """
        
        # Only reset if this is currently the camera
        if self.axes.camera is not self:
            return
        
        # call the 3D camera reset... It calls Draw(), which is thus called
        # unnecesary, but hell, you dont reset that often...
        ThreeDCamera.Reset(self)
        
        # get aspect ratio
        ar = self.axes.daspect
        
        # change centre, we move at the minimum x and y, but at a higher z.
        rx,ry,rz = self.xlim.range, self.ylim.range, self.zlim.range
        dx,dy,dz = self.xlim.min, self.ylim.min, self.zlim.min        
        dd = (rx**2 + ry**2 + rz**2 )**0.5        
        dd *= ar[2]
        #self.view_loc = rx/2.0+dx+500, ry/2.0+dy+500, rz/2.0/rz-dd
        self.view_loc = dx, dy, dz + rz/2.0 + dd
        
        # set angles        
        self.view_az = -math.atan2(ar[0],ar[1])*180/math.pi
        self.view_el = 80 # look down
        
        # refresh
        for axes in self.axeses:
            axes.Draw()
        
        
    def OnKeyDown(self, event):
        # Detect whether the used wants to set things in motion.
        if event.text == 'w':
            self.ref_speed1 += 1
        elif event.text == 's':
            self.ref_speed1 -= 1
        elif event.text == 'd':
            self.ref_speed2 += 1
        elif event.text == 'a':
            self.ref_speed2 -= 1
   
     
    def Move(self, event=None):
        # Move the fly -> change its position.
        
        # get aspect ratio, we need to normalize with it...
        ar = self.axes.daspect
        # calculate distance to travel            
        rx,ry,rz = self.xlim.range, self.ylim.range, self.zlim.range
        distance = dd = (rx**2 + ry**2 + rz**2 )**0.5/200.0
        # express angles in radians
        rad_az = self.view_az * math.pi / 180.0
        rad_el = self.view_el * math.pi / 180.0
        
        # init
        dx=dy=dz = 0.0
        sp1, sp2 = self.ref_speed1, self.ref_speed2
        
        if sp1:
            f = math.cos( -rad_el )
            dx += sp1 * distance * math.sin( -rad_az ) * f / ar[0]
            dy += sp1 * distance * math.cos( -rad_az ) * f / ar[1] 
            dz += sp1 * distance * math.sin( -rad_el ) / ar[2]
        if sp2:
            dx +=   sp2 * distance * math.cos( -rad_az ) / ar[0]
            dy += - sp2 * distance * math.sin( -rad_az ) / ar[1] 
        
        # update location
        self.view_loc = ( self.view_loc[0] + dx ,  self.view_loc[1] + dy , 
            self.view_loc[2] + dz )
        
        # refresh is performed by the caller
        
    
    
    def OnMouseDown(self, event):
        
        # store mouse position and button
        self.ref_mloc = event.x, event.y
        self.ref_but = event.button
        self.ref_axes = event.owner
        
        # store current view parameters
        self.ref_az = self.view_az
        self.ref_el = self.view_el
        self.ref_loc = self.view_loc
        self.ref_zoomx = self.view_zoomx 
        self.ref_zoomy = self.view_zoomy 
        
        # start moving!
        self.ref_speed1 = 0
        self.ref_speed2 = 0
        self._timer.Start()
   
    
    def OnMouseUp(self, event):        
        self.ref_but = 0
        for axes in self.axeses:
            axes.Draw()
        self._timer.Stop()
    
    
    def OnTimer(self, event):
       
        if not self.ref_but:
            return
        if not self.axes.camera is self:
            return False
        
        # get loc (as the event comes from the figure, not the axes)
        mloc = self.axes.mousepos
        
        if self.ref_but==1:
            # rotate
            
            # get normalized delta values
            sze = self.axes.position.size
            d_az = float( self.ref_mloc[0] - mloc[0] ) / sze[0]
            d_el = -float( self.ref_mloc[1] - mloc[1] ) / sze[1]
            
            # change az and el accordingly
            self.view_az = self.ref_az + d_az * 90.0
            self.view_el = self.ref_el + d_el * 90.0
            
            # keep within bounds            
            while self.view_az < -180:
                self.view_az += 360
            while self.view_az >180:
                self.view_az -= 360
            if self.view_el < -90:
                self.view_el = -90
            while self.view_el > 90:
                self.view_el = 90
            #print self.view_az, self.view_el
        
        elif self.ref_but==2:
            # zoom
            
            # get movement in x (in pixels) and normalize
            factorx = float(self.ref_mloc[0] - mloc[0])
            factorx /= self.axes.position.width
            
            # get movement in y (in pixels) and normalize
            factory = float(self.ref_mloc[1] - mloc[1])
            factory /= self.axes.position.height
            
            # apply (use only y-factor if daspect is valid.
            if self.axes.daspectAuto:
                self.view_zoomx = self.ref_zoomx * math.exp(factorx)
                self.view_zoomy = self.ref_zoomy * math.exp(-factory)
            else:
                self.view_zoomy = self.ref_zoomy * math.exp(-factory)
                self.view_zoomx = self.view_zoomy
        
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
            if self.view_zoomx != self.view_zoomy:
                # apply average zoom
                tmp = self.view_zoomx + self.view_zoomy
                self.view_zoomx = self.view_zoomy = tmp / 2.0
#         if self.view_zoomx < 2:
#             self.view_zoomx = 2.0
#         if self.view_zoomy < 2:
#             self.view_zoomy = 2.0
        
        # get zoom
        fx, fy = self.view_zoomx, self.view_zoomy
        
        # correct for window size        
        if not self.axes.daspectAuto:
            w, h = self.axes.position.size
            w, h = float(w), float(h)        
            if w / h > 1:#self.ylim.range / self.xlim.range:
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
        gl.glRotate(self.view_el-90, 1.0, 0.0, 0.0)        
        gl.glRotate(-self.view_az, 0.0, 0.0, 1.0)
        
        # Prepare for models ...
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        
        # 2. Set aspect ratio (scale the whole world), and flip any axis...
        daspect = self.axes.daspect        
        gl.glScale( daspect[0], daspect[1] , daspect[2] )
        
        # 1. Translate to view location. Do this first because otherwise
        # the translation is not in world coordinates.
        gl.glTranslate(-self.view_loc[0], -self.view_loc[1], -self.view_loc[2])


