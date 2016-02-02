"""
Plot map of ROB earthquake catalog.
This script demonstrates the simultaneous use of thematic size (earthquake
magnitude) and thematic color (focal depth) for point data.
"""
from mapping.Basemap.LayeredBasemap import *
import eqcatalog.seismodb as seismodb


region = (0,8,49,52)
projection = "tmerc"
title = "ROB earthquake catalog"
resolution = "h"
graticule_interval = (2, 1)

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

## Rivers
data = BuiltinData("rivers")
river_style = LineStyle(line_color="b")
layer = MapLayer(data, river_style)
layers.append(layer)

## ROB earthquake catalog
catalog = seismodb.query_ROB_LocalEQCatalog(region=region)
values = {}
values['magnitude'] = catalog.get_magnitudes()
values['depth'] = catalog.get_depths()
values['year'] = [eq.datetime.year for eq in catalog]
point_data = MultiPointData(catalog.get_longitudes(), catalog.get_latitudes(), values=values)
#point_data = MultiPointData([2.0, 3.0, 4.0, 5.0, 6.0], [50, 50, 50, 50, 50], values=[2,3,4,5,6])
thematic_legend_style = LegendStyle(title="Magnitude", location=3, shadow=True, fancy_box=True, label_spacing=0.7)
colorbar_style = ColorbarStyle(title="Depth (km)", location="bottom", format="%d", label_size=18, tick_label_size=18)
thematic_size = ThematicStyleGradient([1,3,5], [4,12,24], value_key="magnitude")
#thematic_color = ThematicStyleColormap(value_key="depth")
thematic_color = ThematicStyleRanges([0,1,10,25,50], ['red', 'orange', 'yellow', 'green'], value_key="depth", colorbar_style=colorbar_style)
#thematic_color = ThematicStyleRanges([1350,1910,2050], ['green', (1,1,1,0)], value_key="year")
#point_style = PointStyle(shape='+', size=thematic_size, fill_color='k', line_color=thematic_color, line_width=0.5)
point_style = PointStyle(shape='o', size=thematic_size, line_color='k', fill_color=thematic_color, line_width=0.5, thematic_legend_style=thematic_legend_style)
layer = MapLayer(point_data, point_style, legend_label="ROB Catalog")
layers.append(layer)

legend_style = LegendStyle(location=0)
title_style = DefaultTitleTextStyle
title_style.weight = "bold"
scalebar_style = ScalebarStyle((4.,49.25), 100, bar_style="fancy")
map = LayeredBasemap(layers, title, projection, region=region, title_style=title_style, graticule_interval=graticule_interval, resolution=resolution, legend_style=legend_style, scalebar_style=scalebar_style)
map.plot()
