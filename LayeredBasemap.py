"""
Generic wrapper for creating maps with Basemap
"""

import datetime
import numpy as np
import matplotlib
from mpl_toolkits.basemap import Basemap
import pylab
import shapely
import shapely.geometry

from mapping.geo.readGIS import read_GIS_file


## Styles
class TextStyle:
	def __init__(self, font_family="sans-serif", font_size=12, font_weight="normal", font_style="normal", font_stretch="normal", font_variant="normal", color='k', background_color=None, line_spacing=12, rotation=0, horizontal_alignment="center", vertical_alignment="center", offset=(0,0), alpha=1.):
		self.font_family = font_family
		self.font_size = font_size
		self.font_weight = font_weight
		self.font_style = font_style
		self.font_stretch = font_stretch
		self.font_variant = font_variant
		self.color = color
		#self.background_color = background_color
		self.line_spacing = line_spacing
		self.rotation = rotation
		self.horizontal_alignment = horizontal_alignment
		self.vertical_alignment = vertical_alignment
		self.offset = offset
		self.alpha = alpha


class PointStyle:
	def __init__(self, shape='o', size=12, line_width=1, line_color='k', fill_color='None', label_style=None, alpha=1.):
		self.shape = shape
		self.size = size
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.label_style = label_style
		self.alpha = alpha


class LineStyle:
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', label_style=None, alpha=1.):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.label_style = label_style
		self.alpha = alpha


class PolygonStyle:
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', fill_color='y', fill_hatch=None, label_style=None, alpha=1.):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.fill_hatch = fill_hatch
		self.label_style = label_style
		self.alpha = alpha


class FocmecStyle:
	def __init__(self, line_width=1, line_color='k', fill_color='k', bg_color='w', alpha=1.):
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.bg_color = bg_color
		self.alpha = alpha


class CompositeStyle:
	def __init__(self, point_style=None, line_style=None, polygon_style=None, text_style=None, grid_style=None):
		self.point_style = point_style
		self.line_style = line_style
		self.polygon_style = polygon_style
		self.text_style = text_style
		self.grid_style = grid_style


class ThematicStyle(object):
	def __init__(self, value_key=None):
		self.value_key = value_key

	def apply_value_key(self, values):
		if self.value_key == None:
			return values
		else:
			return values[self.value_key]


class ThematicStyleDict(ThematicStyle):
	def __init__(self, style_dict, value_key=None):
		super(ThematicStyleDict, self).__init__(value_key)
		self.style_dict = style_dict

	def __call__(self, values):
		"""
		values can be numbers or strings
		"""
		return [self.style_dict[val] for val in self.apply_value_key(values)]


class ThematicStyleRanges(ThematicStyle):
	def __init__(self, bin_edges, bin_values, value_key=None):
		"""
		bin_edges must be monotonically increasing or decreasing
		bin_values may be colors
		"""
		super(ThematicStyleRanges, self).__init__(value_key)
		self.bin_edges = bin_edges
		self.bin_values = bin_values

	def __call__(self, values):
		"""
		values must be numbers
		"""
		bin_indexes = np.digitize(self.apply_value_key(values), self.bin_edges) - 1
		return [self.bin_values[bi] for bi in bin_indexes]


class ThematicStyleGradient(ThematicStyle):
	def __init__(self, in_values, out_values, value_key=None):
		"""
		in_values must be monotonically increasing or decreasing
		out_values must be numbers too
		"""
		super(ThematicStyleGradient, self).__init__(value_key)
		self.in_values = in_values
		self.out_values = out_values

	def __call__(self, values):
		return np.interp(self.apply_value_key(values), self.in_values, self.out_values)


class ThematicStyleColormap(ThematicStyle):
	def __init__(self, color_map="jet", norm=None, vmin=None, vmax=None, alpha=1.0, value_key=None):
		super(ThematicStyleColormap, self).__init__(value_key)
		self.color_map = color_map
		self.norm = norm
		self.vmin = vmin
		self.vmax = vmax
		self.alpha = alpha
		#TODO set alpha in self.color_map  ??

	def __call__(self, values):
		from matplotlib.cm import ScalarMappable
		sm = ScalarMappable(self.color_map, self.norm)
		sm.set_clim(self.vmin, self.vmax)
		return sm.to_rgba(self.apply_value_key(values), alpha=self.alpha)


class GridStyle:
	# TODO
	def __init__(self, color_map_theme=ThematicStyleColormap("jet"), continuous=True, line_style=None, contour_levels=[], label_format='%.2f'):
		self.color_map_theme = color_map_theme
		self.continuous = continuous
		self.line_style = line_style
		self.contour_levels = contour_levels
		self.label_format = label_format


## Data types
class BuiltinData:
	def __init__(self, feature="continents", **kwargs):
		assert feature in ("bluemarble", "coastlines", "continents", "countries", "nightshade", "rivers", "shadedrelief"), "%s not recognized as builtin data" % feature
		self.feature = feature
		for key, val in kwargs.items():
			setattr(self, key, val)


class PointData():
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

	@classmethod
	def from_wkt(self, wkt):
		pt = shapely.geometry.Point(shapely.wkt.loads(wkt))
		return PointData(pt.x, pt.y)

	@classmethod
	def from_ogr(self, geom):
		return self.from_wkt(geom.ExportToWkt())


class MultiPointData():
	def __init__(self, lons, lats, values=[], labels=[]):
		self.lons = lons
		self.lats = lats
		self.values = values
		self.labels = labels

	def __len__(self):
		return len(self.lons)

	def __iter__(self):
		for i in range(len(self.lons)):
			yield self.__getitem__(i)

	def __getitem__(self, index):
		lon = self.lons[index]
		lat = self.lats[index]
		# TODO: does this work with values with different value_keys??
		try:
			value = self.values[index]
		except:
			value = None
		try:
			label = self.labels[index]
		except:
			label = ""
		return PointData(lon, lat, value, label)

	def append(self, pt):
		assert isinstance(pt, PointData)
		self.lons.append(pt.lon)
		self.lats.append(pt.lat)
		if pt.value:
			self.values.append(pt.value)
		if pt.label:
			self.labels.append(pt.label)

	def to_shapely(self):
		return shapely.geometry.MultiPoint(zip(self.lons, self.lats))

	def to_wkt(self):
		return self.to_shapely().wkt

	@classmethod
	def from_wkt(self, wkt):
		mp = shapely.geometry.MultiPoint(shapely.wkt.loads(wkt))
		return MultiPointData([pt.x for pt in mp], [pt.y for pt in mp])

	@classmethod
	def from_ogr(self, geom):
		return self.from_wkt(geom.ExportToWkt())

	def get_centroid(self):
		centroid = self.to_shapely().centroid
		return PointData(centroid.x, centroid.y)


class LineData():
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
	def from_wkt(self, wkt):
		ls = shapely.geometry.LineString(shapely.wkt.loads(wkt))
		lons, lats = zip(*ls.coords)
		return LineData(lons, lats)

	@classmethod
	def from_ogr(self, geom):
		return self.from_wkt(geom.ExportToWkt())

	def get_midpoint(self):
		ls = self.to_shapely()
		midPoint = ls.interpolate(ls.length/2)
		return PointData(midPoint.x, midPoint.y)

	def get_centroid(self):
		centroid = self.to_shapely().centroid
		return PointData(centroid.x, centroid.y)


class MultiLineData():
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
		assert isinstance(line, LineData)
		self.lons.append(line.lons)
		self.lats.append(line.lats)
		if line.value:
			self.values.append(line.value)
		if line.label:
			self.labels.append(line.label)

	def to_shapely(self):
		coords = [zip(self.lons[i], self.lats[i]) for i in range(len(lons))]
		return shapely.geometry.MultiLineString(coords)

	def to_wkt(self):
		return self.to_shapely().wkt

	@classmethod
	def from_wkt(self, wkt):
		mls = shapely.geometry.MultiLineString(shapely.wkt.loads(wkt))
		lons, lats =  [], []
		for ls in mls:
			x, y = zip(*ls.coords)
			lons.append(x)
			lats.append(y)
		yield MultiLineData(lons, lats)

	@classmethod
	def from_ogr(self, geom):
		return self.from_wkt(geom.ExportToWkt())


class PolygonData():
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
	def from_wkt(self, wkt):
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
	def from_ogr(self, geom):
		return self.from_wkt(geom.ExportToWkt())

	def get_centroid(self):
		centroid = self.to_shapely().centroid
		return PointData(centroid.x, centroid.y)


class MultiPolygonData():
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
	def from_wkt(self, wkt):
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
	def from_ogr(self, geom):
		return self.from_wkt(geom.ExportToWkt())


class FocmecData(MultiPointData):
	pass


class MaskData:
	def __init__(self, polygon, outside=True):
		self.polygon = polygon
		self.outside = outside


class CompositeData:
	def __init__(self, points=None, lines=[], polygons=[], texts=[]):
		self.points = points
		self.lines = lines
		self.polygons = polygons
		self.texts = texts


class GridData:
	def __init__(self, lons, lats, values):
		self.lons = lons
		self.lats = lats
		self.values = values


class GisData:
	def __init__(self, filespec, label_colname=None):
		self.filespec = filespec
		self.label_colname = label_colname


class MapLayer:
	def __init__(self, data, style, legend_label="_nolegend_"):
		self.data = data
		self.style = style
		self.legend_label = legend_label


class LayeredBasemap:
	def __init__(self, layers, region, projection, title, origin=(None, None), grid_interval=(None, None), resolution="i", annot_axes="SE", legend_location=0):
		#TODO: width, height
		self.layers = layers
		self.region = region
		self.projection = projection
		self.title = title
		self.origin = origin
		self.grid_interval = grid_interval
		self.resolution = resolution
		self.annot_axes = annot_axes
		self.legend_location = legend_location
		self.map = self.init_basemap()
		self.ax = pylab.gca()
		#self.draw()

	#@property
	#def ax(self):
	#	return pylab.gca()

	@property
	def llcrnrlon(self):
		return self.region[0]

	@property
	def urcrnrlon(self):
		return self.region[1]

	@property
	def llcrnrlat(self):
		return self.region[2]

	@property
	def urcrnrlat(self):
		return self.region[3]

	@property
	def lon_0(self):
		return self.origin[0]

	@property
	def lat_0(self):
		return self.origin[1]

	@property
	def dlon(self):
		return self.grid_interval[0]

	@property
	def dlat(self):
		return self.grid_interval[1]

	def init_basemap(self):
		self.zorder = 0
		llcrnrlon, urcrnrlon, llcrnrlat, urcrnrlat = self.region
		lon_0, lat_0 = self.origin
		if lon_0 is None:
			lon_0 = (llcrnrlon + urcrnrlon) / 2.
		if lat_0 is None:
			lat_0 = (llcrnrlat + urcrnrlat) / 2.
		self.origin = (lon_0, lat_0)

		map = Basemap(projection=self.projection, resolution=self.resolution, llcrnrlon=self.llcrnrlon, llcrnrlat=self.llcrnrlat, urcrnrlon=self.urcrnrlon, urcrnrlat=self.urcrnrlat, lon_0=self.lon_0, lat_0=self.lat_0)
		return map

	## Drawing primitives

	def _draw_points(self, points, style, legend_label="_nolegend_"):
		x, y = self.map(points.lons, points.lats)
		if isinstance(style.size, ThematicStyle) or isinstance(style.line_width, ThematicStyle) or isinstance(style.line_color, ThematicStyle) or isinstance(style.fill_color, ThematicStyle):
			cmap, norm, vmin, vmax = None, None, None, None
			if isinstance(style.size, ThematicStyle):
				sizes = style.size(points.values)
			else:
				sizes = style.size
			sizes = np.power(sizes, 2)
			if isinstance(style.line_width, ThematicStyle):
				line_widths = style.line_width(points.values)
			else:
				line_widths = style.line_width
			## Note: only one of line_color / fill_color may be a ThematicStyleColormap
			## Note: thematic line_color only works for markers like '+'
			## thematic fill_color only works for markers like '-'
			assert not (isinstance(style.line_color, ThematicStyle) and isinstance(style.fill_color, ThematicStyle)), "Only one of line_color and fill_color may be ThematicStyle!"
			if isinstance(style.line_color, ThematicStyle):
				line_colors = None
				if isinstance(style.line_color, ThematicStyleColormap):
					c = style.line_color.apply_value_key(points.values)
					cmap = style.line_color.color_map
					norm = style.line_color.norm
					vmin, vmax = style.line_color.vmin, style.line_color.vmax
				elif isinstance(style.line_color, (ThematicStyleDict, ThematicStyleRanges)):
					color_conv = matplotlib.colors.ColorConverter()
					c = style.line_color(points.values)
					c = color_conv.to_rgba_array(c)
			else:
				line_colors = style.line_color
			if isinstance(style.fill_color, ThematicStyle):
				fill_colors = None
				if isinstance(style.fill_color, ThematicStyleColormap):
					c = style.fill_color.apply_value_key(points.values)
					cmap = style.fill_color.color_map
					norm = style.fill_color.norm
					vmin, vmax = style.fill_color.vmin, style.fill_color.vmax
				elif isinstance(style.fill_color, (ThematicStyleDict, ThematicStyleRanges)):
					color_conv = matplotlib.colors.ColorConverter()
					c = style.fill_color(points.values)
					c = color_conv.to_rgba_array(c)
			else:
				## Note: this is not used at the moment
				fill_colors = style.fill_color

			self.map.scatter(x, y, marker=style.shape, s=sizes, c=c, edgecolors=line_colors, linewidths=line_widths, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, label=legend_label, alpha=style.alpha, zorder=self.zorder)
		else:
			self.map.plot(x, y, marker=style.shape, ms=style.size, mfc=style.fill_color, mec=style.line_color, mew=style.line_width, ls="None", lw=0, label=legend_label, alpha=style.alpha, zorder=self.zorder)

	def _draw_line(self, line, style, legend_label="_nolegend_"):
		x, y = self.map(line.lons, line.lats)
		self.map.plot(x, y, ls=style.line_pattern, lw=style.line_width, color=style.line_color, label=legend_label, alpha=style.alpha, zorder=self.zorder)

	def _draw_polygon(self, polygon, style, legend_label="_nolegend_"):
		if len(polygon.interior_lons) == 0:
			x, y = self.map(polygon.lons, polygon.lats)
			self.ax.fill(x, y, ls=style.line_pattern, lw=style.line_width, ec=style.line_color, fc=style.fill_color, hatch=style.fill_hatch, label=legend_label, alpha=style.alpha, zorder=self.zorder)
		else:
			## Complex polygon with holes
			exterior_x, exterior_y = self.map(polygon.lons, polygon.lats)
			interior_x, interior_y = [], []
			for i in range(len(polygon.interior_lons)):
				x, y = self.map(polygon.interior_lons[i], polygon.interior_lats[i])
				interior_x.append(x)
				interior_y.append(y)
			if style.fill_color in (None, 'None', 'none'):
				self.map.plot(exterior_x, exterior_y, ls=style.line_pattern, lw=style.line_width, color=style.line_color, label=legend_label, alpha=style.alpha, zorder=self.zorder)
				for x, y in zip(interior_x, interior_y):
					self.map.plot(x, y, ls=style.line_pattern, lw=style.line_width, color=style.line_color, label="_nolegend_", alpha=style.alpha, zorder=self.zorder)
			else:
				from descartes.patch import PolygonPatch
				proj_polygon = PolygonData(exterior_x, exterior_y, interior_x, interior_y).to_shapely()
				## Make sure exterior and interior rings of polygon are properly oriented
				proj_polygon = shapely.geometry.polygon.orient(proj_polygon)
				patch = PolygonPatch(proj_polygon, fill=1, ls=style.line_pattern, lw=style.line_width, ec=style.line_color, fc=style.fill_color, hatch=style.fill_hatch, label=legend_label, alpha=style.alpha)
				patch.set_zorder(self.zorder)
				print self.ax
				self.ax.add_patch(patch)

	def _draw_texts(self, text_points, style):
		# TODO: offset
		x, y = self.map(text_points.lons, text_points.lats)
		for i, label in enumerate(text_points.labels):
			self.ax.text(x[i], y[i], label, family=style.font_family, size=style.font_size, weight=style.font_weight, style=style.font_style, stretch=style.font_stretch, variant=style.font_variant, color=style.color, linespacing=style.line_spacing, rotation=style.rotation, ha=style.horizontal_alignment, va=style.vertical_alignment, alpha=style.alpha, zorder=self.zorder)

	def draw_polygon_layer(self, polygon_data, polygon_style, legend_label="_nolegend_"):
		"""
		polygon_data: MultiPolygon
		"""
		num_polygons = len(polygon_data)
		if isinstance(polygon_style.line_pattern, ThematicStyle):
			line_patterns = polygon_style.line_pattern(polygon_data.values)
		else:
			line_patterns = [polygon_style.line_pattern] * num_polygons
		if isinstance(polygon_style.line_width, ThematicStyle):
			line_widths = polygon_style.line_width(polygon_data.values)
		else:
			line_widths = [polygon_style.line_width] * num_polygons
		if isinstance(polygon_style.line_color, ThematicStyle):
			line_colors = polygon_style.line_color(polygon_data.values)
		else:
			line_colors = [polygon_style.line_color] * num_polygons
		if isinstance(polygon_style.fill_color, ThematicStyle):
			fill_colors = polygon_style.fill_color(polygon_data.values)
		else:
			fill_colors = [polygon_style.fill_color] * num_polygons
		if isinstance(polygon_style.fill_hatch, ThematicStyle):
			fill_hatches = polygon_style.fill_hatch(polygon_data.values)
		else:
			fill_hatches = [polygon_style.fill_hatch] * num_polygons

		for i, polygon in enumerate(polygon_data):
			legend_label = {True: legend_label, False: "_nolegend_"}[i==0]
			## Apply thematic styles
			line_pattern = line_patterns[i]
			line_width = line_widths[i]
			line_color = line_colors[i]
			fill_color = fill_colors[i]
			fill_hatch = fill_hatches[i]
			style = PolygonStyle(line_pattern=line_pattern, line_width=line_width, line_color=line_color, fill_color=fill_color, fill_hatch=fill_hatch, label_style=None, alpha=polygon_style.alpha)
			self._draw_polygon(polygon, style, legend_label)
		self.zorder += 1
		if polygon_data.labels and polygon_style.label_style:
			centroids = MultiPointData([], [], labels=[])
			for pg in polygon_data:
				centroid = pg.get_centroid()
				centroids.lons.append(centroid.lon)
				centroids.lats.append(centroid.lat)
				centroids.labels.append(pg.label)
			self._draw_texts(centroids, polygon_style.label_style)
			self.zorder += 1

	def draw_line_layer(self, line_data, line_style, legend_label="_nolegend_"):
		"""
		line_data: MultiLine
		"""
		num_lines = len(line_data)
		if isinstance(line_style.line_pattern, ThematicStyle):
			line_patterns = line_style.line_pattern(polygon_data.values)
		else:
			line_patterns = [line_style.line_pattern] * num_lines
		if isinstance(line_style.line_width, ThematicStyle):
			line_widths = line_style.line_width(polygon_data.values)
		else:
			line_widths = [line_style.line_width] * num_lines
		if isinstance(line_style.line_color, ThematicStyle):
			line_colors = line_style.line_color(polygon_data.values)
		else:
			line_colors = [line_style.line_color] * num_lines

		for i, line in enumerate(line_data):
			legend_label = {True: legend_label, False: "_nolegend_"}[i==0]
			## Apply thematic styles
			line_pattern = line_patterns[i]
			line_width = line_widths[i]
			line_color = line_colors[i]
			style = LineStyle(line_pattern=line_pattern, line_width=line_width, line_color=line_color, label_style=None, alpha=line_style.alpha)
			self._draw_line(line, line_style, legend_label)
		self.zorder += 1
		if line_data.labels and line_style.label_style:
			midpoints = MultiPointData([], [], labels=[])
			for line in line_data:
				midpoint = line.get_midpoint()
				midpoints.lons.append(midpoint.lon)
				midpoints.lats.append(midpoint.lat)
				midpoints.labels.append(line.label)
			self._draw_texts(midpoints, line_style.label_style)
			self.zorder += 1

	def draw_point_layer(self, point_data, point_style, legend_label="_nolegend_"):
		self._draw_points(point_data, point_style, legend_label)
		self.zorder += 1
		if point_data.labels and point_style.label_style:
			self._draw_texts(point_data, point_style.label_style)
			self.zorder += 1

	def draw_composite_layer(self, point_data=[], point_style=None, line_data=[], line_style=None, polygon_data=[], polygon_style=None, text_data=[], text_style=None, legend_label={"points": "_nolegend_", "lines": "_nolegend_", "polygons": "_nolegend_"}):
		if polygon_data and len(polygon_data) > 0 and polygon_style:
			self.draw_polygon_layer(polygon_data, polygon_style, legend_label["polygons"])
		if line_data and len(line_data) > 0 and line_style:
			self.draw_line_layer(line_data, line_style, legend_label["lines"])
		if point_data and len(point_data) > 0 and point_style:
			self.draw_point_layer(point_data, point_style, legend_label["points"])
		if text_data and len(text_data) > 0 and text_style:
			self._draw_texts(text_data, text_style)

	def draw_gis_layer(self, gis_data, gis_style, legend_label={"points": "_nolegend_", "lines": "_nolegend_", "polygons": "_nolegend_"}):
		point_style = gis_style.point_style
		line_style = gis_style.line_style
		polygon_style = gis_style.polygon_style
		point_value_colnames = set()
		if point_style:
			if isinstance(point_style.size, ThematicStyle):
				point_value_colnames.add(point_style.size.value_key)
			if isinstance(point_style.line_color, ThematicStyle):
				point_value_colnames.add(point_style.line_color.value_key)
			elif isinstance(point_style.fill_color, ThematicStyle):
				point_value_colnames.add(point_style.fill_color.value_key)
		line_value_colnames = set()
		if line_style:
			if isinstance(line_style.line_pattern, ThematicStyle):
				line_value_colnames.add(line_style.line_pattern.value_key)
			if isinstance(line_style.line_width, ThematicStyle):
				line_value_colnames.add(line_style.line_width.value_key)
			if isinstance(line_style.line_color, ThematicStyle):
				line_value_colnames.add(line_style.line_color.value_key)
		polygon_value_colnames = set()
		if polygon_style:
			if isinstance(polygon_style.line_pattern, ThematicStyle):
				polygon_value_colnames.add(polygon_style.line_pattern.value_key)
			if isinstance(polygon_style.line_width, ThematicStyle):
				polygon_value_colnames.add(polygon_style.line_width.value_key)
			if isinstance(polygon_style.line_color, ThematicStyle):
				polygon_value_colnames.add(polygon_style.line_color.value_key)
			if isinstance(polygon_style.fill_color, ThematicStyle):
				polygon_value_colnames.add(polygon_style.fill_color.value_key)
			if isinstance(polygon_style.fill_hatch, ThematicStyle):
				polygon_value_colnames.add(polygon_style.fill_hatch.value_key)

		point_data = MultiPointData([], [], labels=[])
		point_data.values = {}
		for colname in point_value_colnames:
			point_data.values[colname] = []
		line_data = MultiLineData([], [])
		line_data.values = {}
		for colname in line_value_colnames:
			line_data.values[colname] = []
		polygon_data = MultiPolygonData([], [])
		polygon_data.values = {}
		for colname in polygon_value_colnames:
			polygon_data.values[colname] = []
		for rec in read_GIS_file(gis_data.filespec):
			label = rec.get(gis_data.label_colname)
			geom = rec['obj']
			geom_type = geom.GetGeometryName()
			# TODO: MultiPoint, MultiLineString, MultiPolygon
			if geom_type == "POINT":
				pt = PointData.from_ogr(geom)
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
				multi_polygon = MultiPolygonData.from_ogr(geom)
				for polygon in multi_polygon:
					polygon.label = label
					polygon_data.append(polygon)
					for colname in polygon_value_colnames:
						polygon_data.values[colname].append(rec[colname])


		self.draw_composite_layer(point_data=point_data, point_style=point_style, line_data=line_data, line_style=line_style, polygon_data=polygon_data, polygon_style=polygon_style, legend_label=legend_label)

	def draw_grid_layer(self, grid_data, grid_style, legend_label=""):
		# TODO: coloured contour lines
		x, y = self.map(grid_data.lons, grid_data.lats)
		cmap = grid_style.color_map_theme.color_map
		norm = grid_style.color_map_theme.norm
		vmin = grid_style.color_map_theme.vmin
		vmax = grid_style.color_map_theme.vmax
		alpha = grid_style.color_map_theme.alpha
		if grid_style.continuous == False:
			if isinstance(cmap, str):
				cmap_obj = getattr(matplotlib.cm, cmap)
			else:
				cmap_obj = cmap
			cs = self.map.contourf(x, y, grid_data.values, levels=grid_style.contour_levels, cmap=cmap_obj, norm=norm, vmin=vmin, vmax=vmax, extend="both", alpha=alpha, zorder=self.zorder)
		else:
			cs = self.map.pcolor(x, y, grid_data.values, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, alpha=alpha, zorder=self.zorder)
		if grid_style.line_style:
			line_style = grid_style.line_style
			cl = self.map.contour(x, y, grid_data.values, levels=grid_style.contour_levels, colors=line_style.line_color, linewidths=line_style.line_width, alpha=line_style.alpha, zorder=self.zorder)
			label_style = line_style.label_style
			# TODO: other font properties?
			self.ax.clabel(cl, colors='k', inline=True, fontsize=label_style.font_size, fmt=grid_style.label_format, alpha=label_style.alpha, zorder=self.zorder+1)
		# TODO: colorbar_style
		cbar = self.map.colorbar(cs, location='bottom', pad="10%", format='%.2f', spacing="uniform", ticks=grid_style.contour_levels)
		cbar.set_label(legend_label)
		self.zorder += 2

	def draw_continents(self, continent_style):
		if continent_style.fill_color or continent_style.bg_color:
			self.map.fillcontinents(color=continent_style.fill_color, lake_color=continent_style.fill_color, zorder=self.zorder)
			#self.map.drawlsmask(land_color=continent_style.fill_color, ocean_color=continent_style.fill_color, resolution=self.resolution, zorder=self.zorder)
		if continent_style.line_color:
			self.draw_coastlines(continent_style)
		self.zorder += 1

	def draw_coastlines(self, coastline_style):
		self.map.drawcoastlines(linewidth=coastline_style.line_width, color=coastline_style.line_color, zorder=self.zorder)
		self.zorder += 1

	def draw_countries(self, style):
		if style.line_color:
			self.map.drawcountries(linewidth=style.line_width, color=style.line_color, zorder=self.zorder)
			self.zorder += 1

	def draw_rivers(self, style):
		if style.line_color:
			## linestyle argument not supported by current version of basemap
			self.map.drawrivers(linewidth=style.line_width, color=style.line_color, zorder=self.zorder)
			self.zorder += 1

	def draw_nightshade(self, date_time, style, alpha=0.5):
		self.map.nightshade(date_time, color=style.fill_color, alpha=alpha, zorder=self.zorder)
		self.zorder += 1

	def draw_bluemarble(self, style=None):
		try:
			self.map.bluemarble(zorder=self.zorder)
		except:
			print("Bluemarble layer failed. This feature requires an internet connection")
		else:
			self.zorder += 1

	def draw_shadedrelief(self, style=None):
		try:
			self.map.shadedrelief(zorder=self.zorder)
		except:
			print("Shadedrelief layer failed. This feature requires an internet connection")
		else:
			self.zorder += 1

	def draw_etopo(self, style=None):
		try:
			self.map.etopo(zorder=self.zorder)
		except:
			print("Etopo layer failed. This feature requires an internet connection")
		else:
			self.zorder += 1

	def draw_focmecs(self, focmec_data, focmec_style):
		# TODO: (variable) size (width is in map units??)
		from obspy.imaging.beachball import Beach
		x, y = self.map(focmec_data.lons, focmec_data.lats)
		for i in range(len(focmec_data)):
			b = Beach(focmec_data.values[i], xy=(x[i], y[i]), width=50000, linewidth=focmec_style.line_width, edgecolor=focmec_style.line_color, facecolor=focmec_style.fill_color, bgcolor=focmec_style.bg_color, alpha=focmec_style.alpha)
			b.set_zorder(self.zorder)
			self.ax.add_collection(b)
		self.zorder += 1

	def draw_geotiff(self, tif_filespec):
		# TODO
		import gdal
		geo = gdal.Open("file.geotiff")
		ar = geo.ReadAsArray()

	def draw_mask(self, polygon, mask_style=None, outside=True):
		if not mask_style:
			mask_style = PolygonStyle(fill_color="w", line_color="None", line_width=0)
		if not outside:
			self._draw_polygon(polygon, mask_style)
		else:
			proj_polygon = self.get_projected_polygon(polygon)
			llcrnrx, llcrnry = self.map(self.llcrnrlon, self.llcrnrlat, inverse=True)
			urcrnrx, urcrnry = self.map(self.urcrnrlon, self.urcrnrlat, inverse=True)
			ulcrnrlon, ulcrnrlat = self.map(llcrnrx, urcrnry)
			lrcrnrlon, lrcrnrlat = self.map(urcrnrx, llcrnry)
			exterior_lons = [self.llcrnrlon, lrcrnrlon, self.urcrnrlon, ulcrnrlon, self.llcrnrlon]
			exterior_lats = [self.llcrnrlat, lrcrnrlat, self.urcrnrlat, ulcrnrlat, self.llcrnrlat]
			print zip(exterior_lons, exterior_lats)
			interior_lons = [polygon.lons]
			interior_lats = [polygon.lats]
			for i in range(len(polygon.interior_lons)):
				interior_lons.append(polygon.interior_lons[i])
				interior_lats.append(polygon.interior_lats[i])
			mask_polygon = MultiPolygonData(exterior_lons, exterior_lats, interior_lons, interior_lats)
			self._draw_polygon(mask_polygon, mask_style)

		self.zorder += 1

	def draw_mask_image(self, polygon, resolution=1000, outside=True):
		llcrnrx, llcrnry = self.map(self.llcrnrlon, self.llcrnrlat)
		urcrnrx, urcrnry = self.map(self.urcrnrlon, self.urcrnrlat)
		llcrnrx = np.floor((llcrnrx / resolution)) * resolution
		llcrnry = np.floor((llcrnry / resolution)) * resolution
		urcrnrx = np.ceil((urcrnrx / resolution)) * resolution
		urcrnry = np.ceil((urcrnry / resolution)) * resolution
		width = (urcrnrx - llcrnrx) / resolution + 1
		height = (urcrnry - llcrnry) / resolution + 1
		y, x = np.mgrid[:height, :width]
		x = x * resolution + llcrnrx
		y = y * resolution + llcrnry
		grid_points = np.transpose((x.ravel(), y.ravel()))

		x, y = self.map(polygon.lons, polygon.lats)
		vertices = zip(x, y)

		mask = matplotlib.nxutils.points_inside_poly(grid_points, vertices)
		mask = mask.reshape(height, width)
		print mask
		if not outside:
			mask = -mask

		#img[~mask] = np.uint8(np.clip(img[~mask] - 100., 0, 255))

		cmap = getattr(matplotlib.cm, "binary")
		cmap._init()
		cmap._lut[1:,3] = 0
		self.map.imshow(mask, cmap=cmap, zorder=self.zorder)
		self.zorder += 1

	def draw_layers(self):
		for layer in self.layers:
			if isinstance(layer.data, BuiltinData):
				if layer.data.feature == "continents":
					#continent_style = layer.style
					#ocean_style = PolygonStyle(fill_color="blue")
					self.draw_continents(layer.style)
				if layer.data.feature == "coastlines":
					coastline_style = layer.style
					self.draw_coastlines(coastline_style)
				if layer.data.feature == "countries":
					self.draw_countries(layer.style)
				if layer.data.feature == "rivers":
					self.draw_rivers(layer.style)
				if layer.data.feature == "nightshade":
					self.draw_nightshade(layer.data.date_time, layer.style)
				if layer.data.feature == "bluemarble":
					self.draw_bluemarble(layer.style)
				if layer.data.feature == "shadedrelief":
					self.draw_shadedrelief(layer.style)
				if layer.data.feature == "etopo":
					self.draw_etopo(layer.style)
			elif isinstance(layer.data, FocmecData):
				self.draw_focmecs(layer.data, layer.style)
			elif isinstance(layer.data, MaskData):
				self.draw_mask(layer.data.polygon, layer.style, layer.data.outside)
			elif isinstance(layer.data, MultiPointData):
				self.draw_point_layer(layer.data, layer.style, layer.legend_label)
			elif isinstance(layer.data, (LineData, MultiLineData)):
				self.draw_line_layer(layer.data, layer.style, layer.legend_label)
			elif isinstance(layer.data, (PolygonData, MultiPolygonData)):
				self.draw_polygon_layer(layer.data, layer.style, layer.legend_label)
			elif isinstance(layer.data, GisData):
				self.draw_gis_layer(layer.data, layer.style, layer.legend_label)
			elif isinstance(layer.data, CompositeData):
				polygon_data = layer.data.polygons
				polygon_style = layer.style.polygon_style
				line_data = layer.data.lines
				line_style = layer.style.line_style
				point_data = layer.data.points
				point_style = layer.style.point_style
				text_data = layer.data.texts
				text_style = layer.style.text_style
				legend_label = {"points": layer.legend_label, "lines": layer.legend_label, "polygons": layer.legend_label}
				self.draw_composite_layer(point_data=point_data, point_style=point_style, line_data=line_data, line_style=line_style, polygon_data=polygon_data, polygon_style=polygon_style, text_data=text_data, text_style=text_style)
			elif isinstance(layer.data, GridData):
				self.draw_grid_layer(layer.data, layer.style, layer.legend_label)

	def draw_decoration(self):
		self.draw_graticule()
		# TODO: title style
		self.ax.set_title(self.title)
		# TODO: legend location
		try:
			## May fail if there is no legend
			self.ax.legend(loc=self.legend_location).set_zorder(self.zorder)
		except:
			pass

	def draw_graticule(self):
		"""
		Draw meridians and parallels
		"""
		if self.annot_axes is None:
			self.annot_axes = "SE"
		ax_labels = [c in self.annot_axes for c in "WENS"]
		if self.dlon != None:
			first_meridian = np.ceil(self.region[0] / self.dlon) * self.dlon
			last_meridian = np.floor(self.region[1] / self.dlon) * self.dlon + self.dlon
			meridians = np.arange(first_meridian, last_meridian, self.dlon)
			self.map.drawmeridians(meridians, labels=ax_labels, zorder=self.zorder)
		if self.dlat != None:
			first_parallel = np.ceil(self.region[2] / self.dlat) * self.dlat
			last_parallel = np.floor(self.region[3] / self.dlat) * self.dlat + self.dlat
			parallels = np.arange(first_parallel, last_parallel, self.dlat)
			self.map.drawparallels(parallels, labels=ax_labels, zorder=self.zorder)
		self.zorder += 1

	def draw(self):
		self.draw_layers()
		self.draw_decoration()

	def get_projected_polygon(self, polygon):
		exterior_x, exterior_y = self.map(polygon.lons, polygon.lats)
		interior_x, interior_y = [], []
		for i in range(len(polygon.interior_lons)):
			x, y = self.map(polygon.interior_lons[i], polygon.interior_lats[i])
			interior_x.append(x)
			interior_y.append(y)
		proj_polygon = PolygonData(exterior_x, exterior_y, interior_x, interior_y, value=polygon.value, label=polygon.label)

	def to_display_coordinates(self, lons, lats):
		## Convert lon, lat to display coordinates
		x, y = self.map(lons, lats)
		return zip(*self.ax.transData.transform(zip(x, y)))

	def from_display_coordinates(self, display_x, display_y):
		## Convert display coordinates to lon, lat
		x, y = self.ax.transData.inverted().transform(display_x, display_y)
		return self.map(x, y, inverse=True)

	def plot(self, fig_filespec=None, fig_width=0, dpi=300):
		#fig = pylab.figure()
		#subplot = fig.draw_subplot(111)
		#subplot.set_axes(self.ax)
		if fig_filespec:
			default_figsize = pylab.rcParams['figure.figsize']
			default_dpi = pylab.rcParams['figure.dpi']
			if fig_width:
				fig_width /= 2.54
				dpi = dpi * (fig_width / default_figsize[0])
			pylab.savefig(fig_filespec, dpi=dpi)
			pylab.clf()
		else:
			pylab.show()


if __name__ == "__main__":
	import os

	region = (0,8,49,52)
	projection = "tmerc"
	title = "Test"
	resolution = "h"
	grid_interval = (2, 1)

	layers = []

	## BlueMarble image
	bm_style = None
	data = BuiltinData("bluemarble")
	layer = MapLayer(data, bm_style)
	#layers.append(layer)

	## Continents
	continent_style = PolygonStyle(fill_color="lightgray")
	data = BuiltinData("continents")
	layer = MapLayer(data, continent_style)
	layers.append(layer)

	## Gis file: source-zone model
	#gis_filespec = r"D:\GIS-data\KSB-ORB\Source Zone Models\Seismotectonic Hybrid.TAB"
	gis_filespec = r"D:\GIS-data\KSB-ORB\Source Zone Models\SLZ+RVG.TAB"
	gis_data = GisData(gis_filespec, label_colname="ShortName")
	point_style = PointStyle()
	line_style = LineStyle(line_width=2)
	fill_color = ThematicStyleDict({"SLZ": "green", "RVG": "orange"}, value_key="ShortName")
	polygon_style = PolygonStyle(line_width=2, fill_color=fill_color, alpha=0.5)
	label_style = TextStyle()
	gis_style = CompositeStyle(point_style=point_style, line_style=line_style, polygon_style=polygon_style, text_style=label_style)
	layer = MapLayer(gis_data, gis_style, legend_label={"polygons": "Area sources", "lines": "Fault sources"})
	layers.append(layer)

	## Grid: hazard map
	import hazard.rshalib as rshalib
	root_folder = r"D:\PSHA\LNE\CRISIS"
	model = "VG_Ambr95DD_Leynaud_EC8"
	crisis_filespec = os.path.join(root_folder, model)
	return_period = 475
	hms = rshalib.crisis.readCRISIS_MAP(crisis_filespec)
	hm = hms.getHazardMap(return_period=return_period)
	contour_interval = {475: 0.02, 3000:0.04, 5000:0.05}[return_period]
	num_grid_cells = 100
	grid_lons, grid_lats = hm.meshgrid(num_cells=num_grid_cells)
	grid_intensities = hm.get_grid_intensities(num_cells=num_grid_cells)
	vmin = np.floor(hm.min() / contour_interval) * contour_interval
	vmax = np.ceil(hm.max() / contour_interval) * contour_interval
	contour_levels = np.arange(vmin, vmax+contour_interval, contour_interval)
	norm = matplotlib.colors.Normalize(vmin, vmax)
	color_map_theme = ThematicStyleColormap(color_map="jet", norm=norm, vmin=vmin, vmax=vmax, alpha=1)
	grid_style = GridStyle(color_map_theme, continuous=True, line_style=LineStyle(label_style=TextStyle()), contour_levels=contour_levels, label_format='%.2f')
	grid_data = GridData(grid_lons, grid_lats, grid_intensities)
	layer = MapLayer(grid_data, grid_style, legend_label="PGA (g)")
	layers.append(layer)

	## Coastlines
	coastline_style = LineStyle(line_color="r", line_width=2)
	data = BuiltinData("coastlines")
	layer = MapLayer(data, coastline_style)
	layers.append(layer)

	## Country borders
	data = BuiltinData("countries")
	country_style = LineStyle(line_color="r", line_width=2, line_pattern='--')
	layer = MapLayer(data, country_style)
	layers.append(layer)

	## Rivers
	data = BuiltinData("rivers")
	river_style = LineStyle(line_color="b")
	layer = MapLayer(data, river_style)
	layers.append(layer)

	## Night shading
	data = BuiltinData("nightshade", date_time=datetime.datetime.now())
	style = PolygonStyle(fill_color='k', alpha=0.5)
	layer = MapLayer(data, style)
	#layers.append(layer)

	## Point data
	point_data = MultiPointData([3,4,4,3], [50,50,51,51], labels=['a','b','c','d'], values=[1,2,2,1])
	point_style = PointStyle(shape='o')
	text_style = TextStyle(offset=[1,1])
	point_style.label_style = text_style
	layer = MapLayer(point_data, point_style)
	#layers.append(layer)

	## ROB earthquake catalog
	import eqcatalog.seismodb as seismodb
	catalog = seismodb.query_ROB_LocalEQCatalog(region=region)
	values = {}
	values['magnitudes'] = catalog.get_magnitudes()
	values['depths'] = catalog.get_depths()
	point_data = MultiPointData(catalog.get_longitudes(), catalog.get_latitudes(), values=values)
	#point_data = MultiPointData([2.0, 3.0, 4.0, 5.0, 6.0], [50, 50, 50, 50, 50], values=[2,3,4,5,6])
	thematic_size = ThematicStyleGradient([1,6], [4, 24], value_key="magnitudes")
	#thematic_color = ThematicStyleColormap(value_key="depths")
	thematic_color = ThematicStyleRanges([0,1,10,25,50], ['red', 'orange', 'yellow', 'green'], value_key="depths")
	#point_style = PointStyle(shape='+', size=thematic_size, fill_color='k', line_color=thematic_color, line_width=0.5)
	point_style = PointStyle(shape='o', size=thematic_size, line_color='k', fill_color=thematic_color, line_width=0.5)
	layer = MapLayer(point_data, point_style, legend_label="ROB Catalog")
	layers.append(layer)

	## Point data: NPP sites
	point_data = MultiPointData([4.259, 5.274], [51.325, 50.534], labels=["Doel", "Tihange"])
	point_style = PointStyle(fill_color='y', label_style=TextStyle(color='w', horizontal_alignment="left", offset=(20,0)))
	layer = MapLayer(point_data, point_style, legend_label="NPP")
	layers.append(layer)

	## Focal mechanisms
	focmecs = FocmecData([4.5], [51.], values=[[135, 60, -90]])
	focmec_style = FocmecStyle()
	layer = MapLayer(focmecs, focmec_style)
	#layers.append(layer)

	#layers = []
	legend_location = 0
	map = LayeredBasemap(layers, region, projection, title, grid_interval=grid_interval, resolution=resolution, legend_location=legend_location)
	mask_polygon = PolygonData([2,3,4,4,3,2,2], [50,50,50,51,51,51,50])
	map.draw_mask(mask_polygon, outside=False)

	## Convert display coordinates to lon, lat
	x, y = map.ax.transData.inverted().transform((328,237))
	lon, lat = map.map(x, y, inverse=True)
	print x, y
	print lon, lat

	## Convert lon, lat to display coordinates
	lon, lat = 4, 50.5
	x, y = map.map(lon, lat)
	a, b = map.ax.transData.transform((x, y))
	print x, y
	print a, b
	#fig_filespec = r"C:\Temp\layeredbasemap.png"
	fig_filespec = None
	map.plot(fig_filespec=fig_filespec)

