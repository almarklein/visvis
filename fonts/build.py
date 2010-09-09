import os, sys
import ssdf

# vv.imwrite('d:/almar/projects/ims/test0.png', vv.getframe(vv.gcf()))
fontGenApp = r'"C:\Program Files (x86)\BMFontGen\bmfontgen.exe"'

# If the size is even, the even fontsizes in visvis will look much better
# than the uneven. Matlab uses fontsize 9 for tickmarks by default, but I
# like even fontsizes better. Additionally, too large size will result in
# aliasing for smaller fontsizes in visvis.

size = 16 # 18 is good, 20 won't fit, 
bmsize = 1024
outdir = 'tmp/'

s = ssdf.new()
s.serif = ssdf.new()
s.serif.name = 'FreeSerif'

fonts = {   'mono':'FreeMono', 'sans':'FreeSans', 'serif':'FreeSerif'}
#fonts = {   'mono':'Courier New', 'sans':'Arial', 'serif':'Times new roman'}

for font in fonts:
    fontName = fonts[font]
    
    options = []
    
    # parameters
    options.append( '-name %s' % fontName )
    options.append( '-size %i' % size )
    options.append( '-bmsize %i' % bmsize )
    
    # fixed options
    options.append( '-trh aa' ) # aa looks best on large AND small fontsizes
    options.append( '-blackbg' )
    
    # number, alphabet and greek
    ranges1 = ['-range 0020-003f','-range 0040-00bf','-range 0380-03ff']
    # latin extended and symbols
    ranges2 = ['-range 00c0-037f','-range 2000-23ff']
    
    for type in 'rib': # regular, italic, bold
        tekst = []
        if type == 'r':
            tekst.extend(options)
            tekst.extend(ranges1)
            tekst.extend(ranges2)
            #tekst.append( '-trh 1bpp-grid' )
            tekst.append( '-output %s%s_%s' % (outdir,font,type) )
        elif type == 'i':
            tekst.extend(options)
            tekst.extend(ranges1)
            tekst.append('-italic')
            #tekst.append( '-trh aa-grid' )
            tekst.append( '-output %s%s_%s' % (outdir,font,type) )
        elif type == 'b':
            tekst.extend(options)
            tekst.extend(ranges1)
            tekst.append('-bold')
            #tekst.append( '-trh aa-grid' )
            tekst.append( '-output %s%s_%s' % (outdir,font,type) )
        
        # write file
        fname = outdir+'temp_font.txt'
        f = open(fname,'w')
        f.write( '\n'.join(tekst) )
        f.close()
        
        # call fontgen
        status = os.system(fontGenApp + ' -optfile ' + fname)
        if status != 0:
            raw_input('an error occured, press enter to continue')
