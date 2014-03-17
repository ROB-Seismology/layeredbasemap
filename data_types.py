"""
Data types used in LayeredBasemap
"""

import numpy as np
import shapely
import shapely.geometry
import shapely.wkt



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
		return shapely.geometry.Point(self.lon, self.lat)

	def to_wkt(self):
		return self.to_shapely().wkt

	def to_multi_point(self):
		if isinstance(self.value, dict):
			values = {}
			for key in self.value:
				values[key] = [self.value[key]]
		else:
			values = [self.value]
		return MultiPointData([self.lon], [self.lat], values=values, labels=[self.label])

	@classmethod
	def from_wkt(cls, wkt):
		pt = shapely.geometry.Point(shapely.wkt.loads(wkt))
		return PointData(pt.x, pt.y)

	@classmethod
	def from_ogr(cls, geom):
		return cls.from_wkt(geom.ExportToWkt())


class MultiPointData(BasemapData):
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
		assert isinstance(pt, PointData)
		self.lons.append(pt.lon)
		self.lats.append(pt.lat)
		if pt.value:
			self.values.append(pt.value)
		if pt.label:
			self.labels.append(pt.label)

	def get_masked_data(self, bbox):
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
		return shapely.geometry.MultiPoint(zip(self.lons, self.lats))

	def to_wkt(self):
		return self.to_shapely().wkt

	@classmethod
	def from_wkt(cls, wkt):
		mp = shapely.geometry.MultiPoint(shapely.wkt.loads(wkt))
		return MultiPointData([pt.x for pt in mp], [pt.y for pt in mp])

	@classmethod
	def from_ogr(cls, geom):
		return cls.from_wkt(geom.ExportToWkt())

	def get_centroid(self):
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


class GisData(BasemapData):
	def __init__(self, filespec, label_colname=None, selection_dict={}):
		self.filespec = filespec
		self.label_colname = label_colname
		self.selection_dict = selection_dict


