"""
Point data
"""

from __future__ import absolute_import, division, print_function, unicode_literals


import numpy as np
import shapely
import shapely.geometry
import shapely.wkt
import ogr

from .base import SingleData, MultiData


__all__ = ['PointData', 'MultiPointData']


class PointData(SingleData):
	"""
	Basemap data corresponding to a single point

	:param lon:
		float, longitude
	:param lat:
		float, latitude
	:param z:
		float depth
		(default: None)
	:param value:
		str, int, float or dictionary mapping keywords to str, int or
		float. Used for thematic mapping, in conjunction with a layer
		style containing thematic elements
		(default: None)
	:param label:
		str, label to be plotted alongside point (if label_style in
		corresponding layer style is not None)
		(default: "")
	:param style_params:
		dict, mapping style parameters to a value. These values will
		override the overall layer style.
		Note: style parameter keys correspond to any single-valued
		property of a given style or text-style properties of the
		label style in the given style, if present, as there is no overlap
		in property names between PointStyle, LineStyle and PolygonStyle
		on the one hand and TextStyle on the other hand.
		(default: None --> {})
	"""
	def __init__(self, lon, lat, z=None, value=None, label="", style_params=None):
		self.lon = lon
		self.lat = lat
		self.z = z
		self.value = value
		self.label = label
		self.style_params = style_params or {}

	def __len__(self):
		return 1

	def __iter__(self):
		for i in range(1):
			yield self

	def to_shapely(self):
		"""
		Convert to shapely Point object
		"""
		if self.z is None:
			return shapely.geometry.Point(self.lon, self.lat)
		else:
			return shapely.geometry.Point(self.lon, self.lat, self.z)

	def get_ogr_geomtype(self):
		return ogr.wkbPoint

	def to_multi_point(self):
		"""
		Convert to multi-point data

		:return:
			instance of :class:`MultiPointData`
		"""
		values = self._get_multi_values(self.value)
		style_params = self._get_multi_values(self.style_params)
		return MultiPointData([self.lon], [self.lat], [self.z], values=values,
							labels=[self.label], style_params=style_params)

	@classmethod
	def from_shapely(cls, pt, value=None, label="", style_params=None):
		"""
		Create from shapely Point object.

		:param pt:
			instance of :class:`shapely.geometry.Point`
		:param value:
		:param label:
		:param style_params:
			see :meth:`__init__`

		:return:
			instance of :class:`PointData`
		"""
		assert pt.geom_type == "Point"
		z = pt.z if pt.has_z else None
		return PointData(pt.x, pt.y, z=z, value=value, label=label,
						style_params=style_params)

	@classmethod
	def from_wkt(cls, wkt, value=None, label="", style_params=None):
		"""
		Create from well-known text

		:param wkt:
			str, well-known text desciption of geometry
		:param value:
		:param label:
		:param style_params:
			see :meth:`__init__`

		:return:
			instance of :class:`PointData`
		"""
		pt = shapely.geometry.Point(shapely.wkt.loads(wkt))
		return cls.from_shapely(pt, value=value, label=label,
								style_params=style_params)

	@classmethod
	def from_ogr(cls, geom, value=None, label="", style_params=None):
		"""
		Create from OGRPoint object

		:param geom:
			OGRPoint object
		:param value:
		:param label:
		:param style_params:
			see :meth:`__init__`

		:return:
			instance of :class:`PointData`
		"""
		return cls.from_wkt(geom.ExportToWkt(), value=value, label=label,
							style_params=style_params)

	def is_inside(self, pg_data):
		"""
		Check if this point is inside given polygon

		:param pg_data:
			instance of :class:`PolygonData`

		:return:
			bool
		"""
		from .polygon import PolygonData
		assert isinstance(pg_data, PolygonData)
		return pg_data.contains(self)


class MultiPointData(MultiData):
	"""
	Basemap data corresponding to a group of points

	:param lons:
		list or array of floats, longitudes
	:param lats:
		list or array of floats, latitudes
	:param z:
		list or array of floats, depths
		(default: None)
	:param values:
		list of strings, ints or floats, or dictionary mapping
		keywords to lists of strings, ints or floats.
		Used for thematic mapping, in conjunction with a layer style
		containing thematic elements
		(default: None --> [])
	:param labels:
		list of strings, labels to be plotted alongside points (if
		label_style in corresponding layer style is not None)
		(default: None --> [])
	:param style_params:
		dict, mapping style parameters to a list of values. These values
		will override the overall layer style.
		Note: style parameter keys correspond to any single-valued
		property of a given style or text-style properties of the
		label style in the given style, if present, as there is no overlap
		in property names between PointStyle, LineStyle and PolygonStyle
		on the one hand and TextStyle on the other hand.
		(default: None --> {})
	"""
	def __init__(self, lons, lats, z=None, values=None, labels=None, style_params=None):
		self.lons = lons
		self.lats = lats
		self.z = z or [None] * len(lons)
		self.values = values or []
		self.labels = labels or []
		self.style_params = style_params or {}

	def __getitem__(self, index):
		lon = self.lons[index]
		lat = self.lats[index]
		z = self.z[index]
		value = self._get_value_at_index(index)
		label = self._get_label_at_index(index)
		style_params = self._get_style_params_at_index(index)
		return PointData(lon, lat, z=z, value=value, label=label,
						style_params=style_params)

	@classmethod
	def from_points(cls, point_list):
		"""
		Create from a list of points

		:param point_list:
			list with instances of :class:`PointData`

		:return:
			instance of :class:`MultiPointData`
		"""
		lons, lats, Z, labels = [], [], [], []
		pt0 = point_list[0]
		values = SingleData._get_multi_values(pt0.value)
		style_params = SingleData._get_multi_values(pt0.style_params)
		for pt in point_list:
			lons.append(pt.lon)
			lats.append(pt.lat)
			Z.append(pt.z)
			labels.append(pt.label)
			cls._append_to_multi_values(values, pt.value)
			cls._append_to_multi_values(style_params, pt.style_params)
		return MultiPointData(lons, lats, z=Z, values=values, labels=labels,
							style_params=style_params)

	def append(self, pt):
		"""
		Append point(s)

		:param pt:
			instance of :class:`PointData` or :class:`MultiPointData`
		"""
		if isinstance(pt, PointData):
			pt = pt.to_multi_point()
		if isinstance(pt, MultiPointData):
			self.lons = np.concatenate([self.lons, pt.lons])
			self.lats = np.concatenate([self.lats, pt.lats])
			self.z = np.concatenate([self.z, pt.z])
			self._extend_multi_values(self.values, pt.values)
			self.labels.extend(pt.labels)
			self._extend_multi_values(self.style_params, pt.style_params)

	def get_masked_data(self, bbox):
		"""
		Apply rectangular mask to multipoint data.

		:param bbox:
			(lonmin,  lonmax, latmin, latmax) tuple

		:return:
			instance of :class:`MultiPointData`, where lons, lats,
			values and labels are replaced with masked arrays
		"""
		import numpy.ma as ma
		lonmin, lonmax, latmin, latmax = bbox
		lon_mask = ma.masked_outside(self.lons, lonmin, lonmax)
		lat_mask = ma.masked_outside(self.lats, latmin, latmax)
		lons = ma.array(self.lons, mask=lon_mask.mask + lat_mask.mask).compressed()
		lats = ma.array(self.lats, mask=lon_mask.mask + lat_mask.mask).compressed()
		Z = ma.array(self.z, lon_mask.mask + lat_mask.mask).compressed()
		labels = ma.array(self.labels, mask=lon_mask.mask + lat_mask.mask).compressed()
		if isinstance(self.values, dict):
			values = {}
			for key, val in self.values.items():
				values[key] = ma.array(val, mask=lon_mask.mask + lat_mask.mask).compressed()
		else:
			values = ma.array(values, mask=lon_mask.mask + lat_mask.mask).compressed()
		style_params = {}
		for key, val in self.style_params.items():
			style_params[key] = ma.array(val, mask=lon_mask.mask + lat_mask.mask).compressed()
		return MultiPointData(lons, lats, z=Z, values=values, labels=labels,
							style_params=style_params)

	def to_shapely(self):
		"""
		Convert to shapely Point object
		"""
		if self.z is None or set(self.z) == set([None]):
			return shapely.geometry.MultiPoint(list(zip(self.lons, self.lats)))
		else:
			return shapely.geometry.MultiPoint(list(zip(self.lons, self.lats, self.z)))

	def get_ogr_geomtype(self):
		return ogr.wkbMultiPoint

	@classmethod
	def from_shapely(cls, mp, values=None, labels=None, style_params=None):
		"""
		Create from shapely MultiPoint object

		:param mp:
			instance of :class:`shapely.geometry.MultiPoint`
		:param values:
		:param labels:
		:param style_params:
			see :meth:`__init__`

		:return:
			instance of :class:`MultiPointData`
		"""
		assert mp.geom_type == "MultiPoint"
		Z = [pt.z for pt in mp] if mp.has_z else None
		return MultiPointData([pt.x for pt in mp], [pt.y for pt in mp], Z,
						values=values, labels=labels, style_params=style_params)

	@classmethod
	def from_wkt(cls, wkt, values=None, labels=None, style_params=None):
		"""
		Create from well-known text

		:param wkt:
			str, well-known text desciption of geometry
		:param values:
		:param labels:
		:param style_params:
			see :meth:`__init__`

		:return:
			instance of :class:`MultiPointData`
		"""
		mp = shapely.geometry.MultiPoint(shapely.wkt.loads(wkt))
		return cls.from_shapely(mp, values=values, labels=labels,
								style_params=style_params)

	@classmethod
	def from_ogr(cls, geom, values=None, labels=None, style_params=None):
		"""
		Create from OGRMultiPoint object

		:param geom:
			OGRMultiPoint object
		:param values:
		:param labels:
		:param style_params:
			see :meth:`__init__`

		:return:
			instance of :class:`MultiPointData`
		"""
		return cls.from_wkt(geom.ExportToWkt(), values=values, labels=labels,
							style_params=style_params)

	def get_centroid(self):
		"""
		Determine centroid of point cloud

		:return:
			instance of :class:`PointData`
		"""
		centroid = self.to_shapely().centroid
		return PointData(centroid.x, centroid.y)

	def sort(self, value_key=None, ascending=True):
		"""
		Sort data in-place based on a value column

		:param value_key:
			str, name of value column to be used for sorting
			(default: None, assumes values is a single list or array)
		:param ascending:
			bool, whether sort order should be ascending (True)
			or descending (False)
			(default: True)

		:return:
			array with indexes representing sort order
		"""
		sorted_indexes = None
		if value_key is None and not isinstance(self.values, dict):
			sorted_indexes = np.argsort(self.values)
			if not ascending:
				sorted_indexes = sorted_indexes[::-1]
			self.values = np.array(self.values)[sorted_indexes]
		elif isinstance(self.values, dict):
			sorted_indexes = np.argsort(self.values[value_key])
			if not ascending:
				sorted_indexes = sorted_indexes[::-1]
			for key in self.values:
				self.values[key] = np.array(self.values[key])[sorted_indexes]
		if not sorted_indexes is None:
			self.lons = np.array(self.lons)[sorted_indexes]
			self.lats = np.array(self.lats)[sorted_indexes]
			self.z = np.array(self.z)[sorted_indexes]
			for key in self.style_params:
				self.style_params[key] = np.array(self.style_params[key])[sorted_indexes]
		return sorted_indexes

	def to_unstructured_grid_data(self, value_key=None, unit=""):
		"""
		Cast point cloud to unstructured grid.
		Note that values must not be empty for this to work

		:return:
			instance of :class:`UnstructuredGrid`
		"""
		assert not self.values in (None, [])
		if not isinstance(self.values, dict):
			values = self.values
		else:
			values = self.values[value_key]
		return UnstructuredGridData(self.lons, self.lats, self.values, unit=unit)

	def is_inside(self, pg_data):
		"""
		Check if points are inside given polygon

		:param pg_data:
			instance of :class:`PolygonData`

		:return:
			bool array
		"""
		from .polygon import PolygonData
		assert isinstance(pg_data, PolygonData)
		return pg_data.contains(self)
