# -*- coding: iso-Latin-1 -*-

"""
Plot poster-size map of ROB earthquake catalog.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


import os
import numpy as np
import pylab
import mapping.layeredbasemap as lbm
import eqcatalog.seismodb as seismodb


out_folder = "E:\\Home\\_kris\\Meetings\\2018 - Opendeurdagen"



region = (1, 8, 49, 52)
projection = "tmerc"
#title = "ROB earthquake catalog"
title = ""
resolution = "h"
graticule_interval = (2, 1)

layers = []

## DEM
"""
url = 'http://seishaz.oma.be:8080/geoserver/wcs'
layer_name, wcs_resolution, bbox = 'ngi:DTM10k', 500, []
wcs_data = lbm.WCSData(url, layer_name, resolution=wcs_resolution, bbox=bbox)
#colorbar_style = lbm.ColorbarStyle("Elevation (m)")
colorbar_style = None
hillshade_style = lbm.HillshadeStyle(azimuth=45,elevation_angle=30, scale=0.1)
#hillshade_style = None
cmap, norm = lbm.cm.from_cpt_city(r"td/DEM_poster")
#cmap = "gist_earth"
tsc = lbm.ThematicStyleColormap(color_map=cmap, vmin=0, vmax=700)
#tsc.color_map = None
style = lbm.GridStyle(color_map_theme=tsc, colorbar_style=colorbar_style, line_style=None, pixelated=False, hillshade_style=hillshade_style)
layer = lbm.MapLayer(wcs_data, style)
#layers.append(layer)
"""

## GeoTiff
"""
import mapping.geotools.coordtrans as ct
tif_filespec = r"D:\GIS-data\Belgium\DEM\ngi_dem1_Lambert.tif"
grd_data = lbm.GdalRasterData(tif_filespec, band_nr=0)
grd_data.srs = ct.get_epsg_srs(31370)
grd_style = lbm.GridImageStyle(alpha=0.75)
layer = lbm.MapLayer(grd_data, grd_style)
layers.append(layer)
"""


## Coastlines
coastline_style = lbm.LineStyle(line_color="k", line_width=1)
data = lbm.BuiltinData("coastlines")
layer = lbm.MapLayer(data, coastline_style)
#layers.append(layer)

## Country borders
data = lbm.BuiltinData("countries")
country_style = lbm.LineStyle(line_color="k", line_width=0.75)
layer = lbm.MapLayer(data, country_style)
#layers.append(layer)

## Countries
country_color = "oldlace"
for country in ("france", "germany", "luxembourg", "netherlands", "united_kingdom"):
	gis_filename = country + ".TAB"
	gis_filespec = os.path.join("D:\seismo-gis\collections\DCW_countries\Europe\TAB", gis_filename)
	data = lbm.GisData(gis_filespec)
	style = lbm.PolygonStyle(line_color="k", line_width=0.75, fill_color=country_color)
	layer = lbm.MapLayer(data, style)
	layers.append(layer)

## Provinces
gis_filespec = r"D:\seismo-gis\collections\Bel_administrative_ROB\TAB\Bel_provinces.TAB"
data = lbm.GisData(gis_filespec)
style = lbm.PolygonStyle(line_color="dimgrey", line_width=0.75, fill_color=country_color)
#style = lbm.LineStyle(line_color="w", line_width=0.75)
layer = lbm.MapLayer(data, style)
layers.append(layer)


## Regions
gis_filespec = r"D:\seismo-gis\collections\Bel_administrative_ROB\TAB\Bel_regions.TAB"
data = lbm.GisData(gis_filespec)
style = lbm.LineStyle(line_color="k", line_width=0.75)
layer = lbm.MapLayer(data, style)
layers.append(layer)


## Rivers
data = lbm.BuiltinData("rivers")
river_style = lbm.LineStyle(line_color="b", line_width=0.75)
layer = lbm.MapLayer(data, river_style)
#layers.append(layer)


## ROB earthquake catalog
catalog = seismodb.query_ROB_LocalEQCatalog(region=region)
values = {}
values['magnitude'] = catalog.get_magnitudes()
values['depth'] = catalog.get_depths()
values['year'] = [eq.datetime.year for eq in catalog]
point_data = lbm.MultiPointData(catalog.get_longitudes(), catalog.get_latitudes(), values=values)

legend_label_style = lbm.TextStyle(font_size=10)
thematic_legend_style = lbm.LegendStyle(title="Magnitude", location=3, shadow=True,
						label_style=legend_label_style, fancy_box=True, label_spacing=0.7)
thematic_size = lbm.ThematicStyleGradient([1,3,5,6.3], [1,4,10,15],
						labels=["1.0", "3.0", "5.0", "6.3"], value_key="magnitude")

## Color scale for depth
#colorbar_style = lbm.ColorbarStyle(title="Depth (km)", location="bottom", format="%d", label_size=18, tick_label_size=18)
#thematic_color = lbm.ThematicStyleColormap(value_key="depth")
#thematic_color = lbm.ThematicStyleRanges([0,1,10,25,50], ['red', 'orange', 'yellow', 'green'], value_key="depth", colorbar_style=colorbar_style)

## Color scale for time
## Discontinuous color scale
"""
colorbar_style = lbm.ColorbarStyle(title=u"Jaar - Année - Year", location="bottom", format="%d",
					label_size=15, tick_label_size=8, spacing="uniform")
thematic_color = lbm.ThematicStyleRanges([1350,1910,1985,2000,2015,2018], ['blue', 'green', 'yellow', 'orange', 'red'], value_key="year", colorbar_style=colorbar_style)
file_name_ext = "_discont_colorscale"
"""

## Continuous color scale
colorbar_style = lbm.ColorbarStyle(title=u"Jaar - Année - Year", location="bottom", format="%d",
					label_size=15, tick_label_size=8, spacing="uniform",
					ticks=[1350, 1910, 1985,2018])
cmap = pylab.get_cmap("rainbow", 6)
colors = cmap(np.linspace(0, 1, 6))
thematic_color = lbm.ThematicStyleGradient([1350,1910,1985,2000,2015,2018], colors, value_key="year", colorbar_style=colorbar_style)
file_name_ext = "_cont_colorscale"


point_style = lbm.PointStyle(shape='o', size=thematic_size, line_color='k', fill_color=thematic_color, line_width=0.5, thematic_legend_style=thematic_legend_style)
layer = lbm.MapLayer(point_data, point_style, legend_label="ROB Catalog")
layers.append(layer)


## Seismic stations
import datetime
station_recs = seismodb.query_ROB_Stations(activity_date_time=datetime.date.today())
seismometers = [r for r in station_recs if r['instrument_type'] == 'S']
accelerometers = [r for r in station_recs if r['instrument_type'] == 'A']
instruments_list = (seismometers, accelerometers)
colors = ('cyan', 'magenta')
#label_style = lbm.TextStyle(font_size=4, vertical_alignment='top', offset=(0,-5))
label_style = None
for instruments, color in zip(instruments_list, colors):
	lons = [r['longitude'] for r in instruments]
	lats = [r['latitude'] for r in instruments]
	codes = [r['code'] for r in instruments]
	data = lbm.MultiPointData(lons, lats, labels=codes)
	style = lbm.PointStyle('^', size=8, fill_color=color, label_style=label_style)
	layer = lbm.MapLayer(data, style)
	#layers.append(layer)


## Logo
"""
logo_filespec = r"E:\Home\_kris\Logos\logo Seismo-facebook-EN.jpg"
img_data = lbm.ImageData(logo_filespec, 7.96, 51.98, coord_frame='geographic')
img_style = lbm.ImageStyle(width=400, horizontal_alignment='right', vertical_alignment='top', on_top=True)
layer = lbm.MapLayer(img_data, img_style)
layers.append(layer)
"""

#legend_style = lbm.LegendStyle(location=0)
legend_style = None
title_style = lbm.DefaultTitleTextStyle
title_style.weight = "bold"
#scalebar_style = lbm.ScalebarStyle((4.,49.25), 100, bar_style="fancy")
scalebar_style = None
border_style = lbm.MapBorderStyle(fill_color='powderblue')
#graticule_style = lbm.GraticuleStyle(annot_axes="")
graticule_style = None
map = lbm.LayeredBasemap(layers, title, projection, region=region, resolution=resolution,
						title_style=title_style, graticule_interval=graticule_interval,
						graticule_style=graticule_style, legend_style=legend_style,
						scalebar_style=scalebar_style, border_style=border_style,
						dpi=200)


fig_filename = "ROB_catalog%s.PNG" % file_name_ext
#fig_filespec = os.path.join(out_folder, fig_filename)
fig_filespec = None
if fig_filespec:
	dpi = 600
else:
	dpi = None

map.plot(fig_filespec=fig_filespec, dpi=dpi)
