# This file is part of VISVIS. 
# Copyright (C) 2010 Almar Klein

import visvis as vv

# from visvis.images2gif import writeGif
# from visvis.images2swf import writeSwf

import OpenGL.GL as gl
import OpenGL.GL.ARB.shader_objects as gla
import OpenGL.GLU as glu

import os, time
import numpy as np

class Recorder:
    """ Recorder class that makes snapshots right after each draw event.
    It allows storing of the movie in an animated gif.
    Get the raw frames using GetFrames().
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
    
    
    def ExportToGif(self, filename, duration=0.1, loops=0, dither=1):
        """ ExportToGif(filename, duration=0.1, loops=0, dither=1)
        Export movie to an animated GIF file using PIL. Note that
        Gif only supports 256 colors, while SWF supports full 24 bit
        colors.
        """
        writeGif(filename, self.GetFrames(), duration, loops, dither)
    
    
    def ExportToSwf(self, filename, fps=10):
        """ ExportToSwf(filename, fps=10)
        Export movie to a Shockwave Flash (SWF) file.
        """
        writeSwf(filename, self.GetFrames(), fps)
    
    
    def ExportToImages(self, filename):
        """ ExportToImages(filename)
        Export movie to a series of image files. A sequence number 
        is introduced right before the final dot of the given filename.
        
        If the filename is on a non-existing path, it is created.
        """
        
        # Get dirname and filename
        filename = os.path.abspath(filename)
        dirname, filename = os.path.split(filename)
        
        # Create dir(s) if we need to
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        
        # Get frames
        frames = self.GetFrames()
        
        # Insert sequence number formatter
        formatter = '%04i'
        if len(frames) < 10:
            formatter = '%i'
        elif len(frames) < 100:
            formatter = '%02i'
        elif len(frames) < 1000:
            formatter = '%03i'
        #
        root, ext = os.path.splitext(filename)
        filename = root + formatter + ext
        
        # Write
        t0 = time.time()
        seq = 0
        for frame in frames:
            seq += 1
            fname = os.path.join(dirname, filename%seq)
            vv.imwrite(fname, frame)
        tt = time.time() - t0
        
        # Write message
        print "written %i images in %1.2f seconds (%1.0f ms/frame)" % (
        len(frames), tt, 1000*tt/len(frames) )
    
    
    def ExportToAvi(self, filename, fps=10, encoding='mpeg4'):
        """ ExportToAvi(self, filename, fps=10, encoding='mpeg4')
        Export movie to a AVI file, which is encoded with the given 
        encoding. Hint for Windows users: the 'msmpeg4v2' codec is 
        natively supported on Windows.
        
        Requires the "mencoder" application:
          * Most linux users can install using their package manager
          * There is a windows installer on the visvis website
        """
        import subprocess, shutil
        
        # Determine temp dir and create images
        tempDir = os.path.join( os.path.expanduser('~'), 'tempIms')
        self.ExportToImages( os.path.join(tempDir, 'im.jpg'))
        
        # Compile command to create avi
        command = "mencoder mf://*.jpg -mf fps=%i:type=jpg -ovc lavc "
        command += "-lavcopts vcodec=%s:mbd=2:trell "
        command += "-o output.avi"
        command = command % (int(fps), encoding)
        
        # Run mencodec
        S = subprocess.Popen(command, shell=True, cwd=tempDir,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Show what mencodec has to say
        print S.stdout.read()
        
        if S.wait():    
            # An error occured, show
            print S.stderr.read() 
            # Clean up
            shutil.rmtree(tempDir)
        else:
            # Copy avi
            shutil.copy(os.path.join(tempDir, 'output.avi'), filename)
            # Clean up
            shutil.rmtree(tempDir)
            # Done
            print 'Successfully wrote avi file.'


def record(ob):
    """ record(object)
    Take a snapshot if the given figure or axes after each draw.
    A Recorder instance is returned, with which the recording can
    be stopped, continued, exported to gif and swf, or the frames retrieved.
    """
    
    # establish wheter we can record that
    if not isinstance(ob, (vv.BaseFigure, vv.Axes)):
        raise ValueError("The given object is not a figure nor an axes.")
    
    # create recorder
    return Recorder(ob)    
