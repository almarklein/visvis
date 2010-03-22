import visvis as vv
app = vv.use()

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

# Wait
raw_input('\nPress enter to continue...')
