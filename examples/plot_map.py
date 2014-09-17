
from mapping.Basemap.LayeredBasemap import *

region = (1,8,49,52)
projection = "tmerc"
title = "Test"
resolution = "i"

layers = []

coastline_style = LineStyle(line_color="k", line_width=2)
data = BuiltinData("coastlines")
layer = MapLayer(data, coastline_style)
layers.append(layer)

data = BuiltinData("countries")
country_style = LineStyle(line_color="k", line_width=2, line_pattern='--')
layer = MapLayer(data, country_style)
layers.append(layer)

lons = 1 + np.random.random(10) * (8-1)
lats = 49 + np.random.random(10) * (52-49)
depths = np.random.random(10) * 25

tsr = ThematicStyleRanges([0., 5., 15., 20.], ['r', 'g', 'b'], value_key='depths')
print tsr(values={'depths': depths})
multipoint_data = MultiPointData(lons, lats, values={'depths': depths})
multipoint_style = PointStyle(
#	shape='x',
	shape='o',
	line_color=ThematicStyleRanges([0., 5., 15., 20.], ['r', 'g', 'b'], value_key='depths'),
	fill_color='r',
#	fill_color=None,
	)
layers.append(MapLayer(multipoint_data, multipoint_style))

map = LayeredBasemap(layers, title, projection, region=region, resolution=resolution)
map.plot()
