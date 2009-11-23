
import visvis as vv
app = vv.App('wx')
f = vv.clf()
a = vv.cla()


vv.plot([12,34,21,38], lc='b', ls=':',mc='b', mw=12, lw=2, ms='')
vv.plot([1,3,4],[33,47,12], lc='r', mc='r', ms='.')
vv.plot([35,14,40,31], lc='g', ls='--', mc='g', mw=12, lw=3, ms='*')

a = vv.gca()
a.legend = 'line 1', 'line 2', 'line 3'
a.showGrid = 1

vv.xlabel = 'measurement number'
vv.ylabel = 'some quantity [unit]'
vv.title('An example of \b{plotting}')

app.run()
