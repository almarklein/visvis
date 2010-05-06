#   This file is part of VISVIS. This file may be distributed 
#   seperately, but under the same license as VISVIS (LGPL).
#    
#   images2swf is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as 
#   published by the Free Software Foundation, either version 3 of 
#   the License, or (at your option) any later version.
# 
#   images2swf is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
# 
#   You should have received a copy of the GNU Lesser General Public 
#   License along with this program.  If not, see 
#   <http://www.gnu.org/licenses/>.
#
#   Copyright (C) 2009 Almar Klein

""" Module images2swf

Provides a function (writeSwf) to store a series of PIL images or numpy 
arrays in an SWF movie, that can be played on a wide range of OS's. 

This module came into being because I wanted to store a series of images
in a movie that can be viewed by other people, and which I can embed in 
flash presentations. For writing AVI or MPEG you really need a c/c++ 
library, and allthough the filesize is then very small, the quality is 
sometimes not adequate. Besides I'd like to be independant of yet another 
package. I tried writing animated gif using PIL (which is widely available), 
but the quality is so poor because it only allows for 256 different colours.
I also looked into MNG and APNG, two standards similar to the PNG stanard.
Both standards promise exactly what I need. However, hardly any application
can read those formats, and I cannot import them in flash. 

Therefore I decided to check out the swf file format, which is very well
documented. This is the result: a pure python module to create an SWF file
that shows a series of images. The images are stored using the DEFLATE
algorithm (same as PNG and ZIP and which is included in the standard Python
distribution). As this compression algorithm is much more effective than 
that used in GIF images, we obtain better quality (24 bit colours + alpha
channel) while still producesing smaller files (a test showed ~75%).
Although SWF also allows for JPEG compression, doing so would probably 
require a third party library (because encoding JPEG is much harder).

This module requires Python 2.x and numpy.

sources and tools:
- SWF on wikipedia
- Adobes "SWF File Format Specification" version 10
  (http://www.adobe.com/devnet/swf/pdf/swf_file_format_spec_v10.pdf)
- swftools (swfdump in specific) for debugging
- iwisoft swf2avi can be used to convert swf to avi/mpg/flv with really
  good quality, while file size is reduced with factors 20-100.
  A good program in my opinion. The free version has the limitation
  of a watermark in the upper left corner. 

$Author$
$Date$
$Rev$

"""

try: 
    import PIL.Image
except ImportError:
    PIL = None

import numpy as np
import zlib
import sys, time


## Base functions and classes

if int(sys.version[0])<3:
    bytes = str

class BitArray:
    """ Dynamic array of bits that automatically resizes
    with factors of two. 
    Append bits using .Append() or += 
    You can reverse bits using .Reverse()
    """
    
    def __init__(self, initvalue=None):
        self.data = np.zeros((16,), dtype=np.uint8)
        self._len = 0
        if initvalue is not None:
            self.Append(initvalue)
    
    def __len__(self):
        return self._len #self.data.shape[0]
    
    def __repr__(self):
        return self.data[:self._len].tostring()
    
    def _checkSize(self):
        # check length... grow if necessary
        arraylen = self.data.shape[0]
        if self._len >= arraylen:
            tmp = np.zeros((arraylen*2,), dtype=np.uint8)
            tmp[:self._len] = self.data[:self._len]
            self.data = tmp
    
    def __add__(self, value):
        self.Append(value)
        return self
    
    def Append(self, bits):
        
        # check input
        if isinstance(bits, BitArray):
            bits = str(bits)
        if isinstance(bits, int):
            bits = str(bits)
        if not isinstance(bits, basestring):
            raise ValueError("Append bits as strings or integers!")
        
        # add bits
        for bit in bits:
            self.data[self._len] = ord(bit)
            self._len += 1
            self._checkSize()
    
    def Reverse(self):
        """ In-place reverse. """
        tmp = self.data[:self._len].copy()
        self.data[:self._len] = np.flipud(tmp)
    
    def ToBytes(self):
        """ Convert to bytes. If necessary,
        zeros are padded to the end (right side).
        """
        bits = str(self)
        
        # determine number of bytes
        nbytes = 0
        while nbytes*8 < len(bits):
            nbytes +=1
        # pad
        bits = bits.ljust(nbytes*8, '0')
        
        # go from bits to bytes
        bb = bytes()
        for i in range(nbytes):
            tmp = int( bits[i*8:(i+1)*8], 2)
            bb += intToUint8(tmp)
        
        # done
        return bb


def intToUint32(i):
    number = int(i)
    n1, n2, n3, n4 = 1, 256, 256*256, 256*256*256
    b4, number = number // n4, number % n4
    b3, number = number // n3, number % n3
    b2, number = number // n2, number % n2
    b1 = number
    return chr(b1) + chr(b2) + chr(b3) + chr(b4)


def intToUint16(i):
    i = int(i)
    # devide in two parts (bytes)    
    i1 = i % 256
    i2 = int( i//256)
    # make string (little endian)
    return chr(i1) + chr(i2)


def intToUint8(i):
    return chr(int(i))
    

def intToBits(i,n=None):
    """ convert int to a string of bits (0's and 1's in a string), 
    pad to n elements. Convert back using int(ss,2). """
    ii = i
    
    # make bits    
    bb = BitArray()
    while ii > 0:
        bb += str(ii % 2)
        ii = ii >> 1
    bb.Reverse()
    
    # justify
    if n is not None:
        if len(bb) > n:
            raise ValueError("intToBits fail: len larger than padlength.")
        bb = str(bb).rjust(n,'0')
    
    # done
    return BitArray(bb)


def signedIntToBits(i,n=None):
    """ convert signed int to a string of bits (0's and 1's in a string), 
    pad to n elements. Negative numbers are stored in 2's complement bit
    patterns, thus positive numbers always start with a 0.
    """
    
    # negative number?
    ii = i    
    if i<0:
        # A negative number, -n, is represented as the bitwise opposite of
        ii = abs(ii) -1  # the positive-zero number n-1.
    
    # make bits    
    bb = BitArray()
    while ii > 0:
        bb += str(ii % 2)
        ii = ii >> 1
    bb.Reverse()
    
    # justify
    bb = '0' + str(bb) # always need the sign bit in front
    if n is not None:
        if len(bb) > n:
            raise ValueError("signedIntToBits fail: len larger than padlength.")
        bb = bb.rjust(n,'0')
    
    # was it negative? (then opposite bits)
    if i<0:
        bb = bb.replace('0','x').replace('1','0').replace('x','1')
    
    # done
    return BitArray(bb)


def twitsToBits(arr):
    """ Given a few (signed) numbers, store them 
    as compactly as possible in the wat specifief by the swf format.
    The numbers are multiplied by 20, assuming they
    are twits.
    Can be used to make the RECT record.
    """
    
    # first determine length using non justified bit strings
    maxlen = 1
    for i in arr:
        tmp = len(signedIntToBits(i*20))
        if tmp > maxlen:
            maxlen = tmp
    
    # build array
    bits = intToBits(maxlen,5) 
    for i in arr:
        bits += signedIntToBits(i*20, maxlen)
    
    return bits


def floatsToBits(arr):
    """ Given a few (signed) numbers, convert them to bits, 
    stored as FB (float bit values). We always use 16.16. 
    Negative numbers are not (yet) possible, because I don't
    know how the're implemented (ambiguity).
    """
    bits = intToBits(31, 5) # 32 does not fit in 5 bits!
    for i in arr:
        if i<0:
            raise ValueError("Dit not implement negative floats!")
        i1 = int(i)
        i2 = i - i1
        bits += intToBits(i1, 15)
        bits += intToBits(i2*2**16, 16)
    return bits
    
    

## Base Tag

class Tag:
    
    def __init__(self):
        self.bytes = ''        
        self.tagtype = -1
    
    def ProcessTag(self):
        """ Implement this to create the tag. """
        raise NotImplemented()
    
    def GetTag(self):
        """ Calls processTag and attaches the header. """
        self.ProcessTag()
        
        # tag to binary
        bits = intToBits(self.tagtype,10)
        
        # complete header uint16 thing
        bits += '1'*6 # = 63 = 0x3f
        # make uint16
        bb = intToUint16( int(str(bits),2) )
        bb = bytes(bb)
        
        # now add 32bit length descriptor
        bb += intToUint32(len(self.bytes))
        
        # done, attach and return
        bb += self.bytes
        return str(bb)
    
    def MakeRectRecord(self, xmin, xmax, ymin, ymax):
        """ Simply uses makeCompactArray to produce
        a RECT Record. """
        return twitsToBits([xmin, xmax, ymin, ymax])

    def MakeMatrixRecord(self, scale_xy=None, rot_xy=None, trans_xy=None):
        
        # empty matrix?
        if scale_xy is None and rot_xy is None and trans_xy is None:
            return "0"*8
        
        # init
        bits = BitArray()
        
        # scale
        if scale_xy: 
            bits += '1'
            bits += floatsToBits([scale_xy[0], scale_xy[1]])
        else: 
            bits += '0'
        
        # rotation
        if rot_xy: 
            bits += '1'
            bits += floatsToBits([rot_xy[0], rot_xy[1]])
        else: 
            bits += '0'
        
        # translation (no flag here)
        if trans_xy: 
            bits += twitsToBits([trans_xy[0], trans_xy[1]])
        else: 
            bits += twitsToBits([0,0])
        
        # done
        return bits


## Control tags

class ControlTag(Tag):
    def __init__(self):
        Tag.__init__(self)


class FileAttributesTag(ControlTag):
    def __init__(self):
        ControlTag.__init__(self)
        self.tagtype = 69
    
    def ProcessTag(self):
        self.bytes = bytes( '\x00' * (1+3) )


class ShowFrameTag(ControlTag):
    def __init__(self):
        ControlTag.__init__(self)
        self.tagtype = 1
    def ProcessTag(self):
        self.bytes = bytes()

class SetBackgroundTag(ControlTag):
    """ Set the color in 0-255, or 0-1 (if floats given). """
    def __init__(self, *rgb):
        self.tagtype = 9
        if len(rgb)==1:
            rgb = rgb[0]
        self.rgb = rgb
    
    def ProcessTag(self):
        bb = bytes()
        for i in range(3):            
            clr = self.rgb[i]
            if isinstance(clr, float):
                clr = clr * 255
            bb += intToUint8(clr)
        self.bytes = bb


class DoActionTag(Tag):
    def __init__(self, action='stop'):
        Tag.__init__(self)
        self.tagtype = 12
        self.actions = [action]
    
    def Append(self, action):
        self.actions.append( action )
    
    def ProcessTag(self):
        bb = bytes()
        
        for action in self.actions:
            action = action.lower()            
            if action == 'stop':
                bb += '\x07'
            elif action == 'play':
                bb += '\x06'
            else:
                print "warning, unkown action: %s" % action
        
        bb += intToUint8(0)
        self.bytes = bb
        


## Definition tags

class DefinitionTag(Tag):
    counter = 0 # to give automatically id's
    def __init__(self):
        Tag.__init__(self)
        DefinitionTag.counter += 1
        self.id = DefinitionTag.counter  # id in dictionary


class BitmapTag(DefinitionTag):
    
    def __init__(self, im):
        DefinitionTag.__init__(self)
        self.tagtype = 36 # DefineBitsLossless2
        
        # convert image (note that format is ARGB)
        # even a grayscale image is stored in ARGB, nevetheless,
        # the fabilous deflate compression will make it that not much
        # more data is required for storing (25% or so, and less than 10%
        # when storing RGB as ARGB).
        
        if len(im.shape)==3:
            if im.shape[2] in [3, 4]:
                tmp = np.ones((im.shape[0], im.shape[1], 4), dtype=np.uint8)*255
                for i in range(3):
                    if im.dtype in [np.float32 or np.float64]:
                        tmp[:,:,i+1] = im[:,:,i]*255
                    else:
                        tmp[:,:,i+1] = im[:,:,i]
                if im.shape[2]==4:
                    tmp[:,:,0] = im[:,:,3] # swap channel where alpha is in
            else:
                raise ValueError("Invalid shape to be an image.")
            
        elif len(im.shape)==2:
            tmp = np.ones((im.shape[0], im.shape[1], 4), dtype=np.uint8)*255
            for i in range(3):
                if im.dtype in [np.float32 or np.float64]:                    
                    tmp[:,:,i+1] = im[:,:]*255
                else:
                    tmp[:,:,i+1] = im[:,:]
        
        else:
            raise ValueError("Invalid shape to be an image.")
        
        # we changed the image to uint8 4 channels.
        # now compress!
        self._data = zlib.compress(tmp.tostring(), zlib.DEFLATED)
        self.imshape = im.shape
    
    
    def ProcessTag(self):
        
        # build tag
        bb = bytes()   
        bb += intToUint16(self.id)   # CharacterID    
        bb += intToUint8(5)     # BitmapFormat
        bb += intToUint16(self.imshape[1])   # BitmapWidth
        bb += intToUint16(self.imshape[0])   # BitmapHeight       
        bb += self._data            # ZlibBitmapData
        
        self.bytes = bb


class PlaceObjectTag(ControlTag):
    def __init__(self, depth, idToPlace=None, xy=(0,0), move=False):
        ControlTag.__init__(self)
        self.tagtype = 26
        self.depth = depth
        self.idToPlace = idToPlace
        self.xy = xy
        self.move = move
    
    def ProcessTag(self):
        # retrieve stuff
        depth = self.depth
        xy = self.xy
        id = self.idToPlace
        
        # build PlaceObject2
        bb = bytes()
        if self.move:
            bb += '\x07'
        else:
            bb += '\x06'  # (8 bit flags): 4:matrix, 2:character, 1:move
        bb += intToUint16(depth) # Depth
        bb += intToUint16(id) # character id
        bb += self.MakeMatrixRecord(trans_xy=xy).ToBytes() # MATRIX record
        self.bytes = bb
    

class ShapeTag(DefinitionTag):
    def __init__(self, bitmapId, xy, wh):
        DefinitionTag.__init__(self)
        self.tagtype = 2
        self.bitmapId = bitmapId
        self.xy = xy
        self.wh = wh
    
    def ProcessTag(self):
        """ Returns a defineshape tag. with a bitmap fill """
        
        bb = bytes()
        bb += intToUint16(self.id)
        xy, wh = self.xy, self.wh
        tmp = self.MakeRectRecord(xy[0],wh[0],xy[1],wh[1])  # ShapeBounds
        bb += tmp.ToBytes()
        
        # make SHAPEWITHSTYLE structure
        
        # first entry: FILLSTYLEARRAY with in it a single fill style
        bb += intToUint8(1)  # FillStyleCount
        bb += '\x41' # FillStyleType  (0x41 or 0x43, latter is non-smoothed)
        bb += intToUint16(self.bitmapId)  # BitmapId
        #bb += '\x00' # BitmapMatrix (empty matrix with leftover bits filled)
        bb += self.MakeMatrixRecord(scale_xy=(20,20)).ToBytes()
        
#         # first entry: FILLSTYLEARRAY with in it a single fill style
#         bb += intToUint8(1)  # FillStyleCount
#         bb += '\x00' # solid fill
#         bb += '\x00\x00\xff' # color
        
        
        # second entry: LINESTYLEARRAY with a single line style
        bb += intToUint8(0)  # LineStyleCount
        #bb += intToUint16(0*20) # Width
        #bb += '\x00\xff\x00'  # Color
        
        # third and fourth entry: NumFillBits and NumLineBits (4 bits each)
        bb += '\x44'  # I each give them four bits, so 16 styles possible.
        
        self.bytes = bb
        
        # last entries: SHAPERECORDs ... (individual shape records not aligned)
        # STYLECHANGERECORD
        bits = BitArray()
        bits += self.MakeStyleChangeRecord(0,1,moveTo=(self.wh[0],self.wh[1]))
        # STRAIGHTEDGERECORD 4x
        bits += self.MakeStraightEdgeRecord(-self.wh[0], 0)
        bits += self.MakeStraightEdgeRecord(0, -self.wh[1])
        bits += self.MakeStraightEdgeRecord(self.wh[0], 0)
        bits += self.MakeStraightEdgeRecord(0, self.wh[1])
        
        # ENDSHAPRECORD
        bits += self.MakeEndShapeRecord()
        
        self.bytes += bits.ToBytes()
        
        # done
        #self.bytes = bb

    def MakeStyleChangeRecord(self, lineStyle=None, fillStyle=None, moveTo=None):
        
        # first 6 flags
        # Note that we use FillStyle1. If we don't flash (at least 8) does not
        # recognize the frames properly when importing to library.
        
        bits = BitArray()
        bits += '0' # TypeFlag (not an edge record)
        bits += '0' # StateNewStyles (only for DefineShape2 and Defineshape3)
        if lineStyle:  bits += '1' # StateLineStyle
        else: bits += '0'
        if fillStyle: bits += '1' # StateFillStyle1
        else: bits += '0'
        bits += '0' # StateFillStyle0        
        if moveTo: bits += '1' # StateMoveTo
        else: bits += '0'
        
        # give information
        # todo: nbits for fillStyle and lineStyle is hard coded.
        
        if moveTo:
            bits += twitsToBits([moveTo[0], moveTo[1]])
        if fillStyle:
            bits += intToBits(fillStyle,4)
        if lineStyle:
            bits += intToBits(lineStyle,4)
        
        return bits
        #return bitsToBytes(bits)


    def MakeStraightEdgeRecord(self, *dxdy):
        if len(dxdy)==1:
            dxdy = dxdy[0]
        
        # determine required number of bits
        xbits, ybits = signedIntToBits(dxdy[0]*20), signedIntToBits(dxdy[1]*20)
        nbits = max([len(xbits),len(ybits)])
        
        bits = BitArray()
        bits += '11'  # TypeFlag and StraightFlag
        bits += intToBits(nbits-2,4)
        bits += '1' # GeneralLineFlag
        bits += signedIntToBits(dxdy[0]*20,nbits)
        bits += signedIntToBits(dxdy[1]*20,nbits)
        
        # note: I do not make use of vertical/horizontal only lines...
        
        return bits
        #return bitsToBytes(bits)
        

    def MakeEndShapeRecord(self):
        bits = BitArray()
        bits +=  "0"     # TypeFlag: no edge 
        bits += "0"*5   # EndOfShape
        return bits
        #return bitsToBytes(bits)




## Last few functions

    

def buildFile(fp, taglist, nframes=1, framesize=(500,500), 
        fps=10, version=8):
    """ Give the given file (as bytes) a header. """
    
    # compose header
    bb = bytes()
    bb += 'F'  # uncompressed 
    bb += 'WS'  # signature bytes
    bb += intToUint8(version) # version
    bb += '0000' # FileLength (leave open for now)
    bb += Tag().MakeRectRecord(0,framesize[0], 0, framesize[1]).ToBytes()
    bb += intToUint8(0) + intToUint8(fps) # FrameRate
    bb += intToUint16(nframes)    
    fp.write(bb)
    
    # produce all tags    
    for tag in taglist:
        fp.write( tag.GetTag() )
    
    # finish with end tag
    fp.write( '\x00\x00' )
    
    # set size
    sze = fp.tell()    
    fp.seek(4)
    fp.write( intToUint32(sze) )


def writeSwf(filename, images, fps=10, repeat=True, delays=None):
    """ writeSwf(filename, images, fps=10, repeat=True, delays=None)
    Write an swf-file from the specified images. 
    images should be a list of numpy arrays or PIL images.
    Numpy images of type float should have pixels between 0 and 1.
    Numpy images of other types are expected to have values between 0 and 255.
    When repeat is False, the movie is finished with a stop action.
    delays (when given) should be a list (or numpy array) of integers
    specifying for each image how many frames it should be shown.
    """
    t0 = time.time()
    
    # check images
    if not images:
        raise ValueError("Image list is empty!")
    images2 = []
    for im in images:
        if PIL and isinstance(im, PIL.Image.Image):
            im = np.asarray(im)
        images2.append(im)
    
    # init 
    taglist = [ FileAttributesTag(), SetBackgroundTag(0,0,0) ]
    
    # check delays
    if delays is None:
        delays = [1 for i in range(len(images2))]
    if len(delays) != len(images2):
        raise Exception("Amount of delays does not match amount of images.")
    
    # produce series of tags for each image
    t1 = time.time()
    nframes = 0
    for im in images2:
        bm = BitmapTag(im)
        wh = (im.shape[1], im.shape[0])
        sh = ShapeTag(bm.id, (0,0), wh)
        po = PlaceObjectTag(1,sh.id, move=nframes>0)
        taglist.extend( [bm, sh, po] )
        for i in range(delays[nframes]):
            taglist.append( ShowFrameTag() )
        nframes += 1
        
    if not repeat:
        taglist.append(DoActionTag('stop'))
    
    # build file
    #print "prepared tags (%1.2f s), building file..." % (time.time()-t1)
    
    t1 = time.time()
    fp = open(filename,'wb')    
    try:
        buildFile(fp, taglist, nframes=nframes, framesize=wh, fps=fps)
    except Exception:
        raise
    finally:
        fp.close()
    
    #print "build tags (%1.2f s)" % (time.time()-t1)
    
    tt = time.time()-t0
    print "written %i frames to swf in %1.2f seconds (%1.0f ms/frame)" % (
        len(images), tt, 1000*tt/len(images) )
    
    
if __name__ == "__main__":
    import visvis as vv
    
    im = np.zeros((200,200), dtype=np.uint8)
    im[10:30,:] = 100
    im[:,80:120] = 255
    im[-50:-40,:] = 50
    
    im = vv.imread(r'D:\almar\projects\_p\smith.jpg')
    
    images = [im*i for i in np.arange(0.1,1,0.1)]
    delays = [1 for i in range(len(images))]
    delays[2]=3
    delays[3]=5
    writeSwf( 'test.swf', images, 5, 1, delays )
    
    