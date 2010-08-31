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

""" Package vvmovie (visvis-movie)
All submodules have been designed to be work independant of each-other 
(except the AVI module, which requires the IMS module).

Provides the following functions:

  * readGif & writeGif  -> a movie stored as animated GIF
  * readSwf & writeSwf  -> a movie stored as shockwave flash
  * readAvi & writeAvi  -> a movie stored as compressed video
  * readIms & writeIms  -> a movie stored as a series of images

Two additional functions are provided for ease of use, that call
the right function depending on the used file extension:
  * movieRead
  * movieWrite

More information about compression and limitations:

  * GIF. Requires PIL. Animated GIF applies a color-table of maximal
    256 colors and applies poor compression. It's widely applicable though. 
  * SWF. Provides lossless storage of movie frames with good (ZLIB) 
    compression. Reading of SWF files is limited to images stored using ZLIB
    compression (no JPEG files). Requires no external libraries.
  * AVI. Requires ffmpeg. Most Linux can obtain it using their package
    manager. Windows users can use the installer at the visvis website.
    Provides excelent mpeg4 (or any other supported by ffmpeg) compression.
    Not intended for reading very large movies.
  * IMS. Requires PIL. Quality depends on the used image type. Use png for  
    lossless compression and jpg otherwise.

"""

import os, time

from images2gif import readGif, writeGif
from images2swf import readSwf, writeSwf
from images2avi import readAvi, writeAvi
from images2ims import readIms, writeIms


def movieWrite(filename, images, duration=0.1, repeat=True, encoding='mpeg4', 
                **kwargs):
    """ movieWrite(fname, images, duration=0.1, repeat=True, encoding='mpeg4')
    
    Write the movie specified in images to GIF, SWF, AVI, or a series
    of images (PNG,JPG,TIF,BMP). Images should be a list consisting of
    PIL images or numpy arrays. The latter should be between 0 and 255 
    for integer types, and between 0 and 1 for float types.
    
      * duration is the duration per frame for GIF, SWF and AVI. For GIF
        and SWF, the duration can be set per frame (using a list).
      * repeat can be used in GIF and SWF to indicate that the movie should
        loop. For GIF, an integer can be given to specify the number of loops.      
      * encoding is the encoding to use for AVI. Hint for Windows users: 
        the 'msmpeg4v2' codec is natively supported on Windows.
    
    When writing a series of images: if the filenenumber contains an 
    asterix, a sequence number is introduced at its location. Otherwise 
    the sequence number is introduced right before the final dot. To 
    enable easy creation of a new directory with image files, it is made 
    sure that the full path exists.
    
    Notice: writing AVI requires the "ffmpeg" application:
      * Most linux users can install it using their package manager
      * There is a windows installer on the visvis website
    
    """
    
    # Get extension
    EXT = os.path.splitext(filename)[1].upper()
    
    # Start timer
    t0 = time.time()
    
    # Write
    if EXT == '.GIF':
        writeGif(filename, images, duration, repeat, **kwargs)
    elif EXT == '.SWF':
        writeSwf(filename, images, duration, repeat, **kwargs)
    elif EXT in ['.AVI', '.MPG', '.MPEG']:
        writeAvi(filename, images, duration, encoding, **kwargs)
    elif EXT in ['.JPG', '.JPEG', '.PNG', '.TIF', '.TIFF', '.BMP']:
        writeIms(filename, images, **kwargs)
    else:
        raise ValueError('Given file extension not valid: '+EXT)
    
    # Stop timer
    t1 = time.time()
    dt = t1-t0
    
    # Notify    
    print "Wrote %i frames to %s in %1.2f seconds (%1.0f ms/frame)" % (
                        len(images), EXT[1:], dt, 1000*dt/len(images))


def movieRead(filename, **kwargs):
    """ movieRead(fname)
    
    Read the movie from GIF, SWF, AVI, or a series of images (PNG,JPG,TIF,BMP). 
    Returns a list of numpy arrays.
    
    Notice: reading AVI requires the "ffmpeg" application:
      * Most linux users can install it using their package manager
      * There is a windows installer on the visvis website
    
    """
    
    # Get extension
    EXT = os.path.splitext(filename)[1].upper()
    
    # Start timer
    t0 = time.time()
    
    # Write
    if EXT == '.GIF':
        images = readGif(filename, **kwargs)
    elif EXT == '.SWF':
        images = readSwf(filename, **kwargs)
    elif EXT in ['.AVI', '.MPG', '.MPEG']:
        images = readAvi(filename, **kwargs)
    elif EXT in ['.JPG', '.JPEG', '.PNG', '.TIF', '.TIFF', '.BMP']:
        images = readIms(filename, **kwargs)
    else:
        raise ValueError('Given file extension not valid: '+EXT)
    
    # Stop timer
    t1 = time.time()
    dt = t1-t0
    
    # Notify    
    print "Read %i frames from %s in %1.2f seconds (%1.0f ms/frame)" % (
                        len(images), EXT[1:], dt, 1000*dt/len(images))

    # Done
    return images

