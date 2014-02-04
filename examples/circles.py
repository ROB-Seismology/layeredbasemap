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
uccle = (4.367785, 50.795003)
distances = [25, 50, 75, 100]
circle_data = CircleData([uccle[0]]*4, [uccle[1]]*4, distances, values=distances, azimuthal_resolution=5)
thematic_color = ThematicStyleIndividual(distances, ["yellow", "orange", "red", "purple"], colorbar_style=None)
circle_style = LineStyle(line_color=thematic_color, line_width=2)
layer = MapLayer(circle_data, circle_style)
layers.append(layer)

## Point
point_data = PointData(*uccle).to_multi_point()
point_style = PointStyle(shape='*')
layer = MapLayer(point_data, point_style)
layers.append(layer)

legend_style = LegendStyle(location=0)
title_style = DefaultTitleTextStyle
title_style.weight = "bold"
scalebar_style = ScalebarStyle((1.,49.25), 100, bar_style="fancy")
border_style = MapBorderStyle(line_width=2)
map = LayeredBasemap(layers, title, projection, region=region, title_style=title_style, grid_interval=grid_interval, resolution=resolution, legend_style=legend_style, scalebar_style=scalebar_style, border_style=border_style)
map.plot()
