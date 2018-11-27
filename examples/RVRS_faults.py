"""
Plot map of the RVRS fault model
"""

import os

from eqcatalog.source_models import rob_source_models_dict
import mapping.layeredbasemap as lbm


fig_folder = r"E:\Home\_kris\Publications\2014 - DGEB"
fig_filespec = None
#fig_filespec = os.path.join(fig_folder, "SourceModel_RVRS_CSS.png")


layers = []

## Coastlines
data = lbm.BuiltinData("coastlines")
style = lbm.LineStyle()
layer = lbm.MapLayer(data, style)
layers.append(layer)

## Countries
data = lbm.BuiltinData("countries")
style = lbm.LineStyle(line_pattern="dashed")
layer = lbm.MapLayer(data, style)
layers.append(layer)

## Fault sources (projected fault planes)
sm_name = "RVRS_CSS"
gis_filespec = rob_source_models_dict[sm_name].gis_filespec
gis_filespec = gis_filespec.split('_')[0] + ".TAB"
#src_label_name = rob_source_models_dict[sm_name].column_map['id']
src_label_name = None
data = lbm.GisData(gis_filespec, src_label_name)
label_style = lbm.TextStyle(color='indigo', font_weight="bold", horizontal_alignment="center", vertical_alignment="center")
#polygon_style = lbm.PolygonStyle(line_width=1, line_color="None", fill_color="orangered", label_style=label_style, alpha=0.5)
polygon_style = lbm.PolygonStyle(line_width=2, line_color="black", line_pattern='dashed', fill_color="orangered", label_style=label_style, alpha=0.5)
style = lbm.CompositeStyle(polygon_style=polygon_style)
layer = lbm.MapLayer(data, style, legend_label={"polygons": "Fault planes"})
layers.append(layer)

## Fault sources (surface traces)
sm_name = "RVRS_CSS"
gis_filespec = rob_source_models_dict[sm_name].gis_filespec
#src_label_name = rob_source_models_dict[sm_name].column_map['id']
src_label_name = None
data = lbm.GisData(gis_filespec, src_label_name)
#label_style = lbm.TextStyle(color='indigo', font_weight="bold", horizontal_alignment="center", vertical_alignment="center")
front_style = lbm.FrontStyle('asterisk', interval=15, num_sides=1, line_color=None, line_width=None, angle=180)
line_style = lbm.LineStyle(line_width=3, line_color="red", label_style=None, front_style=front_style)
style = lbm.CompositeStyle(line_style=line_style)
layer = lbm.MapLayer(data, style, legend_label={"lines": "Fault traces"})
layers.append(layer)

## Background source
sm_name = "RVRS_area"
gis_filespec = rob_source_models_dict[sm_name].gis_filespec
#src_label_name = rob_source_models_dict[sm_name].column_map['id']
src_label_name = None
data = lbm.GisData(gis_filespec, src_label_name)
label_style = lbm.TextStyle(color='indigo', font_weight="bold", horizontal_alignment="center", vertical_alignment="center")
polygon_style = lbm.PolygonStyle(line_width=2, line_color="indigo", fill_color="None", label_style=label_style)
style = lbm.CompositeStyle(polygon_style=polygon_style)
layer = lbm.MapLayer(data, style, legend_label={"polygons": "Background zone"})
layers.append(layer)

region = (4, 7.5, 50.25, 52)
projection = "merc"
legend_style = lbm.LegendStyle(location=1)
#legend_style = None
title = "RVG fault model"
graticule_style = lbm.GraticuleStyle(annot_axes="SE")
map = lbm.LayeredBasemap(layers, title, projection, region=region, graticule_interval=(1,0.5), graticule_style=graticule_style, legend_style=legend_style)
map.plot(fig_filespec=fig_filespec)
