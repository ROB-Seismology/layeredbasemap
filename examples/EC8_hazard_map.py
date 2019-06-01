"""
Plot seismic hazard map that was used for Eurocode 8
"""

import os
import numpy as np
import mapping.layeredbasemap as lbm


layers = []

## Hazard grid
grd_file = r"D:\PSHA\EC8\CRISIS\Runs\MapInfo\GMT\E8_CRISIS_Ambr95DD_2s5km_475y.grd"
grd_data = lbm.GdalRasterData(grd_file)
#cmap = lbm.cm.get_cmap('hazard', 'gshap')
#norm = lbm.cm.get_norm('hazard', 'gshap')
cmap = 'rainbow'
#cpt_file = r"D:\GIS-data\Misc\Color profiles\PSHA\EC8_BEL_rainbow.cpt"
#cpt_file = r"D:\GIS-data\Misc\Color profiles\GMT\GMT_rainbow.cpt"
#cmap, _ = lbm.cm.from_cpt(cpt_file)
norm = lbm.cm.norm.LinearNorm(vmin=0, vmax=0.18)
color_map_theme = lbm.ThematicStyleColormap(cmap, norm=norm)
label_style = lbm.TextStyle(font_size=6, background_color=(1,1,1,0.67), border_pad=0)
line_style = lbm.LineStyle(line_width=0.5, line_pattern=None, dash_pattern=[3,3], label_style=label_style)
contour_levels = np.arange(0.02, 0.17, 0.02)
contour_labels = contour_levels[::2]
tick_labels = ["%.2f" % contour_levels[i] if i%2 == 0 else '' for i in range(len(contour_levels))]
colorbar_style = lbm.ColorbarStyle('PGA (g), 10% probability of exceedance in 50 yr',
									format='%.2f', spacing='uniform',
									ticks=contour_levels, tick_labels=tick_labels)
grd_style = lbm.GridStyle(color_map_theme, contour_levels=contour_levels,
						contour_labels=contour_labels, line_style=line_style,
						colorbar_style=colorbar_style)
layer = lbm.MapLayer(grd_data, grd_style)
layers.append(layer)

## Coastlines
coastline_style = lbm.LineStyle(line_color="k", line_width=1)
data = lbm.BuiltinData("coastlines")
layer = lbm.MapLayer(data, coastline_style)
layers.append(layer)

## Provinces
gis_file = r"D:\seismo-gis\collections\Bel_administrative_ROB\TAB\Bel_provinces.TAB"
data = lbm.GisData(gis_file)
style = lbm.PolygonStyle(line_color="k", line_width=0.5, fill_color=None)
layer = lbm.MapLayer(data, style)
layers.append(layer)

## Regions
gis_file = r"D:\seismo-gis\collections\Bel_administrative_ROB\TAB\Bel_regions.TAB"
data = lbm.GisData(gis_file)
style = lbm.LineStyle(line_color="k", line_width=0.75)
layer = lbm.MapLayer(data, style)
layers.append(layer)

## Source zone model
gis_file = r"D:\GIS-data\KSB-ORB\Source Zone Models\ROB Seismic Source Model (Leynaud, 2000).TAB"
data = lbm.GisData(gis_file)
style = lbm.LineStyle(line_color="w", line_width=1)
layer = lbm.MapLayer(data, style)
layers.append(layer)


## Map parameters
region = (2.15, 6.85, 49.25, 51.75)
projection = 'merc'
title = ""
resolution = "h"
graticule_interval = (1, 1)

#fig_filespec = None
fig_filespec = r"C:\Temp\Eurocode8_hazard_map_new.PNG"

if fig_filespec:
	dpi = 600
else:
	dpi = 200


legend_style = None
title_style = None
#scalebar_style = lbm.ScalebarStyle((4.,49.25), 100, bar_style="fancy")
scalebar_style = None
border_style = lbm.MapBorderStyle()
graticule_style = lbm.GraticuleStyle(line_style=lbm.LineStyle(line_width=0.1),
									label_style=lbm.TextStyle(font_size=10))

map = lbm.LayeredBasemap(layers, title, projection, region=region, resolution=resolution,
						title_style=title_style, graticule_interval=graticule_interval,
						graticule_style=graticule_style, legend_style=legend_style,
						scalebar_style=scalebar_style, border_style=border_style,
						dpi=dpi)

map.plot(fig_filespec=fig_filespec, dpi=dpi)
