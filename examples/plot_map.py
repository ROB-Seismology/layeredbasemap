
import numpy as np
import mapping.layeredbasemap as lbm



region = (1,8,49,52)
projection = "merc"
#projection = "EPSG:31300"
title = "Test"
resolution = "i"
graticule_interval = (2, 1)

layers = []

data = lbm.WMSData("http://seishaz.oma.be:8080/geoserver/rob/wms?", layers=["bel_villages_polygons"], verbose=True)
style = lbm.WMSStyle(xpixels=1200)
layer = lbm.MapLayer(data, style)
#layers.append(layer)

coastline_style = lbm.LineStyle(line_color="r", line_width=1)
data = lbm.BuiltinData("coastlines")
layer = lbm.MapLayer(data, coastline_style)
layers.append(layer)

#data = lbm.GdalRasterData(r"C:\Temp\matplotlib.tif", band_nr=0)
#style = lbm.GridImageStyle(masked=True, alpha=0.5)
#layer = lbm.MapLayer(data, style)
#layers.append(layer)

data = lbm.BuiltinData("countries")
country_style = lbm.LineStyle(line_color="r", line_width=1, line_pattern='--')
layer = lbm.MapLayer(data, country_style)
layers.append(layer)


lons = 1 + np.random.random(10) * (8-1)
lats = 49 + np.random.random(10) * (52-49)
depths = np.random.random(10) * 25

tsr = lbm.ThematicStyleRanges([0., 5., 15., 20.], ['r', 'g', 'b'], value_key='depths')
print tsr(values={'depths': depths})
multipoint_data = lbm.MultiPointData(lons, lats, values={'depths': depths})
multipoint_style = lbm.PointStyle(
#	shape='x',
	shape='o',
	line_color=lbm.ThematicStyleRanges([0., 5., 15., 20.], ['r', 'g', 'b'], value_key='depths'),
	fill_color='r',
#	fill_color=None,
	)
layers.append(lbm.MapLayer(multipoint_data, multipoint_style))

image_data = lbm.ImageData(r"C:\Temp\banerNL.gif", 1, 49)
image_style = lbm.ImageStyle(horizontal_alignment='left', vertical_alignment='bottom')
layer = lbm.MapLayer(image_data, image_style)
#layers.append(layer)

map = lbm.LayeredBasemap(layers, title, projection, region=region, resolution=resolution, graticule_interval=graticule_interval)

#lons = [map.llcrnrlon, map.urcrnrlon]
#lats = [map.llcrnrlat, map.urcrnrlat]
#print zip(lons, lats)
#x, y = map.lonlat_to_map_coordinates(lons, lats)
#print zip(x, y)

#map.plot()

map.export_geotiff(out_filespec=r"C:\Temp\matplotlib.tif", dpi=200, verbose=True)
