import visvis as vv
app = vv.use('wx')

# we need to create an opengl context
f=vv.figure() 

# get info
version, vendor, renderer, ext = vv.getOpenGlInfo()
if not ext:
    ext = ''

# remove figure
f.Close()

# print!
print 'Information about the OpenGl version on this system:\n'
print 'version:    ', version
print 'vendor:     ', vendor
print 'renderer:   ', renderer
print 'extensions: ', len(ext.split()),'different extensions'

# let the widget close and then wait
app.run()
raw_input('\nPress enter to continue...')
