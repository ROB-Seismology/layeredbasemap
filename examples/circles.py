"""
Plot circles
"""

from __future__ import absolute_import, division, print_function, unicode_literals


import mapping.layeredbasemap as lbm


region = (0,8,49,52)
projection = "tmerc"
title = "Circles demo"
resolution = "h"
graticule_interval = (2, 1)

layers = []

## Coastlines
coastline_style = lbm.LineStyle(line_color="k", line_width=2)
data = lbm.BuiltinData("coastlines")
layer = lbm.MapLayer(data, coastline_style)
layers.append(layer)

## Country borders
data = lbm.BuiltinData("countries")
country_style = lbm.LineStyle(line_color="k", line_width=2, line_pattern='--')
layer = lbm.MapLayer(data, country_style)
layers.append(layer)

## Circles
uccle = (4.367785, 50.795003)
distances = [25, 50, 75, 100]
circle_data = lbm.CircleData([uccle[0]]*4, [uccle[1]]*4, distances, values=distances, azimuthal_resolution=5)
thematic_color = lbm.ThematicStyleIndividual(distances, ["yellow", "orange", "red", "purple"], colorbar_style=None)
circle_style = lbm.LineStyle(line_color=thematic_color, line_width=2)
layer = lbm.MapLayer(circle_data, circle_style)
layers.append(layer)

## Point
point_data = lbm.PointData(*uccle).to_multi_point()
point_style = lbm.PointStyle(shape='*')
layer = lbm.MapLayer(point_data, point_style)
layers.append(layer)

legend_style = lbm.LegendStyle(location=0)
title_style = lbm.DefaultTitleTextStyle
title_style.weight = "bold"
scalebar_style = lbm.ScalebarStyle((1.,49.25), 100, bar_style="fancy")
border_style = lbm.MapBorderStyle(line_width=2)
map = lbm.LayeredBasemap(layers, title, projection, region=region, title_style=title_style, graticule_interval=graticule_interval, resolution=resolution, legend_style=legend_style, scalebar_style=scalebar_style, border_style=border_style)
map.plot()
