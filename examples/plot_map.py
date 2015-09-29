
from mapping.Basemap.LayeredBasemap import *

region = (1,8,49,52)
#projection = "merc"
projection = "EPSG:31300"
title = "Test"
resolution = "i"
grid_interval = (2, 1)

layers = []

data = WMSData("http://seishaz.oma.be:8080/geoserver/rob/wms?", layers=["bel_villages_polygons"], verbose=True)
style = WMSStyle(xpixels=1200)
layer = MapLayer(data, style)
layers.append(layer)

coastline_style = LineStyle(line_color="r", line_width=1)
data = BuiltinData("coastlines")
layer = MapLayer(data, coastline_style)
layers.append(layer)

data = GdalRasterData(r"C:\Temp\matplotlib.tif", band_nr=0)
style = GridImageStyle(masked=True, alpha=0.5)
layer = MapLayer(data, style)
layers.append(layer)

data = BuiltinData("countries")
country_style = LineStyle(line_color="r", line_width=1, line_pattern='--')
layer = MapLayer(data, country_style)
layers.append(layer)


lons = 1 + np.random.random(10) * (8-1)
lats = 49 + np.random.random(10) * (52-49)
depths = np.random.random(10) * 25

tsr = ThematicStyleRanges([0., 5., 15., 20.], ['r', 'g', 'b'], value_key='depths')
print tsr(values={'depths': depths})
multipoint_data = MultiPointData(lons, lats, values={'depths': depths})
multipoint_style = PointStyle(
#	shape='x',
	shape='o',
	line_color=ThematicStyleRanges([0., 5., 15., 20.], ['r', 'g', 'b'], value_key='depths'),
	fill_color='r',
#	fill_color=None,
	)
layers.append(MapLayer(multipoint_data, multipoint_style))

image_data = ImageData(r"C:\Temp\banerNL.gif", 1, 49)
image_style = ImageStyle(horizontal_alignment='left', vertical_alignment='bottom')
layer = MapLayer(image_data, image_style)
layers.append(layer)

map = LayeredBasemap(layers, title, projection, region=region, resolution=resolution, grid_interval=grid_interval)

#lons = [map.llcrnrlon, map.urcrnrlon]
#lats = [map.llcrnrlat, map.urcrnrlat]
#print zip(lons, lats)
#x, y = map.lonlat_to_map_coordinates(lons, lats)
#print zip(x, y)

map.plot()

#map.export_geotiff(out_filespec=r"C:\Temp\matplotlib.tif", dpi=200, verbose=True)
