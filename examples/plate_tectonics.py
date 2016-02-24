"""
Plot global plate tectonic map
"""

import os
import mapping.Basemap as lbm
from mapping.geo.readGIS import wgs84


#region = (-30, 330, -90, 90)
region = (-180, 180, -90, 90)
projection = "robin"
resolution = "c"
graticule_interval = (60, 30)


layers = []

## Plates
gis_filespec = r"D:\GIS-data\Plate Tectonics\Plates\NUVEL-1A Plates.TAB"
data = lbm.GisData(gis_filespec, label_colname="Name")
#thematic_values = range(0, 17)
#thematic_styles = "random_color,4"
thematic_values = ["Antarctic plate", "African plate", "Australian plate",
					"Arabian plate", "Eurasian plate", "North American plate",
					"South American plate", "Indian plate", "Scotia plate",
					"Nazca plate", "Cocos plate", "Pacific plate",
					"Philippine plate", "Juan de Fuca plate", "Caribbean plate"]
thematic_styles = ["#8c9cbd", "#ff9c7b", "#ffb584",
					"#ffce5a", "#84a573", "#a5847b",
					"#ad84b5", "#ff424a", "#a5c6bd",
					"#c6efe7", "#9cadce", "#ffe7ad",
					"#ff7373", "#9cadce", "#ffa59c"]
thematic_color = lbm.ThematicStyleIndividual(thematic_values, thematic_styles, value_key='Name')
thematic_legend_style = None
def text_filter(plate_name):
	return plate_name.replace(" plate", "\nplate").title()
label_style = lbm.TextStyle(font_weight='demi', font_size=8, text_filter=text_filter)
polygon_style = lbm.PolygonStyle(line_color='k', line_width=0.5, fill_color=thematic_color,
							thematic_legend_style=thematic_legend_style, label_style=label_style)
plate_style = lbm.CompositeStyle(polygon_style=polygon_style)
layer = lbm.MapLayer(data, plate_style, legend_label={"polygons": "Name"})
layers.append(layer)


## Coastlines and countries
data = lbm.BuiltinData("continents")
continent_style = lbm.PolygonStyle(line_color='k', line_width=0.5, fill_color="w", alpha=0.2)
layer = lbm.MapLayer(data, continent_style)
layers.append(layer)

data = lbm.BuiltinData("countries")
country_style = lbm.LineStyle(line_color='k', line_width=0.25)
layer = lbm.MapLayer(data, country_style)
layers.append(layer)


## Plate motion vectors
gis_folder = r"D:\GIS-data\Plate Tectonics\Stress & Strain"
vx_filespec = os.path.join(gis_folder, "nnr_nuvel1a.vx.1.-1.grd")
data = lbm.MeshGridVectorData.from_vx_filespec(vx_filespec, down_sampling=15)
data.grdx.srs = wgs84
data.grdy.srs = wgs84
vector_style = lbm.VectorStyle(color='r', scale=0.3, width=2, head_axis_length=2.5, head_width=5)
layer = lbm.MapLayer(data, vector_style)
layers.append(layer)


legend_style = None
title = ""
scalebar_style = None
title_style = lbm.TextStyle()
graticule_style = lbm.GraticuleStyle(line_style=lbm.LineStyle(line_width=0.5, dash_pattern=[2,2], alpha=0.25),
						label_style=lbm.TextStyle(font_size=9), annot_style="+/-")
map = lbm.LayeredBasemap(layers, title, projection, region=region, title_style=title_style,
						graticule_interval=graticule_interval, resolution=resolution,
						legend_style=legend_style, scalebar_style=scalebar_style,
						graticule_style=graticule_style)

#fig_filespec = os.path.join(out_folder, fig_filename)
fig_filespec = None
map.plot(fig_filespec=fig_filespec, dpi=120)
