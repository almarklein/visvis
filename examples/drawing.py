#!/usr/bin/env python
""" This example illustrates how to draw lines in an axis,
for instance for creating annotations.
"""

import visvis as vv
from visvis import Point, Pointset

class Drawer:
    
    def __init__(self):
        
        # Create figure and axes
        vv.figure()
        self._a = a = vv.gca()
        vv.title("Hold mouse to draw lines. Use 'rgbcmyk' and '1-9' keys.")
        
        # Set axes
        a.SetLimits((0,1), (0,1))
        a.cameraType = '2d'
        a.daspectAuto = False
        a.axis.showGrid = True
        
        # Init variables needed during drawing
        self._active = None
        self._pp = Pointset(2)
        
        # Create null and empty line objects
        self._line1 = None
        self._line2 = vv.plot(vv.Pointset(2), ls='+', lc='c', lw='2', axes=a)
        
        # Bind to events
        a.eventMouseDown.Bind(self.OnDown)
        a.eventMouseUp.Bind(self.OnUp)
        a.eventMotion.Bind(self.OnMotion)
        a.eventKeyDown.Bind(self.OnKey)
    
    
    def OnKey(self, event):
        """ Called when a key is pressed down in the axes.
        """
        
        if event.text and event.text.lower() in 'rgbcmywk':
            self._line2.lc = event.text.lower()
        else:
            try:
                tickness = int(event.text)
            except Exception:
                tickness = 0
            if tickness > 0:
                self._line2.lw = tickness
    
    
    def OnDown(self, event):
        """ Called when the mouse is pressed down in the axes.
        """
        
        # Only process left mouse button
        if event.button != 1:
            return False
        
        # Store location
        self._active = Point(event.x2d, event.y2d)
        
        # Clear temp line object
        if self._line1:
            self._line1.Destroy()
        
        # Create line objects
        tmp = Pointset(2)
        tmp.append(self._active)
        tmp.append(self._active)
        self._line1 = vv.plot(tmp, lc='r', lw='1', axes=self._a, axesAdjust=0)
        
        # Draw
        self._a.Draw()
        
        # Prevent dragging by indicating the event needs no further handling
        return True

    
    def OnMotion(self, event):
        """ Called when the mouse is moved in the axes.
        """
        
        if self._active and self._line1:
            # Update line
            tmp = Pointset(2)
            tmp.append(self._active)
            tmp.append(event.x2d, event.y2d)
            self._line1.SetPoints(tmp)
            # Draw
            self._a.Draw()
    
    
    def OnUp(self, event):
        """ Called when the mouse is released (when first pressed down
        in the axes).
        """
        
        # Only if a point is active
        if self._active is None:
            return False
        
        # Get points
        p1 = self._active
        p2 = Point(event.x2d, event.y2d)
        
        # Add!
        self._pp.append(p1)
        self._pp.append(p2)
        
        # We're done with this one
        self._active = None
        
        # Clear temp line object
        if self._line1:
            self._line1.Destroy()
            self._line1 = None
        
        # Update lines
        self._line2.SetPoints(self._pp)
        
        # Draw
        self._a.Draw()


if __name__ == '__main__':
    d = Drawer()
    app = vv.use()
    app.Run()
