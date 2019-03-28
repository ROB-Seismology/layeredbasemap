"""
Grid data types
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
import osr, gdal

from .base import BasemapData, WGS84
from .point import MultiPointData
from .line import LineData, MultiLineData
from .polygon import PolygonData, MultiPolygonData


__all__ = ['GridData', 'MeshGridData', 'UnstructuredGridData',
			'GdalRasterData', 'WCSData', 'MeshGridVectorData']


class GridData(BasemapData):
	def __init__(self, lons, lats, values, unit=""):
		self.lons = np.asarray(lons)
		self.lats = np.asarray(lats)
		self.values = np.asarray(values)
		self.unit = unit


class UnstructuredGridData(GridData):
	"""
	Unstructured 2-dimensional data (e.g., point clouds)

	Provides method(s) to interpolate into meshed grid

	:param lons:
		1-D array of longitudes
	:param lats:
		1-D array of latitudes
	:param values:
		1-D array of values
	:param unit:
		str, measurement unit of values
		(default: "")
	"""
	def __init__(self, lons, lats, values, unit=""):
		if lons.ndim != 1 or lats.ndim != 1 or values.ndim != 1:
			raise ValueError("lons, lats, and values should be 1-dimensional")
		super(UnstructuredGridData, self).__init__(lons, lats, values, unit)

	def __len__(self):
		return len(self.lons)

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

	def get_extent(self):
		"""
		:return:
			(lonmin, lonmax, latmin, latmax) tuple
		"""
		return (self.lonmin(), self.lonmax(), self.latmin(), self.latmax())

	def confine_to_extent(self, extent):
		"""
		Confine grid to given rectangular extent

		:param extent:
			(lonmin, lonmax, latmin, latmax) tuple

		:return:
			instance of :class:`UnstructuredGridData`
		"""
		lonmin, lonmax, latmin, latmax = extent
		idxs = np.where((self.lons >= lonmin) & (self.lons <= lonmax)
						& (self.lats >= latmin) & (self.lats <= latmax))
		lons = self.lons[idxs]
		lats = self.lats[idxs]
		values = self.values[idxs]
		return UnstructuredGridData(lons, lats, values, unit=self.unit)

	def to_multi_point_data(self):
		"""
		Convert to multi-point data

		:return:
			instance of :class:`MultiPointData`
		"""
		lons = self.lons.flatten()
		lats = self.lats.flatten()
		values = self.values.flatten()
		return MultiPointData(lons, lats, list(values))

	def to_mesh_grid_data(self, num_cells, extent=(None, None, None, None),
						interpolation_method='cubic', max_dist=5.):
		"""
		Convert to meshed grid data

		:param num_cells:
			Integer or tuple, number of grid cells in lon and lat direction
		:param extent:
			(lonmin, lonmax, latmin, latmax) tuple of floats
			(default: (None, None, None, None)
		:param interpolation_method:
			Str, interpolation method supported by griddata, either
			"linear", "nearestN" (with N number of neighbors to consider),
			"cubic" or "idwP" (with P power to raise distances to)
			(default: "cubic")
		:param max_dist:
			float, maximum interpolation distance (in km)
			Only relevant for "nearestN" and "idwP" methods
			(default: 5.)

		:return:
			instance of :class:`MeshGridData`
		"""
		if isinstance(num_cells, int):
			num_cells = (num_cells, num_cells)
		num_lons, num_lats = num_cells
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

		max_dist *= 1000  ## km --> m

		if (interpolation_method in ('linear', 'cubic') or
			interpolation_method[:7] == 'nearest'):
			from scipy.interpolate import griddata
			from mapping.geotools.coordtrans import lonlat_to_meter
			## Convert geographic to cartesian coordinates
			ref_lat = np.mean([latmin, latmax])
			x, y = lonlat_to_meter(self.lons, self.lats, ref_lat=ref_lat)
			mesh_x, mesh_y = lonlat_to_meter(mesh_lons, mesh_lats, ref_lat=ref_lat)

			if interpolation_method[:7] == 'nearest':
				from scipy.spatial import cKDTree
				tree = cKDTree(zip(x, y))
				num_neighbors = 1
				if len(interpolation_method) > 7:
					num_neighbors = int(interpolation_method[7:])
				d, idxs = tree.query(zip(mesh_x.flatten(), mesh_y.flatten()),
						k=num_neighbors, eps=0, distance_upper_bound=max_dist)
				if num_neighbors == 1:
					## When k == 1, the last dimension of the output is squeezed
					idxs.shape += (1,)
				if max_dist == np.inf:
					mesh_values = self.values[idxs]
				else:
					mesh_values = np.ones_like(idxs) * np.nan
					for i in range(idxs.shape[0]):
						i_idxs = idxs[i]
						## Missing neighbors are indicated with index = len(tree)
						i_idxs = i_idxs[i_idxs < len(self.lons)]
						mesh_values[i,:len(i_idxs)] = self.values[idxs[i,:len(i_idxs)]]
				mesh_values = np.nanmean(mesh_values, axis=-1)
				mesh_values.shape = mesh_lons.shape
			else:
				mesh_values = griddata((x, y), self.values,
							(mesh_x, mesh_y), method=interpolation_method)

		elif interpolation_method[:3] == 'idw':
			from mapping.geotools.geodetic import spherical_distance
			pow = 1
			if len(interpolation_method) > 3:
				pow = int(interpolation_method[3:])
			mesh_values = np.ones_like(mesh_lons) * np.nan
			for i in range(num_lons):
				lon = lons[i]
				for j in range(num_lats):
					lat = lats[j]
					d = spherical_distance(lon, lat, self.lons, self.lats)
					idxs = (d <= max_dist)
					weights = 1. / d[idxs]
					if pow != 1:
						weights **= pow
					if np.sum(weights):
						mesh_values[j, i] = np.average(self.values[idxs], weights=weights)

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
	:param unit:
		str
	"""
	# TODO: add srs parameter and define similar properties as GdalRasterData
	# e.g.: x0, x1, dx instead of lon0, lon1, dlon
	# TODO: correctly implement edge_lons, edge_lats!
	# TODO: add nodata_value (np.nan only works for float arrays!)
	def __init__(self, lons, lats, values, unit=""):
		if lons.ndim != 2 or lats.ndim != 2 or values.ndim != 2:
			raise ValueError("lons, lats, and values should be 2-dimensional")
		## Not sure the following is really necessary
		dlon = np.diff(lons)
		dlat = np.diff(lats)
		if not np.allclose(dlon, dlon[0]) or not np.allclose(dlat, dlat[0]):
			raise ValueError("Grid spacing must be uniform")
		super(MeshGridData, self).__init__(lons, lats, values, unit)

		# TODO: need to make functions for these using source srs
		# (in which grid is rectangular)
		self.center_lons = lons
		self.center_lats = lats
		self._edge_lons, self._edge_lats = None, None

		## For compatibility with GdalRasterData
		self.srs = WGS84

	@property
	def edge_lons(self):
		if self._edge_lons is None:
			lons = np.linspace(self.lon0 - self.dlon/2., self.lon1 + self.dlon/2., self.ncols + 1)
			lats = np.linspace(self.lat0 - self.dlat/2., self.lat1 + self.dlat/2., self.nrows + 1)
			self._edge_lons, self._edge_lats = np.meshgrid(lons, lats)
		return self._edge_lons

	@property
	def edge_lats(self):
		if self._edge_lats is None:
			self._edge_lons
		return self._edge_lats

	@property
	def dlon(self):
		return self.center_lons[0,1] - self.center_lons[0,0]

	@property
	def dlat(self):
		return self.center_lats[1,0] - self.center_lats[0,0]

	@property
	def lon0(self):
		return self.center_lons[0,0]

	@property
	def lon1(self):
		return self.center_lons[0,-1]

	@property
	def lat0(self):
		return self.center_lats[0,0]

	@property
	def lat1(self):
		return self.center_lats[-1,0]

	@property
	def ncols(self):
		return self.center_lons.shape[1]

	@property
	def nrows(self):
		return self.center_lons.shape[0]

	def get_mesh_coordinates(self, cell_registration="corner"):
		"""
		To make MeshGridData compatible with GdalRasterData
		"""
		if cell_registration == "corner":
			return (self.edge_lons, self.edge_lats)
		else:
			return (self.lons, self.lats)

	def to_multi_point_data(self, apply_mask=True):
		"""
		Convert to multi-point data

		:param apply_mask:
			bool, whether or not to leave out masked data
			(default: True)

		:return:
			instance of :class:`MultiPointData`
		"""
		if apply_mask and self.is_masked():
			mask = self.values.mask
			values = self.values[~mask].data
			lons = self.lons[~mask]
			lats = self.lats[~mask]
		else:
			values = self.values.flatten()
			lons = self.lons.flatten()
			lats = self.lats.flatten()
		return MultiPointData(lons, lats, list(values))

	def mask_oceans(self, resolution, mask_lakes=False, grid_spacing=1.25):
		from mpl_toolkits.basemap import maskoceans
		masked_values = maskoceans(self.lons, self.lats, self.values, inlands=mask_lakes, resolution=resolution, grid=grid_spacing)
		return MeshGridData(self.lons, self.lats, masked_values)

	def is_masked(self):
		"""
		:return:
			bool, whether grid is masked or not
		"""
		return hasattr(self.values, 'mask')

	def apply_mask(self, mask):
		"""
		Apply mask to grid

		:param mask:
			numpy bool array with same shape as grid
		"""
		assert mask.shape == self.values.shape
		self.values = np.ma.array(self.values, mask=mask)

	def mask_polygons(self, polygon_data, inside=True):
		"""
		Mask grid according to given polygon(s)

		:param polygon_data:
			instance of :class:`PolygonData` or :class:`MultiPolygonData`
		:param inside:
			bool, whether grid should be masked inside or outside of polygon
			(default: True)

		:return:
			None, mask will be applied in-place
		"""
		ogr_polygon_data = polygon_data.to_ogr_geom()
		if inside:
			mask = np.zeros_like(self.values, dtype=np.bool)
		else:
			mask = np.ones_like(self.values, dtype=np.bool)
		mpt = self.to_multi_point_data()
		ogr_mpt = mpt.to_ogr_geom()
		ogr_intersection = ogr_mpt.Intersection(ogr_polygon_data)
		if ogr_intersection:
			intersection = MultiPointData.from_ogr(ogr_intersection)
			for pt in intersection:
				row = int(round((pt.lat - self.lat0) / self.dlat))
				col = int(round((pt.lon - self.lon0) / self.dlon))
				if inside:
					mask[row, col] = True
				else:
					mask[row, col] = False

		self.apply_mask(mask)

	def set_mask_from_distance_to_data_points(self, data_points, max_dist):
		"""
		Mask grid depending on minimum distance to data points

		:param data_points:
			instance of :class:`MultiPointData` or :class:`UnstructuredGrid`
		:param max_dist:
			float, maximum distance to consider as valid grid cell
			Grid cells with larger minimum distance to data points
			will be masked
			If :param:`data_points` is instance of :class:`MultiPointData`,
			distance is expressed in meters
			If :param:`data_points` is instance of :class:`UnstructuredGrid`,
			distance is expressed in fractional degrees latitude

		:return:
			None, mask will be applied in-place
		"""
		from mapping.geotools.geodetic import spherical_distance
		mask = np.zeros_like(self.values, dtype=np.bool)
		if isinstance(data_points, MultiPointData):
			for r in range(self.nrows):
				for c in range(self.ncols):
					lon, lat = self.lons[r,c], self.lats[r,c]
					distances = spherical_distance(lon, lat, data_points.lons, data_points.lats)
					if np.min(distances) >= max_dist:
						mask[r,c] = True
		elif isinstance(data_points, UnstructuredGridData):
			## max_dist is distance in degrees
			max_lon_dist = max_dist / np.cos(np.radians(max_dist))
			for r in range(self.nrows):
				for c in range(self.ncols):
					lon, lat = self.lons[r,c], self.lats[r,c]
					extent = (lon - max_lon_dist, lon + max_lon_dist,
							lat - max_dist, lat + max_dist)
					close_data_points = data_points.confine_to_extent(extent)
					if len(close_data_points) == 0:
						mask[r,c] = True

		self.apply_mask(mask)

	def reproject(self, target_srs):
		pass

	def interpolate(self, xout, yout, srs=None, checkbounds=False, masked=True,
					order=1):
		"""
		Interpolate grid.
		Note: masked values will be replaced with NaN values

		:param xout:
			array, X coordinates in native SRS or :param:`srs`
		:param yout:
			array, Y coordinates in native SRS or :param:`srs`
		:param srs:
			osr SpatialReference object, SRS of output coordinates
			(default: None)
		:param checkbounds:
			bool, whether or not values of xout and yout are checked
			to see that they are within the range of the grid. If True,
			points falling outside the grid are masked if :param:`masked`
			is True, else they are clipped to the boundary of the grid
			(default: False)
		:param masked:
			bool, whether or not points outside the range of the grid
			are masked
			(default: True)
		:param order:
			int, type of interpolation, 0=nearest neighbor, 1=bilinear,
			3=cubic spline
			(default: 1)

		:return:
			array, interpolated grid values
		"""
		## Check scipy.interpolate.Rbf for additional interpolation methods
		from mpl_toolkits.basemap import interp
		from mapping.geotools.coordtrans import transform_mesh_coordinates

		## xin, yin must be linearly increasing
		values = self.values
		if self.lon0 < self.lon1:
			xin = np.linspace(self.lon0, self.lon1, self.ncols)
		else:
			xin = np.linspace(self.lon1, self.lon0, self.ncols)
			values = values[:,::-1]
		if self.lat0 < self.lat1:
			yin = np.linspace(self.lat0, self.lat1, self.nrows)
		else:
			yin = np.linspace(self.lat1, self.lat0, self.nrows)
			values = values[::-1,:]

		## Transform output coordinates to lon/lat coordinates if necessary
		if srs and srs != self.srs:
			xout, yout = transform_mesh_coordinates(self.srs, WGS84, xout, yout)

		out_data = interp(values, xin, yin, xout, yout, checkbounds=checkbounds,
							masked=masked, order=order)
		if hasattr(out_data, 'mask'):
			out_data = out_data.filled(np.nan)

		return out_data

	def calc_hillshade(self, azimuth, elevation_angle, scale=1.):
		"""
		Compute hillshading

		:param azimuth:
			float, azimuth of light source in degrees
		:param elevation_angle:
			float, elevation angle of light source in degrees
		:param scale:
			float, multiplication factor to apply (default: 1.)
		"""

		"""
		## Source: http://rnovitsky.blogspot.com.es/2010/04/using-hillshade-image-as-intensity.html
		az = np.radians(azimuth)
		elev = np.radians(elevation_angle)
		data = self.values[::-1]

		## Gradient in x and y directions
		dx, dy = np.gradient(data * float(scale))
		slope = 0.5 * np.pi - np.arctan(np.hypot(dx, dy))
		aspect = np.arctan2(dx, dy)
		shade = np.sin(elev) * np.sin(slope) + np.cos(elev) * np.cos(slope) * np.cos(-az - aspect - 0.5*np.pi)
		## Normalize
		shade = (shade - np.nanmin(shade))/(np.nanmax(shade) - np.nanmin(shade))
		shade = shade[::-1]
		"""

		from matplotlib.colors import LightSource
		ls = LightSource(azimuth, elevation_angle)
		# TODO: look into vertical exaggeration with true dx and dy

		if hasattr(self, 'dx'):
			shade = ls.hillshade(self.values, dx=np.sign(self.dx), dy=-np.sign(self.dy))
		else:
			shade = ls.hillshade(self.values, dx=np.sign(self.dlon), dy=-np.sign(self.dlat))

		## Eliminate nan values, they result in black when blended
		# TODO: maybe these values should be masked or made transparent
		shade[np.isnan(shade)] = 0.5

		return shade

	def extract_contour_lines(self, levels):
		"""
		Extract contour lines from grid

		:param levels:
			list or array, contour line values

		:return:
			list with instances of :class:`MultiLineData`
		"""
		import matplotlib._cntr as cntr

		contour_engine = cntr.Cntr(self.lons, self.lats, self.values)
		contour_lines = []
		for level in levels:
			nlist = contour_engine.trace(level, level, 0)
			nseg = len(nlist) // 2
			segs = nlist[:nseg]
			contour_line = MultiLineData([], [])
			for seg in segs:
				cl = LineData(seg[:,0], seg[:,1], value=level)
				contour_line.append(cl)
			contour_lines.append(contour_line)
		return contour_lines

	def extract_contour_intervals(self, levels):
		"""
		Extract contour intervals from grid

		:param levels:
			list or array, contour line values

		:return:
			list with instances of :class:`MultiPolygonData`
		"""
		import numpy.ma as ma
		import matplotlib._contour as _contour

		values = ma.asarray(self.values)
		contour_engine = _contour.QuadContourGenerator(self.lons, self.lats,
												values.filled(), None, False, 0)
		contour_polygons = []
		for lower_level, upper_level in zip(levels[:-1], levels[1:]):
			segs, path_codes = contour_engine.create_filled_contour(lower_level, upper_level)
			contour_mpg = MultiPolygonData([], [])
			for i in range(len(segs)):
				seg = segs[i]
				path_code = path_codes[i]
				seg = np.split(seg, np.where(path_code == 1)[0][1:])
				for s, coords in enumerate(seg):
					if s == 0:
						lons, lats = coords[:,0], coords[:,1]
						interior_lons, interior_lats = [], []
					else:
						if coords.shape[0] > 2:
							interior_lons.append(coords[:,0])
							interior_lats.append(coords[:,1])
				contour_pg = PolygonData(lons, lats, interior_lons, interior_lats,
										lower_level)
				contour_mpg.append(contour_pg)
			contour_polygons.append(contour_mpg)
		return contour_polygons

	@classmethod
	def from_XYZ(cls, xyz_filespec, sep=',', num_header_lines=1, comment_char='#',
				dtype=np.float64):
		"""
		Create meshed grid from potentially unsorted XYZ file

		:param xyz_filespec:
			str, full path to XYZ file
		:param sep:
			char, character separating X, Y, Z values
			(default: ',')
		:param num_header_lines:
			int, number of header lines to skip
			(default: 1)
		:param comment_char:
			char, character indicating comment line
			(default: '#')

		:return:
			instance of :class:`MeshGridData`
		"""
		lons, lats, values = [], [], []
		for l, line in enumerate(open(xyz_filespec)):
			if l >= num_header_lines and line[0] != comment_char:
				lon, lat, val = line.split(';')
				lons.append(float(lon))
				lats.append(float(lat))
				values.append(dtype(val))

		grd_lons = sorted(np.unique(lons))
		grd_lats = sorted(np.unique(lats))
		mesh_lons, mesh_lats = np.meshgrid(grd_lons, grd_lats)
		mesh_values = np.zeros_like(mesh_lons)
		mesh_values[:] = np.nan

		lon0, lat0 = grd_lons[0], grd_lats[0]
		dlon = float(grd_lons[1] - grd_lons[0])
		dlat = float(grd_lats[1] - grd_lats[0])
		for i in range(len(values)):
			lon_idx = round(int((lons[i] - lon0) / dlon))
			lat_idx = round(int((lats[i] - lat0) / dlat))
			#[lon_idx] = np.argwhere(grd_lons == lons[i])
			#[lat_idx] = np.argwhere(grd_lats == lats[i])
			mesh_values[lat_idx, lon_idx] = values[i]

		return cls(mesh_lons, mesh_lats, mesh_values)

	def get_gdal_geotransform(self):
		"""
		Construct GDAL geotransform
		See http://lists.osgeo.org/pipermail/gdal-dev/2011-July/029449.html

		:return:
			6-element array
		"""
		## Note: for rotated grids
		#geotransform[0] = corner lon
		#geotransform[1] = cos(alpha)*(scaling)
		#geotransform[2] = -sin(alpha)*(scaling)
		#geotransform[3] = corner lat
		#geotransform[4] = sin(alpha)*(scaling)
		#geotransform[5] = cos(alpha)*(scaling)
		## where scaling maps pixel space to lat/lon space
		## and alpha denotes rotation to the East in radians

		geotransform = np.zeros(6, dtype='d')
		geotransform[0] = self.lon0 - self.dlon * 0.5	# top-left X
		geotransform[1] = self.dlon					# w-e pixel resolution
		geotransform[2] = 0							# rotation, 0 for north-up
		geotransform[3] = self.lat0 - self.dlat * 0.5	# top-left Y
		geotransform[4] = 0							# rotation, 0 for north-up
		geotransform[5] = self.dlat					# n-s pixel resolution
		return geotransform

	def export_gdal(self, driver_name, out_filespec, proj_info="EPSG:4326",
					nodata_value=np.nan):
		"""
		:param driver_name:
			str, name of driver supported by GDAL
		:param out_filespec:
			str, full path to output file
		:param proj_info:
			int (EPSG code), str (EPSG string or WKT) or osr SpatialReference
			object
			(default: "EPSG:4326" (= WGS84)
		"""
		from mapping.geotools.coordtrans import get_epsg_srs

		driver = gdal.GetDriverByName(driver_name)
		num_bands = 1
		dtype = self.values.dtype.type
		gdal_data_type = {
			np.byte: gdal.GDT_Byte,
			np.int8: gdal.GDT_Byte,
			np.int16: gdal.GDT_Int16,
			np.int32: gdal.GDT_Int32,
			np.float16: gdal.GDT_Float32,
			np.float32: gdal.GDT_Float32,
			np.float64: gdal.GDT_Float64,
			np.uint16: gdal.GDT_UInt16,
			np.uint32: gdal.GDT_UInt16}[dtype]
		ds = driver.Create(out_filespec, self.ncols, self.nrows, num_bands, gdal_data_type)
		ds.SetGeoTransform(self.get_gdal_geotransform())

		if isinstance(proj_info, int):
			wkt = get_epsg_srs(proj_info).ExportToWkt()
		elif isinstance(proj_info, basestring):
			if proj_info[:4].upper() == "EPSG":
				wkt = get_epsg_srs(proj_info).ExportToWkt()
			else:
				wkt = proj_info
		elif isinstance(proj_info, osr.SpatialReference):
			wkt = proj_info.ExportToWkt()
		ds.SetProjection(wkt)

		band = ds.GetRasterBand(1)
		band.WriteArray(self.values)
		band.SetNoDataValue(nodata_value)
		band.ComputeStatistics(False)
		band.SetUnitType(self.unit)
		band.FlushCache()

		return GdalRasterData(out_filespec)


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
	:param nodata_value:
		float, value indicating absence of data
		(default: None)
	:param unit:
		str, measurement unit of gridded values
		(default: "")
	:param bbox:
		list or tuple of floats: (llx, lly, urx, ury) in native coordinates
		(default: [], will use bounding box of dataset)
	:param region:
		list or tuple of floats: (lonmin, lonmax, latmin, latmax)
		that will be used to determine bbox
		(default: [])
	:param value_conversion:
		function to apply to stored grid values.
		Only applies if :param:`band_nr` is not null
		(default: None)
	"""
	def __init__(self, filespec, band_nr=1, down_sampling=1., nodata_value=None,
				unit="", bbox=[], region=[], value_conversion=None):
		self.filespec = filespec
		self.band_nr = band_nr
		self.read_grid_info()
		self.set_down_sampling(max(1, down_sampling))
		self.nodata_value = nodata_value
		if unit is None:
			self.unit = self.read_band_unit_type(self.band_nr)
		else:
			self.unit = unit

		if region:
			bbox = self.get_bbox_from_region(region)
		if not bbox:
			bbox = self.get_native_bbox()
		self.apply_bbox(bbox)

		self.value_conversion = value_conversion or (lambda x:x)

		## Store these when first computed to avoid computing more than once
		self._edge_lons = None
		self._edge_lats = None
		self._center_lons = None
		self._center_lats = None

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

	## Following methods are based on:
	## http://stackoverflow.com/questions/20488765/plot-gdal-raster-using-matplotlib-basemap

	def read_grid_info(self):
		"""
		Read raster parameters.

		The following properties are set:
		- :prop:`srs`: instance of class osr.SpatialReference
		- :prop:`num_bands`: int, number of raster bands
		- :prop:`_ncols`, :prop:`_nrows`: int, number of raster columns
			and rows in native grid extent
		- :prop:`_dx`, :prop:`_dy`: int, cell size in X and Y direction
			in the native spatial reference system
		- :prop:`_x0`, :prop:`_x1`: float, extent in X direction in
			the native spatial reference system (center of grid cells)
		- :prop:`_y0`, :prop:`_y1`: float, extent in Y direction in
			the native spatial reference system (center of grid cells)
		"""
		ds = gdal.Open(self.filespec, gdal.GA_ReadOnly)
		self.srs = osr.SpatialReference()
		projection = ds.GetProjection()
		if projection:
			self.srs.ImportFromWkt(projection)
		else:
			self.srs = WGS84
			print("Warning: no spatial reference system defined, assuming WGS84!")
		self.num_bands = ds.RasterCount

		gt = ds.GetGeoTransform()
		# TODO: support rotated grids
		if gt[2] or gt[4]:
			print("Warning: rotation of GDAL rasters not supported yet!")
		self._ncols, self._nrows = ds.RasterXSize, ds.RasterYSize
		self._dx, self._dy = gt[1], gt[5]
		## (x0, y0) and (x1, y1) now correspond to cell centers
		self._x0 = gt[0] + self._dx * 0.5
		self._x1 = gt[0] + (self._dx * self._ncols) - self._dx * 0.5
		#if self.dx < 0:
			#xmin, xmax = xmax, xmin
			#self.dx = -self.dx
		self._y0 = gt[3] + self._dy * 0.5
		self._y1 = gt[3] + (self._dy * self._nrows) - self._dy * 0.5
		#if self.dy < 0:
		#ymin, ymax = ymax, ymin
			#self.dy = -self.dy

		ds = None

	def set_down_sampling(self, down_sampling):
		"""
		The following properties are set:
		- :prop:`down_sampling`: float, downsampling factor
		- :prop:`dx`, :prop:`dy`: int, cell size in X and Y direction
			in the native spatial reference system
		"""
		self.down_sampling = float(down_sampling)
		#self.x0 = self._x0 / down_sampling * down_sampling
		#self.x1 = self._x1 / down_sampling * down_sampling
		#self.y0 = self._y0 / down_sampling * down_sampling
		#self.y1 = self._y1 / down_sampling * down_sampling
		self.dx = self._dx * down_sampling
		self.dy = self._dy * down_sampling
		#self.ncols = int(abs((self.x0 - self.x1) / self.dx)) + 1
		#self.nrows = int(abs((self.y0 - self.y1) / self.dy)) + 1

	def get_native_bbox(self):
		return (self._x0, self._y0, self._x1, self._y1)

	def get_bbox(self):
		return (self.x0, self.y0, self.x1, self.y1)

	def adjust_bbox(self, bbox):
		"""
		Make sure bbox has same order as native bbox
		"""
		x0, y0, x1, y1 = bbox
		if np.sign(x0 - x1) != np.sign(self._x0 - self._x1):
			x0, x1 = x1, x0
		if np.sign(y0 - y1) != np.sign(self._y0 - self._y1):
			y0, y1 = y1, y0
		return (x0, y0, x1, y1)

	def align_bbox(self, bbox):
		"""
		Note: bbox must already be adjusted!
		Align x0 to native dx, (x1-x0) to dx
		"""
		x0, y0, x1, y1 = bbox
		if self._x1 > self._x0:
			x0 = max(self._x0, np.floor(x0 / self._dx) * self._dx)
			nx = min(np.ceil((x1 - x0) / self.dx), np.floor((self._x1 - x0) / self.dx))
			x1 = x0 + nx * self.dx
		else:
			x0 = min(self._x0, np.ceil(x0 / self._dx) * self._dx)
			nx = max(np.floor((x0 - x1) / self.dx), np.ceil((x0 - self._x1) / self.dx))
			x1 = x0 - nx * self.dx

		if self._y1 > self._y0:
			y0 = max(self._y0, np.floor(y0 / self._dy) * self._dy)
			ny = min(np.ceil((y1 - y0) / self.dy), np.floor((self._y1 - y0) / self.dy))
			y1 = y0 + ny * self.dy
		else:
			y0 = min(self._y0, np.ceil(y0 / self._dy) * self._dy)
			ny = max(np.floor((y0 - y1) / self.dy), np.ceil((y0 - self._y1) / self.dy))
			y1 = y0 - ny * self.dy

		return (x0, y0, x1, y1)

	def apply_bbox(self, bbox):
		"""
		Apply bounding box

		The following properties are set:
		- :prop:`ncols`, :prop:`nrows`: int, number of raster columns
			and rows in native grid extent
		- :prop:`x0`, :prop:`x1`: float, extent in X direction in
			the native spatial reference system (center of grid cells)
		- :prop:`y0`, :prop:`y1`: float, extent in Y direction in
			the native spatial reference system (center of grid cells)
		"""
		bbox = self.align_bbox(self.adjust_bbox(bbox))
		self.x0, self.y0, self.x1, self.y1 = bbox
		#self.ncols = int(abs((self.x0 - self.x1) / self.dx)) + 1
		#self.nrows = int(abs((self.y0 - self.y1) / self.dy)) + 1

	@property
	def ncols(self):
		return int(round(abs((self.x0 - self.x1) / self.dx))) + 1

	@property
	def nrows(self):
		return int(round(abs((self.y0 - self.y1) / self.dy))) + 1

	def get_bbox_from_region(self, region, margin_fraction=1./20):
		from mapping.geotools.coordtrans import transform_coordinates

		srs = self.srs

		lonmin, lonmax, latmin, latmax = region
		lon_margin = (lonmax - lonmin) * margin_fraction
		lat_margin = (latmax - latmin) * margin_fraction
		coords_in = np.array([(lonmin-lon_margin, latmin-lat_margin),
					(lonmax+lon_margin, latmax+lat_margin)])
		if srs.ExportToWkt() == WGS84.ExportToWkt():
			coords = coords_in
		else:
			coords = transform_coordinates(WGS84, srs, coords_in)

		bbox = (list(np.floor(coords[0] / self._dx) * self._dx) +
				list(np.ceil(coords[1] / self._dy) * self._dy))
		return bbox

	def _get_x_index(self, x):
		"""
		Compute index of x coordinate in native X range

		:param x:
			float, X coordinate

		:return:
			int, index
		"""
		return int(round((x - self._x0) / self._dx))

	def _get_y_index(self, y):
		"""
		Compute index of y coordinate in native Y range

		:param y:
			float, Y coordinate

		:return:
			int, index
		"""
		return int(round((y - self._y0) / self._dy))

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
		from mapping.geotools.coordtrans import transform_mesh_coordinates

		## Create meshed coordinates
		if cell_registration == "center":
			xx, yy = np.meshgrid(np.linspace(self.x0, self.x1, self.ncols),
							np.linspace(self.y0, self.y1, self.nrows))
		elif cell_registration in ("corner", "edge"):
			xx, yy = np.meshgrid(np.linspace(self.x0 - self.dx/2., self.x1 + self.dx/2., self.ncols+1),
							np.linspace(self.y0 - self.dy/2., self.y1 + self.dy/2., self.nrows+1))

		## Convert from source projection to WGS84
		target_srs = WGS84
		lons, lats = transform_mesh_coordinates(self.srs, target_srs, xx, yy)
		if cell_registration == "corner":
			self._edge_lons, self._edge_lats = lons, lats
			self._center_lons, self._center_lats = None, None
		elif cell_registration == "center":
			self._edge_lons, self._edge_lats = None, None
			self._center_lons, self._center_lats = lons, lats
		return lons, lats

	def to_mesh_grid(self):
		"""
		Convert to regular MeshGridData

		:return:
			instance of :class:`MeshGridData`
		"""
		lons, lats = self.get_mesh_coordinates( cell_registration="center")
		values = self.values
		return MeshGridData(lons, lats, values, self.unit)

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
			return self.value_conversion(self.read_band(self.band_nr))
		else:
			return self.read_image_array()

	def read_band_unit_type(self, band_nr):
		"""
		Read unit type for a given raster band

		:param band_nr:
			int, raster band number (one-based)

		:return:
			str, unit type
		"""
		import gdal
		ds = gdal.Open(self.filespec, gdal.GA_ReadOnly)
		band = ds.GetRasterBand(band_nr)
		return band.GetUnitType()

	def read_band(self, band_nr):
		"""
		Read a particular raster band

		:param band_nr:
			int, raster band number (one-based)

		:return:
			2-D array containing raster data values
		"""
		# TODO: allow choosing between masking nodata values and replacing with NaNs
		import gdal
		ds = gdal.Open(self.filespec, gdal.GA_ReadOnly)
		band = ds.GetRasterBand(band_nr)
		if self.nodata_value is None:
			nodata = band.GetNoDataValue()
		else:
			nodata = self.nodata_value

		xoff = self._get_x_index(self.x0)
		yoff = self._get_y_index(self.y0)
		buf_xsize = self.ncols
		buf_ysize = self.nrows
		win_xsize = int(round(abs((self._x0 - self._x1) / self._dx))) + 1
		win_ysize = int(round(abs((self._y0 - self._y1) / self._dy))) + 1

		values = band.ReadAsArray(xoff=xoff, yoff=yoff, win_xsize=win_xsize,
				win_ysize=win_ysize, buf_xsize=buf_xsize, buf_ysize=buf_ysize)
		## Mask nodata values
		#values[np.isclose(values, nodata)] = np.nan
		if nodata != None:
			values = np.ma.array(values, mask=np.isclose(values, nodata))
			self.nodata_value = values.fill_value

		ds = None

		return values

	def read_image_array(self):
		"""
		Read raster data as truecolor (RGB[A]) image array

		:return:
			3-D (RGB[A], Y, X) float array
		"""
		# TODO: implement xoff, yoff, etc. as in read_band method
		import gdal
		ds = gdal.Open(self.filespec, gdal.GA_ReadOnly)
		#import matplotlib.image as mpimg
		#values = mpimg.imread(self.filespec)
		values = np.zeros((self.num_bands, self.nrows, self.ncols), dtype=np.uint8)
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

	def interpolate(self, xout, yout, srs=None, checkbounds=False, masked=True,
					order=1):
		"""
		Interpolate grid.
		Note: masked values will be replaced with NaN values

		:param xout:
			array, X coordinates in native SRS or :param:`srs`
		:param yout:
			array, Y coordinates in native SRS or :param:`srs`
		:param srs:
			osr SpatialReference object, SRS of output coordinates
			(default: None)
		:param checkbounds:
			bool, whether or not values of xout and yout are checked
			to see that they are within the range of the grid. If True,
			points falling outside the grid are masked if :param:`masked`
			is True, else they are clipped to the boundary of the grid
			(default: False)
		:param masked:
			bool, whether or not points outside the range of the grid
			are masked
			(default: True)
		:param order:
			int, type of interpolation, 0=nearest neighbor, 1=bilinear,
			3=cubic spline
			(default: 1)

		:return:
			array, interpolated grid values
		"""
		## Check scipy.interpolate.Rbf for additional interpolation methods
		from mpl_toolkits.basemap import interp
		from mapping.geotools.coordtrans import transform_mesh_coordinates

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

		## Transform output coordinates to native grid coordinates if necessary
		if srs and srs.ExportToWkt() != self.srs.ExportToWkt():
			xout, yout = transform_mesh_coordinates(srs, self.srs, xout, yout)

		if self.band_nr:
			## Single band
			out_data = interp(values, xin, yin, xout, yout, checkbounds=checkbounds,
								masked=masked, order=order)
			if hasattr(out_data, 'mask'):
				out_data = out_data.filled(np.nan)
		else:
			## RGB image
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

	def interpolate_grid(self, xout, yout, srs=None, checkbounds=False, masked=True, order=1):
		values = self.interpolate(xout, yout, srs=srs, checkbounds=checkbounds, masked=masked, order=order)
		return MeshGridData(xout, yout, values)

	def cross_section(self, xy0, xy1, num_points=100):
		"""
		Native coordinates!
		"""
		x0, y0 = xy0
		x1, y1 = xy1
		X = np.linspace(x0, x1, num_points)
		Y = np.linspace(y0, y1, num_points)
		## TODO: distances in km (take into account lon-lat rasters)
		return self.interpolate(X, Y)

	def warp_to_map(self, map, checkbounds=False, masked=True, order=1):
		from mapping.geotools.coordtrans import transform_mesh_coordinates

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
	def __init__(self, grdx, grdy, unit=""):
		self.grdx = grdx
		self.grdy = grdy
		self.unit = unit

	@classmethod
	def from_vx_filespec(self, vx_filespec, band_nr=1, down_sampling=1., nodata_value=None, unit=""):
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
		grdx = GdalRasterData(vx_filespec, band_nr=band_nr, down_sampling=down_sampling, nodata_value=nodata_value)
		grdy = GdalRasterData(vy_filespec, band_nr=band_nr, down_sampling=down_sampling, nodata_value=nodata_value)
		return MeshGridVectorData(grdx, grdy, unit=unit)
		# TODO: nodata_value?

	@classmethod
	def from_azimuths(self, lons, lats, azimuths, unit=""):
		"""
		Construct from meshed azimuth array

		:param lons:
			2-D array, meshed longitudes
		:param lats:
			2-D array, meshed latitudes
		:param azimuths:
			2-D array, meshed azimuths

		:return:
			instance of :class:`MeshGridVectorData`
		"""
		vx = MeshGridData(lons, lats, np.sin(np.radians(azimuths)))
		vy = MeshGridData(lons, lats, np.cos(np.radians(azimuths)))
		return MeshGridVectorData(vx, vy, unit=unit)


class WCSData(GdalRasterData):
	"""
	:param url:
		str, base URL of WCS server
	:param layer_name:
		str, name of requested dataset on WCS server
	:param down_sampling:
		float > 1, factor for downsampling, i.e. to divide number of columns and
		rows with
		(default: 1., no downsampling)
	:param resolution:
		float or tuple of floats, resolution in units of dataset's SRS
		(default: None)
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
	def __init__(self, url, layer_name, down_sampling=1, resolution=None, band_nr=1, bbox=[], region=[],
				wcs_version='1.0.0', verbose=True):
		self.url = url
		self.layer_name = layer_name

		## Query server for some information
		self.wcs_version = wcs_version
		self.wcs = self.init_wcs(verbose=verbose)

		if resolution:
			dx, dy = self.get_native_cellsize()
			if isinstance(resolution, (int, float)):
				resolution = (resolution, resolution)
				down_sampling = min(resolution[0] / dx, resolution[1] / dy)
		self.down_sampling = max(1, down_sampling)
		self.band_nr = band_nr

		## Set bounding box
		if region:
			bbox = self.get_bbox_from_region(region)
		elif not bbox:
			bbox = self.get_native_bbox()
		self.bbox = self.add_margin_to_bbox(bbox)

		## Read coverage
		import urllib

		response = self.get_coverage(self.layer_name)
		if verbose:
			if PY2:
				unquote_func = urllib.unquote
			else:
				import urllib.parse
				unquote_func = urllib.parse.unquote
			print(unquote_func(response.geturl()))

		#import tempfile
		#fd = tempfile.NamedTemporaryFile(suffix=".tif")
		#fd.write(response.read())
		#fd.close()
		#super(WCSData, self).__init__(fd.name, band_nr=band_nr, down_sampling=1)

		try:
			super(WCSData, self).__init__(response.geturl(), band_nr=band_nr,
									down_sampling=1)
		except:
			print(response.read())
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
			print(sorted(wcs.contents.keys()))
		return wcs

	def get_coverage_info(self, layer_name):
		"""
		Get coordinate system and bounding box for a particular coverage

		:param layer_name:
			str, name of requested dataset on WCS server

		:return:
			(crs, bbox, (dx, dy)) tuple
		"""
		coverage = self.wcs[layer_name]
		crs = coverage.supportedCRS[0]
		bbox = coverage.boundingboxes[0]['bbox']
		dx = np.abs(float(coverage.grid.offsetvectors[0][0]))
		dy = np.abs(float(coverage.grid.offsetvectors[1][1]))
		return (crs, bbox, (dx, dy))

	def get_crs(self):
		coverage = self.wcs[self.layer_name]
		crs = coverage.supportedCRS[0]
		return crs

	def get_native_srs(self):
		"""
		Read native Spatial Reference System

		:return:
			osr SpatialReference object
		"""
		from mapping.geotools.coordtrans import get_epsg_srs

		crs = self.get_crs()
		if crs.authority == 'EPSG':
			srs = get_epsg_srs(crs.getcode())
			return srs

	def get_native_cellsize(self):
		"""
		Read native cellsize

		:return:
			(dx, dy) tuple
		"""
		coverage = self.wcs[self.layer_name]
		dx = np.abs(float(coverage.grid.offsetvectors[0][0]))
		dy = np.abs(float(coverage.grid.offsetvectors[1][1]))
		return (dx, dy)

	def get_native_bbox(self):
		"""
		Read native bounding box

		:return:
			(llx, lly, urx, ury) tuple in native coordinates
		"""
		coverage = self.wcs[self.layer_name]
		bbox = coverage.boundingboxes[0]['bbox']
		return bbox

	def get_bbox_from_region(self, region, margin_fraction=1./20):
		"""
		Get bounding box in native coordinates from region in geographic
		coordinates

		:param region:
			list or tuple of floats: (lonmin, lonmax, latmin, latmax)
		:param margin_fraction:
			float, fraction of map range to add to region extent to
			ensure extracted grid covers entire region
			(default: 1./20)

		:return:
			list or tuple of floats: (llx, lly, urx, ury)
			bbox in native coordinates
		"""
		from mapping.geotools.coordtrans import transform_coordinates

		srs = self.get_native_srs()
		if not srs:
			crs = self.get_crs()
			raise Exception("CRS %s not supported!" % crs.getcode())

		lonmin, lonmax, latmin, latmax = region
		lon_margin = (lonmax - lonmin) * margin_fraction
		lat_margin = (latmax - latmin) * margin_fraction
		coords_in = [(lonmin-lon_margin, latmin-lat_margin),
					(lonmax+lon_margin, latmax+lat_margin)]
		coords = transform_coordinates(WGS84, srs, coords_in)

		resx, resy = self.resx, self.resy
		bbox = (list(np.floor(coords[0] / resx) * resx) +
				list(np.ceil(coords[1] / resy) * resy))
		return bbox

	def add_margin_to_bbox(self, bbox):
		"""
		Add margin of one cell spacing around bounding box

		:param bbox:
			(llx, lly, urx, ury) tuple

		:return:
			(llx, lly, urx, ury) tuple
		"""
		native_bbox = self.get_native_bbox()
		resx, resy = self.resx, self.resy
		llx, lly, urx, ury = bbox
		llx = max(native_bbox[0], llx - resx)
		urx = min(native_bbox[2], urx + resx)
		lly = max(native_bbox[1], lly - resy)
		ury = min(native_bbox[3], ury + resy)
		return (llx, lly, urx, ury)

	def get_coverage(self, layer_name):
		"""
		Fetch coverage from server

		:param layer_name:
			str, name of requested dataset on WCS server

		:return:
			instance of :class:`owslib.util.ResponseWrapper`
		"""
		width, height = None, None
		try:
			crs = self.get_crs()
		except:
			crs_code = "EPSG:31370"
		else:
			crs_code = crs.getcode()

		format = "GeoTIFF"
		return self.wcs.getCoverage(identifier=self.layer_name, width=width,
					height=height, resx=self.resx, resy=self.resy, bbox=self.bbox,
					format=format, crs=crs_code)

	def to_gdal_raster_data(self, verbose=True):
		"""
		Convert to GDAL raster

		:param verbose:
			bool, whether or not to print some information

		:return:
			instance of :class:`GdalRasterData`
		"""
		## Read coverage
		import urllib

		response = self.get_coverage(self.layer_name)
		if verbose:
			print(urllib.unquote(response.geturl()))

		#import tempfile
		#fd = tempfile.NamedTemporaryFile(suffix=".tif")
		#fd.write(response.read())
		#fd.close()
		#super(WCSData, self).__init__(fd.name, band_nr=band_nr, down_sampling=1)

		try:
			data = GdalRasterData(response.geturl(), band_nr=self.band_nr,
									down_sampling=1)
		except:
			print(response.read())
			raise
		else:
			return data

	@property
	def resx(self):
		return self.get_native_cellsize()[0] * self.down_sampling

	@property
	def resy(self):
		return self.get_native_cellsize()[1] * self.down_sampling
