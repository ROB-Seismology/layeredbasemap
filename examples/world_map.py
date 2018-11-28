from __future__ import absolute_import, division, print_function, unicode_literals


import datetime
import mapping.layeredbasemap as lbm


region = (-180, 180, -90, 90)
origin = (0, 0)
projection = "moll"
title = "Hello World from LayeredBasemap"
resolution = "c"
graticule_interval = (60, 30)

layers = []

## BlueMarble image
bm_style = None
data = lbm.BuiltinData("bluemarble")
layer = lbm.MapLayer(data, bm_style)
#layers.append(layer)

## Continents
continent_style = lbm.PolygonStyle(fill_color="cornsilk", line_pattern=None, line_width=0)
continent_style.bg_color = "powderblue"
data = lbm.BuiltinData("continents")
layer = lbm.MapLayer(data, continent_style)
layers.append(layer)

## Coastlines
coastline_style = lbm.LineStyle(line_color="burlywood", line_width=2)
data = lbm.BuiltinData("coastlines")
layer = lbm.MapLayer(data, coastline_style)
layers.append(layer)

## Country borders
data = lbm.BuiltinData("countries")
country_style = lbm.LineStyle(line_color="w", line_width=1, line_pattern='-')
layer = lbm.MapLayer(data, country_style)
layers.append(layer)

## Rivers
data = lbm.BuiltinData("rivers")
river_style = lbm.LineStyle(line_color="b", line_width=0.5)
layer = lbm.MapLayer(data, river_style)
#layers.append(layer)

## Great circles
lons = [0, 60, 0, 120, 0, -60, 0, -120]
lats = [0, 30, 0, -30, 0, -60, 0, 60]
gc_data = lbm.GreatCircleData(lons, lats, resolution=100)
gc_style = lbm.LineStyle(line_width=1.5)
layer = lbm.MapLayer(gc_data, gc_style)
layers.append(layer)

## Night shading
data = lbm.BuiltinData("nightshade", date_time=datetime.datetime.now())
style = lbm.PolygonStyle(fill_color='k', alpha=0.5)
layer = lbm.MapLayer(data, style)
layers.append(layer)

legend_style = lbm.LegendStyle(location=0)
title_style = lbm.DefaultTitleTextStyle
title_style.weight = "bold"
graticule_style = lbm.GraticuleStyle(line_style=lbm.LineStyle(line_color="magenta"))
map = lbm.LayeredBasemap(layers, title, projection, origin=origin, title_style=title_style, graticule_interval=graticule_interval, resolution=resolution, legend_style=legend_style, graticule_style=graticule_style)
map.plot()
