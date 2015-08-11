"""
GeoTIFF example
"""

import mapping.Basemap as lbm


#region = (1, 8, 49, 52)
#region = (6, 7, 49, 50)
region = (5, 8, 49.5, 51.5)
projection = "tmerc"
title = "GeoTIFF example"

layers = []

## GeoTiff
## http://www.eurogeographics.org/content/products-services-eurodem
#geotiff_filespec = r"C:\Users\kris\Downloads\euro_sample.tif"
geotiff_filespec = r"D:\seismo-gis\collections\ASTER_GDEM\GEOTIFF\ASTGTM_N50E006.tif"
gdal_data = lbm.GdalRasterData(geotiff_filespec)
colorbar_style = lbm.ColorbarStyle("DEM sample")
style = lbm.GridStyle(colorbar_style=colorbar_style, pixelated=True)
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
