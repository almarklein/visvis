# -*- coding: utf-8 -*-
# Copyright (c) 2010, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

""" Module wobjects

All wobjects are inserted in this namespace, thereby providing
the user with a list of all wobjects. All wobjects are also
inserted in the root visvis namespace.

"""

from base import Wobject
from textRender import Text
from line import Line
from textures import Texture2D, Texture3D
from polygonalModeling import Mesh, OrientableMesh

class MotionDataContainer(Wobject):
    """ MotionDataContainer(parent, interval=100)
    
    The motion data container is a wobject that can contain
    several data, which are displayed alternatively using a 
    timer.
    
    The data are simply stored as the wobject's children, and are
    made visible one at a time.
    
    Example
    -------
    # read image
    ims = [vv.imread('lena.png')]

    # make list of images: decrease red channel in subsequent images
    for i in range(9):
        im = ims[i].copy()
        im[:,:,0] = im[:,:,0]*0.9
        ims.append(im)

    # create figure, axes, and data container object
    a = vv.gca()
    m = vv.MotionDataContainer(a)

    # create textures, loading them into opengl memory, and insert into container.
    for im in ims:
        t = vv.imshow(im)
        t.parent = m
    
    """
    
    def __init__(self, parent, interval=100):
        Wobject.__init__(self,parent)    
        
        # setup timer        
        from events import Timer
        self._timer = Timer(self, interval, False)
        self._timer.Bind(self._Next)
        self._timer.Start()
        
        
        # counter to keep track which object was visible.
        self._counter = -1
    
    @property
    def timer(self):
        """ Get the timer object used to make the objects visible. 
        """
        return self._timer
    
    
    def _Next(self, event):
        
        a = self.GetAxes()
        if not a:            
            return
        
        # increase counter
        self._counter += 1
        if self._counter >= len(self._children):
            self._counter = 0
        
        # set all invisible
        for child in self._children:
            child.visible = False
        # except one
        if self._children:
            self._children[self._counter].visible = True
        
        # show it!        
        a.Draw()

