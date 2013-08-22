"""
Generic wrapper for creating maps with Basemap
"""

import numpy as np
from mpl_toolkits.basemap import Basemap
import pylab


class TextStyle:
	def __init__(self, font_family="sans-serif", font_size=12, font_weight="normal", font_style="normal", font_stretch="normal", font_variant="normal", color='k', background_color=None, line_spacing=12, rotation=0, horizontal_alignment="center", vertical_alignment="center", offset=(0,0)):
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


class PointStyle:
	def __init__(self, shape='o', size=12, line_width=1, line_color='k', fill_color='None', label_style=None):
		self.shape = shape
		self.size = size
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.label_style = label_style


class LineStyle:
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', label_style=None):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.label_style = label_style


class PolygonStyle:
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', fill_color='y', fill_hatch=None, label_style=None):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.fill_hatch = fill_hatch
		self.label_style = label_style


class GridStyle:
	def __init__(self, color_map="jet", continuous=True, point_style=None):
		self.color_map = color_map
		self.continuous = continuous
		self.point_style = point_style


class LayerData:
	def __init__(self, points=None, lines=[], polygons=[], texts=None, grid=None):
		self.points = points
		self.lines = lines
		self.polygons = polygons
		self.texts = texts
		self.grid = grid


class BuiltinLayerData:
	def __init__(self, feature="continents"):
		self.feature = feature


class CompositeStyle:
	def __init__(self, point_style=None, line_style=None, polygon_style=None, text_style=None, grid_style=None):
		self.point_style = point_style
		self.line_style = line_style
		self.polygon_style = polygon_style
		self.text_style = text_style
		self.grid_style = grid_style


class PointData:
	def __init__(self, lons, lats, values=[], labels=[]):
		self.lons = lons
		self.lats = lats
		self.values = values
		self.labels = labels

	def get_centroid(self):
		pass


class PolyData:
	def __init__(self, lons, lats, values=[], labels=[]):
		self.lons = lons
		self.lats = lats
		self.values = values
		self.labels = labels

	def __iter__(self):
		for lons, lats, value, label in zip(self.lons, self.lats, self.values, self.labels):
			yield lons, lats, value, label


class GisData:
	pass


class MapLayer:
	def __init__(self, data, style, label="_nolegend_", alpha=1):
		self.data = data
		self.style = style
		self.label = label
		self.alpha = alpha


class ThematicLayer:
	pass


class LayeredBasemap:
	def __init__(self, layers, region, projection, title, lon_0=None, lat_0=None, resolution="i", dlon=None, dlat=None, annot_axes="SE", legend_location=0):
		#TODO: width, height
		self.layers = layers
		self.region = region
		self.projection = projection
		self.title = title
		self.lon_0 = lon_0
		self.lat_0 = lat_0
		self.resolution = resolution
		self.dlon = dlon
		self.dlat = dlat
		self.annot_axes = annot_axes
		self.legend_location = legend_location
		self.map = self.init_basemap()
		self.ax = pylab.gca()
		self.add_layers()
		self.add_decoration()

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

	def init_basemap(self):
		llcrnrlon, urcrnrlon, llcrnrlat, urcrnrlat = self.region
		if self.lon_0 is None:
			self.lon_0 = (llcrnrlon + urcrnrlon) / 2.
		if self.lat_0 is None:
			self.lat_0 = (llcrnrlat + urcrnrlat) / 2.

		map = Basemap(projection=self.projection, resolution=self.resolution, llcrnrlon=self.llcrnrlon, llcrnrlat=self.llcrnrlat, urcrnrlon=self.urcrnrlon, urcrnrlat=self.urcrnrlat, lon_0=self.lon_0, lat_0=self.lat_0)
		return map

	def _add_points(self, points, style, label, alpha):
		x, y = self.map(points.lons, points.lats)
		self.map.plot(x, y, marker=style.shape, ms=style.size, mfc=style.fill_color, mec=style.line_color, mew=style.line_width, ls="None", lw=0, label=label, alpha=alpha)

	def _add_line(self, line, style, label, alpha):
		x, y = self.map(line.lons, line.lats)
		self.map.plot(x, y, ls=style.line_pattern, lw=style.line_width, color=style.line_color, label=label, alpha=alpha)

	def _add_polygon(self, polygon, style, label, alpha):
		x, y = self.map(polygon.lons, polygon.lats)
		self.ax.fill(x, y, ls=style.line_pattern, lw=style.line_width, ec=style.line_color, fc=style.fill_color, hatch=style.fill_hatch, label=label, alpha=alpha)

	def _add_texts(self, text_points, style, alpha):
		# TODO: offset
		x, y = self.map(text_points.lons, text_points.lats)
		for i, label in enumerate(text_points.labels):
			self.ax.text(x[i], y[i], label, family=style.font_family, size=style.font_size, weight=style.font_weight, style=style.font_style, stretch=style.font_stretch, variant=style.font_variant, color=style.color, linespacing=style.line_spacing, rotation=style.rotation, ha=style.horizontal_alignment, va=style.vertical_alignment, alpha=alpha)

	def _add_continents(self, continent_style, lake_style):
		if continent_style.fill_color or lake_style.fill_color:
			self.map.fillcontinents(color=continent_style.fill_color, lake_color=lake_style.fill_color)
		if continent_style.line_color:
			self._add_coastlines(continent_style)

	def _add_coastlines(self, coastline_style):
		self.map.drawcoastlines(linewidth=coastline_style.line_width, color=coastline_style.line_color)

	def _add_countries(self, style):
		if style.line_color:
			self.map.drawcountries(linewidth=style.line_width, color=style.line_color)

	def _add_rivers(self, style):
		if style.line_color:
			## linestyle argument not supported by current version of basemap
			self.map.drawrivers(linewidth=style.line_width, color=style.line_color)

	def _add_bluemarble(self, style=None):
		try:
			self.map.bluemarble()
		except:
			print("Bluemarble layer failed. This feature requires an internet connection")

	def _add_shadedrelief(self, style=None):
		try:
			self.map.shadedrelief()
		except:
			print("Shadedrelief layer failed. This feature requires an internet connection")

	def _add_etopo(self, style=None):
		try:
			self.map.etopo()
		except:
			print("Etopo layer failed. This feature requires an internet connection")

	def _add_focmecs(self, points, focmec_data):
		from obspy.imaging.beachball import Beach
		x, y = self.map(points.lons, points.lats)
		for i in range(len(focmec_data)):
			b = Beach(focmecs[i], xy=(x[i], y[i]), width=1000, linewidth=1)
			#b.set_zorder(10)
			self.ax.add_collection(b)

	def add_layers(self):
		for layer in self.layers:
			if isinstance(layer.data, BuiltinLayerData):
				if layer.data.feature == "continents":
					continent_style = layer.style
					ocean_style = PolygonStyle(fill_color="blue")
					self._add_continents(continent_style, ocean_style)
				if layer.data.feature == "coastlines":
					coastline_style = layer.style
					self._add_coastlines(coastline_style)
				if layer.data.feature == "countries":
					self._add_countries(layer.style)
				if layer.data.feature == "rivers":
					self._add_rivers(layer.style)
				if layer.data.feature == "bluemarble":
					self._add_bluemarble(layer.style)
				if layer.data.feature == "shadedrelief":
					self._add_shadedrelief(layer.style)
				if layer.data.feature == "etopo":
					self._add_etopo(layer.style)
			elif isinstance(layer.data, LayerData):
				if len(layer.data.polygons) > 0 and layer.style.polygon_style:
					style = layer.style.polygon_style
					for polygon in layer.data.polygons:
						self._add_polygon(polygon, style, layer.label, layer.alpha)
						if polygon.labels and style.label_style:
							self._add_texts(polygon.labels, style.label_style, layer_alpha)
				if len(layer.data.lines) > 0 and layer.style.line_style:
					style = layer.style.line_style
					for line in layer.data.lines:
						self._add_line(line, style, layer.label, layer.alpha)
						if line.labels and style.label_style:
							self._add_texts(line.labels, style.label_style, layer_alpha)
				if layer.data.points and layer.style.point_style:
					points = layer.data.points
					style = layer.style.point_style
					self._add_points(points, style, layer.label, layer.alpha)
					if points.labels and style.label_style:
						self._add_texts(points, style.label_style, layer.alpha)
				if layer.data.texts and layer.style.text_style:
					style = layer.style.text_style
					self._add_texts(layer.data.texts, style, layer.alpha)

	def add_decoration(self):
		self.add_graticule()
		self.ax.set_title(self.title)
		self.ax.legend()

	def add_graticule(self):
		"""
		Draw meridians and parallels
		"""
		if self.annot_axes is None:
			self.annot_axes = "SE"
		ax_labels = [c in self.annot_axes for c in "WENS"]
		if self.dlon != None:
			first_meridian = np.ceil(region[0] / self.dlon) * self.dlon
			last_meridian = np.floor(region[1] / self.dlon) * self.dlon + self.dlon
			meridians = np.arange(first_meridian, last_meridian, self.dlon)
			self.map.drawmeridians(meridians, labels=ax_labels)
		if self.dlat != None:
			first_parallel = np.ceil(region[2] / self.dlat) * self.dlat
			last_parallel = np.floor(region[3] / self.dlat) * self.dlat + self.dlat
			parallels = np.arange(first_parallel, last_parallel, self.dlat)
			self.map.drawparallels(parallels, labels=ax_labels)


	def plot(self, fig_filespec=None, fig_width=0, dpi=300):
		#fig = pylab.figure()
		#subplot = fig.add_subplot(111)
		#subplot.set_axes(self.ax)
		if fig_filespec:
			default_figsize = pylab.rcParams['figure.figsize']
			default_dpi = pylab.rcParams['figure.dpi']
			if fig_width:
				fig_width /= 2.54
				dpi = dpi * (fig_width / default_figsize[0])
			fig.savefig(fig_filespec, dpi=dpi)
			fig.clf()
		else:
			pylab.show()


def prepare_map(layers, region, projection, resolution=None, dlon=None, dlat=None, title=None, legend_location=0):
	llcrnrlon, urcrnrlon, llcrnrlat, urcrnrlat = region
	lon_0 = (llcrnrlon + urcrnrlon) / 2.
	lat_0 = (llcrnrlat + urcrnrlat) / 2.

	map = Basemap(projection=projection, resolution=resolution, llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, urcrnrlat=urcrnrlat, lon_0=lon_0, lat_0=lat_0)

	for layer in layers:
		if layer.style.polygon_style:
			style = layer.style.polygon_style
			for polygon in layer.data.polygons:
				x, y = map(polygon.lons, polygon.lats)
				pylab.fill(x, y, ls=style.line_pattern, lw=style.line_width, ec=style.line_color, fc=style.fill_color, hatch=style.fill_hatch, label=layer.label, alpha=layer.alpha)
		if layer.style.line_style:
			style = layer.style.line_style
			for line in layer.data.lines:
				x, y = map(line.lons, line.lats)
				map.plot(x, y, ls=style.line_pattern, lw=style.line_width, color=style.line_color, label=layer.label, alpha=layer.alpha)
		if layer.data.points and layer.style.point_style:
			style = layer.style.point_style
			x, y = map(data.points.lons, data.points.lats)
			map.plot(x, y, marker=style.shape, ms=style.size, mfc=style.fill_color, mec=style.line_color, mew=style.line_width, ls="None", lw=0, label=layer.label, alpha=layer.alpha)
		if layer.style.text_style:
			style = layer.style.text_style
			x, y = map(data.texts.lons, data.texts.lats)
			for i, label in enumerate(data.texts.labels):
				pylab.text(x[i], y[i], label, family=style.font_family, size=style.font_size, weight=style.font_weight, style=style.font_style, stretch=style.font_stretch, variant=style.font_variant, color=style.color, linespacing=style.line_spacing, rotation=style.rotation, ha=style.horizontal_alignment, va=style.vertical_alignment, alpha=layer.alpha)
				#pylab.text(x[i], y[i], label)

	pylab.title(title)

	return map


def plot_map(layers, region, projection, resolution=None, dlon=None, dlat=None, title=None, legend_location=0, fig_filespec=None, fig_width=0, dpi=300):
	map = prepare_map(layers, region, projection, resolution, dlon, dlat, title, legend_location)
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
	layers = []
	bm_style = None
	data = BuiltinLayerData("etopo")
	layer = MapLayer(data, bm_style)
	layers.append(layer)

	continent_style = PolygonStyle(fill_color="lightgray")
	data = BuiltinLayerData("continents")
	layer = MapLayer(data, continent_style)
	#layers.append(layer)

	coastline_style = LineStyle(line_color="r", line_width=2)
	data = BuiltinLayerData("coastlines")
	layer = MapLayer(data, coastline_style)
	layers.append(layer)

	data = BuiltinLayerData("countries")
	country_style = LineStyle(line_color="r", line_width=2)
	layer = MapLayer(data, country_style)
	layers.append(layer)

	data = BuiltinLayerData("rivers")
	river_style = LineStyle(line_color="b")
	layer = MapLayer(data, river_style)
	layers.append(layer)

	points = PointData([3,4,4,3,3], [50,50,51,51,50], labels=['a','b','c','d','e'])
	data = LayerData(points=points, lines=[], polygons=[], texts=None)
	point_style = PointStyle()
	line_style = LineStyle()
	text_style = TextStyle(offset=[1,1])
	polygon_style = PolygonStyle()
	point_style.label_style = text_style
	style = CompositeStyle(point_style, line_style, polygon_style, text_style)
	layer = MapLayer(data, style)
	layers.append(layer)

	region = (1,8,49,52)
	projection = "merc"
	title = "Test"
	resolution = "h"
	dlon, dlat = 2, 1
	map = LayeredBasemap(layers, region, projection, title, resolution=resolution, dlon=dlon, dlat=dlat)
	map.plot()

