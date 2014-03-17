import datetime
from mapping.Basemap import *
#from mapping.Basemap.styles import *
#from mapping.Basemap.data_types import *


region = (-180, 180, -90, 90)
origin = (0, 0)
projection = "robin"
title = "Hello World from LayeredBasemap"
resolution = "c"
grid_interval = (60, 30)

layers = []

## BlueMarble image
bm_style = None
data = BuiltinData("bluemarble")
layer = MapLayer(data, bm_style)
#layers.append(layer)

## Continents
continent_style = PolygonStyle(fill_color="cornsilk", line_pattern="None", line_width=0)
continent_style.bg_color = "powderblue"
data = BuiltinData("continents")
layer = MapLayer(data, continent_style)
layers.append(layer)

## Coastlines
coastline_style = LineStyle(line_color="burlywood", line_width=2)
data = BuiltinData("coastlines")
layer = MapLayer(data, coastline_style)
layers.append(layer)

## Country borders
data = BuiltinData("countries")
country_style = LineStyle(line_color="w", line_width=1, line_pattern='-')
layer = MapLayer(data, country_style)
layers.append(layer)

## Rivers
data = BuiltinData("rivers")
river_style = LineStyle(line_color="b", line_width=0.5)
layer = MapLayer(data, river_style)
#layers.append(layer)

## Great circles
lons = [0, 60, 0, 120, 0, -60, 0, -120]
lats = [0, 30, 0, -30, 0, -60, 0, 60]
gc_data = GreatCircleData(lons, lats, resolution=100)
gc_style = LineStyle(line_width=1.5)
layer = MapLayer(gc_data, gc_style)
layers.append(layer)

## Night shading
data = BuiltinData("nightshade", date_time=datetime.datetime.now())
style = PolygonStyle(fill_color='k', alpha=0.5)
layer = MapLayer(data, style)
layers.append(layer)

legend_style = LegendStyle(location=0)
title_style = DefaultTitleTextStyle
title_style.weight = "bold"
graticule_style = LineStyle(line_color="magenta")
map = LayeredBasemap(layers, title, projection, origin=origin, title_style=title_style, grid_interval=grid_interval, resolution=resolution, legend_style=legend_style, graticule_style=graticule_style)
map.plot()
