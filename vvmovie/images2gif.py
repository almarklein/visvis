#   Copyright (c) 2010, Almar Klein
#   All rights reserved.
#
#   This code is subject to the (new) BSD license:
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY 
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" Module images2gif

Provides functionality for reading and writing animated GIF images.
Use writeGif to write a series of numpy arrays or PIL images as an 
animated GIF. Use readGif to read an animated gif as a series of numpy
arrays.

Many thanks to Ant1 for:
* noting the use of "palette=PIL.Image.ADAPTIVE", which significantly
  improves the results. 
* the modifications to save each image with its own palette, or optionally
  the global palette (if its the same).

- based on gifmaker (in the scripts folder of the source distribution of PIL)
- based on gif file structure as provided by wikipedia

"""

import os

try:
    import PIL
    from PIL import Image, ImageChops
    from PIL.GifImagePlugin import getheader, getdata
except ImportError:
    PIL = None

try:
    import numpy as np
except ImportError:
    np = None    

# getheader gives a 87a header and a color palette (two elements in a list).
# getdata()[0] gives the Image Descriptor up to (including) "LZW min code size".
# getdatas()[1:] is the image data itself in chuncks of 256 bytes (well
# technically the first byte says how many bytes follow, after which that
# amount (max 255) follows).

def checkImages(images):
    """ checkImages(images)
    Check numpy images and correct intensity range etc.
    The same for all movie formats.
    """ 
    # Init results
    images2 = []
    
    for im in images:
        if PIL and isinstance(im, PIL.Image.Image):
            # We assume PIL images are allright
            images2.append(im)
        
        elif np and isinstance(im, np.ndarray):
            # Check and convert dtype
            if im.dtype == np.uint8:
                images2.append(im) # Ok
            elif im.dtype in [np.float32, np.float64]:
                im = im.copy()
                im[im<0] = 0
                im[im>1] = 1
                im *= 255
                images2.append( im.astype(np.uint8) )
            else:
                im = im.astype(np.uint8)
                images2.append(im)
            # Check size
            if im.ndim == 2:
                pass # ok
            elif im.ndim == 3:
                if im.shape[2] not in [3,4]:
                    raise ValueError('This array can not represent an image.')
            else:
                raise ValueError('This array can not represent an image.')
        else:
            raise ValueError('Invalid image type: ' + str(type(im)))
    
    # Done
    return images2


def intToBin(i):
    """ Integer to two bytes """
    # devide in two parts (bytes)
    i1 = i % 256
    i2 = int( i/256)
    # make string (little endian)
    return chr(i1) + chr(i2)


def getheaderAnim(im):
    """ Animation header. To replace the getheader()[0] """
    bb = "GIF89a"
    bb += intToBin(im.size[0])
    bb += intToBin(im.size[1])
    bb += "\x87\x00\x00"
    return bb


def getImageDescriptor(im):
    """ Used for the local color table properties per image.
    Otherwise global color table applies to all frames irrespective of
    wether additional colours comes in play that require a redefined palette
    Still a maximum of 256 color per frame, obviously.
    
    Written by Ant1 on 2010-08-22
    """
    bb = '\x2C' # Image separator,
    bb += intToBin( 0 ) # Left position
    bb += intToBin( 0 ) # Top position
    bb += intToBin( im.size[0] ) # image width
    bb += intToBin( im.size[1] ) # image height
    bb += '\x87' # packed field : local color table flag1, interlace0, sorted table0, reserved00, lct size111=7=2^(7+1)=256.
    # LZW minimum size code now comes later, begining of [image data] blocks
    return bb


def getAppExt(loops=float('inf')):
    """ Application extention. Part that specifies amount of loops. 
    If loops is inf, it goes on infinitely.
    """
    if loops == 0:
        loops = 2**16-1
        #bb = "" # application extension should not be used
                # (the extension interprets zero loops
                # to mean an infinite number of loops)
                # Mmm, does not seem to work
    if True:
        bb = "\x21\xFF\x0B"  # application extension
        bb += "NETSCAPE2.0"
        bb += "\x03\x01"
        if loops == float('inf'):
            loops = 2**16-1
        bb += intToBin(loops)
        bb += '\x00'  # end
    return bb


def getGraphicsControlExt(duration=0.1):
    """ Graphics Control Extension. A sort of header at the start of
    each image. Specifies transparancy and duration. """
    bb = '\x21\xF9\x04'
    bb += '\x08'  # no transparancy
    bb += intToBin( int(duration*100) ) # in 100th of seconds
    bb += '\x00'  # no transparant color
    bb += '\x00'  # end
    return bb


def _writeGifToFile(fp, images, durations, loops):
    """ Given a set of images writes the bytes to the specified stream.
    """
    
    # Obtain palette for all images and count each occurance
    palettes, occur = [], []
    for im in images: 
        palettes.append( getheader(im)[1] )
    for palette in palettes: 
        occur.append( palettes.count( palette ) )
    
    # Select most-used palette as the global one (or first in case no max)
    globalPalette = palettes[ occur.index(max(occur)) ]
    
    # Init
    frames = 0
    firstFrame = True
    
    
    for im, palette in zip(images, palettes):
        
        if firstFrame:
            # Write header
            
            # Gather info
            header = getheaderAnim(im)
            appext = getAppExt(loops)
            
            # Write
            fp.write(header)
            fp.write(globalPalette)
            fp.write(appext)
            
            # Next frame is not the first
            firstFrame = False
        
        if True:
            # Write palette and image data
            
            # Gather info
            data = getdata(im) 
            imdes, data = data[0], data[1:]       
            graphext = getGraphicsControlExt(durations[frames])
            # Make image descriptor suitable for using 256 local color palette
            lid = getImageDescriptor(im) 
            
            # Write local header
            if palette != globalPalette:
                # Use local color palette
                fp.write(graphext)
                fp.write(lid) # write suitable image descriptor
                fp.write(palette) # write local color table
                fp.write('\x08') # LZW minimum size code
            else:
                # Use global color palette
                fp.write(graphext)
                fp.write(imdes) # write suitable image descriptor
            
            # Write image data
            for d in data:
                fp.write(d)
        
        # Prepare for next round
        frames = frames + 1
    
    fp.write(";")  # end gif
    return frames


## Exposed functions 

def writeGif(filename, images, duration=0.1, repeat=True, dither=False):
    """ writeGif(filename, images, duration=0.1, repeat=True, dither=False)
    
    Write an animated gif from the specified images. Duration may also
    be a list with durations for each frame. Repeat can also be an 
    integer specifying the amount of loops.
    
    Images should be a list consisting of PIL images or numpy arrays. 
    The latter should be between 0 and 255 for integer types, and 
    between 0 and 1 for float types.
    
    """
    
    # Check PIL
    if PIL is None:
        raise RuntimeError("Need PIL to write animated gif files.")
    
    # Check images
    images = checkImages(images)
    
    # Check loops
    if repeat is False: 
        loops = 1
    elif repeat is True:
        loops = 0 # zero means infinite
    else:
        loops = int(repeat)
    
    # More init
    AD = Image.ADAPTIVE
    images2 = []
    
    # Convert to paletted PIL images
    for im in images:
        if isinstance(im, Image.Image):
            images2.append( im.convert('P', palette=AD, dither=dither) )
        elif np and isinstance(im, np.ndarray):
            if im.ndim==3 and im.shape[2]==3:
                im = Image.fromarray(im,'RGB').convert('P', 
                                                    palette=AD, dither=dither)
            elif im.ndim==2:
                im = Image.fromarray(im,'L').convert('P', 
                                                    palette=AD, dither=dither)
            images2.append(im)
    
    # Check duration
    if hasattr(duration, '__len__'):
        if len(duration) == len(images2):
            durations = [d for d in duration]
        else:
            raise ValueError("len(duration) doesn't match amount of images.")
    else:
        duration = [duration for im in images2]
    
    # Open file
    fp = open(filename, 'wb')
    
    # Write
    try:
        n = _writeGifToFile(fp, images2, duration, loops)
    finally:
        fp.close()
    

def readGif(filename, asNumpy=True):
    """ readGif(filename, asNumpy=True)
    
    Read images from an animated GIF file.  Returns a list of numpy 
    arrays, or, if asNumpy is false, a list if PIL images.
    
    """
    
    # Check PIL
    if PIL is None:
        raise RuntimeError("Need PIL to read animated gif files.")
    
    # Check Numpy
    if np is None:
        raise RuntimeError("Need Numpy to read animated gif files.")
    
    # Check whether it exists
    if not os.path.isfile(filename):
        raise IOError('File not found: '+str(filename))
    
    # Load file using PIL
    pilIm = PIL.Image.open(filename)    
    pilIm.seek(0)
    
    # Read all images inside
    images = []
    try:
        while True:
            # Get image as numpy array
            tmp = pilIm.convert() # Make without palette
            a = np.asarray(tmp)
            if len(a.shape)==0:
                raise MemoryError("Too little memory to convert PIL image to array")
            # Store, and next
            images.append(a)
            pilIm.seek(pilIm.tell()+1)
    except EOFError:
        pass
    
    # Convert to normal PIL images if needed
    if not asNumpy:
        images2 = images
        images = []
        for im in images2:            
            images.append( PIL.Image.fromarray(im) )
    
    # Done
    return images


if __name__ == '__main__':
    im = np.zeros((200,200), dtype=np.uint8)
    im[10:30,:] = 100
    im[:,80:120] = 255
    im[-50:-40,:] = 50
    
    images = [im*1.0, im*0.8, im*0.6, im*0.4, im*0]
    writeGif('lala3.gif',images, duration=0.5, dither=0)
