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
	pass


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


class PointData(BasemapData):
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
	"""
	def __init__(self, lon, lat, value=None, label=""):
		self.lon = lon
		self.lat = lat
		self.value = value
		self.label = label

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
			instance of :class:`MultiPoint`
		"""
		if isinstance(self.value, dict):
			values = {}
			for key in self.value:
				values[key] = [self.value[key]]
		else:
			values = [self.value]
		return MultiPointData([self.lon], [self.lat], values=values, labels=[self.label])

	@classmethod
	def from_wkt(cls, wkt):
		"""
		Create from well-known text

		:param wkt:
			str, well-known text desciption of geometry

		:return:
			instance of :class:`PointData`
		"""
		pt = shapely.geometry.Point(shapely.wkt.loads(wkt))
		return PointData(pt.x, pt.y)

	@classmethod
	def from_ogr(cls, geom):
		"""
		Create from OGRPoint object

		:param geom:
			OGRPoint object

		:return:
			instance of :class:`PointData`
		"""
		return cls.from_wkt(geom.ExportToWkt())


class MultiPointData(BasemapData):
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
		(default: [])
	:param labels:
		list of strings, labels to be plotted alongside points (if
		label_style in corresponding layer style is not None)
		(default: [])
	"""
	def __init__(self, lons, lats, values=[], labels=[]):
		self.lons = lons
		self.lats = lats
		self.values = values
		self.labels = labels

	def __len__(self):
		return len(self.lons)

	def __iter__(self):
		for i in range(len(self)):
			yield self.__getitem__(i)

	def __getitem__(self, index):
		lon = self.lons[index]
		lat = self.lats[index]
		if isinstance(self.values, dict):
			value = {}
			value_keys = self.values.keys()
			for key in value_keys:
				try:
					value[key] = self.values[key][i]
				except:
					value[key] = None
		else:
			try:
				value = self.values[index]
			except:
				value = None
		try:
			label = self.labels[index]
		except:
			label = ""
		return PointData(lon, lat, value, label)

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
		if isinstance(pt0.value, dict):
			values = {}
			for key in pt0.value.keys():
				values[key] = []
		else:
			values = []
		for pt in point_list:
			lons.append(pt.lon)
			lats.append(pt.lat)
			labels.append(pt.label)
			if isinstance(values, dict):
				for key in values.keys():
					values[key].append(pt.value[key])
			else:
				values.append(pt.value)
		return MultiPointData(lons, lats, values, labels)

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
			if isinstance(self.values, dict):
				for key in self.values.keys():
					self.values[key].extend(pt.values[key])
			else:
				self.values.extend(pt.values)
			self.labels.extend(pt.labels)

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
		return MultiPointData(lons, lats, values, labels)

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
	def from_wkt(cls, wkt):
		"""
		Create from well-known text

		:param wkt:
			str, well-known text desciption of geometry

		:return:
			instance of :class:`MultiPointData`
		"""
		mp = shapely.geometry.MultiPoint(shapely.wkt.loads(wkt))
		return MultiPointData([pt.x for pt in mp], [pt.y for pt in mp])

	@classmethod
	def from_ogr(cls, geom):
		"""
		Create from OGRMultiPoint object

		:param geom:
			OGRMultiPoint object

		:return:
			instance of :class:`MultiPointData`
		"""
		return cls.from_wkt(geom.ExportToWkt())

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
		return sorted_indexes


class LineData(BasemapData):
	def __init__(self, lons, lats, value=None, label=""):
		self.lons = lons
		self.lats = lats
		self.value = value
		self.label = label

	def __len__(self):
		return 1

	def __iter__(self):
		for i in range(1):
			yield self

	def to_shapely(self):
		return shapely.geometry.LineString(zip(self.lons, self.lats))

	def to_wkt(self):
		return self.to_shapely().wkt

	@classmethod
	def from_wkt(cls, wkt):
		ls = shapely.geometry.LineString(shapely.wkt.loads(wkt))
		lons, lats = zip(*ls.coords)
		return LineData(lons, lats)

	@classmethod
	def from_ogr(cls, geom):
		return cls.from_wkt(geom.ExportToWkt())

	def get_midpoint(self):
		ls = self.to_shapely()
		midPoint = ls.interpolate(ls.length/2)
		return PointData(midPoint.x, midPoint.y)

	def get_centroid(self):
		centroid = self.to_shapely().centroid
		return PointData(centroid.x, centroid.y)

	def to_polygon(self):
		# TODO: should we check if first point == last point?
		return PolygonData(self.lons, self.lats, value=self.value, label=self.label)


class MultiLineData(BasemapData):
	def __init__(self, lons, lats, values=[], labels=[]):
		if lons:
			assert isinstance(lons[0], (list, tuple, np.ndarray)), "lons items must be sequences"
		self.lons = lons
		if lats:
			assert isinstance(lats[0], (list, tuple, np.ndarray)), "lats items must be sequences"
		self.lats = lats
		self.values = values
		self.labels = labels

	def __len__(self):
		return len(self.lons)

	def __iter__(self):
		for i in range(len(self.lons)):
			yield self.__getitem__(i)

	def __getitem__(self, index):
		lons = self.lons[index]
		lats = self.lats[index]
		if isinstance(self.values, dict):
			value = {}
			value_keys = self.values.keys()
			for key in value_keys:
				try:
					value[key] = self.values[key][i]
				except:
					value[key] = None
		else:
			try:
				value = self.values[index]
			except:
				value = None
		try:
			label = self.labels[index]
		except:
			label = ""
		return LineData(lons, lats, value, label)

	def append(self, line):
		if isinstance(line, LineData):
			self.lons.append(line.lons)
			self.lats.append(line.lats)
			if line.value:
				self.values.append(line.value)
			if line.label:
				self.labels.append(line.label)
		elif isinstance(line, MultiLineData):
			self.lons.extend(line.lons)
			self.lats.extend(line.lats)
			if line.values:
				self.values.extend(line.values)
			if line.labels:
				self.labels.extend(line.labels)

	def to_shapely(self):
		coords = [zip(self.lons[i], self.lats[i]) for i in range(len(lons))]
		return shapely.geometry.MultiLineString(coords)

	def to_wkt(self):
		return self.to_shapely().wkt

	@classmethod
	def from_wkt(cls, wkt):
		mls = shapely.geometry.MultiLineString(shapely.wkt.loads(wkt))
		lons, lats =  [], []
		for ls in mls:
			x, y = zip(*ls.coords)
			lons.append(x)
			lats.append(y)
		yield MultiLineData(lons, lats)

	@classmethod
	def from_ogr(cls, geom):
		return cls.from_wkt(geom.ExportToWkt())


class PolygonData(BasemapData):
	def __init__(self, lons, lats, interior_lons=[], interior_lats=[], value=None, label=""):
		"""
		lons, lats: lists
		interior_lons, interior_lats: 3-D lists
		"""
		self.lons = lons
		self.lats = lats
		self.interior_lons = interior_lons
		self.interior_lats = interior_lats
		self.value = value
		self.label = label

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
	def from_wkt(cls, wkt):
		#pg = shapely.geometry.Polygon(shapely.wkt.loads(wkt))
		pg = shapely.wkt.loads(wkt)
		exterior_lons, exterior_lats = zip(*pg.exterior.coords)
		interior_lons, interior_lats = [], []
		for interior_ring in pg.interiors:
			lons, lats = zip(*interior_ring.coords)
			interior_lons.append(lons)
			interior_lats.append(lats)
		return PolygonData(exterior_lons, exterior_lats, interior_lons, interior_lats)

	@classmethod
	def from_ogr(cls, geom):
		## Correct invalid polygons with more than 1 linear ring
		import ogr
		num_rings = geom.GetGeometryCount()
		if num_rings > 1:
			ring_lengths = [geom.GetGeometryRef(i).GetPointCount() for i in range(num_rings)]
			idx = int(np.argmax(ring_lengths))
			poly = ogr.Geometry(ogr.wkbPolygon)
			poly.AddGeometry(geom.GetGeometryRef(idx))
			geom = poly
		return cls.from_wkt(geom.ExportToWkt())

	def get_centroid(self):
		centroid = self.to_shapely().centroid
		return PointData(centroid.x, centroid.y)

	def to_line(self):
		## Interior rings are ignored
		return LineData(self.lons, self.lats, value=self.value, label=self.label)


class MultiPolygonData(BasemapData):
	def __init__(self, lons, lats, interior_lons=[], interior_lats=[], values=[], labels=[]):
		"""
		lons, lats: 2-D lists
		interior_lons, interior_lats: 3-D lists
		"""
		self.lons = lons
		self.lats = lats
		self.interior_lons = interior_lons
		self.interior_lats = interior_lats
		self.values = values
		self.labels = labels

	def __len__(self):
		return len(self.lons)

	def __iter__(self):
		for i in range(len(self.lons)):
			yield self.__getitem__(i)

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
		if isinstance(self.values, dict):
			value = {}
			value_keys = self.values.keys()
			for key in value_keys:
				try:
					value[key] = self.values[key][i]
				except:
					value[key] = None
		else:
			try:
				value = self.values[index]
			except:
				value = None
		try:
			label = self.labels[index]
		except:
			label = ""
		return PolygonData(lons, lats, interior_lons, interior_lats, value, label)

	def append(self, polygon):
		assert isinstance(polygon, PolygonData)
		self.lons.append(polygon.lons)
		self.lats.append(polygon.lats)
		if polygon.interior_lons:
			self.interior_lons.append(polygon.interior_lons)
			self.interior_lats.append(polygon.interior_lats)
		if polygon.value:
			self.values.append(polygon.value)
		if polygon.label:
			self.labels.append(polygon.label)

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
		try:
			value = self.values[0]
		except IndexError:
			value = None
		try:
			label = self.labels[0]
		except IndexError:
			label = ""

		return PolygonData(lons, lats, interior_lons, interior_lats, value, label)

	def to_shapely(self):
		shapely_polygons = [pg.to_shapely() for pg in self]
		return shapely.geometry.MultiPolygon(shapely_polygons)

	def to_wkt(self):
		return self.to_shapely().wkt

	@classmethod
	def from_wkt(cls, wkt):
		mpg = shapely.geometry.MultiPolygon(shapely.wkt.loads(wkt))
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
		return MultiPolygonData(exterior_lons, exterior_lats, interior_lons, interior_lats)

	@classmethod
	def from_ogr(cls, geom):
		return cls.from_wkt(geom.ExportToWkt())


class FocmecData(MultiPointData):
	"""
	"""
	# TODO: Add possibility to plot mechanism at different location
	# (different coordinates or offset?)
	def __init__(self, lons, lats, sdr, values=[], labels=[]):
		super(FocmecData, self).__init__(lons, lats, values, labels)
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
		return self.lons[0,1] - self.lons[0,0]

	@property
	def dlat(self):
		return self.lats[1,0] - self.lats[0,0]

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
	:param downsampling:
		float, factor for downsampling, i.e. to divide number of columns and
		rows with
		(default: 1., no downsampling)
	"""
	def __init__(self, filespec, band_nr=1, down_sampling=1.):
		self.filespec = filespec
		self.band_nr = band_nr
		self.read_grid_info()
		self._edge_lons = None
		self._edge_lats = None
		self._center_lons = None
		self._center_lats = None
		self.set_down_sampling(down_sampling)

	def set_down_sampling(self, down_sampling):
		self.down_sampling = float(down_sampling)
		self.ncols = int(round(self.ncols / self.down_sampling))
		self.nrows = int(round(self.nrows / self.down_sampling))

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
		- :prop:`xmin`, :prop:`xmax`: float, extent in X direction in
			the native spatial reference system
		- :prop:`xmin`, :prop:`xmax`: float, extent in Y direction in
			the native spatial reference system
		"""
		import gdal, osr

		ds = gdal.Open(self.filespec)
		self.srs = osr.SpatialReference()
		self.srs.ImportFromWkt(ds.GetProjection())
		self.num_bands = ds.RasterCount

		gt = ds.GetGeoTransform()
		# TODO: support rotated grids
		self.ncols, self.nrows = ds.RasterXSize, ds.RasterYSize
		self.dx, self.dy = gt[1], gt[5]
		xmin = gt[0] + self.dx * 0.5
		xmax = gt[0] + (self.dx * self.ncols) - self.dx * 0.5
		if self.dx < 0:
			xmin, xmax = xmax, xmin
		ymin = gt[3] + (self.dy * self.nrows) + self.dy * 0.5
		ymax = gt[3] - self.dy * 0.5
		if self.dy < 0:
			ymin, ymax = ymax, ymin
		self.xmin, self.xmax = xmin, xmax
		self.ymin, self.ymax = ymin, ymax

		ds = None

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
		if cell_registration in ("corner", "edge"):
			xx, yy = np.meshgrid(np.linspace(self.xmin, self.xmax, self.ncols+1),
							np.linspace(self.ymin, self.ymax, self.nrows+1))
		elif cell_registration == "center":
			xx, yy = np.meshgrid(np.linspace(self.xmin + self.dx/2., self.xmax - self.dx/2., self.ncols),
							np.linspace(self.ymin + self.dy/2., self.ymax - self.dy/2., self.nrows))

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
		ds = gdal.Open(self.filespec)
		band = ds.GetRasterBand(band_nr)
		nodata = band.GetNoDataValue()
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
		ds = gdal.Open(self.filespec)
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

		xin = np.linspace(self.xmin, self.xmax, self.ncols)
		## yin must be linearly increasing, so we need to reverse!
		yin = np.linspace(self.ymax, self.ymin, self.nrows)

		if self.band_nr:
			out_data = interp(self.values[::-1,:], xin, yin, xout, yout, checkbounds=checkbounds,
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

	def cross_section(self):
		pass

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
			str, GDAL format speciication
		:param out_filespec:
			str, full path to output file
		"""
		from osgeo import gdal

		## Open output format driver, see gdal_translate --formats for list
		driver = gdal.GetDriverByName(format)
		if driver and driver.GetMetaData().get(gdal.DCAP_CREATE) == 'YES':
			## Open existing dataset
			src_ds = gdal.Open(self.filespec)

			## Output to new format
			dst_ds = driver.CreateCopy(out_filespec, src_ds, 0)

			## Properly close the datasets to flush to disk
			dst_ds = None
			src_ds = None

		else:
			print("Driver %s does not support CreateCopy() method" % format)


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
	"""
	def __init__(self, filespec, label_colname=None, selection_dict={}, joined_attributes={}):
		self.filespec = filespec
		self.label_colname = label_colname
		self.selection_dict = selection_dict
		self.joined_attributes = joined_attributes

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
		from mapping.geo.readGIS import read_GIS_file, read_GIS_file_attributes

		if None in (point_value_colnames, line_value_colnames, polygon_value_colnames):
			colnames = read_GIS_file_attributes(self.filespec)
		if point_value_colnames is None:
			point_value_colnames = colnames
		if line_value_colnames is None:
			line_value_colnames = colnames
		if polygon_value_colnames is None:
			polygon_value_colnames = colnames

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
		polygon_data = MultiPolygonData([], [], interior_lons=[], interior_lats=[], values=[], labels=[])
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
				geom = rec['obj']
				geom_type = geom.GetGeometryName()
				if geom_type == "POINT":
					pt = PointData.from_ogr(geom)
					pt.label = label
					point_data.append(pt)
					for colname in point_value_colnames:
						point_data.values[colname].append(rec[colname])
				elif geom_type == "MULTIPOINT":
					# TODO: needs to be tested
					multi_pt = MultiPointData.from_ogr(geom)
					for pt in multi_pt:
						pt.label = label
						point_data.append(pt)
						for colname in point_value_colnames:
							point_data.values[colname].append(rec[colname])
				elif geom_type == "LINESTRING":
					line = LineData.from_ogr(geom)
					line.label = label
					line_data.append(line)
					for colname in line_value_colnames:
						line_data.values[colname].append(rec[colname])
				elif geom_type == "MULTILINESTRING":
					multi_line = MultiLineData.from_ogr(geom)
					for line in multi_line:
						line.label = label
						line_data.append(line)
						for colname in line_value_colnames:
							line_data.values[colname].append(rec[colname])
				elif geom_type == "POLYGON":
					polygon = PolygonData.from_ogr(geom)
					polygon.label = label
					polygon_data.append(polygon)
					for colname in polygon_value_colnames:
						polygon_data.values[colname].append(rec[colname])
				elif geom_type == "MULTIPOLYGON":
					try:
						multi_polygon = MultiPolygonData.from_ogr(geom)
					except:
						print label
					for polygon in multi_polygon:
						polygon.label = label
						polygon_data.append(polygon)
						for colname in polygon_value_colnames:
							polygon_data.values[colname].append(rec[colname])

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

	def export(format, out_filespec):
		"""
		Export GIS file to another format

		:param format:
			str, OGR format speciication
		:param out_filespec:
			str, full path to output file
		"""
		driver = ogr.GetDriverByName(format)
		if driver:
			in_ds = ogr.Open(self.filespec, 0)
			out_ds = driver.CopyDataSource(in_ds, out_filespec)
		else:
			print("Driver %s does not support CreateCopy() method" % format)


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
