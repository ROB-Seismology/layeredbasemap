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



## Styles
class FontStyle:
	def __init__(self, family="sans-serif", style="normal", variant="normal", stretch="normal", weight="normal", size=12):
		self.family = family
		self.style = style
		self.variant = variant
		self.stretch = stretch
		self.weight = weight
		self.size = size

	def get_font_prop(self):
		fp = matplotlib.font_manager.FontProperties(family=self.family, style=self.style, variant=self.variant, stretch=self.stretch, weight=self.weight, size=self.size)
		return fp


class TextStyle:
	def __init__(self, font_family="sans-serif", font_style="normal", font_variant="normal", font_stretch="normal", font_weight="normal", font_size=12, color='k', background_color=None, line_spacing=12, rotation=0, horizontal_alignment="center", vertical_alignment="center", offset=(0,0), alpha=1.):
		self.font_family = font_family
		self.font_style = font_style
		self.font_variant = font_variant
		self.font_stretch = font_stretch
		self.font_weight = font_weight
		self.font_size = font_size
		self.color = color
		#self.background_color = background_color
		self.line_spacing = line_spacing
		self.rotation = rotation
		self.horizontal_alignment = horizontal_alignment
		self.vertical_alignment = vertical_alignment
		self.offset = offset
		self.alpha = alpha

	def get_font_prop(self):
		fp = matplotlib.font_manager.FontProperties(family=self.font_family, style=self.font_style, variant=self.font_variant, stretch=self.font_stretch, weight=self.font_weight, size=self.font_size)
		return fp


class PointStyle:
	def __init__(self, shape='o', size=12, line_width=1, line_color='k', fill_color='None', label_style=None, alpha=1.):
		self.shape = shape
		self.size = size
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.label_style = label_style
		self.alpha = alpha

	def is_thematic(self):
		if (isinstance(self.shape, ThematicStyle) or isinstance(self.size, ThematicStyle) or
			isinstance(self.line_width, ThematicStyle) or isinstance(self.line_color, ThematicStyle) or
			isinstance(self.fill_color, ThematicStyle)):
			return True
		else:
			return False


class LineStyle:
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', label_style=None, alpha=1.):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.label_style = label_style
		self.alpha = alpha

	def is_thematic(self):
		if (isinstance(self.line_pattern, ThematicStyle) or isinstance(self.line_width, ThematicStyle)
			or isinstance(self.line_color, ThematicStyle)):
			return True
		else:
			return False


class PolygonStyle:
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', fill_color='y', fill_hatch=None, label_style=None, alpha=1.):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.fill_hatch = fill_hatch
		self.label_style = label_style
		self.alpha = alpha

	def is_thematic(self):
		if (isinstance(self.line_pattern, ThematicStyle) or isinstance(self.line_width, ThematicStyle)
			or isinstance(self.line_color, ThematicStyle) or isinstance(self.fill_color, ThematicStyle)
			or isinstance(self.fill_hatch, ThematicStyle)):
			return True
		else:
			return False


class FocmecStyle:
	def __init__(self, size=50, line_width=1, line_color='k', fill_color='k', bg_color='w', alpha=1.):
		self.size = size
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.bg_color = bg_color
		self.alpha = alpha

	def is_thematic(self):
		if (isinstance(self.size, ThematicStyle) or isinstance(self.line_width, ThematicStyle) or
			isinstance(self.line_color, ThematicStyle) or isinstance(self.fill_color, ThematicStyle)):
			return True
		else:
			return False


class CompositeStyle:
	def __init__(self, point_style=None, line_style=None, polygon_style=None):
		self.point_style = point_style
		self.line_style = line_style
		self.polygon_style = polygon_style

	def is_thematic(self):
		if self.point_style.is_thematic() or self.line_style.is_thematic() or self.polygon_style.is_thematic():
			return True
		else:
			return False


class ThematicStyle(object):
	def __init__(self, value_key=None, add_legend=True):
		self.value_key = value_key
		self.add_legend = add_legend

	def apply_value_key(self, values):
		if self.value_key == None:
			return values
		else:
			return values[self.value_key]


class ThematicStyleDict(ThematicStyle):
	def __init__(self, style_dict, value_key=None, add_legend=True):
		super(ThematicStyleDict, self).__init__(value_key, add_legend)
		self.style_dict = style_dict

	def __call__(self, values):
		"""
		values can be numbers or strings
		"""
		return [self.style_dict[val] for val in self.apply_value_key(values)]

	def to_colormap(self):
		try:
			cmap = matplotlib.colors.ListedColormap(self.style_dict.values(), name=value_key)
		except:
			pass
		else:
			return cmap


class ThematicStyleRanges(ThematicStyle):
	def __init__(self, bin_edges, bin_values, value_key=None, add_legend=True):
		"""
		bin_edges must be monotonically increasing or decreasing
		bin_values may be colors
		"""
		super(ThematicStyleRanges, self).__init__(value_key, add_legend)
		self.bin_edges = bin_edges
		self.bin_values = bin_values

	def __call__(self, values):
		"""
		values must be numbers
		"""
		bin_indexes = np.digitize(self.apply_value_key(values), self.bin_edges) - 1
		return [self.bin_values[bi] for bi in bin_indexes]

	def to_colormap(self):
		try:
			cmap = matplotlib.colors.ListedColormap(self.bin_values, name=value_key)
		except:
			pass
		else:
			return cmap


class ThematicStyleGradient(ThematicStyle):
	def __init__(self, in_values, out_values, value_key=None, add_legend=True):
		"""
		in_values must be monotonically increasing or decreasing
		out_values must be numbers too
		"""
		super(ThematicStyleGradient, self).__init__(value_key, add_legend)
		self.in_values = in_values
		self.out_values = out_values

	def __call__(self, values):
		return np.interp(self.apply_value_key(values), self.in_values, self.out_values)

	def to_colormap(self):
		x = np.array(self.in_values, dtype='f')
		x /= x.max()
		return matplotlib.colors.LinearSegmentedColormap.from_list(self.value_key, zip(x, self.out_values))


class ThematicStyleColormap(ThematicStyle):
	def __init__(self, color_map="jet", norm=None, vmin=None, vmax=None, alpha=1.0, value_key=None, add_legend=True):
		super(ThematicStyleColormap, self).__init__(value_key, add_legend)
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

	def to_colormap(self):
		return self.color_map


class GridStyle:
	def __init__(self, color_map_theme=ThematicStyleColormap("jet"), continuous=True, line_style=None, contour_levels=[], label_format='%.2f'):
		self.color_map_theme = color_map_theme
		self.continuous = continuous
		self.line_style = line_style
		self.contour_levels = contour_levels
		self.label_format = label_format


class LegendStyle:
	def __init__(self, title="", location=0, label_style=FontStyle(), title_style=FontStyle(weight='bold'), marker_scale=None, frame_on=True, fancy_box=False, shadow=False, ncol=1, border_pad=None, label_spacing=None, handle_length=None, handle_text_pad=None, border_axes_pad=None, column_spacing=None):
		self.title = title
		self.location = location
		self.label_style = label_style
		self.title_style = title_style
		self.marker_scale = marker_scale
		self.frame_on = frame_on
		self.fancy_box = fancy_box
		self.shadow = shadow
		self.ncol = ncol
		self.border_pad = border_pad
		self.label_spacing = label_spacing
		self.handle_length = handle_length
		self.handle_text_pad = handle_text_pad
		self.border_axes_pad = border_axes_pad
		self.column_spacing = column_spacing


## Data types
class BuiltinData:
	def __init__(self, feature="continents", **kwargs):
		assert feature in ("bluemarble", "coastlines", "continents", "countries", "nightshade", "rivers", "shadedrelief"), "%s not recognized as builtin data" % feature
		self.feature = feature
		for key, val in kwargs.items():
			setattr(self, key, val)


class PointData(object):
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


class MultiPointData(object):
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


class LineData(object):
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


class MultiLineData(object):
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


class PolygonData(object):
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


class MultiPolygonData(object):
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
	def __init__(self, lons, lats, sdr, values=[], labels=[]):
		super(FocmecData, self).__init__(lons, lats, values, labels)
		self.sdr = sdr


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
	def __init__(self, filespec, label_colname=None, selection_dict={}):
		self.filespec = filespec
		self.label_colname = label_colname
		self.selection_dict = selection_dict


class MapLayer:
	def __init__(self, data, style, legend_label="_nolegend_"):
		self.data = data
		self.style = style
		self.legend_label = legend_label


class LayeredBasemap:
	def __init__(self, layers, region, projection, title, origin=(None, None), grid_interval=(None, None), resolution="i", annot_axes="SE", title_style=TextStyle(font_size="large", horizontal_alignment="center", vertical_alignment="bottom"), legend_style=LegendStyle(), thematic_legend_style=LegendStyle()):
		#TODO: width, height
		self.layers = layers
		self.region = region
		self.projection = projection
		self.title = title
		self.origin = origin
		self.grid_interval = grid_interval
		self.resolution = resolution
		self.annot_axes = annot_axes
		self.legend_style = legend_style
		self.thematic_legend_style = thematic_legend_style
		self.title_style = title_style
		self.map = self.init_basemap()
		self.ax = pylab.gca()
		self._legend_artists = []
		self._legend_labels = []
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
		if style.is_thematic():
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
			if not (isinstance(style.line_color, ThematicStyle) or isinstance(style.fill_color, ThematicStyle)):
				c = []

			cs = self.map.scatter(x, y, marker=style.shape, s=sizes, c=c, edgecolors=line_colors, linewidths=line_widths, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, label=legend_label, alpha=style.alpha, zorder=self.zorder)
			if isinstance(style.fill_color, ThematicStyleColormap) or isinstance(style.line_color, ThematicStyleColormap):
				# TODO: colorbar style
				cbar = self.map.colorbar(cs)
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
			proj_polygon = self.get_projected_polygon(polygon)
			exterior_x, exterior_y = proj_polygon.lons, proj_polygon.lats
			interior_x, interior_y = proj_polygon.interior_lons, proj_polygon.interior_lats
			if style.fill_color in (None, 'None', 'none'):
				self.map.plot(exterior_x, exterior_y, ls=style.line_pattern, lw=style.line_width, color=style.line_color, label=legend_label, alpha=style.alpha, zorder=self.zorder)
				for x, y in zip(interior_x, interior_y):
					self.map.plot(x, y, ls=style.line_pattern, lw=style.line_width, color=style.line_color, label="_nolegend_", alpha=style.alpha, zorder=self.zorder)
			else:
				from descartes.patch import PolygonPatch
				proj_polygon = proj_polygon.to_shapely()
				## Make sure exterior and interior rings of polygon are properly oriented
				proj_polygon = shapely.geometry.polygon.orient(proj_polygon)
				patch = PolygonPatch(proj_polygon, fill=1, ls=style.line_pattern, lw=style.line_width, ec=style.line_color, fc=style.fill_color, hatch=style.fill_hatch, label=legend_label, alpha=style.alpha)
				patch.set_zorder(self.zorder)
				self.ax.add_patch(patch)

	def _draw_texts(self, text_points, style):
		## Compute offset in map units
		#display_x, display_y = self.lonlat_to_display_coordinates(text_points.lons, text_points.lats)
		#display_x = np.array(display_x) + style.offset[0]
		#display_y = np.array(display_y) + style.offset[1]
		#x, y = self.map_from_display_coordinates(display_x, display_y)
		x, y = self.map(text_points.lons, text_points.lats)
		for i, label in enumerate(text_points.labels):
			if isinstance(label, str):
				label = label.decode('iso-8859-1')
			#self.ax.text(x[i], y[i], label, family=style.font_family, size=style.font_size, weight=style.font_weight, style=style.font_style, stretch=style.font_stretch, variant=style.font_variant, color=style.color, linespacing=style.line_spacing, rotation=style.rotation, ha=style.horizontal_alignment, va=style.vertical_alignment, alpha=style.alpha, zorder=self.zorder)
			if style.offset:
				xytext = style.offset
				textcoords = "offset points"
			else:
				xytext = None
				textcoords = ""
			self.ax.annotate(label, (x[i], y[i]), xytext=xytext, textcoords=textcoords, family=style.font_family, size=style.font_size, weight=style.font_weight, style=style.font_style, stretch=style.font_stretch, variant=style.font_variant, color=style.color, linespacing=style.line_spacing, rotation=style.rotation, ha=style.horizontal_alignment, va=style.vertical_alignment, alpha=style.alpha, zorder=self.zorder)

	def draw_polygon_layer(self, polygon_data, polygon_style, legend_label="_nolegend_"):
		"""
		polygon_data: MultiPolygon
		"""
		# TODO: use PolyCollection / PatchCollection
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

		## thematic legend
		if polygon_style.is_thematic():
			#legend_artists, legend_labels = self.ax.get_legend_handles_labels()
			if isinstance(polygon_style.fill_color, (ThematicStyleDict, ThematicStyleRanges)) and polygon_style.fill_color.add_legend:
				#p = matplotlib.patches.Circle((0, 0), radius=0.001, lw=0, fc='none')
				#self._legend_artists.append(None)
				#self._legend_labels.append("Zone")
				for key, val in polygon_style.fill_color.style_dict.items():
					label = key
					color = val
					p = matplotlib.patches.Rectangle((0, 0), 1, 1, fill=1, ls='solid', lw=1, fc=color, ec='k', hatch=None, alpha=polygon_style.alpha)
					self._legend_artists.append(p)
					self._legend_labels.append(label)
			#self.ax.legend(legend_artists, legend_labels, loc=self.legend_location).set_zorder(len(self.layers))
			#self.draw_legend((legend_artists, legend_labels))

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
		from mapping.geo.readGIS import read_GIS_file

		point_style = gis_style.point_style
		line_style = gis_style.line_style
		polygon_style = gis_style.polygon_style
		point_value_colnames = set()
		if point_style:
			if isinstance(point_style.size, ThematicStyle):
				point_value_colnames.add(point_style.size.value_key)
			if isinstance(point_style.line_width, ThematicStyle):
				point_value_colnames.add(point_style.line_width.value_key)
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
			selected = np.zeros(len(gis_data.selection_dict.keys()))
			for i, (selection_colname, selection_value) in enumerate(gis_data.selection_dict.items()):
				if rec[selection_colname] == selection_value or rec[selection_colname] in selection_value:
					selected[i] = 1
				else:
					selected[i] = 0
			if selected.all():
				label = rec.get(gis_data.label_colname)
				geom = rec['obj']
				geom_type = geom.GetGeometryName()
				# TODO: MultiPoint
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
		from obspy.imaging.beachball import Beach
		## Determine conversion factor between display coordinates
		## and map coordinates for beachball size
		x0, y0 = self.map(self.lon_0, self.lat_0)
		display_x0, display_y0 = self.map_to_display_coordinates([x0], [y0])
		display_x1 = display_x0[0] + 100
		x1, y1 = self.map_from_display_coordinates([display_x1], display_y0)
		conv_factor = float(x1[0] - x0) / 100

		## Thematic mapping
		if isinstance(focmec_style.size, ThematicStyle):
			sizes = focmec_style.size(focmec_data.values)
		else:
			sizes = [focmec_style.size] * len(focmec_data)
		if isinstance(focmec_style.line_width, ThematicStyle):
			line_widths = focmec_style.line_width(focmec_data.values)
		else:
			line_widths = [focmec_style.line_width] * len(focmec_data)
		if isinstance(focmec_style.line_color, ThematicStyle):
			line_colors = focmec_style.line_color(focmec_data.values)
		else:
			line_colors = [focmec_style.line_color] * len(focmec_data)
		if isinstance(focmec_style.fill_color, ThematicStyle):
			fill_colors = focmec_style.fill_color(focmec_data.values)
		else:
			fill_colors = [focmec_style.fill_color] * len(focmec_data)

		x, y = self.map(focmec_data.lons, focmec_data.lats)
		for i in range(len(focmec_data)):
			width = sizes[i] * conv_factor
			b = Beach(focmec_data.sdr[i], xy=(x[i], y[i]), width=width, linewidth=line_widths[i], edgecolor=line_colors[i], facecolor=fill_colors[i], bgcolor=focmec_style.bg_color, alpha=focmec_style.alpha)
			b.set_zorder(self.zorder)
			self.ax.add_collection(b)
		self.zorder += 1

	def draw_geotiff(self, tif_filespec):
		# TODO
		import gdal
		geo = gdal.Open("file.geotiff")
		ar = geo.ReadAsArray()

	def draw_mask(self, polygon, mask_style=None, outside=True):
		"""
		polygon or multipolygon, holes are disregarded
		"""
		if not mask_style:
			mask_style = PolygonStyle(fill_color="w", line_color="None", line_width=0)
		if not outside:
			self._draw_polygon(polygon, mask_style)
		else:
			llcrnrx, llcrnry = self.map(self.llcrnrlon, self.llcrnrlat, inverse=True)
			urcrnrx, urcrnry = self.map(self.urcrnrlon, self.urcrnrlat, inverse=True)
			ulcrnrlon, ulcrnrlat = self.map(llcrnrx, urcrnry)
			lrcrnrlon, lrcrnrlat = self.map(urcrnrx, llcrnry)
			exterior_lons = [self.llcrnrlon, lrcrnrlon, self.urcrnrlon, ulcrnrlon, self.llcrnrlon]
			exterior_lats = [self.llcrnrlat, lrcrnrlat, self.urcrnrlat, ulcrnrlat, self.llcrnrlat]
			interior_lons = []
			interior_lats = []
			for pg in polygon:
				interior_lons.append(pg.lons)
				interior_lats.append(pg.lats)
			mask_polygon = PolygonData(exterior_lons, exterior_lats, interior_lons, interior_lats)
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
		self.draw_legend()
		self.draw_title()

	def draw_legend(self):
		## Thematic legend
		if self.thematic_legend_style and self._legend_artists:
			title = self.thematic_legend_style.title
			if isinstance(title, str):
				title = title.decode('iso-8859-1')
			loc = self.thematic_legend_style.location
			label_style = self.thematic_legend_style.label_style
			title_style = self.thematic_legend_style.title_style
			marker_scale = self.thematic_legend_style.marker_scale
			frame_on = self.thematic_legend_style.frame_on
			fancy_box = self.thematic_legend_style.fancy_box
			shadow = self.thematic_legend_style.shadow
			ncol = self.thematic_legend_style.ncol
			border_pad = self.thematic_legend_style.border_pad
			label_spacing = self.thematic_legend_style.label_spacing
			handle_length = self.thematic_legend_style.handle_length
			handle_text_pad = self.thematic_legend_style.handle_text_pad
			border_axes_pad = self.thematic_legend_style.border_axes_pad
			column_spacing = self.thematic_legend_style.column_spacing

			tl = self.ax.legend(self._legend_artists, self._legend_labels, loc=loc, prop=label_style.get_font_prop(), markerscale=marker_scale, frameon=frame_on, fancybox=fancy_box, shadow=shadow, ncol=ncol, borderpad=border_pad, labelspacing=label_spacing, handlelength=handle_length, handletextpad=handle_text_pad, borderaxespad=border_axes_pad, columnspacing=column_spacing)
			# TODO: in current version of matplotlib set_title does not accept prop
			#tl.set_title(title, prop=title_style.get_font_prop())
			tl.set_title(title)
			tl.set_zorder(self.zorder)

		## Main legend
		if self.legend_style:
			title = self.legend_style.title
			if isinstance(title, str):
				title = title.decode('iso-8859-1')
			loc = self.legend_style.location
			label_style = self.legend_style.label_style
			title_style = self.legend_style.title_style
			marker_scale = self.legend_style.marker_scale
			frame_on = self.legend_style.frame_on
			fancy_box = self.legend_style.fancy_box
			shadow = self.legend_style.shadow
			ncol = self.legend_style.ncol
			border_pad = self.legend_style.border_pad
			label_spacing = self.legend_style.label_spacing
			handle_length = self.legend_style.handle_length
			handle_text_pad = self.legend_style.handle_text_pad
			border_axes_pad = self.legend_style.border_axes_pad
			column_spacing = self.legend_style.column_spacing

			ml = self.ax.legend(loc=loc+1, prop=label_style.get_font_prop(), markerscale=marker_scale, frameon=frame_on, fancybox=fancy_box, shadow=shadow, ncol=ncol, borderpad=border_pad, labelspacing=label_spacing, handlelength=handle_length, handletextpad=handle_text_pad, borderaxespad=border_axes_pad, columnspacing=column_spacing)
			if ml:
				ml.set_title(title)
				ml.set_zorder(self.zorder)

			## Re-attach thematic legend to axes
			if tl:
				self.ax.add_artist(tl)

	def draw_title(self):
		if isinstance(self.title, str):
			title = self.title.decode('iso-8859-1')
		else:
			title = self.title
		style = self.title_style
		self.ax.set_title(title, ha=style.horizontal_alignment, family=style.font_family, size=style.font_size, weight=style.font_weight, style=style.font_style, stretch=style.font_stretch, variant=style.font_variant, color=style.color, linespacing=style.line_spacing, va=style.vertical_alignment, alpha=style.alpha)

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
		return proj_polygon

	def lonlat_to_display_coordinates(self, lons, lats):
		## Convert lon, lat to display coordinates
		x, y = self.map(lons, lats)
		return self.map_to_display_coordinates(x, y)

	def map_to_display_coordinates(self, x, y):
		return zip(*self.ax.transData.transform(zip(x, y)))

	def lonlat_from_display_coordinates(self, display_x, display_y):
		## Convert display coordinates to lon, lat
		x, y = self.map_from_display_coordinates(display_x, display_y)
		return self.map(x, y, inverse=True)

	def map_from_display_coordinates(self, display_x, display_y):
		return zip(*self.ax.transData.inverted().transform(zip(display_x, display_y)))

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
	label_style = TextStyle()
	line_style = LineStyle(line_width=2, label_style=label_style)
	fill_color = ThematicStyleDict({"SLZ": "green", "RVG": "orange"}, value_key="ShortName")
	polygon_style = PolygonStyle(line_width=2, fill_color=fill_color, alpha=0.5, label_style=label_style)
	gis_style = CompositeStyle(line_style=line_style, polygon_style=polygon_style)
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
	#layers.append(layer)

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
	values['magnitude'] = catalog.get_magnitudes()
	values['depth'] = catalog.get_depths()
	values['year'] = [eq.datetime.year for eq in catalog]
	point_data = MultiPointData(catalog.get_longitudes(), catalog.get_latitudes(), values=values)
	#point_data = MultiPointData([2.0, 3.0, 4.0, 5.0, 6.0], [50, 50, 50, 50, 50], values=[2,3,4,5,6])
	thematic_size = ThematicStyleGradient([1,6], [2, 24], value_key="magnitude")
	#thematic_color = ThematicStyleColormap(value_key="depth")
	thematic_color = ThematicStyleRanges([0,1,10,25,50], ['red', 'orange', 'yellow', 'green'], value_key="depth")
	#thematic_color = ThematicStyleRanges([1350,1910,2050], ['green', (1,1,1,0)], value_key="year")
	#point_style = PointStyle(shape='+', size=thematic_size, fill_color='k', line_color=thematic_color, line_width=0.5)
	point_style = PointStyle(shape='o', size=thematic_size, line_color='k', fill_color=thematic_color, line_width=0.5)
	layer = MapLayer(point_data, point_style, legend_label="ROB Catalog")
	layers.append(layer)

	## Point data: NPP sites
	point_data = MultiPointData([4.259, 5.274], [51.325, 50.534], labels=["Doel", "Tihange"])
	point_style = PointStyle(fill_color='y', label_style=TextStyle(color='w', horizontal_alignment="left", offset=(10,0)))
	layer = MapLayer(point_data, point_style, legend_label="NPP")
	layers.append(layer)

	## Focal mechanisms
	thematic_size = ThematicStyleRanges([3,4,5,6,7], [20,30,40,50,60], value_key="magnitude")
	thematic_color = ThematicStyleDict({"normal": 'g', "reverse": "b"}, value_key="sof")
	focmecs = FocmecData([4.5, 6.0], [51., 49.5], sdr=[[135, 60, -90], [0, 30, 90]], values={"magnitude": [4,6], "sof": ["normal", "reverse"]})
	focmec_style = FocmecStyle(size=thematic_size, fill_color=thematic_color)
	layer = MapLayer(focmecs, focmec_style)
	layers.append(layer)

	#layers = []
	legend_style = LegendStyle(location=0)
	title_style = TextStyle(font_size="large", horizontal_alignment="left", font_weight="bold", color="r")
	map = LayeredBasemap(layers, region, projection, title, title_style=title_style, grid_interval=grid_interval, resolution=resolution, legend_style=legend_style)
	mask_polygon = PolygonData([2,3,4,4,3,2,2], [50,50,50,51,51,51,50])
	map.draw_mask(mask_polygon, outside=False)

	#fig_filespec = r"C:\Temp\layeredbasemap.png"
	fig_filespec = None
	map.draw()
	map.plot(fig_filespec=fig_filespec)

