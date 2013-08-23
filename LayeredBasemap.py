"""
Generic wrapper for creating maps with Basemap
"""

import numpy as np
from mpl_toolkits.basemap import Basemap
import pylab

from mapping.geo.readGIS import read_GIS_file


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


class FocmecStyle:
	def __init__(self):
		pass


class GridStyle:
	def __init__(self, color_map="jet", continuous=True, point_style=None):
		self.color_map = color_map
		self.continuous = continuous
		self.point_style = point_style


class CompositeStyle:
	def __init__(self, point_style=None, line_style=None, polygon_style=None, text_style=None, grid_style=None):
		self.point_style = point_style
		self.line_style = line_style
		self.polygon_style = polygon_style
		self.text_style = text_style
		self.grid_style = grid_style


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


class MultiPointData:
	def __init__(self, lons, lats, values=[], labels=[]):
		self.lons = lons
		self.lats = lats
		self.values = values
		self.labels = labels

	def __len__(self):
		return len(self.lons)

	def get_centroid(self):
		pass


class FocmecData(MultiPointData):
	pass


class PolyData:
	def __init__(self, lons, lats, value=None, label=""):
		self.lons = lons
		self.lats = lats
		self.value = value
		self.label = label

	def __len__(self):
		return len(self.lons)


class MultiPolyData:
	def __init__(self, lons, lats, values=[], labels=[]):
		self.lons = lons
		self.lats = lats
		self.values = values
		self.labels = labels

	def __iter__(self):
		for i in range(len(self.lons)):
			lons = self.lons[i]
			lats = self.lats[i]
			try:
				value = self.values[i]
			except:
				value = None
			try:
				label = self.labels[i]
			except:
				label = ""
			yield PolyData(lons, lats, value, label)

	def __len__(self):
		return len(self.lons)


class GisData:
	def __init__(self, filespec, point_label="", line_label="", polygon_label="", label_colname=None):
		self.filespec = filespec
		self.point_label = point_label
		self.line_label = line_label
		self.polygon_label = polygon_label
		self.label_colname = label_colname


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

	def _add_points(self, points, style, label="_nolegend_", alpha=1.0):
		x, y = self.map(points.lons, points.lats)
		self.map.plot(x, y, marker=style.shape, ms=style.size, mfc=style.fill_color, mec=style.line_color, mew=style.line_width, ls="None", lw=0, label=label, alpha=alpha)

	def _add_line(self, line, style, label="_nolegend_", alpha=1.0):
		x, y = self.map(line.lons, line.lats)
		self.map.plot(x, y, ls=style.line_pattern, lw=style.line_width, color=style.line_color, label=label, alpha=alpha)

	def _add_polygon(self, polygon, style, label="_nolegend_", alpha=1.0):
		x, y = self.map(polygon.lons, polygon.lats)
		self.ax.fill(x, y, ls=style.line_pattern, lw=style.line_width, ec=style.line_color, fc=style.fill_color, hatch=style.fill_hatch, label=label, alpha=alpha)

	def _add_texts(self, text_points, style, alpha=1.0):
		# TODO: offset
		x, y = self.map(text_points.lons, text_points.lats)
		for i, label in enumerate(text_points.labels):
			self.ax.text(x[i], y[i], label, family=style.font_family, size=style.font_size, weight=style.font_weight, style=style.font_style, stretch=style.font_stretch, variant=style.font_variant, color=style.color, linespacing=style.line_spacing, rotation=style.rotation, ha=style.horizontal_alignment, va=style.vertical_alignment, alpha=alpha)

	def add_polygon_layer(self, polygon_data, polygon_style, label_style, layer_label="_nolegend_", alpha=1.0):
		for i, polygon in enumerate(polygon_data):
			print i, len(polygon)
			label = {True: layer_label, False: "_nolegend_"}[i==0]
			self._add_polygon(polygon, polygon_style, label, alpha)
		# TODO: we need centroid!
		#if polygon_data.labels and label_style:
		#	self._add_texts(polygon_data.labels, label_style, alpha)

	def add_line_layer(self, line_data, line_style, label_style, layer_label="_nolegend_", alpha=1.0):
		for i, line in enumerate(line_data):
			label = {True: layer_label, False: "_nolegend_"}[i==0]
			self._add_line(line, line_style, label, alpha)
		#if line_data.labels and label_style:
		#	self._add_texts(line_data.labels, label_style, alpha)

	def add_gis_data(self, gis_data, gis_style, alpha=1.0):
		point_data = MultiPointData([], [])
		line_data = MultiPolyData([], [])
		polygon_data = MultiPolyData([], [])
		for rec in read_GIS_file(gis_data.filespec):
			label = rec.get(gis_data.label_colname)
			geom = rec['obj']
			if geom.GetGeometryName() == "LINESTRING":
				lons, lats = zip(*geom.GetPoints())
				line_data.lons.append(lons)
				line_data.lats.append(lats)
				line_data.labels.append(label)
			elif geom.GetGeometryName() == "POLYGON":
				# TODO: complex polygons with holes
				for linear_ring in geom:
					lons, lats = zip(*linear_ring.GetPoints())
					polygon_data.lons.append(lons)
					polygon_data.lats.append(lats)
					polygon_data.labels.append(label)
			else:
				# TODO: test
				lon, lat = geom.GetPoints()[0]
				point_data.lons.append(lon)
				point_data.lats.append(lat)
				point_data.labels.append(label)
		polygon_style = gis_style.polygon_style
		line_style = gis_style.line_style
		point_style = gis_style.point_style
		label_style = gis_style.text_style
		self.add_polygon_layer(polygon_data, polygon_style, label_style, gis_data.polygon_label, alpha)
		self.add_line_layer(line_data, line_style, label_style, gis_data.line_label, alpha)
		if len(point_data) > 0:
			self._add_points(point_data, gis_style.point_style, label, alpha)

	def add_continents(self, continent_style, lake_style):
		if continent_style.fill_color or lake_style.fill_color:
			self.map.fillcontinents(color=continent_style.fill_color, lake_color=lake_style.fill_color)
		if continent_style.line_color:
			self.add_coastlines(continent_style)

	def add_coastlines(self, coastline_style):
		self.map.drawcoastlines(linewidth=coastline_style.line_width, color=coastline_style.line_color)

	def add_countries(self, style):
		if style.line_color:
			self.map.drawcountries(linewidth=style.line_width, color=style.line_color)

	def add_rivers(self, style):
		if style.line_color:
			## linestyle argument not supported by current version of basemap
			self.map.drawrivers(linewidth=style.line_width, color=style.line_color)

	def add_bluemarble(self, style=None):
		try:
			self.map.bluemarble()
		except:
			print("Bluemarble layer failed. This feature requires an internet connection")

	def add_shadedrelief(self, style=None):
		try:
			self.map.shadedrelief()
		except:
			print("Shadedrelief layer failed. This feature requires an internet connection")

	def add_etopo(self, style=None):
		try:
			self.map.etopo()
		except:
			print("Etopo layer failed. This feature requires an internet connection")

	def add_focmecs(self, focmec_data, focmec_style, alpha):
		from obspy.imaging.beachball import Beach
		x, y = self.map(focmec_data.lons, focmec_data.lats)
		for i in range(len(focmec_data)):
			b = Beach(focmec_data.values[i], xy=(x[i], y[i]), width=100000, linewidth=1, alpha=alpha)
			#b.set_zorder(10)
			self.ax.add_collection(b)

	def add_layers(self):
		for layer in self.layers:
			if isinstance(layer.data, BuiltinLayerData):
				if layer.data.feature == "continents":
					continent_style = layer.style
					ocean_style = PolygonStyle(fill_color="blue")
					self.add_continents(continent_style, ocean_style)
				if layer.data.feature == "coastlines":
					coastline_style = layer.style
					self.add_coastlines(coastline_style)
				if layer.data.feature == "countries":
					self.add_countries(layer.style)
				if layer.data.feature == "rivers":
					self.add_rivers(layer.style)
				if layer.data.feature == "bluemarble":
					self.add_bluemarble(layer.style)
				if layer.data.feature == "shadedrelief":
					self.add_shadedrelief(layer.style)
				if layer.data.feature == "etopo":
					self.add_etopo(layer.style)
			elif isinstance(layer.data, FocmecData):
				self.add_focmecs(layer.data, layer.style, layer.alpha)
			elif isinstance(layer.data, GisData):
				self.add_gis_data(layer.data, layer.style, layer.alpha)
			elif isinstance(layer.data, LayerData):
				if len(layer.data.polygons) > 0 and layer.style.polygon_style:
					polygon_data = layer.data.polygons
					polygon_style = layer.style.polygon_style
					label_style = layer.style.text_style
					self.add_polygon_layer(polygon_data, polygon_style, label_style, layer.label, layer.alpha)
				if len(layer.data.lines) > 0 and layer.style.line_style:
					line_data = layer.data.lines
					line_style = layer.style.line_style
					label_style = layer.style.text_style
					self.add_line_layer(line_data, line_style, label_style, layer.label, layer.alpha)
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
	data = BuiltinLayerData("bluemarble")
	layer = MapLayer(data, bm_style)
	#layers.append(layer)

	continent_style = PolygonStyle(fill_color="lightgray")
	data = BuiltinLayerData("continents")
	layer = MapLayer(data, continent_style)
	layers.append(layer)

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

	points = MultiPointData([3,4,4,3,3], [50,50,51,51,50], labels=['a','b','c','d','e'])
	data = LayerData(points=points, lines=[], polygons=[], texts=None)
	point_style = PointStyle()
	line_style = LineStyle()
	text_style = TextStyle(offset=[1,1])
	polygon_style = PolygonStyle()
	point_style.label_style = text_style
	style = CompositeStyle(point_style, line_style, polygon_style, text_style)
	layer = MapLayer(data, style)
	layers.append(layer)

	gis_filespec = r"D:\GIS-data\KSB-ORB\Source Zone Models\Seismotectonic Hybrid.TAB"
	gis_data = GisData(gis_filespec, label_colname="ShortName", polygon_label="Area sources", line_label="Fault sources")
	point_style = PointStyle()
	line_style = LineStyle(line_width=2)
	polygon_style = PolygonStyle(line_width=2, fill_color='None')
	label_style = TextStyle()
	gis_style = CompositeStyle(point_style=point_style, line_style=line_style, polygon_style=polygon_style, text_style=label_style)
	layer = MapLayer(gis_data, gis_style)
	layers.append(layer)

	focmecs = FocmecData([4.5], [51.], values=[[135, 60, -90]])
	focmec_style = FocmecStyle()
	layer = MapLayer(focmecs, focmec_style)
	layers.append(layer)

	region = (1,8,49,52)
	projection = "merc"
	title = "Test"
	resolution = "h"
	dlon, dlat = 2, 1
	map = LayeredBasemap(layers, region, projection, title, resolution=resolution, dlon=dlon, dlat=dlat)
	map.plot()

