"""
Plot circles
"""

from mapping.Basemap.LayeredBasemap import *


region = (0,8,49,52)
projection = "tmerc"
title = "Circles demo"
resolution = "h"
grid_interval = (2, 1)

layers = []

## Coastlines
coastline_style = LineStyle(line_color="k", line_width=2)
data = BuiltinData("coastlines")
layer = MapLayer(data, coastline_style)
layers.append(layer)

## Country borders
data = BuiltinData("countries")
country_style = LineStyle(line_color="k", line_width=2, line_pattern='--')
layer = MapLayer(data, country_style)
layers.append(layer)

## Circles
circle_data = CircleData([4.5, 4.5, 4.5], [50.5, 50.5, 50.5], [25, 50, 75], values=[25, 50, 75], azimuthal_resolution=5)
thematic_color = ThematicStyleIndividual([25, 50, 75], ["yellow", "orange", "red"], colorbar_style=None)
circle_style = LineStyle(line_color=thematic_color, line_width=2)
layer = MapLayer(circle_data, circle_style)
layers.append(layer)

legend_style = LegendStyle(location=0)
title_style = DefaultTitleTextStyle
title_style.weight = "bold"
map = LayeredBasemap(layers, title, projection, region=region, title_style=title_style, grid_interval=grid_interval, resolution=resolution, legend_style=legend_style)
map.plot()

