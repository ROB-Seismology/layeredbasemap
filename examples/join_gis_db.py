"""
Example showing how information from e.g. a database can be joined with
geographic objects from a GIS file.
"""

import numpy as np
import eqcatalog.seismodb as seismodb
from mapping.geotools.readGIS import read_GIS_file
import mapping.Basemap as lbm


## Read communes from database
db_records = list(seismodb.query_seismodb_table("communes", where_clause='country="BE"'))

## Read GIS table
#gis_filespec = r"D:\seismo-gis\collections\Bel_administrative_ROB\TAB\Bel_villages_points.TAB"
gis_filespec = r"D:\seismo-gis\collections\Bel_administrative_ROB\TAB\Bel_communes_avant_fusion_new.TAB"
gis_records = read_GIS_file(gis_filespec)


## Compare number of records
print("Number of records: %d (db), %d (GIS)" % (len(db_records), len(gis_records)))


## Plot a database attribute
attribute = "language"
#attribute = "id_province"
#attribute = "id_main"
region = (1,8,49,52)
projection = "tmerc"
title = "Join between seismodb and GIS"

layers = []

joined_attributes = {}
joined_attributes[attribute] = {'key': 'ID', 'values': {rec['id']: rec[attribute] for rec in db_records}}

## Commune layer
gis_data = lbm.GisData(gis_filespec, joined_attributes=joined_attributes)
if attribute == "language":
	tsi = lbm.ThematicStyleIndividual(["FR", "NL", "DE"], ['r', 'y', 'b'], value_key='language')
	thematic_legend_style = lbm.LegendStyle(title=attribute, location=3)
elif attribute == "id_province":
	tsi = lbm.ThematicStyleGradient(values=[1,6,11], styles=["r", "g", "b"], value_key='id_province')
	thematic_legend_style = None
	colorbar_style = lbm.ColorbarStyle(title=attribute, ticks=range(1,11), spacing="proportional")
	tsi.colorbar_style = colorbar_style
elif attribute == "id_main":
	values = joined_attributes[attribute]['values'].values()
	vmin, vmax = np.min(values), np.max(values)
	tsi = lbm.ThematicStyleColormap(value_key="id_main", vmin=vmin, vmax=vmax)
	thematic_legend_style = None
	colorbar_style = lbm.ColorbarStyle(title=attribute)
	tsi.colorbar_style = colorbar_style
polygon_style = lbm.PolygonStyle(fill_color=tsi, line_width=0.1, thematic_legend_style=thematic_legend_style)
style = lbm.CompositeStyle(polygon_style=polygon_style)
commune_layer = lbm.MapLayer(gis_data, style, legend_label={"polygons": ""})
layers.append(commune_layer)

## Province layer
data = lbm.GisData(r"D:\seismo-gis\collections\Bel_administrative_ROB\TAB\Bel_provinces.TAB")
polygon_style = lbm.PolygonStyle(line_width=1, fill_color='none')
gis_style = lbm.CompositeStyle(polygon_style=polygon_style)
province_layer = lbm.MapLayer(data, gis_style, legend_label={"polygons": ""})
layers.append(province_layer)

map = lbm.LayeredBasemap(layers, title, projection, region=region)
fig_filespec = None
#fig_filespec = r"C:\Temp\seismodb_%s.png" % attribute
map.plot(fig_filespec=fig_filespec)
