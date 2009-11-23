""" Record all drawings done to a figure or axes as a list of images. """

import visvis as vv

from visvis.images2gif import writeGif
from visvis.images2swf import writeSwf

import OpenGL.GL as gl
import OpenGL.GL.ARB.shader_objects as gla
import OpenGL.GLU as glu

import numpy as np

class Recorder:
    """ Recorder class that makes snapshots right after each draw event.
    It allows storing of the movie in an animated gif.
    Get the raw frames using GetFrames().
    """
    
    def __init__(self, ob):
        # init
        self.ob = ob
        self.frames = []
        
        # register events
        f = ob.GetFigure()
        f.eventAfterDraw.Bind(self._OnAfterDraw)
    
    def _OnAfterDraw(self, event):
        im = vv.getframe(self.ob)
        self.frames.append(im)

    def Clear(self):
        """ Clear all recorded images up to now.
        """
        self.frames[:] = []

    def Stop(self):
        """ Stop recording. """
        f = self.ob.GetFigure()
        f.eventAfterDraw.Unbind(self._OnAfterDraw)
    
    def Continue(self):
        """ Continue recording. """
        f = self.ob.GetFigure()
        f.eventAfterDraw.Unbind(self._OnAfterDraw)        
        f.eventAfterDraw.Bind(self._OnAfterDraw)
    
    def GetFrames(self):
        """ Get a copy of the list (the frames itself are not copied) 
        recorded up to now. """
        return [frame for frame in self.frames]
    
    
    def ExportToGif(self, filename, duration=0.1, loops=0, dither=1):
        """ Export movie to a GIF. """
        writeGif(filename, self.GetFrames(), duration, loops, dither)
    
    def ExportToSwf(self, filename, fps=10):
        """ Export movie to a GIF. """
        writeSwf(filename, self.GetFrames(), fps)


def record(ob):
    """ record(object)
    Record all drawings done to a figure or axes.
    A Recorder instance is returned, with which the recording can
    be stopped, continued, exported to gif/swf, or the frames retrieved.
    """
    
    # establish wheter we can record that
    if not isinstance(ob, (vv.BaseFigure, vv.Axes)):
        raise ValueError("The given object is not a figure nor an axes.")
    
    # create recorder
    return Recorder(ob)    
    