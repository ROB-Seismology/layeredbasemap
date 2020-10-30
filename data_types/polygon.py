"""
Polygon data
"""

from __future__ import absolute_import, division, print_function, unicode_literals


import numpy as np
import shapely
import shapely.geometry
import shapely.wkt
import osr, ogr, gdal

from .base import SingleData, MultiData
from .point import PointData
from .line import LineData


__all__ = ['PolygonData', 'MultiPolygonData']



class PolygonData(SingleData):
	def __init__(self, lons, lats, z=None, interior_lons=None, interior_lats=None,
				interior_z=None, value=None, label="", style_params=None):
		"""
		lons, lats: lists
		interior_lons, interior_lats: 2-D lists
		"""
		self.lons = lons
		self.lats = lats
		self.z = z or [None] * len(lons)
		self.interior_lons = interior_lons or []
		self.interior_lats = interior_lats or []
		self.interior_z = interior_z or [[None] * len(seq) for seq in self.interior_lons]
		self.value = value
		self.label = label
		self.style_params = style_params or {}

	def __len__(self):
		return 1

	def __iter__(self):
		for i in range(1):
			return self

	def to_shapely(self):
		"""
		"""
		if self.z is None or set(self.z) == set([None]):
			if self.interior_lons:
				shp = shapely.geometry.Polygon(list(zip(self.lons, self.lats)),
					[list(zip(self.interior_lons[i], self.interior_lats[i]))
					for i in range(len(self.interior_lons))])
			else:
				shp = shapely.geometry.Polygon(list(zip(self.lons, self.lats)))
		else:
			if self.interior_lons:
				shp = shapely.geometry.Polygon(list(zip(self.lons, self.lats, self.z)),
					[list(zip(self.interior_lons[i], self.interior_lats[i], self.interior_z[i]))
					for i in range(len(self.interior_lons))])
			else:
				shp = shapely.geometry.Polygon(list(zip(self.lons, self.lats, self.z)))

		return shp

	def get_ogr_geomtype(self):
		return ogr.wkbPolygon

	@classmethod
	def from_shapely(cls, pg, value=None, label="", style_params=None):
		assert pg.geom_type == "Polygon"
		if pg.has_z:
			exterior_lons, exterior_lats, exterior_z = zip(*pg.exterior.coords)
		else:
			exterior_lons, exterior_lats = zip(*pg.exterior.coords)
			exterior_z = [None] * len(exterior_lons)
		interior_lons, interior_lats, interior_z = [], [], []
		for interior_ring in pg.interiors:
			if interior_ring.has_z:
				lons, lats, z = zip(*interior_ring.coords)
			else:
				lons, lats = zip(*interior_ring.coords)
				z = [None] * len(lons)
			interior_lons.append(lons)
			interior_lats.append(lats)
			interior_z.append(z)
		return PolygonData(exterior_lons, exterior_lats, exterior_z,
						interior_lons, interior_lats, interior_z,
						value=value, label=label, style_params=style_params)

	@classmethod
	def from_wkt(cls, wkt, value=None, label="", style_params=None):
		pg = shapely.wkt.loads(wkt)
		return cls.from_shapely(pg, value=value, label=label,
								style_params=style_params)

	@classmethod
	def from_ogr(cls, geom, value=None, label="", style_params=None):
		## Correct invalid polygons containing rings with insufficient points
		import ogr
		if not geom.IsValid():
			poly = ogr.Geometry(ogr.wkbPolygon)
			for i in range(geom.GetGeometryCount()):
				num_points = geom.GetGeometryRef(i).GetPointCount()
				## linear ring must have at least 3 points
				if num_points > 2:
					poly.AddGeometry(geom.GetGeometryRef(i))
			if poly.GetGeometryCount():
				geom = poly
			else:
				print("Skipped invalid polygon")
				return
		## Remove remaining self-intersections
		#if not geom.IsValid():
			#geom = geom.Buffer(0)
			#geom = geom.SimplifyPreserveTopology(0.1)
		return cls.from_wkt(geom.ExportToWkt(), value=value, label=label,
							style_params=style_params)

	@classmethod
	def from_bbox(cls, bbox, value=None, label="", style_params=None):
		lon_min, lon_max, lat_min, lat_max = bbox
		lons = [lon_min, lon_min, lon_max, lon_max, lon_min]
		lats = [lat_min, lat_max, lat_max, lat_min, lat_min]
		return PolygonData(lons, lats, value=value, label=label, style_params=style_params)

	def get_centroid(self):
		centroid = self.to_shapely().centroid
		return PointData(centroid.x, centroid.y)

	def get_west_point(self):
		idx = np.argmin(self.lons)
		return PointData(self.lons[idx], self.lats[idx])

	def get_east_point(self):
		idx = np.argmax(self.lons)
		return PointData(self.lons[idx], self.lats[idx])

	def get_south_point(self):
		idx = np.argmin(self.lats)
		return PointData(self.lons[idx], self.lats[idx])

	def get_north_point(self):
		idx = np.argmax(self.lats)
		return PointData(self.lons[idx], self.lats[idx])

	def to_line(self):
		## Interior rings are ignored
		return LineData(self.lons, self.lats, z=self.z, value=self.value,
						label=self.label, style_params=self.style_params)

	def to_multi_polygon(self):
		values = self._get_multi_values(self.value)
		style_params = self._get_multi_values(self.style_params)
		return MultiPolygonData([self.lons], [self.lats], [self.z],
					interior_lons=[self.interior_lons],
					interior_lats=[self.interior_lats],
					interior_z=[self.interior_z],
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
			print(intersection.wkt)

	def get_bbox(self):
		lonmin, lonmax = np.min(self.lons), np.max(self.lons)
		latmin, latmax = np.min(self.lats), np.max(self.lats)
		return (lonmin, lonmax, latmin, latmax)

	def is_closed(self):
		if self.lons[0] == self.lons[-1] and self.lats[0] == self.lats[-1]:
			return True
		else:
			return False

	def contains(self, geom_data):
		"""
		Check if given geometries are situated inside the polygon.

		:param geom_data:
			instance of :class:`SingleData` or :class:`MultiData`

		:return:
			bool or bool array
		"""
		ogr_geom = self.to_ogr_geom()
		if isinstance(geom_data, SingleData):
			inside = ogr_geom.Contains(geom_data.to_ogr_geom())
		elif isinstance(geom_data, MultiData):
			inside = np.zeros(len(geom_data), dtype='bool')
			for s, single_data in enumerate(geom_data):
				inside[s] = ogr_geom.Contains(single_data.to_ogr_geom())
		return inside

	def get_area(self):
		"""
		Calculate area of polygon

		:return:
			float, polygon area (in square m)
		"""
		## Set up transformation to projection with units in meters (Google projection)
		from mapping.geotools.coordtrans import WGS84, GGL_MERCATOR
		transform = osr.CoordinateTransformation(WGS84, GGL_MERCATOR)

		ogr_geom = self.to_ogr_geom()
		ogr_geom.Transform(transform)

		return ogr_geom.GetArea()

	def get_overlap_ratio(self, other_pg):
		"""
		Calculate overlap fraction with other polygon as the ratio
		between the smallest of the two areas and the overlapping area

		:param other_pg:
			instance of :class:`PolygonData` or :class:`ogr.Geometry`

		:return:
			float in the range 0 - 1
		"""
		from mapping.geotools.coordtrans import WGS84, GGL_MERCATOR
		transform = osr.CoordinateTransformation(WGS84, GGL_MERCATOR)

		ogr_geom = self.to_ogr_geom()
		ogr_geom.Transform(transform)

		if isinstance(other_pg, ogr.Geometry):
			other_ogr_geom = other_pg.Clone()
		elif isinstance(other_pg, (PolygonData, MultiPolygonData)):
			other_ogr_geom = other_pg.to_ogr_geom()
		other_ogr_geom.Transform(transform)

		original_area = min(ogr_geom.GetArea(), other_ogr_geom.GetArea())
		intersection = ogr_geom.Intersection(other_ogr_geom)
		if intersection:
			overlapping_area = intersection.GetArea()
		else:
			overlapping_area = 0.
		return overlapping_area / original_area

	def get_union(self, other_pg):
		"""
		Construct union with other polygon

		:param other_pg:
			instance of :class:`PolygonData`

		:return:
			instance of :class:`PolygonData`
		"""
		assert isinstance(other_pg, self.__class__)

		ogr_geom = self.to_ogr_geom()
		other_ogr_geom = other_pg.to_ogr_geom()

		union = ogr_geom.Union(other_ogr_geom)

		return self.from_ogr(union)

	def get_intersection(self, other_pg):
		"""
		Construct intersection with other polygon

		:param other_pg:
			instance of :class:`PolygonData`

		:return:
			instance of :class:`PolygonData`
		"""
		assert isinstance(other_pg, self.__class__)

		ogr_geom = self.to_ogr_geom()
		other_ogr_geom = other_pg.to_ogr_geom()

		union = ogr_geom.Intersection(other_ogr_geom)

		return self.from_ogr(union)


class MultiPolygonData(MultiData):
	def __init__(self, lons, lats, z=None, interior_lons=None, interior_lats=None,
				interior_z=None, values=None, labels=None, style_params=None):
		"""
		lons, lats: 2-D lists
		interior_lons, interior_lats: 3-D lists
		"""
		self.lons = lons
		self.lats = lats
		self.z = z or [[None] * len(pg) for pg in lons]
		self.interior_lons = interior_lons or []
		self.interior_lats = interior_lats or []
		self.interior_z = interior_z or [[[None] * len(seq) for seq in pg] for pg in self.interior_lons]
		self.values = values or []
		self.labels = labels or []
		self.style_params = style_params or {}

	def __getitem__(self, index):
		lons = self.lons[index]
		lats = self.lats[index]
		Z = self.z[index]
		try:
			interior_lons = self.interior_lons[index]
		except:
			interior_lons = []
			interior_lats = []
			interior_z = []
		else:
			interior_lats = self.interior_lats[index]
			interior_z = self.interior_z[index]
		value = self._get_value_at_index(index)
		label = self._get_label_at_index(index)
		style_params = self._get_style_params_at_index(index)
		return PolygonData(lons, lats, Z, interior_lons, interior_lats, interior_z,
						value=value, label=label, style_params=style_params)

	def append(self, polygon):
		assert isinstance(polygon, PolygonData)
		self.lons.append(polygon.lons)
		self.lats.append(polygon.lats)
		self.z.append(polygon.z)
		self.interior_lons.append(polygon.interior_lons or [])
		self.interior_lats.append(polygon.interior_lats or [])
		self.interior_z.append(polygon.interior_z or [])
		self._append_to_multi_values(self.values, polygon.value or None)
		self.labels.append(polygon.label or "")
		self._append_to_multi_values(self.style_params, polygon.style_params)

	def to_polygon(self):
		"""
		Discard all but the first polygon
		"""
		lons = self.lons[0]
		lats = self.lats[0]
		Z = self.z[0]
		try:
			interior_lons = self.interior_lons[0]
		except IndexError:
			interior_lons = []
			interior_lats = []
			interior_z = []
		else:
			interior_lats = self.interior_lats[0]
			interior_z = self.interior_z[0]
		value = self._get_value_at_index(0)
		label = self._get_label_at_index(0)
		style_params = self._get_style_params_at_index(0)

		return PolygonData(lons, lats, Z, interior_lons, interior_lats,
							interior_z=interior_z, value=value, label=label,
							style_params=style_params)

	def to_shapely(self):
		"""
		"""
		shapely_polygons = [pg.to_shapely() for pg in self]
		return shapely.geometry.MultiPolygon(shapely_polygons)

	def get_ogr_geomtype(self):
		return ogr.wkbMultiPolygon

	@classmethod
	def from_shapely(cls, mpg, values=None, labels=None, style_params=None):
		assert mpg.geom_type == "MultiPolygon"
		exterior_lons, exterior_lats, exterior_z = [], [], []
		interior_lons, interior_lats, interior_z = [], [], []
		for pg in mpg:
			if pg.has_z:
				lons, lats, z = zip(*pg.exterior.coords)
			else:
				lons, lats = zip(*pg.exterior.coords)
				z = [None] * len(lons)
			exterior_lons.append(lons)
			exterior_lats.append(lats)
			exterior_z.append(z)
			pg_interior_lons, pg_interior_lats, pg_interior_z = [], [], []
			for interior_ring in pg.interiors:
				if interior_ring.has_z:
					lons, lats, z = zip(*interior_ring.coords)
				else:
					lons, lats = zip(*interior_ring.coords)
					z = [None] * len(lons)
				pg_interior_lons.append(lons)
				pg_interior_lats.append(lats)
				pg_interior_z.append(z)
			interior_lons.append(pg_interior_lons)
			interior_lats.append(pg_interior_lats)
			interior_z.append(pg_interior_z)
		return MultiPolygonData(exterior_lons, exterior_lats, exterior_z,
							interior_lons, interior_lats, interior_z, values=values,
							labels=labels, style_params=style_params)

	@classmethod
	def from_wkt(cls, wkt, values=None, labels=None, style_params=None):
		mpg = shapely.geometry.MultiPolygon(shapely.wkt.loads(wkt))
		return cls.from_shapely(mpg, values=values, labels=labels,
								style_params=style_params)

	@classmethod
	def from_ogr(cls, geom, values=None, labels=None, style_params=None):
		return cls.from_wkt(geom.ExportToWkt(), values=values, labels=labels,
							style_params=style_params)

	@classmethod
	def from_polygons(cls, pg_list):
		"""
		Construct from list of polygons

		:param pg_list:
			list with instances of :class:`PolygonData`
		"""
		mpg = pg_list[0].to_multi_polygon()
		for pg in pg_list[1:]:
			mpg.append(pg)
		return mpg

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
			print(intersection.wkt)
