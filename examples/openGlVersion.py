import visvis as vv
app=vv.App('wx')

vv.figure() # we need to create an opengl context

descriptions = ['version','vendor', 'renderer', 'extensions']
info = vv.getOpenGlInfo()

print 'Information about the OpenGl version on this system:'
for des, i in zip(descriptions,info):
    print (des+':').ljust(12), i

app.run()