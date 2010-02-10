import visvis as vv
app = vv.use('wx')

# get info
version, vendor, renderer, ext = vv.getOpenGlInfo()
if not ext:
    ext = ''

# print!
print 'Information about the OpenGl version on this system:\n'
print 'version:    ', version
print 'vendor:     ', vendor
print 'renderer:   ', renderer
print 'extensions: ', len(ext.split()),'different extensions'

# let the widget close and then wait
app.Run()
raw_input('\nPress enter to continue...')
