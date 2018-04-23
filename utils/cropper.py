""" Module cropper

Provides functionality to crop data.
"""

import time
import numpy as np
import visvis as vv
from visvis.utils.pypoints import Pointset, Aarray

import OpenGL.GL as gl
import OpenGL.GLU as glu


class RangeWobject2D(vv.Wobject):
    """ RangeWobject2D(parent, data, snap=True)
    This class represents a kind of widjet with which a 2D range
    can be given by hand by dragging the bands of the range.
    Data should be a 2D anisotropic array (points.Aarray). If snap
    is True, the range will snap to powers of two.
    """
    
    def __init__(self, parent, data, snap=True):
        vv.Wobject.__init__(self, parent)
        
        # Store reference to 2D anisotropic array
        self._data = data
        self._snap = snap
        
        # Init range as integers
        self._rangex = vv.Range(0, data.shape[1])
        self._rangey = vv.Range(0, data.shape[0])
        
        # How wide the bar should be
        self._barWidth = 10
        
        # Color to display
        self._clr1 = (0.3, 1.0, 0.3)  # line and highlighted bars
        self._clr2 = (0.0, 0.6, 0.0)  # non-active bars
        
        # To indicate dragging
        self._over = False
        self._dragging = False
        self._refBars = []
        self._refpos = (0,0)
        self._refRangex = vv.Range(0,0)
        self._refRangey = vv.Range(0,0)
        
        # Quad indices of bars
        self._bar1 = [11,6,13,12]
        self._bar2 = [5,13,14,8]
        self._bar3 = [10,7,14,15]
        self._bar4 = [4,9,15,12]
        
        # Buffer of the coords array
        self._cordsBuffer = None
        
        # Create event
        self.eventRangeUpdated = vv.events.BaseEvent(self)
        
        # Callbacks
        self.eventEnter.Bind(self._OnEnter)
        self.eventLeave.Bind(self._OnLeave)
        self.eventMouseDown.Bind(self._OnDown)
        self.eventMouseUp.Bind(self._OnUp)
        axes = self.GetAxes()
        axes.eventMotion.Bind(self._onMotion)
        axes.eventPosition.Bind(self._onPosition)
    
    ## Callbacks
    
    
    def _onPosition(self, event):
        self._cordsBuffer = None
        self.Draw()
    
    
    def _OnEnter(self, event):
        self._over = True
    
    
    def _OnLeave(self, event):
        self._over = False
    
    
    def _OnDown(self, event):
        if event.button == 2:
            # Enable zooming by passing on event
            a = self.GetAxes()
            if a:
                a.eventMouseDown.x = event.x
                a.eventMouseDown.y = event.y
                a.eventMouseDown.x2d = event.x2d
                a.eventMouseDown.y2d = event.y2d
                a.eventMouseDown.button = event.button
                a.eventMouseDown.Fire()
        
        else:
            # Store pos and reference ranges
            self._refpos = event.x2d, event.y2d
            self._refRangex = self._rangex.Copy()
            self._refRangey = self._rangey.Copy()
            # Check which part is being clicked
            self._dragging = True
            self._SetRefBars(*self._refpos)
    
    
    def _OnUp(self, event):
        if event.button == 2:
            # Enable zooming by passing on event
            a = self.GetAxes()
            if a:
                a.eventMouseUp.x = event.x
                a.eventMouseUp.y = event.y
                a.eventMouseUp.x2d = event.x2d
                a.eventMouseUp.y2d = event.y2d
                a.eventMouseUp.button = event.button
                a.eventMouseUp.Fire()
        else:
            self._dragging = False
            # Redraw
            self.Draw()
    
    
    def _onMotion(self, event):
        if not self._dragging:
            
            # If over, set refbar, if not over, remove bars if still active
            if self._over:
                self._SetRefBars(event.x2d, event.y2d)
            elif self._refBars:
                self._refBars = []
                self.Draw()
        
        else:
            
            # Get position change
            dx = event.x2d - self._refpos[0]
            dy = event.y2d - self._refpos[1]
            
            # Correct for sampling and make integer
            dx = round( dx / self._data.sampling[1] )
            dy = round( dy / self._data.sampling[0] )
            
            # Init snapping
            snaps = []
            if len(self._refBars)<4 and self._snap:
                snaps = [8,16,32,64,128,256,512,1024,2048,4096,8192,16384]
            snapFactor = 8.0
            
            # Change ranges
            
            if 1 in self._refBars:
                # Snap
                if snaps:
                    ref = self._refRangex.range-dx
                    for snap in snaps:
                        if abs(snap-ref) < (snap/snapFactor):
                            dx -= snap-ref
                            break
                # Aplly, but do not go beyond other limit
                tmp = self._refRangex.min + dx
                if tmp >= self._rangex.max:
                    self._rangex.min = self._rangex.max-1
                else:
                    self._rangex.min = tmp
            
            if 2 in self._refBars:
                # Snap
                if snaps:
                    ref = self._refRangey.range-dy
                    for snap in snaps:
                        if abs(snap-ref) < (snap/snapFactor):
                            dy -= snap-ref
                            break
                # Aplly, but do not go beyond other limit
                tmp = self._refRangey.min + dy
                if tmp >= self._rangey.max:
                    self._rangey.min = self._rangey.max-1
                else:
                    self._rangey.min = tmp
            
            if 3 in self._refBars:
                # Snap
                if snaps:
                    ref = self._refRangex.range+dx
                    for snap in snaps:
                        if abs(snap-ref) < (snap/snapFactor):
                            dx += snap-ref
                            break
                # Aplly, but do not go beyond other limit
                tmp = self._refRangex.max + dx
                if tmp <= self._rangex.min:
                    self._rangex.max = self._rangex.min+1
                else:
                    self._rangex.max = tmp
            
            if 4 in self._refBars:
                # Snap
                if snaps:
                    ref = self._refRangey.range+dy
                    for snap in snaps:
                        if abs(snap-ref) < (snap/snapFactor):
                            dy += snap-ref
                            break
                # Aplly, but do not go beyond other limit
                tmp = self._refRangey.max + dy
                if tmp <= self._rangey.min:
                    self._rangey.max = self._rangey.min+1
                else:
                    self._rangey.max = tmp
            
            # Limit ranges
            shape = self._data.shape
            if self._rangex.min < 0:
                self._rangex.min = 0
            if self._rangey.min < 0:
                self._rangey.min = 0
            if self._rangex.max > shape[1]: # range is including last
                self._rangex.max = shape[1]
            if self._rangey.max > shape[0]:
                self._rangey.max = shape[0]
            
            # We updated the range, so the coords need invalidating
            self._cordsBuffer = None
            self.eventRangeUpdated.Fire()
            
            # Redraw
            self.Draw()


    ## Helper methods
    
    def _GetRangesInWorldCords(self):
        """ _GetRangesInWorldCords()
        Get the ranges, but expressed in world coordinates rather
        than pixel coordinates in the 2D texture object.
        """
        data = self._data
        rangex = vv.Range(
            data.origin[1]+(self._rangex.min-0.5)*data.sampling[1],
            data.origin[1]+(self._rangex.max-0.5)*data.sampling[1] )
        rangey = vv.Range(
            data.origin[0]+(self._rangey.min-0.5)*data.sampling[0],
            data.origin[0]+(self._rangey.max-0.5)*data.sampling[0] )
        return rangex, rangey
    
    
    def _SetRefBars(self, x, y):
        """ _SetRefBars(x,y)
        Based on the given (mouse) position, it is determined which
        directions the rectangle would be resized if the user would
        start dragging now. This can be one direction, two directions
        (if dragging a corner) or all four directions (if dragging the
        center).
        
        The self._refBars list is updated, which is used in the drawing
        method to color these bars differently. This list is also used
        directly to determine which ranges to update during dragging in
        _OnMotion().
        """
        # Direction diagram:
        #     4
        #  1     3
        #     2
        
        # Get ranges
        rangex, rangey = self._GetRangesInWorldCords()
        
        # fill a refBars list
        refBars = []
        if x < rangex.min:
            refBars.append(1)
        if y < rangey.min:
            refBars.append(2)
        if x > rangex.max:
            refBars.append(3)
        if y > rangey.max:
            refBars.append(4)
        if not refBars:
            refBars = [1,2,3,4]  # special case center
        
        # Should we update screen?
        if self._refBars != refBars:
            self.Draw()
        
        # Update the stored version of the refBars list
        self._refBars = refBars
    
    
    def _GetCords(self):
        """ _GetCords()
        Get a pointset of the coordinates of the wobject. This is used
        for drawing the quads and lines using a vertex array.
        """
        
        # Can we reuse buffered coordinates?
        if self._cordsBuffer is not None:
            return self._cordsBuffer
        
        # Get ranges in world coords
        rangex, rangey = self._GetRangesInWorldCords()
        
        # Project two points to use in OnDrawScreen
        screen1 = glu.gluProject(rangex.min, rangey.min, 0)
        screen2 = glu.gluProject(rangex.max, rangey.max, 0)
        
        # Calculate world-distance of a screendistance of self._barwidth
        # and then do drawing here (not in OnDrawScreen), otherwise I won't
        # be able to detect picking!!
        onePixelx = rangex.range / ( screen2[0] - screen1[0] )
        onePixely = rangey.range / ( screen2[1] - screen1[1] )
        
        # Get coords
        tmp = self._barWidth
        x1, x2, xd = rangex.min, rangex.max, onePixelx*tmp
        y1, y2, yd = rangey.min, rangey.max, onePixely*tmp
        if yd<0:
            y1, y2 = y2, y1 # axis flipped
        
        # Definition of the coordinate indices:
        #
        # 12 11      10 15
        #  4 0 ----- 3 9
        #    |       |
        #    |       |
        #  5 1------ 2 8
        # 13 6       7 14
        #
        
        # Make coords
        pp = Pointset(2)
        #
        pp.append(x1, y1)
        pp.append(x1, y2)
        pp.append(x2, y2)
        pp.append(x2, y1)
        #
        pp.append(x1-xd, y1)
        pp.append(x1-xd, y2)
        pp.append(x1, y2+yd)
        pp.append(x2, y2+yd)
        #
        pp.append(x2+xd, y2)
        pp.append(x2+xd, y1)
        pp.append(x2, y1-yd)
        pp.append(x1, y1-yd)
        #
        pp.append(x1-xd, y1-yd)
        pp.append(x1-xd, y2+yd)
        pp.append(x2+xd, y2+yd)
        pp.append(x2+xd, y1-yd)
        
        # Done
        self._cordsBuffer = pp
        return pp
    
    
    ## Draw methods
    
    def OnDraw(self):
        
        # Get coords and prepare for drawing
        pp = self._GetCords()
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(pp.data)
        
        # Draw outline
        clr = self._clr1
        gl.glColor( clr[0], clr[1], clr[2])
        gl.glLineWidth(1)
        ind = np.array([0,1,2,3,0],dtype=np.uint8)
        gl.glDrawElements(gl.GL_LINE_STRIP, len(ind), gl.GL_UNSIGNED_BYTE, ind)
        
        # Enable transparancy
        # (note that this does not work on all OpenGl versions)
        alpha = 1.0
        if vv.misc.getOpenGlCapable('1.4'):
            alpha = 0.3
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_CONSTANT_ALPHA, gl.GL_ONE_MINUS_CONSTANT_ALPHA)
            gl.glBlendColor(0.0,0.0,0.0, alpha)
        
        # Get which bars to draw in what color
        tmp = [None, self._bar1, self._bar2, self._bar3, self._bar4]
        normalbars = []
        dragbars = []
        for i in range(1,5):
            if i in self._refBars:
                dragbars.extend(tmp[i])
            else:
                normalbars.extend(tmp[i])
        
        # Draw normal bars
        if normalbars:
            clr = self._clr2
            gl.glColor( clr[0], clr[1], clr[2])
            ind = np.array(normalbars,dtype=np.uint8)
            gl.glDrawElements(gl.GL_QUADS, len(ind), gl.GL_UNSIGNED_BYTE, ind)
        
        # Draw bars being moved
        if dragbars:
            clr = self._clr1
            gl.glColor( clr[0], clr[1], clr[2])
            ind = np.array(dragbars,dtype=np.uint8)
            gl.glDrawElements(gl.GL_QUADS, len(ind), gl.GL_UNSIGNED_BYTE, ind)
        
        # Done
        gl.glFlush()
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        if alpha<1.0:
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
    
    
    def OnDrawShape(self, clr):
        
        # Get coords and prepare for drawing
        pp = self._GetCords()
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glVertexPointerf(pp.data)
        
        # Set color etc
        gl.glColor( clr[0], clr[1], clr[2])
        gl.glLineWidth(1)
        
        # Draw grabbable stuff
        ind = np.array([ 12,13,14,15 ],dtype=np.uint8)
        gl.glDrawElements(gl.GL_QUADS, len(ind), gl.GL_UNSIGNED_BYTE, ind)
        
        # Done
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
    
    

class Cropper3D:
    """ A helper class for 3d cropping. Use the crop3d function to
    perform manual cropping.
    """
    
    def __init__(self, vol, a_transversal, a_coronal, a_sagittal, a_text):
        
        # Create text objects
        self._labelx = vv.Label(a_text)
        self._labely = vv.Label(a_text)
        self._labelz = vv.Label(a_text)
        self._labelx.position = 10,10
        self._labely.position = 10,30
        self._labelz.position = 10,50
        
        # Create Finish button
        self._finished = False
        self._but = vv.PushButton(a_text)
        self._but.position = 10,80
        self._but.text = 'Finish'
        
        # Get short name for sampling
        if isinstance(vol, Aarray):
            self._sam = sam = vol.sampling
        else:
            self._sam = None
            sam = (1,1,1)
        
        # Calculate mips and deal with anisotropy
        mipz = np.max(vol,0)
        mipz = Aarray(mipz, (sam[1], sam[2]))
        mipy = np.max(vol,1)
        mipy = Aarray(mipy, (sam[0], sam[2]))
        mipx = np.max(vol,2)
        mipx = Aarray(mipx, (sam[0], sam[1]))
        
        # Display the mips
        vv.imshow(mipz, axes=a_transversal)
        vv.imshow(mipy, axes=a_coronal)
        vv.imshow(mipx, axes=a_sagittal)
        
        # Initialize range objects
        self._range_transversal = RangeWobject2D(a_transversal, mipz)
        self._range_coronal = RangeWobject2D(a_coronal, mipy)
        self._range_sagittal = RangeWobject2D(a_sagittal, mipx)
        
        # Get list of all range wobjects
        self._rangeWobjects = [self._range_transversal,
            self._range_coronal, self._range_sagittal]
        
        # Bind events
        fig = a_text.GetFigure()
        fig.eventClose.Bind(self._OnFinish)
        self._but.eventPress.Bind(self._OnFinish)
        for r in self._rangeWobjects:
            r.eventRangeUpdated.Bind(self._OnRangeUpdated)
        
        # Almost done
        self._SetTexts()
    
    
    def _OnRangeUpdated(self, event):
        # Get ranges of wobject that fired the event
        rangex, rangey = event.owner._rangex, event.owner._rangey
        
        # Update ranges in other wobjects
        if event.owner is self._range_transversal:
            self._range_coronal._rangex = rangex.Copy()
            self._range_sagittal._rangex = rangey.Copy()
        elif event.owner is self._range_coronal:
            self._range_transversal._rangex = rangex.Copy()
            self._range_sagittal._rangey = rangey.Copy()
        elif event.owner is self._range_sagittal:
            self._range_transversal._rangey = rangex.Copy()
            self._range_coronal._rangey = rangey.Copy()
        else:
            print('unknown owner! %s' % repr(event.owner))
        
        # Invalidate all coordinates
        for r in self._rangeWobjects:
            r._cordsBuffer = None
        
        # Set texts
        self._SetTexts()
        
        # Draw all axes
        for r in self._rangeWobjects:
            r.Draw()
    
    
    def _SetTexts(self):
        
        # Get actual ranges in 3D
        rx = self._range_transversal._rangex
        ry = self._range_transversal._rangey
        rz = self._range_coronal._rangey
        
        # Get short names for labels
        lx, ly, lz = self._labelx, self._labely, self._labelz
        
        # Apply texts
        if self._sam:
            tmp = '%s: %i pixels (%i to %i) > %2.1f mm'
            sam = self._sam
            lx.text =  tmp % ('x', rx.range, rx.min, rx.max, rx.range*sam[2])
            ly.text =  tmp % ('y', ry.range, ry.min, ry.max, ry.range*sam[1])
            lz.text =  tmp % ('z', rz.range, rz.min, rz.max, rz.range*sam[0])
        else:
            tmp = '%s: %i pixels (%i to %i)'
            lx.text =  tmp % ('x', rx.range, rx.min, rx.max)
            ly.text =  tmp % ('y', ry.range, ry.min, ry.max)
            lz.text =  tmp % ('z', rz.range, rz.min, rz.max)
    
    
    def _OnFinish(self, event):
        self._finished = True



def crop3d(vol, fig=None):
    """ crop3d(vol, fig=None)
    Manually crop a volume. In the given figure (or a new figure if None),
    three axes are created that display the transversal, sagittal and
    coronal MIPs (maximum intensity projection) of the volume. The user
    can then use the mouse to select a 3D range to crop the data to.
    """
    vv.use()
    
    # Create figure?
    if fig is None:
        fig = vv.figure()
        figCleanup = True
    else:
        fig.Clear()
        figCleanup = False
    
    # Create three axes and a wibject to attach text labels to
    a1 = vv.subplot(221)
    a2 = vv.subplot(222)
    a3 = vv.subplot(223)
    a4 = vv.Wibject(fig)
    a4.position = 0.5, 0.5, 0.5, 0.5
    
    # Set settings
    for a in [a1, a2, a3]:
        a.showAxis = False
    
    # Create cropper3D instance
    cropper3d = Cropper3D(vol, a1, a3, a2, a4)
    
    # Enter a mainloop
    while not cropper3d._finished:
        vv.processEvents()
        time.sleep(0.01)
    
    # Clean up figure (close if we opened it)
    fig.Clear()
    fig.DrawNow()
    if figCleanup:
        fig.Destroy()
    
    # Obtain ranges
    rx = cropper3d._range_transversal._rangex
    ry = cropper3d._range_transversal._rangey
    rz = cropper3d._range_coronal._rangey
    
    # Perform crop
    vol2 = vol[int(rz.min):int(rz.max),
               int(ry.min):int(ry.max),
               int(rx.min):int(rx.max)]
    
    # Done
    return vol2

    
if __name__ == '__main__':
    # testing
    
    vol1 = vv.aVolume(size=128)
    vol2 = crop3d(vol1)
    print('shape1:', vol1.shape)
    print('shape2:', vol2.shape)
