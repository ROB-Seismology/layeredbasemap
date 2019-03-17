"""
Basic data types
"""

from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import int


try:
	## Python 2
	basestring
	PY2 = True
except:
	## Python 3
	PY2 = False
	basestring = str


import numpy as np
import shapely
import shapely.geometry
import shapely.wkt
import osr, ogr, gdal

gdal.UseExceptions()


__all__ = ['BuiltinData', 'export_ogr']


## Define WGS84 spatial reference system
WGS84 = osr.SpatialReference()
WGS84_EPSG = 4326
WGS84.ImportFromEPSG(WGS84_EPSG)


# TODO: add srs parameter (default: WGS84)
# TODO: remove ambiguity between region and bbox (llx, lly, urx, ury)
# TODO: add to_folium methods


class BasemapData(object):
	"""
	Base class for Basemap data, containing common methods
	"""


class BuiltinData(BasemapData):
	"""
	Class representing data built into Basemap

	:param feature:
		str, one of "bluemarble", "coastlines", "continents, "countries",
		"nightshade", "rivers", "shadedrelief")
	:param kwargs:
		additional keyword arguments for specific data sets,
		e.g. date_time for nightshade dataset
	"""
	def __init__(self, feature="continents", **kwargs):
		assert feature in ("bluemarble", "coastlines", "continents", "countries", "nightshade", "rivers", "shadedrelief"), "%s not recognized as builtin data" % feature
		self.feature = feature
		for key, val in kwargs.items():
			setattr(self, key, val)


class SingleData(BasemapData):
	@staticmethod
	def _get_multi_values(value):
		"""
		Convert single-data value parameter to multi-data values,
		used when we invoke to_multi_* methods

		:param value:
			dict or int, float, str, ...

		:return:
			dict or list of ints, floats, strs, ...
		"""
		if isinstance(value, dict):
			values = {}
			for key in value:
				values[key] = [value[key]]
		else:
			values = [value]
		return values

	def get_overriding_style(self, default_style):
		"""
		Override given style with information in :prop:`style_params`

		:param default_style:
			instance of :class:`BasemapStyle` or a derived class

		:return:
			instance of :class:`BasemapStyle` or a derived class
		"""
		if self.style_params:
			style = default_style.copy()
			## Remove style params that are None
			style_params = {k:v for (k,v) in self.style_params.items() if v is not None}
			style.update(style_params)
		else:
			style = default_style
		return style

	def to_multi_data(self):
		from .point import PointData
		from .line import LineData
		from .polygon import PolygonData
		from .text import TextData

		if isinstance(self, PointData):
			return self.to_multi_point()
		elif isinstance(self, LineData):
			return self.to_multi_line()
		elif isinstance(self, PolygonData):
			return self.to_multi_polygon()
		elif isinstance(self, TextData):
			return self.to_multi_text()

	def to_wkt(self):
		"""
		Convert to well-known text format

		:return:
			str
		"""
		return self.to_shapely().wkt

	def to_geojson(self):
		"""
		Convert to GeoJSON.

		:return:
			dict
		"""
		json = {'type': 'Feature'}
		json['geometry'] = shapely.geometry.mapping(self.to_shapely())
		props = {}
		if isinstance(self.value, dict):
			props = self.value.copy()
		elif self.value	is not None:
			props = {'value': self.value}
		if self.label:
			props['label'] = self.label
		if props:
			json["properties"] = props
		return json

	# TODO: dump_geojson method with json_handler for arrays and datetimes cf. eqcatalog

	def to_ogr_geom(self):
		"""
		Convert to ogr geometry

		:return:
			instance of :class:`ogr.Geometry`
		"""
		return ogr.CreateGeometryFromWkt(self.to_wkt())

	def construct_ogr_feature_definition(self, encoding='latin-1'):
		"""
		Construct ogr feature/layer definition based on :prop:`value`.
		Use OrderedDict for :prop:`value` if you want to control
		order of attribute columns

		:param encoding:
			str, encoding to use for non-ASCII characters
			(default: 'latin-1')

		:return:
			instance of :class:`ogr.FeatureDefn`
		"""
		multi_data = self.to_multi_data()
		return multi_data.construct_ogr_feature_definition(encoding=encoding)

	def to_ogr_feature(self, feature_definition=None, encoding='latin-1'):
		"""
		Convert to ogr feature

		:param feature_definition:
			instance of :class:`ogr.FeatureDefn`
			(default: None, will construct automatically from :prop:`value`
		:param encoding:
			str, encoding to use for non-ASCII characters
			(default: 'latin-1')

		:return:
			instance of :class:`ogr.Feature`
		"""
		import datetime
		import decimal

		if not feature_definition:
			feature_definition = self.construct_ogr_feature_definition(encoding)

		feature = ogr.Feature(feature_definition)

		if self.value or self.label:
			json = self.to_geojson()
			attributes = json["properties"]
			for idx in range(feature_definition.GetFieldCount()):
				fd = feature_definition.GetFieldDefn(idx)
				field_name = fd.GetName()
				field_value = attributes.get(field_name)
				if field_value is None or isinstance(field_value, (bool, int,
							np.integer, float, np.floating, decimal.Decimal)):
					pass
				#elif isinstance(field_value, np.integer):
				#	field_value = int(field_value)
				#elif isinstance(field_value, np.floating):
				#	field_value = float(field_value)
				elif isinstance(field_value, basestring):
					if not isinstance(field_value, bytes):
						field_value = field_value.encode(encoding,
										errors='xmlcharrefreplace')
				elif isinstance(field_value, (np.datetime64, datetime.datetime,
												datetime.date, datetime.time)):
					field_value = bytes(field_value)
				elif isinstance(field_value, (list, np.ndarray)):
					field_value = ','.join(map(str, field_value))
				else:
					try:
						isnan = np.isnan(field_value)
					except:
						field_value = str(field_value)
					else:
						if isnan:
							field_value = None

				if field_value is not None:
					feature.SetField(field_name, field_value)
		#feature.SetFID(0)
		feature.SetGeometry(self.to_ogr_geom())
		return feature

	def create_buffer(self, distance):
		"""
		Create buffer around point, line or polygon feature.

		Note: the buffer distance is in the same units as the dataset,
		which is normally degrees. If metric distance is required, the
		dataset should first be reprojected (not supported) or read
		in the native coordinate system!

		:param distance:
			float, buffer distance (in dataset units)

		:return:
			instance of :class:`PolygonData`
		"""
		from .polygon import PolygonData

		geom = self.to_ogr_geom()
		poly = geom.Buffer(distance)
		return PolygonData.from_ogr(poly)


class MultiData(BasemapData):
	def __len__(self):
		return len(self.lons)

	def __iter__(self):
		for i in range(len(self)):
			yield self.__getitem__(i)

	@staticmethod
	def _extend_multi_values(values1, values2):
		"""
		Extend multi-data values with values from another multi-data object.

		:param values1:
			dict or int, float, str, ..., master values
		:param values2:
			dict or int, float, str, ..., values to be appended
		"""
		if isinstance(values1, dict):
			for key in values1.keys():
				if isinstance(values2, dict):
					values1[key].extend(values2[key] or [])
		else:
			values1.extend(values2)

	@staticmethod
	def _append_to_multi_values(values, value):
		"""
		Extend multi-data values with single-data value.

		:param values:
			dict or int, float, str, ..., master values
		:param value:
			dict or int, float, str, ..., single-data value to be appended
		"""
		if isinstance(values, dict):
			for key in values.keys():
				if isinstance(value, dict) and key in value:
					values[key].append(value[key])
				else:
					values[key].append(None)
		else:
			values.append(value)

	def _get_value_at_index(self, index):
		"""
		Fetch value corresponding to given index.

		:param index:
			int

		:return:
			dict or single value
		"""
		if isinstance(self.values, dict):
			value = {}
			for key in self.values.keys():
				try:
					value[key] = self.values[key][index]
				except:
					value[key] = None
		else:
			try:
				value = self.values[index]
			except:
				value = None
		return value

	def _get_label_at_index(self, index):
		"""
		Fetch label corresponding to given index.

		:param index:
			int

		:return:
			str
		"""
		try:
			label = self.labels[index]
		except:
			label = ""
		return label

	def _get_style_params_at_index(self, index):
		"""
		Fetch style params corresponding to given index.

		:param index:
			int

		:return:
			dict
		"""
		style_params = {}
		for key in self.style_params.keys():
			try:
				value = self.style_params[key][index]
			except:
				value = None
			if value is not None:
				style_params[key] = value
		return style_params

	def get_overriding_style(self, default_style, index):
		"""
		Override given style with information in :prop:`style_params`

		:param default_style:
			instance of :class:`BasemapStyle` or a derived class
		:param index:
			int, index of single-data object

		:return:
			instance of :class:`BasemapStyle` or a derived class
		"""
		if self.style_params:
			style = default_style.copy()
			style.update(self._get_style_params_at_index(index))
		else:
			style = default_style
		return style

	def to_wkt(self):
		"""
		Convert to well-known text format

		:return:
			str
		"""
		return self.to_shapely().wkt

	def to_geojson(self, as_multi=False):
		"""
		Convert to GeoJSON.

		:param as_multi:
			bool, whether or not to export as 1 MultiData object (True)
			or as collection of SingleData objects (False)
			(default: False)

		:return:
			dict
		"""
		if as_multi:
			json = shapely.geometry.mapping(self.to_shapely())
			props = {}
			if isinstance(self.values, dict):
				props = self.values.copy()
			elif not (self.values is None or len(self.values) == 0
				or set(self.values) in (set([None]), set(['']), set([]))):
				props = {'values': self.values}
			if not (self.labels is None or len(self.labels) == 0
				or set(self.labels) in (set([None]), set(['']), set([]))):
				props['label'] = self.labels
			if props:
				json["properties"] = props
		else:
			json = {'type': 'FeatureCollection',
					'features': []}
			for item in self:
				json['features'].append(item.to_geojson())
		return json

	def to_ogr_geom(self):
		"""
		Convert to ogr geometry

		:return:
			instance of :class:`ogr.Geometry`
		"""
		return ogr.CreateGeometryFromWkt(self.to_wkt())

	def construct_ogr_feature_definition(self, encoding='latin-1'):
		"""
		Construct ogr feature/layer definition based on :prop:`values`.
		Use OrderedDict for :prop:`values` if you want to control
		order of attribute columns

		:param encoding:
			str, encoding to use for non-ASCII characters
			(default: 'latin-1')

		:return:
			instance of :class:`ogr.FeatureDefn`
		"""
		# TODO: order of field names?
		import datetime, decimal

		MININT, MAXINT = -2**31, 2**31 - 1
		feature_definition = ogr.FeatureDefn()
		if self.values or self.labels:
			json = self.to_geojson(as_multi=True)
			attributes = json["properties"]
			for field_name, field_values in attributes.items():
				field_name = field_name.encode(encoding, errors='xmlcharrefreplace')
				field_val = field_values[0]
				if isinstance(field_val, bool):
					fd = ogr.FieldDefn(field_name, ogr.OFTInteger)
					fd.SetSubType(ogr.OFSTBoolean)
				elif isinstance(field_val, (int, np.integer)):
					min_val = np.min(field_values)
					max_val = np.max(field_values)
					if min_val >= MININT and max_val <= MAXINT:
						fd = ogr.FieldDefn(field_name, ogr.OFTInteger)
					else:
						fd = ogr.FieldDefn(field_name, ogr.OFTInteger64)
				elif isinstance(field_val, (float, np.floating)):
					fd = ogr.FieldDefn(field_name, ogr.OFTReal)
				elif isinstance(field_val, decimal.Decimal):
					fd = ogr.FieldDefn(field_name, ogr.OFTReal)
					num_digits = field_val.as_tuple()[1][0]
					fd.SetPrecision(num_digits)
					#fd.SetWidth()
				elif isinstance(field_val, basestring):
					fd = ogr.FieldDefn(field_name, ogr.OFTString)
					#max_len = max(map(len, field_values))
					#fd.SetWidth(max_len + 5)
				elif isinstance(field_val, (datetime.datetime, np.datetime64)):
					fd = ogr.FieldDefn(field_name, ogr.OFTDateTime)
				elif isinstance(field_val, datetime.date):
					fd = ogr.FieldDefn(field_name, ogr.OFTDate)
				elif isinstance(field_val, datetime.time):
					fd = ogr.FieldDefn(field_name, ogr.OFTTime)
				else:
					msg = "Warning: Data type %s of field %s not recognized!"
					msg %= (type(field_val), field_name)
					print(msg)
					#fd = ogr.FieldDefn(field_name, ogr.OFTBinary)
					fd = ogr.FieldDefn(field_name, ogr.OFTString)

				feature_definition.AddFieldDefn(fd)

		return feature_definition

	def to_ogr_features(self, encoding='latin-1'):
		"""
		Convert to ogr features

		:param encoding:
			str, encoding to use for non-ASCII characters
			(default: 'latin-1')

		:return:
			list with instances of :class:`ogr.Feature`
		"""
		feature_definition = self.construct_ogr_feature_definition(encoding=encoding)
		features = []
		for item in self:
			features.append(item.to_ogr_feature(feature_definition,
												encoding=encoding))
		return features

	def export_gis(self, format, out_filespec, encoding='latin-1'):
		"""
		Export to GIS file
		Use OrderedDict for :prop:`values` if you want to control
		order of attribute columns

		:param format:
			str, OGR format specification (e.g., 'ESRI Shapefile',
			'MapInfo File', 'GeoJSON', 'MEMORY', ...)
		:param out_filespec:
			str, full path to output file, will also be used as layer name
		:param encoding:
			str, encoding to use for non-ASCII characters
			(default: 'latin-1')

		:return:
			instance of :class:`ogr.DataSource` if :param:`format`
			== 'MEMORY', else None
		"""
		import os

		# TODO: determine out_filespec automatically from format, or
		# determine driver from out_filespec extension
		driver = ogr.GetDriverByName(format)
		if not driver:
			print("Format %s not supported by ogr!" % format)
		else:
			ds = driver.CreateDataSource(out_filespec)
			name = os.path.splitext(os.path.split(out_filespec)[-1])[0]
			features = self.to_ogr_features(encoding=encoding)
			feature = features[0]
			geom_type = feature.GetGeometryRef().GetGeometryType()
			layer = ds.CreateLayer(name, WGS84, geom_type)

			## Set layer definition from feature definition
			for i in range(feature.GetFieldCount()):
				field = feature.GetFieldDefnRef(i)
				layer.CreateField(field)

			## Add all features to layer
			for feature in features:
				layer.CreateFeature(feature)
				## Dereference the feature
				feature = None

			if format.upper() == 'MEMORY':
				return ds
			else:
				## Save and close the data source
				ds = None


def export_ogr(lbm_data, layer_name):
	"""
	Create virtual OGR GIS file (in memory)

	return as GisData?
	"""
	import datetime

	#TODO: assert only 1 geometry type (or store in different layers?)
	#TODO: assert attributes are the same (at least for same geometry type)

	## Create an output datasource in memory
	outdriver = ogr.GetDriverByName('MEMORY')
	ds = outdriver.CreateDataSource('memData')

	## Open the memory datasource with write access
	outdriver.Open('memData', 1)

	## Create the spatial reference, WGS84
	srs = WGS84

	## Create the layer
	geom_type = lbm_data[0].get_ogr_geomtype()
	layer = ds.CreateLayer(layer_name, srs, geom_type)

	## Define data attributes
	if lbm_data[0].value:
		for key, val in lbm_data[0].value.items():
			if isinstance(val, basestring):
				field_type = ogr.OFTString
			elif isinstance(val, bool):
				field_type = ogr.OFTBinary
			elif isinstance(val, int):
				field_type = ogr.OFTInteger
			elif isinstance(val, float):
				field_type = ogr.OFTReal
			elif isinstance(val, datetime.datetime):
				field_type = ogr.OFTDateTime
			elif isinstance(val, datetime.date):
				field_type = ogr.OFTDate
			elif isinstance(val, datetime.time):
				field_type = ogr.OFTTime

			field_defn = ogr.FieldDefn(key, field_type)
			#field_defn.SetWidth(24)
			layer.CreateField(field_defn)

	## Process data and add the attributes and features to the shapefile
	for data in lbm_data:
		## Create the feature
		feature = ogr.Feature(layer.GetLayerDefn())

		## Set the attributes using the values from the delimited text file
		if data.value:
			for key, val in data.value.items():
				feature.SetField(key, val)

		## Create geometry from WKT
		geom = ogr.CreateGeometryFromWkt(data.to_wkt())

		## Set the feature geometry
		feature.SetGeometry(geom)

		## Create the feature in the layer (shapefile)
		layer.CreateFeature(feature)

		## Dereference the feature
		feature = None

	## Dereference the layer
	layer = None

	return ds
