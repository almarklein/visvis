import visvis as vv
app=vv.App('wx')

vv.figure() # we need to create an opengl context
print 'OpenGl version on this system:', vv.getGlVersion()

app.run()