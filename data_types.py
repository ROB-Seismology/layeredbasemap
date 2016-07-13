"""
Data types used in LayeredBasemap
"""

import numpy as np
import shapely
import shapely.geometry
import shapely.wkt
import ogr


# TODO: add srs (default: wgs84)

class BasemapData(object):
	"""
	Base class for Basemap data, containing common methods
	"""


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
					values1[key].extend(values2[key, []])
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
				if isinstance(value, dict) and value.has_key(key):
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


class PointData(SingleData):
	"""
	Basemap data corresponding to a single point

	:param lon:
		float, longitude
	:param lat:
		float, latitude
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
	def __init__(self, lon, lat, value=None, label="", style_params=None):
		self.lon = lon
		self.lat = lat
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
		return shapely.geometry.Point(self.lon, self.lat)

	def to_wkt(self):
		"""
		Convert to well-known text format

		:return:
			str
		"""
		return self.to_shapely().wkt

	def to_multi_point(self):
		"""
		Convert to multi-point data

		:return:
			instance of :class:`MultiPointData`
		"""
		values = self._get_multi_values(self.value)
		style_params = self._get_multi_values(self.style_params)
		return MultiPointData([self.lon], [self.lat], values=values,
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
		return PointData(pt.x, pt.y, value=value, label=label,
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


class MultiPointData(MultiData):
	"""
	Basemap data corresponding to a group of points

	:param lons:
		list or array of floats, longitudes
	:param lats:
		list or array of floats, latitudes
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
	def __init__(self, lons, lats, values=None, labels=None, style_params=None):
		self.lons = lons
		self.lats = lats
		self.values = values or []
		self.labels = labels or []
		self.style_params = style_params or {}

	def __getitem__(self, index):
		lon = self.lons[index]
		lat = self.lats[index]
		value = self._get_value_at_index(index)
		label = self._get_label_at_index(index)
		style_params = self._get_style_params_at_index(index)
		return PointData(lon, lat, value=value, label=label,
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
		lons, lats, labels = [], [], []
		pt0 = point_list[0]
		values = SingleData._get_multi_values(pt0.value)
		style_params = SingleData._get_multi_values(pt0.style_params)
		for pt in point_list:
			lons.append(pt.lon)
			lats.append(pt.lat)
			labels.append(pt.label)
			cls._append_to_multi_values(values, pt.value)
			cls._append_to_multi_values(style_params, pt.style_params)
		return MultiPointData(lons, lats, values=values, labels=labels,
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
		lon_mask = ma.mask_outside(self.lons, lonmin, lonmax)
		lat_mask = ma.mask_outside(self.lats, latmin, latmax)
		lons = ma.array(self.lons, mask=lon_mask.mask + latmask.mask).compressed()
		lats = ma.array(self.lats, mask=lon_mask.mask + latmask.mask).compressed()
		labels = ma.array(self.labels, mask=lon_mask.mask + latmask.mask).compressed()
		if isinstance(self.values, dict):
			values = {}
			for key, val in self.values.items():
				values[key] = ma.array(val, mask=lon_mask.mask + latmask.mask).compressed()
		else:
			values = ma.array(values, mask=lon_mask.mask + latmask.mask).compressed()
		style_params = {}
		for key, val in self.style_params.items():
			style_params[key] = ma.array(val, mask=lon_mask.mask + latmask.mask).compressed()
		return MultiPointData(lons, lats, values=values, labels=labels,
							style_params=style_params)

	def to_shapely(self):
		"""
		Convert to shapely Point object
		"""
		return shapely.geometry.MultiPoint(zip(self.lons, self.lats))

	def to_wkt(self):
		"""
		Convert to well-known text format

		:return:
			str
		"""
		return self.to_shapely().wkt

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
		return MultiPointData([pt.x for pt in mp], [pt.y for pt in mp],
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
		if sorted_indexes != None:
			self.lons = np.array(self.lons)[sorted_indexes]
			self.lats = np.array(self.lats)[sorted_indexes]
			for key in self.style_params:
				self.style_params[key] = np.array(self.style_params[key])[sorted_indexes]
		return sorted_indexes


class LineData(SingleData):
	def __init__(self, lons, lats, value=None, label="", style_params=None):
		self.lons = lons
		self.lats = lats
		self.value = value
		self.label = label
		self.style_params = style_params or {}

	def __len__(self):
		return 1

	def __iter__(self):
		for i in range(1):
			yield self

	def to_shapely(self):
		return shapely.geometry.LineString(zip(self.lons, self.lats))

	def to_wkt(self):
		return self.to_shapely().wkt

	def to_multi_line(self):
		values = self._get_multi_values(self.value)
		return MultiLineData([self.lons], [self.lats], values=values,
							labels=[self.label])

	@classmethod
	def from_shapely(cls, ls, value=None, label="", style_params=None):
		assert ls.geom_type == "LineString"
		lons, lats = zip(*ls.coords)
		return LineData(lons, lats, value=value, label=label,
								style_params=style_params)

	@classmethod
	def from_wkt(cls, wkt, value=None, label="", style_params=None):
		ls = shapely.geometry.LineString(shapely.wkt.loads(wkt))
		return cls.from_shapely(ls, value=value, label=label,
								style_params=style_params)

	@classmethod
	def from_ogr(cls, geom, value=None, label="", style_params=None):
		return cls.from_wkt(geom.ExportToWkt(), value=value, label=label,
								style_params=style_params)

	def get_midpoint(self):
		return self.get_point_at_fraction_of_length(0.5)

	def get_point_at_fraction_of_length(self, fraction):
		assert 0 <= fraction <= 1
		ls = self.to_shapely()
		pt = ls.interpolate(ls.length * fraction)
		return PointData(pt.x, pt.y)

	def get_centroid(self):
		centroid = self.to_shapely().centroid
		return PointData(centroid.x, centroid.y)

	def to_polygon(self):
		# TODO: should we check if first point == last point?
		return PolygonData(self.lons, self.lats, value=self.value,
						label=self.label, style_params=self.style_params)


class MultiLineData(MultiData):
	def __init__(self, lons, lats, values=None, labels=None, style_params=None):
		if lons:
			assert isinstance(lons[0], (list, tuple, np.ndarray)), "lons items must be sequences"
		self.lons = lons
		if lats:
			assert isinstance(lats[0], (list, tuple, np.ndarray)), "lats items must be sequences"
		self.lats = lats
		self.values = values or []
		self.labels = labels or []
		self.style_params = style_params or {}

	def __getitem__(self, index):
		lons = self.lons[index]
		lats = self.lats[index]
		value = self._get_value_at_index(index)
		label = self._get_label_at_index(index)
		style_params = self._get_style_params_at_index(index)
		return LineData(lons, lats, value=value, label=label,
						style_params=style_params)

	def append(self, line):
		if isinstance(line, LineData):
			self.lons.append(line.lons)
			self.lats.append(line.lats)
			self._append_to_multi_values(self.values, line.value or None)
			self.labels.append(line.label or "")
			self._append_to_multi_values(self.style_params, line.style_params)
		elif isinstance(line, MultiLineData):
			self.lons.extend(line.lons)
			self.lats.extend(line.lats)
			self._extend_multi_values(self.values, line.values or [None] * len(line))
			self.labels.extend(line.labels or [""] * len(line))
			self._extend_multi_values(self.style_params, line.style_params)

	def to_shapely(self):
		coords = [zip(self.lons[i], self.lats[i]) for i in range(len(lons))]
		return shapely.geometry.MultiLineString(coords)

	def to_wkt(self):
		return self.to_shapely().wkt

	@classmethod
	def from_shapely(cls, mls, values=None, labels=None, style_params=None):
		assert mls.geom_type == "MultiLineString"
		lons, lats =  [], []
		for ls in mls:
			x, y = zip(*ls.coords)
			lons.append(x)
			lats.append(y)
		return MultiLineData(lons, lats, values=values, labels=labels,
							style_params=style_params)

	@classmethod
	def from_wkt(cls, wkt, values=None, labels=None, style_params=None):
		mls = shapely.geometry.MultiLineString(shapely.wkt.loads(wkt))
		return cls.from_shapely(mls, values=values, labels=labels,
								style_params=style_params)

	@classmethod
	def from_ogr(cls, geom, values=None, labels=None, style_params=None):
		return cls.from_wkt(geom.ExportToWkt(), values=values, labels=labels,
							style_params=style_params)


class PolygonData(SingleData):
	def __init__(self, lons, lats, interior_lons=None, interior_lats=None,
				value=None, label="", style_params=None):
		"""
		lons, lats: lists
		interior_lons, interior_lats: 3-D lists
		"""
		self.lons = lons
		self.lats = lats
		self.interior_lons = interior_lons or []
		self.interior_lats = interior_lats or []
		self.value = value
		self.label = label
		self.style_params = style_params or {}

	def __len__(self):
		return 1

	def __iter__(self):
		for i in range(1):
			return self

	def to_shapely(self):
		return shapely.geometry.Polygon(zip(self.lons, self.lats), [zip(self.interior_lons[i], self.interior_lats[i]) for i in range(len(self.interior_lons))])

	def to_wkt(self):
		return self.to_shapely().wkt

	@classmethod
	def from_shapely(cls, pg, value=None, label="", style_params=None):
		assert pg.geom_type == "Polygon"
		exterior_lons, exterior_lats = zip(*pg.exterior.coords)
		interior_lons, interior_lats = [], []
		for interior_ring in pg.interiors:
			lons, lats = zip(*interior_ring.coords)
			interior_lons.append(lons)
			interior_lats.append(lats)
		return PolygonData(exterior_lons, exterior_lats, interior_lons, interior_lats,
						value=value, label=label, style_params=style_params)

	@classmethod
	def from_wkt(cls, wkt, value=None, label="", style_params=None):
		pg = shapely.wkt.loads(wkt)
		return cls.from_shapely(pg, value=value, label=label,
								style_params=style_params)

	@classmethod
	def from_ogr(cls, geom, value=None, label="", style_params=None):
		## Correct invalid polygons with more than 1 linear ring
		import ogr
		num_rings = geom.GetGeometryCount()
		if num_rings > 1:
			ring_lengths = [geom.GetGeometryRef(i).GetPointCount() for i in range(num_rings)]
			idx = int(np.argmax(ring_lengths))
			poly = ogr.Geometry(ogr.wkbPolygon)
			poly.AddGeometry(geom.GetGeometryRef(idx))
			geom = poly
		return cls.from_wkt(geom.ExportToWkt(), value=value, label=label,
							style_params=style_params)

	def get_centroid(self):
		centroid = self.to_shapely().centroid
		return PointData(centroid.x, centroid.y)

	def to_line(self):
		## Interior rings are ignored
		return LineData(self.lons, self.lats, value=self.value, label=self.label,
						style_params=self.style_params)

	def to_multi_polygon(self):
		values = self._get_multi_values(self.value)
		style_params = self._get_multi_values(self.style_params)
		return MultiPolygonData([self.lons], [self.lats],
					interior_lons=[self.interior_lons],
					interior_lats=[self.interior_lats],
					values=values, labels=[self.label],
					style_params=style_params)

	def clip_to_polygon(self, polygon):
		shape = self.to_shapely()
		polygon = polygon.to_shapely()
		intersection = shape.intersection(polygon)
		if intersection.geom_type == "Polygon":
			return self.from_wkt(intersection.wkt, value=self.value,
							label=self.label, style_params=self.style_params)
		elif intersection.geom_type == "MultiPolygon":
			# TODO: set values, labels !
			return MultiPolygonData.from_wkt(intersection.wkt)
		else:
			print intersection.wkt

	def get_bbox(self):
		lonmin, lonmax = np.min(self.lons), np.max(self.lons)
		latmin, latmax = np.min(self.lats), np.max(self.lats)
		return (lonmin, lonmax, latmin, latmax)

	def is_closed(self):
		if self.lons[0] == self.lons[-1] and self.lats[0] == self.lats[-1]:
			return True
		else:
			return False


class MultiPolygonData(MultiData):
	def __init__(self, lons, lats, interior_lons=None, interior_lats=None,
				values=None, labels=None, style_params=None):
		"""
		lons, lats: 2-D lists
		interior_lons, interior_lats: 3-D lists
		"""
		self.lons = lons
		self.lats = lats
		self.interior_lons = interior_lons or []
		self.interior_lats = interior_lats or []
		self.values = values or []
		self.labels = labels or []
		self.style_params = style_params or {}

	def __getitem__(self, index):
		lons = self.lons[index]
		lats = self.lats[index]
		try:
			interior_lons = self.interior_lons[index]
		except:
			interior_lons = []
		try:
			interior_lats = self.interior_lats[index]
		except:
			interior_lats = []
		value = self._get_value_at_index(index)
		label = self._get_label_at_index(index)
		style_params = self._get_style_params_at_index(index)
		return PolygonData(lons, lats, interior_lons, interior_lats,
						value=value, label=label, style_params=style_params)

	def append(self, polygon):
		assert isinstance(polygon, PolygonData)
		self.lons.append(polygon.lons)
		self.lats.append(polygon.lats)
		self.interior_lons.append(polygon.interior_lons or [])
		self.interior_lats.append(polygon.interior_lats or [])
		self._append_to_multi_values(self.values, polygon.value or None)
		self.labels.append(polygon.label or "")
		self._append_to_multi_values(self.style_params, polygon.style_params)

	def to_polygon(self):
		"""
		Discard all but the first polygon
		"""
		lons = self.lons[0]
		lats = self.lats[0]
		try:
			interior_lons = self.interior_lons[0]
		except IndexError:
			interior_lons = []
		try:
			interior_lats = self.interior_lats[0]
		except IndexError:
			interior_lats = []
		value = self._get_value_at_index(0)
		label = self._get_label_at_index(0)
		style_params = self._get_style_params_at_index(0)

		return PolygonData(lons, lats, interior_lons, interior_lats, value=value,
							label=label, style_params=style_params)

	def to_shapely(self):
		shapely_polygons = [pg.to_shapely() for pg in self]
		return shapely.geometry.MultiPolygon(shapely_polygons)

	def to_wkt(self):
		return self.to_shapely().wkt

	@classmethod
	def from_shapely(cls, mpg, values=None, labels=None, style_params=None):
		assert mpg.geom_type == "MultiPolygon"
		exterior_lons, exterior_lats = [], []
		interior_lons, interior_lats = [], []
		for pg in mpg:
			lons, lats = zip(*pg.exterior.coords)
			exterior_lons.append(lons)
			exterior_lats.append(lats)
			pg_interior_lons, pg_interior_lats = [], []
			for interior_ring in pg.interiors:
				lons, lats = zip(*interior_ring.coords)
				pg_interior_lons.append(lons)
				pg_interior_lats.append(lats)
			interior_lons.append(pg_interior_lons)
			interior_lats.append(pg_interior_lats)
		return MultiPolygonData(exterior_lons, exterior_lats, interior_lons,
							interior_lats, values=values, labels=labels,
							style_params=style_params)

	@classmethod
	def from_wkt(cls, wkt, values=None, labels=None, style_params=None):
		mpg = shapely.geometry.MultiPolygon(shapely.wkt.loads(wkt))
		return cls.from_shapely(mpg, values=values, labels=labels,
								style_params=style_params)

	@classmethod
	def from_ogr(cls, geom, values=None, labels=None, style_params=None):
		return cls.from_wkt(geom.ExportToWkt(), values=values, labels=labels,
							style_params=style_params)

	def clip_to_polygon(self, polygon):
		# TODO: set style_params
		shape = self.to_shapely()
		polygon = polygon.to_shapely()
		intersection = shape.intersection(polygon)
		if intersection.geom_type == "Polygon":
			return PolygonData.from_wkt(intersection.wkt).to_multi_polygon()
		elif intersection.geom_type == "MultiPolygon":
			return self.from_wkt(intersection.wkt)
		else:
			print intersection.wkt


class FocmecData(MultiPointData):
	"""
	"""
	def __init__(self, lons, lats, sdr, values=None, labels=None, style_params=None):
		super(FocmecData, self).__init__(lons, lats, values, labels, style_params)
		self.sdr = sdr

	def sort(self, value_key=None, ascending=True):
		"""
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
		sorted_indexes = MultiPointData.sort(self, value_key=value_key, ascending=ascending)
		self.sdr = np.array(self.sdr)[sorted_indexes]
		return sorted_indexes


class CircleData(MultiPointData):
	"""
	radii: in km
	"""
	def __init__(self, lons, lats, radii, values=[], labels=[], azimuthal_resolution=1):
		super(CircleData, self).__init__(lons, lats, values, labels)
		self.radii = radii
		self.azimuthal_resolution = 1


class GreatCircleData(MultiPointData):
	"""
	Class representing data to plot great circles.
	Note that Basemap cannot handle situations in which the great circle
	intersects the edge of the map projection domain, and then re-enters
	the domain.

	:param lons:
		array containing longitudes of start and end points of great circles,
		as follows: [start_lon1, end_lon1, start_lon2, end_lon2, ...]
	:param lats:
		array containing latitudes of start and end points of great circles,
		as follows: [start_lat1, end_lat1, start_lat2, end_lat2, ...]
	:param resolution:
		float, resolution in km for plotting points in between start and end
		(default: 10)
	"""
	def __init__(self, lons, lats, resolution=10):
		assert len(lons) % 2 == 0 and len(lons) == len(lats)
		super(GreatCircleData, self).__init__(lons, lats)
		self.resolution = resolution

	def __len__(self):
		return len(self.lons) / 2

	def __getitem__(self, index):
		"""
		:return:
			(start_lon, start_lat, end_lon, end_lat) tuple of each great circle
		"""
		i = index
		return (self.lons[i*2], self.lats[i*2], self.lons[i*2+1], self.lats[i*2+1])


class TextData(SingleData):
	"""
	Class representing single text label

	:param lon:
		float, longitude
	:param lat:
		float, latitude
	:param label:
		strings, label to be plotted
	:param coord_frame:
		str, matplotlib coordinate frame for lons, lats:
		"geographic" or one of the matplotlib coordinate frames:
		"figure points", "figure pixels", "figure fraction", "axes points",
		"axes pixels", "axes fraction", "data", "offset points" or "polar"
		(default: "geographic")
	:param style_params:
		dict, mapping style parameters to a value. These values will
		override the overall layer style
		(default: None --> {})
	"""
	def __init__(self, lon, lat, label, coord_frame="geographic", style_params=None):
		self.lon = lon
		self.lat = lat
		self.label = label
		self.coord_frame = coord_frame
		self.style_params = style_params or {}

	def to_multi_text(self):
		"""
		Convert to multi-text data

		:return:
			instance of :class:`MultiTextData`
		"""
		style_params = self._get_multi_values(self.style_params)
		return MultiTextData([self.lon], [self.lat], labels=[self.label],
							style_params=style_params)


class MultiTextData(MultiData):
	"""
	Class representing multiple text data.

	:param lons:
		list or array of floats, longitudes
	:param lats:
		list or array of floats, latitudes
	:param labels:
		list of strings, labels to be plotted
	:param coord_frame:
		str, matplotlib coordinate frame for lons, lats:
		"geographic" or one of the matplotlib coordinate frames:
		"figure points", "figure pixels", "figure fraction", "axes points",
		"axes pixels", "axes fraction", "data", "offset points" or "polar"
		(default: "geographic")
	:param style_params:
		dict, mapping style parameters to a list of values. These values
		will override the overall layer style.
		(default: None --> {})
	"""
	def __init__(self, lons, lats, labels, coord_frame="geographic", style_params=None):
		self.lons = lons
		self.lats = lats
		self.labels = labels
		self.coord_frame = coord_frame
		self.style_params = style_params or {}

	def __getitem__(self, index):
		lon = self.lons[index]
		lat = self.lats[index]
		label = self._get_label_at_index(index)
		style_params = self._get_style_params_at_index(index)
		return TextData(lon, lat, label=label, coord_frame=self.coord_frame,
						style_params=style_params)

	def append(self, pt_data):
		"""
		Append from single-value text data.
		Note: we don't check if :prop:`coord_frame` is consistent!

		:param pt_data:
			instance of :class:`PointData`
		"""
		#if getattr(pt_data, "coord_frame") != self.coord_frame:
		#	print("Warning: coord_frame not the same!")
		self.lons.append(pt_data.lon)
		self.lats.append(pt_data.lat)
		self.labels.append(pt_data.label or "")
		self._append_to_multi_values(self.style_params, pt_data.style_params)


class MaskData(BasemapData):
	def __init__(self, polygon, outside=True):
		self.polygon = polygon
		self.outside = outside


class CompositeData(BasemapData):
	def __init__(self, points=None, lines=[], polygons=[], texts=[]):
		self.points = points
		self.lines = lines
		self.polygons = polygons
		self.texts = texts


class GridData(BasemapData):
	def __init__(self, lons, lats, values):
		self.lons = np.asarray(lons)
		self.lats = np.asarray(lats)
		self.values = np.asarray(values)


class UnstructuredGridData(GridData):
	"""
	Unstructured 2-dimensional data

	:param lons:
		1-D array of longitudes
	:param lats:
		1-D array of latitudes
	:param values:
		1-D array of values
	"""
	def __int__(self, lons, lats, values):
		if lons.ndim != 1 or lats.ndim != 1 or values.ndim != 1:
			raise ValueError("lons, lats, and values should be 1-dimensional")
		super(UnstructuredGridData, self).__init__(lons, lats, values)

	def lonmin(self):
		"""
		Return minimum longitude
		"""
		return self.lons.min()

	def lonmax(self):
		"""
		Return maximum longitude
		"""
		return self.lons.max()

	def latmin(self):
		"""
		Return minimum latitude
		"""
		return self.lats.min()

	def latmax(self):
		"""
		Return maximum latitude
		"""
		return self.lats.max()

	def to_mesh_grid_data(self, num_cells, extent=(None, None, None, None), interpolation_method='cubic'):
		"""
		Convert to meshed grid data

		:param num_cells:
			Integer or tuple, number of grid cells in lon and lat direction
		:param extent:
			(lonmin, lonmax, latmin, latmax) tuple of floats
			(default: (None, None, None, None)
		:param interpolation_method:
			Str, interpolation method supported by griddata (either
			"linear", "nearest" or "cubic") (default: "cubic")

		:return:
			instance of :class:`MeshGridData`
		"""
		from scipy.interpolate import griddata
		if isinstance(num_cells, int):
			num_lons = num_lats = num_cels
		lonmin, lonmax, latmin, latmax = extent
		if lonmin is None:
			lonmin = self.lonmin()
		if lonmax is None:
			lonmax = self.lonmax()
		if latmin is None:
			latmin = self.latmin()
		if latmax is None:
			latmax = self.latmax()
		lons = np.linspace(lonmin, lonmax, num_lons)
		lats = np.linspace(latmin, latmax, num_lats)
		mesh_lons, mesh_lats = np.meshgrid(lons, lats)
		mesh_values = griddata((self.lons, self.lats), self.values, (mesh_lons, mesh_lats), method=interpolation_method)
		return MeshGridData(mesh_lons, mesh_lats, mesh_values)


class MeshGridData(GridData):
	"""
	Meshed grid data, representing a grid with regular longitudinal and
	latitudinal spacing

	:param lons:
		2-D array
	:param lats:
		2-D array
	:param values:
		2-D array
	"""
	def __init__(self, lons, lats, values):
		if lons.ndim != 2 or lats.ndim != 2 or values.ndim != 2:
			raise ValueError("lons, lats, and values should be 2-dimensional")
		## Not sure the following is really necessary
		dlon = np.diff(lons)
		dlat = np.diff(lats)
		if not np.allclose(dlon, dlon[0]) or not np.allclose(dlat, dlat[0]):
			raise ValueError("Grid spacing must be uniform")
		super(MeshGridData, self).__init__(lons, lats, values)

		# TODO: need to make functions for these using source srs
		# (in which grid is rectangular)
		self.center_lons = self.edge_lons = lons
		self.center_lats = self.edge_lats = lats

	@property
	def dlon(self):
		return self.center_lons[0,1] - self.center_lons[0,0]

	@property
	def dlat(self):
		return self.center_lats[1,0] - self.center_lats[0,0]

	@property
	def num_cols(self):
		return self.center_lons.shape[1]

	@property
	def num_rows(self):
		return self.center_lons.shape[0]

	def get_mesh_coordinates(self, cell_registration="corner"):
		"""
		To make MeshGridData compatible with GdalRasterData
		Note: cell_registration currently ignored
		"""
		return (self.lons, self.lats)

	def mask_oceans(self, resolution, mask_lakes=False, grid_spacing=1.25):
		from mpl_toolkits.basemap import maskoceans
		masked_values = maskoceans(self.lons, self.lats, self.values, inlands=mask_lakes, resolution=resolution, grid=grid_spacing)
		return MeshGridData(self.lons, self.lats, masked_values)

	def reproject(self, source_srs, target_srs):
		pass

	def calc_hillshade(self, azimuth, elevation_angle, scale=1.):
		"""
		Compute hillshading
		Source: http://rnovitsky.blogspot.com.es/2010/04/using-hillshade-image-as-intensity.html

		:param azimuth:
			float, azimuth of light source in degrees
		:param elevation_angle:
			float, elevation angle of light source in degrees
		:param scale:
			float, multiplication factor to apply (default: 1.)
		"""
		az = np.radians(azimuth)
		elev = np.radians(elevation_angle)
		data = self.values

		## Gradient in x and y directions
		dx, dy = np.gradient(data * float(scale))
		slope = 0.5 * np.pi - np.arctan(np.hypot(dx, dy))
		aspect = np.arctan2(dx, dy)
		shade = np.sin(elev) * np.sin(slope) + np.cos(elev) * np.cos(slope) * np.cos(-az - aspect - 0.5*np.pi)
		## Normalize
		shade = (shade - shade.min())/(shade.max() - shade.min())

		return shade


class GdalRasterData(MeshGridData):
	"""
	GDAL raster data (including GeoTiff)
	Unrotated!

	:param filespec:
		str, full path to GDAL raster dataset
	:param band_nr:
		int,  raster band number (one-based). If 0 or None, data
		will be read as truecolor (RGB) image
		(default: 1)
	:param down_sampling:
		float, factor for downsampling, i.e. to divide number of columns and
		rows with
		(default: 1., no downsampling)
	"""
	def __init__(self, filespec, band_nr=1, down_sampling=1., nodata_value=None):
		self.filespec = filespec
		self.band_nr = band_nr
		self.read_grid_info()
		self._edge_lons = None
		self._edge_lats = None
		self._center_lons = None
		self._center_lats = None
		self.set_down_sampling(down_sampling)
		self.nodata_value = nodata_value

	# TODO: raster subdatasets
	#subdatasets = dataset.GetSubDatasets()
	#mysubdataset_name = subdatasets[1][0]
	#mydata = gdal.Open(mysubdataset_name, gdal.GA_ReadOnly).ReadAsRaster()

	def get_subdataset_names(self):
		import gdal

		ds = gdal.Open(self.filespec, gdal.GA_ReadOnly)
		sds_names = [sds[0] for sds in ds.GetSubDatasets()]
		ds = None
		return sds_names

	def get_subdatasets(self):
		return [self.get_subdataset(sds_name) for sds_name in self.get_subdataset_names()]

	def get_subdataset(self, subdataset_name):
		return GdalRasterData(subdataset_name)

	def set_down_sampling(self, down_sampling):
		self.down_sampling = float(down_sampling)
		if down_sampling != 1.:
			self.x0 = self.x0 / down_sampling * down_sampling
			self.x1 = self.x1  / down_sampling * down_sampling
			self.y0 = self.y0 / down_sampling * down_sampling
			self.y1 = self.y1 / down_sampling * down_sampling
			self.dx *= down_sampling
			self.dy *= down_sampling
			self.ncols = int(abs((self.x0 - self.x1) / self.dx)) + 1
			self.nrows = int(abs((self.y0 - self.y1) / self.dy)) + 1

			# TODO: make sure x0, x1, y0, y1 are multiples of dx,
			# and set xoff and yoff accordingly in read_band

	## Following methods are based on:
	## http://stackoverflow.com/questions/20488765/plot-gdal-raster-using-matplotlib-basemap

	def read_grid_info(self):
		"""
		Read raster parameters.

		The following properties are set:
		- :prop:`srs`: instance of class osr.SpatialReference
		- :prop:`num_bands`: int, number of raster bands
		- :prop:`ncols`, :prop:`nrows`: int, number of raster columns
			and rows
		- :prop:`dx`, :prop:`dy`: int, cell size in X and Y direction
			in the native spatial reference system
		- :prop:`x0`, :prop:`x1`: float, extent in X direction in
			the native spatial reference system (center of grid cells)
		- :prop:`y0`, :prop:`y1`: float, extent in Y direction in
			the native spatial reference system (center of grid cells)
		"""
		import gdal, osr

		ds = gdal.Open(self.filespec, gdal.GA_ReadOnly)
		self.srs = osr.SpatialReference()
		projection = ds.GetProjection()
		if projection:
			self.srs.ImportFromWkt(projection)
		else:
			self.srs.SetWellKnownGeogCS("WGS84")
			print("Warning: no spatial reference system defined, assuming WGS84!")
		self.num_bands = ds.RasterCount

		gt = ds.GetGeoTransform()
		# TODO: support rotated grids
		self.ncols, self.nrows = ds.RasterXSize, ds.RasterYSize
		self.dx, self.dy = gt[1], gt[5]
		## (x0, y0) and (x1, y1) now correspond to cell centers
		self.x0 = gt[0] + self.dx * 0.5
		self.x1 = gt[0] + (self.dx * self.ncols) - self.dx * 0.5
		#if self.dx < 0:
			#xmin, xmax = xmax, xmin
			#self.dx = -self.dx
		self.y0 = gt[3] + self.dy * 0.5
		self.y1 = gt[3] + (self.dy * self.nrows) - self.dy * 0.5
		#if self.dy < 0:
		#ymin, ymax = ymax, ymin
			#self.dy = -self.dy

		ds = None

	@property
	def xmin(self):
		return min(self.x0, self.x1)

	@property
	def xmax(self):
		return max(self.x0, self.x1)

	@property
	def ymin(self):
		return min(self.y0, self.y1)

	@property
	def ymax(self):
		return max(self.y0, self.y1)

	@property
	def shape(self):
		return (self.nrows, self.ncols)

	def get_mesh_coordinates(self, cell_registration="corner"):
		"""
		Get mesh coordinates as WGS84 longitudes and latitudes

		:param cell_registration:
			str, one of "center" or "corner" (= "edge"): whether returned coordinates
			should correspond to cell centers or cell corners
			(default: "corner")

		:return:
			(lons, lats) tuple, 2-D arrays containing raster
			longitudes and raster latitudes
		"""
		from mapping.geo.coordtrans import (transform_mesh_coordinates, wgs84)

		## Create meshed coordinates
		if cell_registration == "center":
			xx, yy = np.meshgrid(np.linspace(self.x0, self.x1, self.ncols),
							np.linspace(self.y0, self.y1, self.nrows))
		elif cell_registration in ("corner", "edge"):
			xx, yy = np.meshgrid(np.linspace(self.x0 - self.dx/2., self.x1 + self.dx/2., self.ncols+1),
							np.linspace(self.y0 - self.dy/2., self.y1 + self.dy/2., self.nrows+1))

		## Convert from source projection to WGS84
		target_srs = wgs84
		lons, lats = transform_mesh_coordinates(self.srs, target_srs, xx, yy)
		if cell_registration == "corner":
			self._edge_lons, self._edge_lats = lons, lats
			self._center_lons, self._center_lats = None, None
		elif cell_registration == "center":
			self._edge_lons, self._edge_lats = None, None
			self._center_lons, self._center_lats = lons, lats
		return lons, lats

	@property
	def edge_lons(self):
		if self._edge_lons is None:
			return self.get_mesh_coordinates("corner")[0]
		else:
			return self._edge_lons

	@property
	def edge_lats(self):
		if self._edge_lats is None:
			return self.get_mesh_coordinates("corner")[1]
		else:
			return self._edge_lats

	@property
	def center_lons(self):
		if self._center_lons is None:
			return self.get_mesh_coordinates("center")[0]
		else:
			return self._center_lons

	@property
	def center_lats(self):
		if self._center_lats is None:
			return self.get_mesh_coordinates("center")[1]
		else:
			return self._center_lats

	@property
	def values(self):
		if self.band_nr:
			return self.read_band(self.band_nr)
		else:
			return self.read_image_array()

	def read_band(self, band_nr):
		"""
		Read a particular raster band

		:param band_nr:
			int, raster band number (one-based)

		:return:
			2-D array containing raster data values
		"""
		# TODO: ReadAsArray method also takes xoff, yoff, xsize, ysize params
		import gdal
		ds = gdal.Open(self.filespec, gdal.GA_ReadOnly)
		band = ds.GetRasterBand(band_nr)
		if self.nodata_value is None:
			nodata = band.GetNoDataValue()
		else:
			nodata = self.nodata_value
		values = band.ReadAsArray(buf_xsize=self.ncols, buf_ysize=self.nrows)
		## Mask nodata values
		#values[values == nodata] = np.nan
		if nodata != None:
			values = np.ma.array(values, mask=np.isclose(values, nodata))
		ds = None

		return values

	def read_image_array(self):
		"""
		Read raster data as truecolor (RGB[A]) image array

		:return:
			3-D (RGB[A], Y, X) float array
		"""
		import gdal
		ds = gdal.Open(self.filespec, gdal.GA_ReadOnly)
		#import matplotlib.image as mpimg
		#values = mpimg.imread(self.filespec)
		values = np.zeros((4, self.nrows, self.ncols), dtype=np.uint8)
		ds.ReadAsArray(buf_obj=values)
		ds = None

		return values

	def read_image(self):
		"""
		Read raster data as truecolor (RGB[A]) image

		:return:
			instance of :class:`PIL.Image`
		"""
		from PIL import Image
		img_ar = self.read_image_array()
		return Image.fromarray(img_ar, 'RGBA')

	def interpolate(self, xout, yout, checkbounds=False, masked=True, order=1):
		## Check scipy.interpolate.Rbf for additional interpolation methods
		from mpl_toolkits.basemap import interp

		## xin, yin must be linearly increasing
		values = self.values
		if self.x0 < self.x1:
			xin = np.linspace(self.x0, self.x1, self.ncols)
		else:
			xin = np.linspace(self.x1, self.x0, self.ncols)
			values = values[:,::-1]
		if self.y0 < self.y1:
			yin = np.linspace(self.y0, self.y1, self.nrows)
		else:
			yin = np.linspace(self.y1, self.y0, self.nrows)
			values = values[::-1,:]

		if self.band_nr:
			out_data = interp(values, xin, yin, xout, yout, checkbounds=checkbounds,
								masked=masked, order=order)
		else:
			in_values = self.values
			ny, nx = xout.shape
			num_channels = in_values.shape[0]
			out_data = np.empty((num_channels, ny, nx), np.uint8)
			#if masked:
			#	mask = np.ma.zeros((num_channels, ny, nx), np.int8)
			for k in range(num_channels):
				ch_out = interp(in_values[k,::-1,:], xin, yin, xout, yout, checkbounds=checkbounds,
								masked=masked, order=order)
				out_data[k] = ch_out
			if masked and num_channels == 4:
				## imshow draws masked part of image black
				## so we make masked part transparent
				#mask[:,] = ch_out.mask
				#out_data = np.ma.masked_array(out_data, mask=mask)
				out_data[3, ch_out.mask==True] = 0

		return out_data

	def interpolate_grid(self, xout, yout, checkbounds=False, masked=True, order=1):
		values = self.interpolate(xout, yout, checkbounds=checkbounds, masked=masked, order=order)
		return MeshGridData(xout, yout, values)

	def cross_section(self, (x0, y0), (x1, y1), num_points=100):
		X = np.linspace(x0, x1, num_points)
		Y = np.linspace(y0, y1, num_points)
		## TODO: distances in km (take into account lon-lat rasters)
		return self.interpolate(X, Y)

	def warp_to_map(self, map, checkbounds=False, masked=True, order=1):
		from mapping.geo.coordtrans import transform_mesh_coordinates

		nx = int(round(map.figsize[0] * float(map.dpi)))
		ny = int(round(map.figsize[1] * float(map.dpi)))
		lonsout, latsout, x_map, y_map = map.map.makegrid(nx, ny, returnxy=True)
		x_grid, y_grid = transform_mesh_coordinates(map.get_srs(), self.srs, x_map, y_map)
		out_values = self.interpolate(x_grid, y_grid, checkbounds=checkbounds,
										masked=masked, order=order)

		return out_values

	def export(self, format, out_filespec):
		"""
		Export raster to another format

		:param format:
			str, GDAL format specification
		:param out_filespec:
			str, full path to output file
		"""
		from osgeo import gdal

		## Open output format driver, see gdal_translate --formats for list
		driver = gdal.GetDriverByName(format)
		if driver and driver.GetMetadata().get(gdal.DCAP_CREATE) == 'YES':
			## Open existing dataset
			src_ds = gdal.Open(self.filespec, gdal.GA_ReadOnly)

			## Output to new format
			dst_ds = driver.CreateCopy(out_filespec, src_ds, 0)

			## Properly close the datasets to flush to disk
			dst_ds = None
			src_ds = None

		else:
			print("Driver %s does not support CreateCopy() method" % format)


class MeshGridVectorData(BasemapData):
	"""
	Evenly spaced vector data

	:param grdx:
		instance of :class:`MeshGridData`, vector X-component
	:param grdy:
		instance of :class:`MeshGridData`, vector Y-component
	"""
	def __init__(self, grdx, grdy):
		self.grdx = grdx
		self.grdy = grdy

	@classmethod
	def from_vx_filespec(self, vx_filespec, band_nr=1, down_sampling=1.):
		"""
		Set from GDAL filespec corresponding to X component,
		assuming it follows '.vx'/'.vy' naming convention

		:param vx_filespec:
			str, full path to GDAL file containing X-component
		:param band_nr:
		:param down_sampling:
			See :class:`GdalRasterData`

		:return:
			instance of :class:`MeshGridVectorData`
		"""
		vy_filespec = vx_filespec.replace('.vx', '.vy')
		grdx = GdalRasterData(vx_filespec, band_nr=band_nr, down_sampling=down_sampling)
		grdy = GdalRasterData(vy_filespec, band_nr=band_nr, down_sampling=down_sampling)
		return MeshGridVectorData(grdx, grdy)


class WCSData(GdalRasterData):
	"""
	:param url:
		str, base URL of WCS server
	:param layer_name:
		str, name of requested dataset on WCS server
	:param resolution:
		float or tuple of floats: resolution in units of dataset's CRS
	:param band_nr:
		int,  raster band number (one-based). If 0 or None, data
		will be read as truecolor (RGB) image
		(default: 1)
	:param bbox:
		list or tuple of floats: (llx, lly, urx, ury) in native coordinates
		(default: [], will use bounding box of dataset)
	:param region:
		list or tuple of floats: (lonmin, lonmax, latmin, latmax)
		that will be used to determine bbox
		(default: [])
	:param wcs_version:
		str, WCS version
		(default: '1.0.0')
	:param verbose:
		bool, whether or not to print information
		(default: True)
	"""
	def __init__(self, url, layer_name, resolution, band_nr=1, bbox=[], region=[],
				wcs_version='1.0.0', verbose=True):
		self.url = url
		self.layer_name = layer_name
		if isinstance(resolution, (int, float)):
			self.resolution = (resolution, resolution)
		else:
			self.resolution = resolution
		self.resolution = np.asarray(self.resolution)

		## Query server for some information
		self.wcs_version = wcs_version
		self.wcs = self.init_wcs(verbose=verbose)

		if region:
			self.bbox = self.get_bbox_from_region(self.layer_name, region)
		else:
			self.bbox = bbox

		## Read coverage
		import tempfile, urllib

		response = self.get_coverage(self.layer_name)
		if verbose:
			print urllib.unquote(response.geturl())
		#fd = tempfile.NamedTemporaryFile(suffix=".tif")
		#fd.write(response.read())
		#fd.close()
		#super(WCSData, self).__init__(fd.name, band_nr=band_nr)
		try:
			super(WCSData, self).__init__(response.geturl(), band_nr=band_nr)
		except:
			print response.read()
			raise

	def init_wcs(self, verbose=True):
		"""
		Initiate WCS connection

		:param verbose:
			bool, whether or not to print information
			(default: True)

		:return:
			instance of :class:`owslib.wcs.WebCoverageService`
		"""
		from owslib.wcs import WebCoverageService
		wcs = WebCoverageService(self.url, version=self.wcs_version)
		if verbose:
			print sorted(wcs.contents.keys())
		return wcs

	def get_coverage_info(self, layer_name):
		"""
		Get coordinate system and bounding box for a particular coverage

		:param layer_name:
			str, name of requested dataset on WCS server

		:return:
			(crs, bbox) tuple
		"""
		coverage = self.wcs[layer_name]
		crs = coverage.supportedCRS[0]
		bbox = coverage.boundingboxes[0]['bbox']
		return (crs, bbox)

	def get_bbox_from_region(self, layer_name, region):
		"""
		Get bounding box in native coordinates for a particular coverage
		from region in geographic coordinates

		:param layer_name:
			str, name of requested dataset on WCS server
		:param region:
			list or tuple of floats: (lonmin, lonmax, latmin, latmax)

		:return:
			list or tuple of floats: (llx, lly, urx, ury)
			bbox in native coordinates
		"""
		from mapping.geo.coordtrans import get_epsg_srs, wgs84, transform_coordinates

		crs, _bbox = self.get_coverage_info(layer_name)
		if crs.authority == 'EPSG':
			srs = get_epsg_srs(crs.getcode())
		else:
			raise Exception("CRS %s not supported!" % crs.getcode())

		lonmin, lonmax, latmin, latmax = region
		lon_margin = (lonmax - lonmin) / 20.
		lat_margin = (latmax - latmin) / 20.
		coords_in = [(lonmin-lon_margin, latmin-lat_margin),
					(lonmax+lon_margin, latmax+lat_margin)]
		coords = transform_coordinates(wgs84, srs, coords_in)
		bbox = (list(np.floor(coords[0] / self.resolution) * self.resolution) +
				list(np.ceil(coords[1] / self.resolution) * self.resolution))
		return bbox

	def get_coverage(self, layer_name):
		"""
		Fetch coverage from server

		:param layer_name:
			str, name of requested dataset on WCS server

		:return:
			instance of :class:`owslib.util.ResponseWrapper`
		"""
		width, height = None, None
		crs, _bbox = self.get_coverage_info(layer_name)
		if not self.bbox:
			bbox = _bbox
		else:
			bbox = self.bbox
		format = "GeoTIFF"
		return self.wcs.getCoverage(identifier=layer_name, width=width, height=height,
					resx=self.resx, resy=self.resy, bbox=bbox, format=format, crs=crs.getcode())

	@property
	def resx(self):
		return self.resolution[0]

	@property
	def resy(self):
		return self.resolution[1]


class ImageData(BasemapData):
	"""
	Class representing image

	:param filespec:
		str, full path to image file
	:param lon:
		float, longitude
	:param lat:
		float, latitude
	"""
	# TODO: should we also support display coordinates instead of lon, lat??
	def __init__(self, filespec, lon, lat):
		self.filespec = filespec
		self.lon = lon
		self.lat = lat


class GisData(BasemapData):
	"""
	:param filespec:
		str, full path to GIS file
	:param label_colname:
		str, name of column to use for labels
		(default: None)
	:param selection_dict:
		dict, mapping column names to values; only matching records will be selected
	:param joined_attributes:
		dict, mapping additional attribute names (not present in the GIS table)
		to dictionaries containing two entries:
		- 'key' string, GIS attribute that will be used to join
		- 'values': dict, mapping values of 'key' to attribute values
	:param convert_closed_lines:
		bool, whether or not to silently convert closed lines to polygons
		(default: True)
	"""
	def __init__(self, filespec, label_colname=None, selection_dict=None,
				joined_attributes={}, style_params={}, convert_closed_lines=True):
		self.filespec = filespec
		self.label_colname = label_colname
		self.selection_dict = selection_dict or {}
		self.joined_attributes = joined_attributes or {}
		self.style_params = style_params or {}
		self.convert_closed_lines = convert_closed_lines

	def get_attributes(self):
		"""
		Read GIS attributes (column names).

		:return:
			list of strings
		"""
		from mapping.geo.readGIS import read_GIS_file_attributes

		return read_GIS_file_attributes(self.filespec)

	def get_data(self, point_value_colnames=None, line_value_colnames=None,
					polygon_value_colnames=None):
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
		from mapping.geo.readGIS import read_GIS_file

		if None in (point_value_colnames, line_value_colnames, polygon_value_colnames):
			colnames = self.get_attributes()
		if point_value_colnames is None:
			point_value_colnames = set(colnames)
		if line_value_colnames is None:
			line_value_colnames = set(colnames)
		if polygon_value_colnames is None:
			polygon_value_colnames = set(colnames)

		## Make sure attributes needed to link with joined_attributes are stored too
		joined_attribute_colnames = set()
		for attrib_name in self.joined_attributes.keys():
			joined_attribute_colnames.add(self.joined_attributes[attrib_name]['key'])
		point_value_colnames = point_value_colnames.union(joined_attribute_colnames)
		line_value_colnames = line_value_colnames.union(joined_attribute_colnames)
		polygon_value_colnames = polygon_value_colnames.union(joined_attribute_colnames)

		## Note: it is absolutely necessary to initialize all empty lists
		## explicitly, otherwise unexpected things may happen in subsequent
		## calls of this method!
		point_data = MultiPointData([], [], values=[], labels=[])
		point_data.values = {}
		for colname in point_value_colnames:
			point_data.values[colname] = []
		line_data = MultiLineData([], [], values=[], labels=[])
		line_data.values = {}
		for colname in line_value_colnames:
			line_data.values[colname] = []
		polygon_data = MultiPolygonData([], [], interior_lons=[], interior_lats=[],
				values=[], labels=[])
		polygon_data.values = {}
		for colname in polygon_value_colnames:
			polygon_data.values[colname] = []

		for rec in read_GIS_file(self.filespec):
			selected = np.zeros(len(self.selection_dict.keys()))
			for i, (selection_colname, selection_value) in enumerate(self.selection_dict.items()):
				if rec[selection_colname] == selection_value or rec[selection_colname] in list(selection_value):
					selected[i] = 1
				else:
					selected[i] = 0
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
					multi_polygon = MultiPolygonData.from_ogr(geom)
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
			try:
				point_data.values[attrib_name] = [value_dict[key_val] for key_val in point_data.values[key]]
				line_data.values[attrib_name] = [value_dict[key_val] for key_val in line_data.values[key]]
				polygon_data.values[attrib_name] = [value_dict[key_val] for key_val in polygon_data.values[key]]
			except:
				print("Warning: %s not found in data value keys!" % key_val)
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


class WMSData(object):
	"""
	Class representing WMS image

	:param url:
		str, WMS server URL
	"""
	def __init__(self, url, layers, verbose=False):
		self.url = url
		self.layers = layers
		self.verbose = verbose
