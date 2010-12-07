# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

import visvis as vv

import OpenGL.GL as gl
import OpenGL.GL.ARB.shader_objects as gla
import OpenGL.GLU as glu

import os, time
import numpy as np

class Recorder:
    """ Recorder(object)
    
    Recorder class that makes snapshots right after each draw event.
    
    It is then possible to export the movie to SWF, GIF, AVI, or a series
    of images.
    
    See also vv.movieWrite().
    
    """
    
    def __init__(self, ob):
        # init
        self._ob = ob
        self._frames = []
        
        # register events
        f = ob.GetFigure()
        f.eventAfterDraw.Bind(self._OnAfterDraw)
    
    
    def _OnAfterDraw(self, event):
        im = vv.getframe(self._ob)
        self._frames.append(im)
    
    
    def Clear(self):
        """ Clear()
        Clear all recorded images up to now.
        """
        self._frames[:] = []
    
    
    def Stop(self):
        """ Stop()
        Stop recording. """
        f = self._ob.GetFigure()
        f.eventAfterDraw.Unbind(self._OnAfterDraw)
    
    
    def Continue(self):
        """ Continue()
        Continue recording. """
        f = self._ob.GetFigure()
        f.eventAfterDraw.Unbind(self._OnAfterDraw)        
        f.eventAfterDraw.Bind(self._OnAfterDraw)
    
    
    def GetFrames(self):
        """ GetFrames()
        Get a copy of the list (the frames itself are not copied) 
        recorded up to now. """
        return [frame for frame in self._frames]
    
    
    def Export(self, filename, duration=0.1, repeat=True, **kwargs):
        """ Export(self, filename, duration=0.1, repeat=True, **kwargs)
        
        Export recorded movie to either:
          * a series of images
          * an animated GIF 
          * an SWF (shockwave flash) file
          * an AVI file
        
        See vv.movieWrite for more information.
        
        """
        frames = self.GetFrames()
        vv.movieWrite(filename, frames, duration, repeat, **kwargs)


def record(ob):
    """ record(object)
    Take a snapshot of the given figure or axes after each draw.
    A Recorder instance is returned, with which the recording can
    be stopped, continued, and exported to GIF, SWF or AVI.
    """
    
    # establish wheter we can record that
    if not isinstance(ob, (vv.BaseFigure, vv.Axes)):
        raise ValueError("The given object is not a figure nor an axes.")
    
    # create recorder
    return Recorder(ob)    
