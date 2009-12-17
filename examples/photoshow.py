""" SCRIPT photoshow
An example program that shows all photos in a directory,
allowing easy zooming on each photo.
"""

# todo: icon in app
# todo: name of window (not "figure 1")
# sometimes first photo is not displayed black?
# todo: use pyfltk backend
    
#from PyQt4 import QtCore, QtGui, QtGui as qt
import wx

import visvis as vv
import numpy as np
import threading, time
import os, gc


# create app
#app = QtGui.QApplication([])
#vv.backends.use('qt4')
app = wx.PySimpleApp() 
vv.backends.use('wx')


# define figure and axes (globals in this module)
f = vv.figure()
a = vv.gca()
a.position = 0,0,1,1
a.bgcolor = 0,0,0

class PhotoStore(threading.Thread):
    def __init__(self, filenames):
        threading.Thread.__init__(self)
        
        # list of all filenames
        self.filenames = filenames
        # list of buffered photos
        self.photos = {}
        # current index
        self.index = 0
        # stop?
        self.stop = False        
        # the lock
        self.thelock = threading.RLock()
    
    
    def GetPhoto(self, index):
        """ Get a photo with the specified index.
        This method is thread save and blocks untill the
        photo is available. """
        
        # set index
        self.thelock.acquire()
        self.index = index
        self.thelock.release()
        
        # retrieve photo
        thephoto = None
        t0 = time.clock()+2.0
        while thephoto is None and time.clock() < t0:
            self.thelock.acquire()
            if index in self.photos:
                thephoto = self.photos[index]
            self.thelock.release()
            time.sleep(0.02)
        if thephoto is None:
            print "warning, photo not available (yet)"
        return thephoto
    
    
    def PutPhoto(self, deltaIndex):
        
        # calculate index, wrap around
        index = self.index + deltaIndex
        if index >= len(self.filenames):
            index = index - len(self.filenames)
        if index < 0:
            index = len(self.filenames) + index
        
        # check availability
        self.thelock.acquire()
        try:
            if index not in self.photos:
                im = vv.imread( self.filenames[index] )
                self.photos[index] = im
                print "loaded", self.filenames[index], '(%i)'%len(self.photos)
        except Exception, why:
            print "Error:", why
        finally:
            self.thelock.release()
    
    
    def CleanPhotos(self, keep):
        
        # calculate indices, wrap around
        keep2 = []
        for deltaIndex in keep:            
            index = self.index + deltaIndex
            if index >= len(self.filenames):
                index = index - len(self.filenames)
            if index < 0:
                index = len(self.filenames) + index
            keep2.append(index)
        
        # check removables
        toremove = []
        for index in self.photos:
            if index not in keep2:
                toremove.append(index)
        
        # remove
        for index in toremove:
            del self.photos[index]
        
        # clean up memory        
        gc.collect()
        time.sleep(0.1)
    
    
    def run(self):
        
        indices = [0, 1, -1, 2, -2]#, 3, -3]
        #indices = [0]
        
        while not self.stop:
            for i in indices:
                self.PutPhoto(i)
                time.sleep(0.02)
            self.CleanPhotos(indices)

    
class Photoshow:
    def __init__(self, path):
        path = os.path.abspath(path)
        
        # check
        if os.path.isdir(path):
            filepath = None  # just use dir
        elif os.path.isfile(path):
            filepath = path.lower()
            path = os.path.dirname(path)  # use dir of given file         
        else:
            print path
            raise RuntimeError("Invalid path given.")
        
        # get all photos
        self.path = path
        filenames = []
        index = 0
        for file in os.listdir(path):
            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                file = os.path.join(path,file)
                filenames.append(file)
                if filepath == file.lower():
                    index = len(filenames)-1
        self.N = len(filenames)
        
        self.t = None # for texture
        
        # set up callbacks
        f.eventKeyDown.Bind(self.OnKeyDown)
        f.eventClose.Bind(self.OnClose)
        
        # create store
        self.index = index # create index attribute
        self.store = PhotoStore(filenames)
        self.store.start()
    
    
    def Start(self, index=0):
        self.ShowPhoto()
    
    
    def OnClose(self, event):
        self.store.stop = True

    
    def OnKeyDown(self, event):
        if event.key in [ord(' '), vv.KEY_DOWN, vv.KEY_RIGHT, vv.KEY_PAGEDOWN]:
            # increase index
            self.index += 1
            if self.index >= self.N:
                self.index = 0
            self.ShowPhoto()
        
        elif event.key in [vv.KEY_UP, vv.KEY_LEFT, vv.KEY_PAGEUP]:
            # decrease index
            self.index -= 1
            if self.index < 0:
                self.index = self.N-1
            self.ShowPhoto()
        
        elif event.text == '0':
            if self.t:
                self.t.aa = 0
                f.Draw()
        elif event.text == '1':
            if self.t:
                self.t.aa = 1
                f.Draw()
        elif event.text == '2':
            if self.t:
                self.t.aa = 2
                f.Draw()
        elif event.text == '3':
            if self.t:
                self.t.aa = 3
                f.Draw()

    
    def ShowPhoto(self):
        
        # get photo
        im = self.store.GetPhoto(self.index)
        if im is None:
            return
        
        if 1:
            # fast
            if self.t:
                self.t.SetData(im)
            else:
                a.Clear()
                self.t = vv.imshow(im,[0,255],a, aa=1)
            a.SetLimits()
            f.Draw()
        else:
            # slow            
            a.Clear()
            aa = 1
            if self.t:
                aa = self.t.aa            
            self.t = vv.imshow(im,[0,255],a, aa=aa)
    
if __name__ == "__main__" or vv.misc.isFrozen():
    #p = Photoshow(r'C:\tmp\fotos italie 2009')
    #p = Photoshow(r'K:\temp\almar\fotos spie 2009')
    import sys
    p = Photoshow(sys.argv[1])
    p.Start(p.index)
    #app.exec_()
    app.MainLoop()
    