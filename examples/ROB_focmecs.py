"""
Plot focal mechanisms in ROB catalog
This script demonstrates how to plot focal mechanisms (aka beach balls)
using thematic styles for their size and color
"""

from __future__ import absolute_import, division, print_function, unicode_literals


import eqcatalog.seismodb as seismodb
from eqcatalog.source_models import rob_source_models_dict
from mapping.geotools.read_gis import read_gis_file
import mapping.layeredbasemap as lbm


#fig_filespec = None
#fig_filespec = "E:\\Home\\_kris\\Projects\\2012 - Electrabel\\Progress Report 2\\Figures\\FocalMechanisms.png"
#fig_filespec = "E:\\Home\\_kris\\Projects\\2013 - cAt_Rev\\Figures\\Maps\\FocalMechanisms.png"
fig_filespec = None

region = (3,7,50,51.5)
projection = "merc"
#title = "ROB focal mechanisms"
title = ""
resolution = "h"
graticule_interval = (1, 0.5)

layers = []

## Coastlines
coastline_style = lbm.LineStyle(line_color="k", line_width=2)
data = lbm.BuiltinData("coastlines")
layer = lbm.MapLayer(data, coastline_style)
layers.append(layer)

## Country borders
data = lbm.BuiltinData("countries")
country_style = lbm.LineStyle(line_color="k", line_width=2, line_pattern='--')
layer = lbm.MapLayer(data, country_style)
layers.append(layer)

## Source model
#sm_name= "Seismotectonic_Hybrid"
sm_name= "Seismotectonic"
gis_filespec = rob_source_models_dict[sm_name].gis_filespec
src_label_name = rob_source_models_dict[sm_name].column_map['id']
data = lbm.GisData(gis_filespec, src_label_name)
#label_style = lbm.TextStyle(color='darkred', font_weight="bold", horizontal_alignment="center", vertical_alignment="center")
label_style = None
polygon_style = lbm.PolygonStyle(line_width=2, line_color="darkred", fill_color="None", label_style=label_style)
line_style = lbm.LineStyle(line_width=2, line_color="red", label_style=None)
style = lbm.CompositeStyle(polygon_style=polygon_style, line_style=line_style)
layer = lbm.MapLayer(data, style, legend_label={"polygons": sm_name + "\narea sources", "lines": sm_name + "\nfault sources"})
layers.append(layer)

## Focal mechanisms
catalog = seismodb.query_ROB_LocalEQCatalog(region=region)
lons, lats, values, sdr = [],[], {"ML": [], "sof": [], "rake": []}, []
focmec_records = seismodb.query_ROB_FocalMechanisms(region=region)
for rec in focmec_records:
	lons.append(rec.lon)
	lats.append(rec.lat)
	values["ML"].append(rec.ML)
	sdr.append((rec.strike, rec.dip, rec.rake))
	if -135 <= rec.rake <= -45:
		sof = "Normal"
	elif 45 <= rec.rake < 135:
		sof = "Reverse"
	else:
		sof = "Strike slip"
	values["sof"].append(sof)
	values["rake"].append(rec.rake)
focmec_data = lbm.FocmecData(lons, lats, sdr, values=values)
focmec_data.sort(value_key="ML", ascending=False)
thematic_size = lbm.ThematicStyleGradient([1,3,5], [5,15,30], value_key="ML")

#colorbar_style = lbm.ColorbarStyle(title="Style of faulting", format="%s", spacing="uniform")
#colorbar_style = None
#thematic_color = lbm.ThematicStyleIndividual(["Normal", "Strike slip", "Reverse"], ['green', "yellow", "red"], value_key="sof", colorbar_style=colorbar_style)
#thematic_legend_style = lbm.LegendStyle(title="Focal mechanisms", location=1, label_spacing=1)

colorbar_style = lbm.ColorbarStyle(title="Rake", format="%s", ticks=None, spacing="proportional")
thematic_color = lbm.ThematicStyleRanges([-180, -135, -45, 45, 135, 180], ['yellow', "green", "yellow", "red", "yellow"], value_key="rake", colorbar_style=colorbar_style)
#thematic_color = lbm.ThematicStyleGradient([-180, -90, 0, 90, 180], ['yellow', "green", "yellow", "red", "yellow"], labels=["RL", "Nf", "LL", "Tf", "RL"], value_key="rake", colorbar_style=colorbar_style)
thematic_legend_style = None

focmec_style = lbm.FocmecStyle(size=thematic_size, fill_color=thematic_color, thematic_legend_style=thematic_legend_style)
layer = lbm.MapLayer(focmec_data, focmec_style)
layers.append(layer)


legend_style = lbm.LegendStyle(location=1)
title_style = lbm.DefaultTitleTextStyle
title_style.weight = "bold"
map = lbm.LayeredBasemap(layers, title, projection, region=region, title_style=title_style, graticule_interval=graticule_interval, resolution=resolution, legend_style=legend_style)
map.plot(fig_filespec=fig_filespec)
