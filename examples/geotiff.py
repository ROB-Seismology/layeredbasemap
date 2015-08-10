"""
GeoTIFF example
"""

import mapping.Basemap as lbm


region = (1, 8, 49, 52)
region = (6, 7, 49, 50)
projection = "tmerc"
title = "GeoTIFF example"

layers = []

## GeoTiff
## http://www.eurogeographics.org/content/products-services-eurodem
geotiff_filespec = r"C:\Users\kris\Downloads\euro_sample.tif"
gdal_data = lbm.GdalRasterData(geotiff_filespec)
colorbar_style = lbm.ColorbarStyle("EuroDEM sample")
style = lbm.GridStyle(colorbar_style=colorbar_style)
layer = lbm.MapLayer(gdal_data, style)
layers.append(layer)

## Coastlines
coastline_style = lbm.LineStyle(line_color="r", line_width=2)
data = lbm.BuiltinData("coastlines")
layer = lbm.MapLayer(data, coastline_style)
layers.append(layer)

## Country borders
data = lbm.BuiltinData("countries")
country_style = lbm.LineStyle(line_color="r", line_width=2, line_pattern='--')
layer = lbm.MapLayer(data, country_style)
layers.append(layer)

map = lbm.LayeredBasemap(layers, title, projection, region=region)
map.plot()
