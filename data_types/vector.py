"""
Mixed vector data
"""

from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import int


try:
	## Python 2
	basestring
except:
	## Python 3
	basestring = str


import numpy as np
import ogr

from .base import BasemapData
from .point import PointData, MultiPointData
from .line import LineData, MultiLineData
from .polygon import PolygonData, MultiPolygonData


__all__ = ['CompositeData', 'GisData']



class CompositeData(BasemapData):
	def __init__(self, points=None, lines=[], polygons=[], texts=[]):
		self.points = points
		self.lines = lines
		self.polygons = polygons
		self.texts = texts


class GisData(BasemapData):
	"""
	:param filespec:
		str, full path to GIS file
	:param label_colname:
		str, name of column to use for labels
		(default: None)
	:param selection_dict:
		dict, mapping column names to values; only matching records will be selected
		Note: multiple values mapped to a column name will act as logical OR,
		multiple keys will act as logical AND operator.
	:param joined_attributes:
		dict, mapping additional attribute names (not present in the GIS table)
		to dictionaries containing two entries:
		- 'key' string, GIS attribute that will be used to join
		- 'values': dict, mapping values of 'key' to attribute values
	:param convert_closed_lines:
		bool, whether or not to silently convert closed lines to polygons
		(default: True)
	:param invert_selection:
		bool, whether or not to invert the selection criteria in
		:param:`selection_dict`
		(default: False)
	"""
	def __init__(self, filespec, label_colname=None, selection_dict=None,
				joined_attributes={}, style_params={}, convert_closed_lines=True,
				invert_selection=False):
		self.filespec = filespec
		self.label_colname = label_colname
		self.selection_dict = selection_dict or {}
		self.joined_attributes = joined_attributes or {}
		self.style_params = style_params or {}
		self.convert_closed_lines = convert_closed_lines
		self.invert_selection = invert_selection

	def get_attributes(self):
		"""
		Read GIS attributes (column names).

		:return:
			list of strings
		"""
		from mapping.geotools.read_gis import read_gis_file_attributes

		return read_gis_file_attributes(self.filespec)

	def get_data(self, point_value_colnames=None, line_value_colnames=None,
					polygon_value_colnames=None, layer_num=None):
		"""
		Read GIS records, transforming into LayeredBasemap data types

		:param point_value_colnames:
			list of strings, names of columns to read for point data
			(default: None, will read all available columns)
		:param line_value_colnames:
			list of strings, names of columns to read for line data
			(default: None, will read all available columns)
		:param polygon_value_colnames:
			list of strings, names of columns to read for polygon data
			(default: None, will read all available columns)

		:return:
			(MultiPointData, MultiLineData, MultiPolygonData) tuple
		"""
		from collections import OrderedDict
		from mapping.geotools.read_gis import read_gis_file

		colnames = self.get_attributes()
		if point_value_colnames is None:
			point_value_colnames = colnames[:]
		if line_value_colnames is None:
			line_value_colnames = colnames[:]
		if polygon_value_colnames is None:
			polygon_value_colnames = colnames[:]

		## Make sure attributes needed to link with joined_attributes are stored too
		linked_attributes = []
		for attrib_name in self.joined_attributes.keys():
			linked_attribute = self.joined_attributes[attrib_name]['key']
			if not linked_attribute in linked_attributes:
				linked_attributes.append(linked_attribute)
		## while preserving order of original GIS attributes
		point_value_colnames = [col for col in colnames if (col in point_value_colnames
								or col in linked_attributes)]
		line_value_colnames = [col for col in colnames if (col in line_value_colnames
								or col in linked_attributes)]
		polygon_value_colnames = [col for col in colnames if (col in polygon_value_colnames
								or col in linked_attributes)]

		## Note: it is absolutely necessary to initialize all empty lists
		## explicitly, otherwise unexpected things may happen in subsequent
		## calls of this method!
		point_data = MultiPointData([], [], values=[], labels=[])
		point_data.values = OrderedDict()
		for colname in point_value_colnames:
			point_data.values[colname] = []
		line_data = MultiLineData([], [], values=[], labels=[])
		line_data.values = OrderedDict()
		for colname in line_value_colnames:
			line_data.values[colname] = []
		polygon_data = MultiPolygonData([], [], interior_lons=[], interior_lats=[],
				values=[], labels=[])
		polygon_data.values = OrderedDict()
		for colname in polygon_value_colnames:
			polygon_data.values[colname] = []

		if not self.invert_selection:
			## Delegate selection to read_gis_file
			attribute_filter = self.selection_dict
		else:
			attribute_filter = None
		for rec in read_gis_file(self.filespec, layer_num=layer_num,
								attribute_filter=attribute_filter):
			selected = np.zeros(len(self.selection_dict.keys()))
			for i, (selection_colname, selection_value) in enumerate(self.selection_dict.items()):
				if rec[selection_colname] == selection_value:
					selected[i] = 1
				elif hasattr(selection_value, '__iter__') and rec[selection_colname] in selection_value:
					selected[i] = 1
				else:
					selected[i] = 0
			if self.invert_selection:
				selected = np.abs(selected - 1)
			if selected.all():
				label = rec.get(self.label_colname)
				if label is None and self.label_colname in self.joined_attributes:
					key = self.joined_attributes[self.label_colname]['key']
					label = self.joined_attributes[self.label_colname]['values'].get(rec[key])
				geom = rec['obj']
				geom_type = geom.GetGeometryName()
				## Silently convert closed polylines to polygons
				if (self.convert_closed_lines and geom_type == "LINESTRING"
					and geom.IsRing() and geom.GetPointCount() > 3):
					wkt = geom.ExportToWkt().replace("LINESTRING (", "POLYGON ((") + ")"
					geom = ogr.CreateGeometryFromWkt(wkt)
					geom_type = "POLYGON"
				if geom_type == "POINT":
					pt = PointData.from_ogr(geom)
					pt.label = label
					pt.value = {k: rec[k] for k in point_value_colnames if k in rec}
					point_data.append(pt)
				elif geom_type == "MULTIPOINT":
					# TODO: needs to be tested
					multi_pt = MultiPointData.from_ogr(geom)
					for pt in multi_pt:
						pt.label = label
						pt.value = {k: rec[k] for k in point_value_colnames if k in rec}
						point_data.append(pt)
				elif geom_type == "LINESTRING":
					if geom.GetPointCount() > 1:
						line = LineData.from_ogr(geom)
						line.label = label
						line.value = {k: rec[k] for k in line_value_colnames if k in rec}
						line_data.append(line)
				elif geom_type == "MULTILINESTRING":
					multi_line = MultiLineData.from_ogr(geom)
					for line in multi_line:
						line.label = label
						line.value = {k: rec[k] for k in line_value_colnames if k in rec}
						line_data.append(line)
				elif geom_type == "POLYGON":
					## Silently skip polygons with less than 3 points
					if geom.GetGeometryRef(0).GetPointCount() > 2:
						polygon = PolygonData.from_ogr(geom)
						polygon.label = label
						polygon.value = {k: rec[k] for k in polygon_value_colnames if k in rec}
						polygon_data.append(polygon)
				elif geom_type == "MULTIPOLYGON":
					try:
						multi_polygon = MultiPolygonData.from_ogr(geom)
					except:
						## Keep only the first polygon
						multi_polygon = []
						for p in range(geom.GetGeometryCount()):
							try:
								polygon = PolygonData.from_ogr(geom.GetGeometryRef(p))
							except:
								print("Warning: Omitting part #%d of multipolygon" % p)
							else:
								if polygon:
									## polygon may sometimes be None
									multi_polygon.append(polygon)
					for polygon in multi_polygon:
						polygon.label = label
						polygon.value = {k: rec[k] for k in polygon_value_colnames if k in rec}
						polygon_data.append(polygon)

		## Set style_params at end to avoid errors when appending data
		point_data.style_params = self.style_params.get('points') or self.style_params
		line_data.style_params = self.style_params.get('lines') or self.style_params
		polygon_data.style_params = self.style_params.get('polygons') or self.style_params

		## Append joined attributes
		for attrib_name in self.joined_attributes.keys():
			key = self.joined_attributes[attrib_name]['key']
			value_dict = self.joined_attributes[attrib_name]['values']
			first_value = list(value_dict.values())[0]
			first_non_none_value = next((val for val in value_dict.values() if val is not None), None)
			if isinstance(first_non_none_value, (int, float)):
				default = np.nan
			elif isinstance(first_non_none_value, basestring):
				default = ""
			else:
				default = np.nan
			point_data.values[attrib_name] = [value_dict.get(key_val, default) for key_val in point_data.values[key]]
			line_data.values[attrib_name] = [value_dict.get(key_val, default) for key_val in line_data.values[key]]
			polygon_data.values[attrib_name] = [value_dict.get(key_val, default) for key_val in polygon_data.values[key]]
		return (point_data, line_data, polygon_data)

	def export(self, format, out_filespec):
		"""
		Export GIS file to another format

		:param format:
			str, OGR format speciication
		:param out_filespec:
			str, full path to output file
		"""
		# TODO: determine out_filespec automatically from format, or
		# determine driver from out_filespec extension
		driver = ogr.GetDriverByName(format)
		if driver:
			in_ds = ogr.Open(self.filespec, 0)
			out_ds = driver.CopyDataSource(in_ds, out_filespec)
		else:
			print("Driver %s does not support CopyDataSource() method" % format)
