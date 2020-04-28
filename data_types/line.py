"""
Line data
"""

from __future__ import absolute_import, division, print_function, unicode_literals


import numpy as np
import shapely
import shapely.geometry
import shapely.wkt
import ogr

from .base import SingleData, MultiData
from .point import PointData


__all__ = ['LineData', 'MultiLineData']


class LineData(SingleData):
	def __init__(self, lons, lats, z=None, value=None, label="", style_params=None):
		self.lons = lons
		self.lats = lats
		self.z = z or [None] * len(lons)
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
		"""
		if self.z is None or set(self.z) == set([None]):
			return shapely.geometry.LineString(list(zip(self.lons, self.lats)))
		else:
			return shapely.geometry.LineString(list(zip(self.lons, self.lats, self.z)))

	def get_ogr_geomtype(self):
		return ogr.wkbLineString

	def to_multi_line(self):
		values = self._get_multi_values(self.value)
		return MultiLineData([self.lons], [self.lats], [self.z], values=values,
							labels=[self.label])

	@classmethod
	def from_shapely(cls, ls, value=None, label="", style_params=None):
		assert ls.geom_type == "LineString"
		if ls.has_z:
			lons, lats, z = zip(*ls.coords)
		else:
			lons, lats = zip(*ls.coords)
			z = None
		return LineData(lons, lats, z=z, value=value, label=label,
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

	def get_incremental_distance(self):
		from mapping.geotools.geodetic import spherical_distance
		lons, lats = np.array(self.lons), np.array(self.lats)
		lons1, lats1 = lons[:-1], lats[:-1]
		lons2, lats2 = lons[1:], lats[1:]
		cum_len = spherical_distance(lons1, lats1, lons2, lats2)
		return np.hstack(([0], cum_len))

	def get_cumulative_distance(self):
		return np.cumsum(self.get_incremental_distance())

	def get_length_degrees(self):
		"""
		Returns length in degrees
		"""
		return self.to_shapely().length

	def get_length(self):
		return self.get_cumulative_distance()[-1]

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

	def get_nearest_index_at_fraction_of_length(self, fraction):
		cum_len = self.get_cumulative_distance()
		cum_len /= cum_len[-1]
		return np.argmin(np.abs(cum_len - fraction))

	def get_point_at_index(self, idx):
		lon = self.lons[idx]
		lat = self.lats[idx]
		z = self.z[idx]
		value = self.value
		style_params = self.style_params
		label = self.label
		return PointData(lon, lat, z=z, value=value, label=label, style_params=style_params)

	def get_intersection(self, line2):
		pt = self.to_shapely().intersection(line2.to_shapely())
		if pt:
			return PointData.from_shapely(pt)

	def get_nearest_index_to_point(self, pt):
		import mapping.geotools.geodetic as geodetic
		distances = geodetic.spherical_distance(pt.lon, pt.lat, self.lons, self.lats)
		return np.argmin(distances)

	def to_polygon(self):
		# TODO: should we check if first point == last point?
		from .polygon import PolygonData

		return PolygonData(self.lons, self.lats, z=self.z, value=self.value,
						label=self.label, style_params=self.style_params)

	def get_mean_strike(self):
		import mapping.geotools.geodetic as geodetic
		from mapping.geotools.angle import Azimuth
		lons, lats = np.array(self.lons), np.array(self.lats)
		lons1, lats1 = lons[:-1], lats[:-1]
		lons2, lats2 = lons[1:], lats[1:]
		distances = geodetic.spherical_distance(lons1, lats1, lons2, lats2)
		azimuths = geodetic.spherical_azimuth(lons1, lats1, lons2, lats2)
		azimuths = Azimuth(azimuths, 'deg')
		weights = distances / np.add.reduce(distances)
		mean_strike = azimuths.mean(weights).deg()
		return mean_strike


class MultiLineData(MultiData):
	def __init__(self, lons, lats, z=None, values=None, labels=None, style_params=None):
		if lons:
			assert isinstance(lons[0], (list, tuple, np.ndarray)), "lons items must be sequences"
		self.lons = lons
		if lats:
			assert isinstance(lats[0], (list, tuple, np.ndarray)), "lats items must be sequences"
		self.lats = lats
		if z:
			assert isinstance(z[0], (list, tuple, np.ndarray)), "z items must be sequences"
		else:
			z = [[None] * len(seq) for seq in lons]
		self.z = z
		self.values = values or []
		self.labels = labels or []
		self.style_params = style_params or {}

	def __getitem__(self, index):
		lons = self.lons[index]
		lats = self.lats[index]
		Z = self.z[index]
		value = self._get_value_at_index(index)
		label = self._get_label_at_index(index)
		style_params = self._get_style_params_at_index(index)
		return LineData(lons, lats, z=Z, value=value, label=label,
						style_params=style_params)

	def append(self, line):
		if isinstance(line, LineData):
			self.lons.append(line.lons)
			self.lats.append(line.lats)
			self.z.append(line.z)
			self._append_to_multi_values(self.values, line.value or None)
			self.labels.append(line.label or "")
			self._append_to_multi_values(self.style_params, line.style_params)
		elif isinstance(line, MultiLineData):
			self.lons.extend(line.lons)
			self.lats.extend(line.lats)
			self.z.extend(line.z)
			self._extend_multi_values(self.values, line.values or [None] * len(line))
			self.labels.extend(line.labels or [""] * len(line))
			self._extend_multi_values(self.style_params, line.style_params)

	def to_shapely(self):
		"""
		:param include_z:
			bool, whether or not to include Z-coordinate(s)
			(default: True)
		"""
		if self.z is None or set(self.z[0]) == set([None]):
			coords = [list(zip(self.lons[i], self.lats[i])) for i in range(len(self.lons))]
		else:
			coords = [list(zip(self.lons[i], self.lats[i], self.z[i])) for i in range(len(self.lons))]
		return shapely.geometry.MultiLineString(coords)

	def get_ogr_geomtype(self):
		return ogr.wkbMultiLineString

	@classmethod
	def from_shapely(cls, mls, values=None, labels=None, style_params=None):
		assert mls.geom_type == "MultiLineString"
		lons, lats, Z =  [], [], []
		for ls in mls:
			if mls.has_z:
				x, y, z = zip(*ls.coords)
			else:
				x, y = zip(*ls.coords)
				z = [None] * len(x)
			lons.append(x)
			lats.append(y)
			Z.append(z)
		return MultiLineData(lons, lats, z=Z, values=values, labels=labels,
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

	@classmethod
	def from_lines(cls, line_list):
		"""
		Construct from list of lines

		:param line_list:
			list with instances of :class:`LineData`
		"""
		ml = line_list[0].to_multi_line()
		for line in line_list[1:]:
			ml.append(line)
		return ml


