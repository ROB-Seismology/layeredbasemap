"""
Plot focal mechanisms in ROB catalog
"""
import eqcatalog.seismodb as seismodb
from eqcatalog.source_models import rob_source_models_dict
from mapping.geo.readGIS import read_GIS_file
from mapping.Basemap.LayeredBasemap import *


region = (2,7,49.25,51.75)
projection = "merc"
title = "ROB focal mechanisms"
resolution = "h"
grid_interval = (2, 1)

layers = []

## Coastlines
coastline_style = LineStyle(line_color="k", line_width=2)
data = BuiltinData("coastlines")
layer = MapLayer(data, coastline_style)
layers.append(layer)

## Country borders
data = BuiltinData("countries")
country_style = LineStyle(line_color="k", line_width=2, line_pattern='--')
layer = MapLayer(data, country_style)
layers.append(layer)

## Source model
sm_name= "Seismotectonic_Hybrid"
gis_filespec = rob_source_models_dict[sm_name].gis_filespec
src_label_name = rob_source_models_dict[sm_name].column_map['id']
data = GisData(gis_filespec, src_label_name)
#label_style = TextStyle(color='darkred', font_weight="bold", horizontal_alignment="center", vertical_alignment="center")
label_style = None
polygon_style = PolygonStyle(line_width=2, line_color="darkred", fill_color="None", label_style=label_style)
line_style = LineStyle(line_width=2, line_color="red", label_style=None)
style = CompositeStyle(polygon_style=polygon_style, line_style=line_style)
layer = MapLayer(data, style, legend_label={"polygons": sm_name + "\narea sources", "lines": sm_name + "\nfault sources"})
layers.append(layer)

## Focal mechanisms
catalog = seismodb.query_ROB_LocalEQCatalog(region=region)
gis_filespec = r"D:\GIS-data\KSB-ORB\FocalMechanisms.TAB"
focmec_records = read_GIS_file(gis_filespec)
lons, lats, values, sdr = [],[], {"ML": [], "sof": []}, []
for rec in focmec_records:
	eq = catalog.get_record(rec["ID_Earth"])
	lons.append(eq.lon)
	lats.append(eq.lat)
	values["ML"].append(eq.ML)
	strike, dip, rake = rec["Strike1"], rec["Dip1"], rec["Rake1"]
	sdr.append((strike, dip, rake))
	if -135 <= rake <= -45:
		sof = "Normal"
	elif 45 <= rake < 135:
		sof = "Reverse"
	else:
		sof = "Strike slip"
	values["sof"].append(sof)
## Sort from large to small magnitude
sorted_indexes = np.argsort(values["ML"])[::-1]
lons = np.array(lons)[sorted_indexes]
lats = np.array(lats)[sorted_indexes]
sdr = np.array(sdr)[sorted_indexes]
values["ML"] = np.array(values["ML"])[sorted_indexes]
values["sof"] = np.array(values["sof"])[sorted_indexes]
focmec_data = FocmecData(lons, lats, sdr, values)
thematic_size = ThematicStyleGradient([1,3,5], [4,12,24], value_key="ML")
thematic_color = ThematicStyleIndividual(["Normal", "Reverse", "Strike slip"], ['green', "red", "yellow"], value_key="sof")
focmec_style = FocmecStyle(size=thematic_size, fill_color=thematic_color)
layer = MapLayer(focmec_data, focmec_style)
layers.append(layer)

legend_style = LegendStyle(location=2)
title_style = DefaultTitleTextStyle
title_style.weight = "bold"
map = LayeredBasemap(layers, title, projection, region=region, title_style=title_style, grid_interval=grid_interval, resolution=resolution, legend_style=legend_style)
map.plot()
