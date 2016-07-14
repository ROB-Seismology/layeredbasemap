"""
Test plotting of maps in multiple axes
"""


import pylab
import matplotlib.gridspec as gridspec
import mapping.Basemap as lbm


FIGSIZE = pylab.rcParams['figure.figsize']
num_cols, num_rows = 2, 1
gs = gridspec.GridSpec(num_rows, num_cols)

layers = []
data = lbm.BuiltinData("continents")
style = lbm.PolygonStyle(fill_color="yellow")
layer = lbm.MapLayer(data, style)
layers.append(layer)

## Map 1
ax1 = pylab.subplot(gs[0, 0])
region1 = (0, 8, 49, 52)
projection1 = "merc"
resolution1 = "h"
graticule_interval1 = (2, 1)

map1 = lbm.LayeredBasemap(layers, "", projection1, region=region1,
						graticule_interval=graticule_interval1,
						resolution=resolution1, ax=ax1)
map1.plot(fig_filespec="hold")

ax2 = pylab.subplot(gs[0, 1])
region2 = (-180, 180, -90, 90)
projection2 = "robin"
resolution2 = "c"
graticule_interval2 = (60, 30)

map2 = lbm.LayeredBasemap(layers, "", projection2, region=region2,
						graticule_interval=graticule_interval2,
						resolution=resolution2, ax=ax2)
map2.plot(fig_filespec="hold")


fig_filespec = None

fig = pylab.gcf()
fig.set_size_inches(FIGSIZE[0] * num_cols, FIGSIZE[1] * num_rows)
if fig_filespec:
	pylab.savefig(fig_filespec)
else:
	pylab.show()
fig.clf()
