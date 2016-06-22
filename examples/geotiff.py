"""
GeoTIFF example
"""

import os
import mapping.Basemap as lbm


os.environ["CPL_TMPDIR"] = r"C:\Temp"


#region = (1, 8, 49, 52)
#region = (6, 7, 49, 50)
region = (5., 8., 49.5, 51.5)
projection = "tmerc"
title = "GeoTIFF example"

layers = []

## GeoTiff / WCS
#geotiff_filespec = r"D:\seismo-gis\collections\ASTER_GDEM\GEOTIFF\ASTGTM_N50E006.tif"
#geotiff_filespec = r"C:\Temp\ASTGTM_N50E006.tif"
#geotiff_filespec = r"C:\Temp\matplotlib.tif"
gdal_data = lbm.GdalRasterData(geotiff_filespec, band_nr=1, down_sampling=3)
url = 'http://seishaz.oma.be:8080/geoserver/wcs'
layer_name, resolution, bbox = 'ngi:DTM10k', 1000, []
#layer_name, resolution, bbox = 'nasa:ASTER_GDEM_V2', 0.02, region[::2]+region[1::2]
wcs_data = lbm.WCSData(url, layer_name, resolution=resolution, bbox=bbox)
colorbar_style = lbm.ColorbarStyle("Elevation (m)")
#colorbar_style = None
#hillshade_style = lbm.HillshadeStyle(azimuth=45,elevation_angle=30, scale=0.1, color_map="copper")
hillshade_style = None
cmap, norm = lbm.cm.from_cpt_city(r"td/DEM_poster")
#cmap = "gist_earth"
tsc = lbm.ThematicStyleColormap(color_map=cmap, vmin=0, vmax=700)
#tsc.color_map = None
style = lbm.GridStyle(color_map_theme=tsc, colorbar_style=colorbar_style, line_style=None, pixelated=True, hillshade_style=hillshade_style)
#style = lbm.GridImageStyle()
layer = lbm.MapLayer(wcs_data, style)
layers.append(layer)

## Country borders
data = lbm.BuiltinData("countries")
country_style = lbm.LineStyle(line_color="r", line_width=2, line_pattern='--')
layer = lbm.MapLayer(data, country_style)
layers.append(layer)

## Coastlines
coastline_style = lbm.LineStyle(line_color="r", line_width=2)
data = lbm.BuiltinData("coastlines")
layer = lbm.MapLayer(data, coastline_style)
layers.append(layer)

map = lbm.LayeredBasemap(layers, title, projection, region=region)
map.plot()
