"""
Generic wrapper for creating maps with Basemap
"""

import os
import datetime

import numpy as np
import matplotlib
import mpl_toolkits.basemap
from mpl_toolkits.basemap import Basemap
import pylab
import shapely
import shapely.geometry


from styles import *
from data_types import *
import cm


# TODO: draw labels with lines/arrows


class MapLayer:
	"""
	Class representing a map layer

	:param data:
		instance of :class:`BasemapData`: data to plot
	:param style:
		style that will be applied to plot data
	:param legend_label:
		string, label to be used for this data set in map legend
		(default: "_nolegend_")
	:param name:
		string, layer name
		(default: "")
	"""
	def __init__(self, data, style, legend_label="_nolegend_", name=""):
		self.data = data
		self.style = style
		self.legend_label = legend_label
		self.name = name


class ThematicLegend:
	"""
	Container holding information to draw thematic legends

	:param artists:
		list of matplotlib artists
	:param labels:
		list of labels corresponding to artists
	:param style:
		instance of :class:`LegendStyle`, legend style
	"""
	def __init__(self, artists, labels, style):
		self.artists = artists
		self.labels = labels
		self.style = style


class LayeredBasemap:
	def __init__(self, layers, title, projection, region=(None, None, None, None), origin=(None, None), extent=(None, None), graticule_interval=(None, None), resolution="i", title_style=DefaultTitleTextStyle, legend_style=LegendStyle(), scalebar_style=None, border_style=MapBorderStyle(), graticule_style=GraticuleStyle(), ax=None, cax=None, figsize=(8,6), dpi=120, **proj_args):
		self.layers = layers
		self.title = title
		self.region = region
		self.projection = projection
		self.origin = origin
		self.extent = extent
		self.graticule_interval = graticule_interval
		self.resolution = resolution
		self.title_style = title_style
		self.legend_style = legend_style
		self.scalebar_style = scalebar_style
		self.border_style = border_style
		self.graticule_style = graticule_style
		self.proj_args = proj_args

		self.map = self.init_basemap(ax)
		self.dpi = dpi
		self.figsize = figsize
		if ax is None:
			self.fig = pylab.figure(figsize=self.figsize, dpi=self.dpi)
			self.ax = pylab.gca()
		else:
			self.ax = ax
			self.fig = pylab.gcf()
		self.cax = cax
		self.thematic_legends = []
		self.legend_artists = []
		self.legend_labels = []
		self.legend_handler_map = {}

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
	def width(self):
		return self.extent[0]

	@property
	def height(self):
		return self.extent[1]

	@property
	def dlon(self):
		return self.graticule_interval[0]

	@property
	def dlat(self):
		return self.graticule_interval[1]

	def init_basemap(self, ax=None):
		self.zorder = 0
		lon_0, lat_0 = self.origin
		llcrnrlon, urcrnrlon, llcrnrlat, urcrnrlat = self.region
		if not None in (llcrnrlon, urcrnrlon, llcrnrlat, urcrnrlat):
			if lon_0 is None:
				lon_0 = (llcrnrlon + urcrnrlon) / 2.
			if lat_0 is None:
				lat_0 = (llcrnrlat + urcrnrlat) / 2.
			self.origin = (lon_0, lat_0)
			width, height = None, None
			self.extent = (width, height)
		else:
			width, height = self.extent

		if mpl_toolkits.basemap.__version__ != '1.0.2':
			if "EPSG:" in self.projection:
				projection = None
				epsg = int(self.projection.split("EPSG:")[1])
			else:
				projection = self.projection
				epsg = None

			map = Basemap(projection=projection, epsg=epsg, resolution=self.resolution, llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, urcrnrlat=urcrnrlat, lon_0=lon_0, lat_0=lat_0, width=width, height=height, ax=ax, **self.proj_args)
		else:
			## Basemap version on Ubuntu 12.04 does not support epsg parameter
			projection = self.projection
			map = Basemap(projection=projection, resolution=self.resolution, llcrnrlon=llcrnrlon, llcrnrlat=llcrnrlat, urcrnrlon=urcrnrlon, urcrnrlat=urcrnrlat, lon_0=lon_0, lat_0=lat_0, width=width, height=height, ax=ax, **self.proj_args)

		self.region = (map.llcrnrlon, map.urcrnrlon, map.llcrnrlat, map.urcrnrlat)
		self.is_drawn = False
		return map

	def get_thematic_legend_artists_and_labels(self, legend_title):
		"""
		Fetch artists and labels from thematic legend with given title.

		:param legend_title:
			str, title of thematic legend

		:return:
			(artists, labels) tuple
		"""
		if legend_title.lower() == "main":
			return (self.legend_artists, self.legend_labels)
		for tl in self.thematic_legends:
			if tl.style.title.lower() == legend_title.lower():
				return (tl.artists, tl.labels)
		return ([], [])

	## Drawing primitives

	def _draw_points(self, points, style, legend_label="_nolegend_", legend_name="main",
					thematic_legend_artists=[], thematic_legend_labels=[]):
		## Note: overriding style params not implemented (except for labels)
		## because we plot all points in one function call!
		x, y = self.map(points.lons, points.lats)
		if not style.is_thematic():
			#self.map.plot(x, y, ls="None", lw=0, label=legend_label, zorder=self.zorder, axes=self.ax, **style.to_kwargs())
			pt, = self.map.plot(x, y, ls="None", lw=0, zorder=self.zorder, axes=self.ax, **style.to_kwargs())
			if legend_label and legend_label != "_nolegend_":
				tl_artists, tl_labels = self.get_thematic_legend_artists_and_labels(legend_name)
				tl_artists.append(pt)
				tl_labels.append(legend_label)
		else:
			## Thematic style, use scatter method
			if isinstance(style.size, ThematicStyle):
				sizes = style.size(points.values)
			else:
				sizes = [style.size] * len(points)

			if isinstance(style.line_width, ThematicStyle):
				line_widths = style.line_width(points.values)
			else:
				line_widths = [style.line_width] * len(points)

			## Note: only one of line_color / fill_color may be a ThematicStyleColormap
			## Note: thematic line_color only works for markers like '+'
			## thematic fill_color only works for markers like 'o'
			assert not (isinstance(style.line_color, ThematicStyle) and isinstance(style.fill_color, ThematicStyle)), "Only one of line_color and fill_color may be ThematicStyle!"
			extra_kwargs = {}
			## Fill color
			if isinstance(style.fill_color, ThematicStyle):
				if not extra_kwargs.has_key("edgecolors"):
					extra_kwargs["edgecolors"] = "None"
				cmap = style.fill_color.to_colormap()
				norm = style.fill_color.get_norm()
				colors = style.fill_color.apply_value_key(points.values)
				vmin, vmax = None, None
				#cmap, norm = None, None
				#colors = style.fill_color(points.values)
			else:
				extra_kwargs["facecolors"] = style.fill_color
			if isinstance(style.line_color, ThematicStyle):
				if not extra_kwargs.has_key("facecolors"):
					extra_kwargs["facecolors"] = "None"
				## Note: it does not seem possible to fill symbols with a
				## fixed color while edge is colored using thematic style,
				## so fill color is ignored in this case.
				extra_kwargs["facecolors"] = "None"
				cmap = style.line_color.to_colormap()
				norm = style.line_color.get_norm()
				colors = style.line_color.apply_value_key(points.values)
				vmin, vmax = None, None
				#colors = style.line_color(points.values)
				#cmap, norm = None, None
			else:
				extra_kwargs["edgecolors"] = style.line_color

			if not (isinstance(style.line_color, ThematicStyle) or isinstance(style.fill_color, ThematicStyle)):
				cmap, norm, vmin, vmax = None, None, None, None
				colors = None

			cs = self.map.scatter(x, y, marker=style.shape, s=np.power(sizes, 2), c=colors, linewidths=line_widths, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, label=legend_label, alpha=style.alpha, zorder=self.zorder, axes=self.ax, **extra_kwargs)

			## Thematic legend
			## Fill color
			if isinstance(style.fill_color, ThematicStyle) and style.fill_color.add_legend:
				colorbar_style = style.fill_color.colorbar_style
				if isinstance(style.fill_color, ThematicStyleColormap) or colorbar_style:
					if colorbar_style is None and isinstance(style.thematic_legend_style, ColorbarStyle):
						## interpret thematic_legend_style as colorbar_style
						colorbar_style = style.thematic_legend_style
					#sm = style.fill_color.to_scalar_mappable()
					#self.draw_colorbar(sm, colorbar_style)
					self.draw_colorbar(cs, colorbar_style)
				else:
					thematic_legend_labels.extend(style.fill_color.labels)
					for fill_color in style.fill_color.styles:
						ntl = style.get_non_thematic_style()
						ntl.fill_color = fill_color
						l = matplotlib.lines.Line2D([0], [0], ls="None", lw=0, **ntl.to_kwargs())
						thematic_legend_artists.append(l)
			## Line color
			elif isinstance(style.line_color, ThematicStyle) and style.line_color.add_legend:
				colorbar_style = style.line_color.colorbar_style
				if isinstance(style.line_color, ThematicStyleColormap) or colorbar_style:
					if colorbar_style is None and isinstance(style.thematic_legend_style, ColorbarStyle):
						## interpret thematic_legend_style as colorbar_style
						colorbar_style = style.thematic_legend_style
					self.draw_colorbar(cs, colorbar_style)
				else:
					thematic_legend_labels.extend(style.line_color.labels)
					for line_color in style.line_color.styles:
						ntl = style.get_non_thematic_style()
						ntl.line_color = line_color
						l = matplotlib.lines.Line2D([0], [0], ls="None", lw=0, **ntl.to_kwargs())
						thematic_legend_artists.append(l)
			## Marker size
			if isinstance(style.size, (ThematicStyleIndividual, ThematicStyleRanges, ThematicStyleGradient)) and style.size.add_legend:
				thematic_legend_labels.extend(style.size.labels)
				for size in style.size.styles:
					ntl = style.get_non_thematic_style()
					ntl.size = size
					l = matplotlib.lines.Line2D([0], [0], ls="None", lw=0, **ntl.to_kwargs())
					thematic_legend_artists.append(l)
			## Line width
			if isinstance(style.line_width, (ThematicStyleIndividual, ThematicStyleRanges, ThematicStyleGradient)) and style.line_width.add_legend:
				thematic_legend_labels.extend(style.line_width.labels)
				for line_width in style.line_width.styles:
					ntl = style.get_non_thematic_style()
					ntl.line_width = line_width
					l = matplotlib.lines.Line2D([0], [0], lw=0, **ntl.to_kwargs())
					thematic_legend_artists.append(l)

	def _draw_line(self, line, line_style, legend_label="_nolegend_",
					legend_name="main"):
		x, y = self.map(line.lons, line.lats)
		style = line.get_overriding_style(line_style)
		#self.map.plot(x, y, label=legend_label, zorder=self.zorder, axes=self.ax, **style.to_kwargs())
		l, = self.map.plot(x, y, zorder=self.zorder, axes=self.ax, **style.to_kwargs())
		if legend_label and legend_label != "_nolegend_":
			tl_artists, tl_labels = self.get_thematic_legend_artists_and_labels(legend_name)
			tl_artists.append(l)
			tl_labels.append(legend_label)

	def _draw_fronts(self, line, line_style, legend_label="_nolegend_",
					legend_name="main"):
		"""
		:param line_style:
			instance of :class:`LineStyle`
		"""
		from frontline import draw_frontline

		x, y = self.map(line.lons, line.lats)
		style = line.get_overriding_style(line_style)
		style_dict = {}
		style_dict["line_style"] = style.line_pattern
		style_dict["line_color"] = style.line_color
		style_dict["line_width"] = style.line_width
		style_dict["line_alpha"] = style.alpha
		#style_dict = {"line_style": "None", "line_color": 'k', "line_width": 0, "line_alpha": 0}
		style_dict.update(style.front_style.to_kwargs())
		lh = draw_frontline(x, y, self.ax, zorder=self.zorder, **style_dict)
		if legend_label and legend_label != "_nolegend_":
			## Note: doesn't work in matplotlib 1.3.1
			dummy_artist = type('DummyArtist', (), {})()
			tl_artists, tl_labels = self.get_thematic_legend_artists_and_labels(legend_name)
			tl_artists.append(dummy_artist)
			tl_labels.append(legend_label)
			self.legend_handler_map[dummy_artist] = lh

	def _draw_polygon(self, polygon, polygon_style, legend_label="_nolegend_",
					legend_name="main"):
		if isinstance(polygon_style, LineStyle):
			self._draw_line(polygon, polygon_style, legend_label)
		if polygon_style.fill_color in (None, "None", "none"):
			fill = 0
		else:
			fill = 1

		style = polygon.get_overriding_style(polygon_style)

		if len(polygon.interior_lons) == 0:
			## Simple polygon
			x, y = self.map(polygon.lons, polygon.lats)
			#self.ax.fill(x, y, fill=fill, label=legend_label, zorder=self.zorder, axes=self.ax, **style.to_kwargs())
			patch, = self.ax.fill(x, y, fill=fill, zorder=self.zorder, axes=self.ax, **style.to_kwargs())
			if legend_label and legend_label != "_nolegend_":
				tl_artists, tl_labels = self.get_thematic_legend_artists_and_labels(legend_name)
				tl_artists.append(patch)
				tl_labels.append(legend_label)
		else:
			## Complex polygon with holes
			proj_polygon = self.get_projected_polygon(polygon)
			exterior_x, exterior_y = proj_polygon.lons, proj_polygon.lats
			interior_x, interior_y = proj_polygon.interior_lons, proj_polygon.interior_lats
			if style.fill_color in (None, 'None', 'none') and style.fill_hatch in (None, 'None', "none"):
				self.map.plot(exterior_x, exterior_y, label=legend_label, zorder=self.zorder, axes=self.ax, **style.to_line_style().to_kwargs())
				for x, y in zip(interior_x, interior_y):
					self.map.plot(x, y, label="_nolegend_", zorder=self.zorder, axes=self.ax, **style.to_line_style().to_kwargs())
			else:
				from descartes.patch import PolygonPatch
				proj_polygon = proj_polygon.to_shapely()
				## Make sure exterior and interior rings of polygon are properly oriented
				proj_polygon = shapely.geometry.polygon.orient(proj_polygon)
				#patch = PolygonPatch(proj_polygon, fill=fill, label=legend_label, **style.to_kwargs())
				patch = PolygonPatch(proj_polygon, fill=fill, **style.to_kwargs())
				patch.set_zorder(self.zorder)
				self.ax.add_patch(patch)
			if legend_label and legend_label != "_nolegend_":
				tl_artists, tl_labels = self.get_thematic_legend_artists_and_labels(legend_name)
				tl_artists.append(patch)
				tl_labels.append(legend_label)

	def _draw_texts(self, text_points, text_style):
		"""
		:param text_points:
			instance of :class:`TextData`, :class:`MultiTextData`,
			instance of :class:`PointData`, :class:`MultiPointData`
		"""
		## Compute offset in map units (not needed for annotate method)
		#display_x, display_y = self.lonlat_to_display_coordinates(text_points.lons, text_points.lats)
		#display_x = np.array(display_x) + style.offset[0]
		#display_y = np.array(display_y) + style.offset[1]
		#x, y = self.map_from_display_coordinates(display_x, display_y)
		if isinstance(text_points, TextData):
			text_points = text_points.to_multi_text()
		elif isinstance(text_points, PointData):
			text_points = text_points.to_multi_point()

		coord_frame = getattr(text_points, "coord_frame", "geographic")
		if coord_frame == "geographic":
			x, y = self.map(text_points.lons, text_points.lats)
			handle_offset = "apply"
		elif coord_frame == "data":
			x, y = text_points.lons, text_points.lats
			handle_offset = "ignore"
		else:
			x, y = np.zeros(len(text_points)), np.zeros(len(text_points))
			handle_offset = "replace"

		for i, label in enumerate(text_points.labels):
			label = text_style.get_text(label)
			style = text_points.get_overriding_style(text_style, i)
			if isinstance(label, str):
				label = label.decode('iso-8859-1')
			#self.ax.text(x[i], y[i], label, zorder=self.zorder, **style.to_kwargs())

			if handle_offset == "ignore":
				xytext = (x[i], y[i])
				textcoords = "data"
			elif handle_offset == "replace":
				xytext = (text_points.lons[i], text_points.lats[i])
				textcoords = coord_frame
			else:
				if not style.offset in ((0, 0), None):
					xytext = style.offset
					textcoords = style.offset_coord_frame
					if textcoords != 'offset points':
						x[i], y[i] = 0, 0
				else:
					print('data.append(lbm.TextData(%.0f, %.0f, label="%s"))' % (x[i], y[i], label))
					xytext = None
					textcoords = "data"
			self.ax.annotate(label, (x[i], y[i]), xytext=xytext, textcoords=textcoords, zorder=self.zorder, axes=self.ax, clip_on=style.clip_on, **style.to_kwargs())

	def draw_polygon_layer(self, polygon_data, polygon_style, legend_label="_nolegend_"):
		"""
		polygon_data: MultiPolygon
		"""
		## Clip to map region
		#region = (self.region[0], self.region[1], self.region[2], self.region[3])
		#lons = [region[0], region[1], region[1], region[0], region[0]]
		#lats = [region[2], region[2], region[3], region[3], region[2]]
		#map_polygon = PolygonData(lons, lats)
		#polygon_data = polygon_data.clip_to_polygon(map_polygon)

		# TODO: use PolyCollection / PatchCollection
		if isinstance(polygon_data, PolygonData):
			polygon_data = polygon_data.to_multi_polygon()
		if isinstance(polygon_style, LineStyle):
			polygon_style = polygon_style.to_polygon_style()
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

		if isinstance(polygon_style.thematic_legend_style, (str, unicode)):
			legend_name = polygon_style.thematic_legend_style
		else:
			legend_name = "main"
		for i, polygon in enumerate(polygon_data):
			if polygon_style.is_thematic():
				legend_label = "_nolegend_"
			else:
				legend_label = {True: legend_label, False: "_nolegend_"}[i==0]
			## Apply thematic styles
			#style = PolygonStyle(line_pattern=line_pattern, line_width=line_width, line_color=line_color, fill_color=fill_color, fill_hatch=fill_hatch, label_style=None, alpha=polygon_style.alpha)
			style = polygon_style.copy()
			style.line_pattern = line_patterns[i]
			style.line_width = line_widths[i]
			style.line_color = line_colors[i]
			style.fill_color = fill_colors[i]
			style.fill_hatch = fill_hatches[i]
			style.label_style = None
			self._draw_polygon(polygon, style, legend_label, legend_name=legend_name)
		self.zorder += 1
		if polygon_data.labels and polygon_style.label_style:
			centroids = MultiPointData([], [], labels=[])
			for pg in polygon_data:
				if pg.label:
					centroid = pg.get_centroid()
					centroids.lons.append(centroid.lon)
					centroids.lats.append(centroid.lat)
					centroids.labels.append(pg.label)
			centroids.style_params = polygon_data.style_params
			self._draw_texts(centroids, polygon_style.label_style)
			self.zorder += 1

		## Thematic legend
		if polygon_style.is_thematic() and polygon_style.thematic_legend_style != None:
			legend_artists, legend_labels = [], []
			## Fill color
			if isinstance(polygon_style.fill_color, ThematicStyle) and polygon_style.fill_color.add_legend:
				colorbar_style = polygon_style.fill_color.colorbar_style
				if isinstance(polygon_style.fill_color, ThematicStyleColormap) or colorbar_style:
					if colorbar_style is None and isinstance(polygon_style.thematic_legend_style, ColorbarStyle):
						## interpret thematic_legend_style as colorbar_style
						colorbar_style = polygon_style.thematic_legend_style
					if colorbar_style:
						sm = polygon_style.fill_color.to_scalar_mappable()
						if not isinstance(polygon_style.fill_color, ThematicStyleColormap):
							if colorbar_style.ticks is None:
								colorbar_style.ticks = polygon_style.fill_color.values
						self.draw_colorbar(sm, colorbar_style)
				else:
					#legend_labels.extend(polygon_style.fill_color.labels)
					# TODO: see if a more elegant solution can be found,
					# and apply to all other thematic styles !!
					# Ideas: e.g. for ranges / gradients
					# np.digitize(np.array(list(set(polygon_style.fill_color.apply_value_key(polygon_data.values)))), np.array(polygon_style.fill_color.values))
					used_colors = []
					for color in fill_colors:
						if isinstance(color, (list, np.ndarray)):
							color = tuple(color)
						if not color in used_colors:
							used_colors.append(color)
					for color, label in zip(polygon_style.fill_color.styles,
											polygon_style.fill_color.labels):
						if isinstance(color, (list, np.ndarray)):
							color = tuple(color)
						if color in used_colors:
							## Keep only colors that are actually used
							ntl = polygon_style.get_non_thematic_style()
							ntl.fill_color = color
							p = matplotlib.patches.Rectangle((0, 0), 1, 1, fill=1, **ntl.to_kwargs())
							legend_artists.append(p)
							legend_labels.append(label)
			## Line color
			if isinstance(polygon_style.line_color, ThematicStyle) and polygon_style.line_color.add_legend:
				colorbar_style = polygon_style.line_color.colorbar_style
				if isinstance(polygon_style.line_color, ThematicStyleColormap) or colorbar_style:
					if colorbar_style is None and isinstance(polygon_style.thematic_legend_style, ColorbarStyle):
						## interpret thematic_legend_style as colorbar_style
						colorbar_style = polygon_style.thematic_legend_style
					if colorbar_style:
						sm = polygon_style.line_color.to_scalar_mappable()
						if not isinstance(polygon_style.line_color, ThematicStyleColormap):
							if colorbar_style.ticks is None:
								colorbar_style.ticks = polygon_style.line_color.values
					self.draw_colorbar(sm, colorbar_style)
				if isinstance(polygon_style.line_color, (ThematicStyleIndividual,  ThematicStyleRanges)):
					legend_labels.extend(polygon_style.line_color.labels)
					for color in polygon_style.line_color.styles:
						ntl = polygon_style.get_non_thematic_style()
						ntl.line_color = color
						p = matplotlib.patches.Rectangle((0, 0), 1, 1, **ntl.to_kwargs())
						legend_artists.append(p)
			## Fill hatch
			if isinstance(polygon_style.fill_hatch, (ThematicStyleIndividual, ThematicStyleRanges)):
				legend_labels.extend(polygon_style.fill_hatch.labels)
				for hatch in polygon_style.fill_hatch.styles:
					ntl = polygon_style.get_non_thematic_style()
					ntl.fill_hatch = hatch
					p = matplotlib.patches.Rectangle((0, 0), 1, 1, **ntl.to_kwargs())
					legend_artists.append(p)
			## Line pattern
			if isinstance(polygon_style.line_pattern, (ThematicStyleIndividual, ThematicStyleRanges)):
				legend_labels.extend(polygon_style.line_pattern.labels)
				for line_pattern in polygon_style.fill_hatch.styles:
					ntl = polygon_style.get_non_thematic_style()
					ntl.line_pattern = line_pattern
					p = matplotlib.patches.Rectangle((0, 0), 1, 1, **ntl_to_kwargs())
					legend_artists.append(p)
			## Line width
			if isinstance(polygon_style.line_width, (ThematicStyleIndividual, ThematicStyleRanges, ThematicStyleGradient)):
				legend_labels.extend(polygon_style.line_width.labels)
				for line_width in polygon_style.line_width.styles:
					ntl = polygon_style.get_non_thematic_style()
					ntl.line_width = line_width
					p = matplotlib.patches.Rectangle((0, 0), 1, 1, **ntl.to_kwargs())
					legend_artists.append(p)

			if polygon_style.thematic_legend_style and len(legend_artists) > 0:
				if isinstance(polygon_style.thematic_legend_style, LegendStyle):
					thematic_legend = ThematicLegend(legend_artists, legend_labels, polygon_style.thematic_legend_style)
					self.thematic_legends.append(thematic_legend)
				elif isinstance(polygon_style.thematic_legend_style, (str, unicode)):
					legend_title = polygon_style.thematic_legend_style
					tl_artists, tl_labels = self.get_thematic_legend_artists_and_labels(legend_title)
					tl_artists.extend(legend_artists)
					tl_labels.extend(legend_labels)

	def draw_line_layer(self, line_data, line_style, legend_label="_nolegend_"):
		"""
		line_data: MultiLine
		"""
		if isinstance(line_data, LineData):
			line_data = line_data.to_multi_line()
		if isinstance(line_style, LineStyle):
			polygon_style = line_style.to_line_style()

		num_lines = len(line_data)
		if isinstance(line_style.line_pattern, ThematicStyle):
			line_patterns = line_style.line_pattern(line_data.values)
		else:
			line_patterns = [line_style.line_pattern] * num_lines
		if isinstance(line_style.line_width, ThematicStyle):
			line_widths = line_style.line_width(line_data.values)
		else:
			line_widths = [line_style.line_width] * num_lines
		if isinstance(line_style.line_color, ThematicStyle):
			line_colors = line_style.line_color(line_data.values)
		else:
			# TODO: more efficient use of iterators ?
			line_colors = [line_style.line_color] * num_lines

		if isinstance(line_style.thematic_legend_style, (str, unicode)):
			legend_name = line_style.thematic_legend_style
		else:
			legend_name = "main"
		for i, line in enumerate(line_data):
			if line_style.is_thematic():
				legend_label = "_nolegend_"
			else:
				legend_label = {True: legend_label, False: "_nolegend_"}[i==0]
			## Apply thematic styles
			# TODO: several line style parameters are missing here
			#style = LineStyle(line_pattern=line_pattern, line_width=line_width, line_color=line_color, label_style=None, alpha=line_style.alpha)
			style = line_style.copy()
			style.line_pattern = line_patterns[i]
			style.line_width = line_widths[i]
			style.line_color = line_colors[i]
			style.label_style = None
			if line_style.front_style:
				style.front_style = line_style.front_style.copy()
				if style.front_style.line_width is None:
					style.front_style.line_width = style.line_width
				if style.front_style.line_color is None:
					style.front_style.line_color = style.line_color
				if style.front_style.fill_color is None:
					style.front_style.fill_color = style.line_color
				self._draw_fronts(line, style, legend_label, legend_name=legend_name)
				# TODO: lines with frontstyle in legend (or thematic legend)
				#handle, label = ax.get_legend_handles_labels()
				#handles = handle+p_handle
				#labels = label+p_label
			else:
				self._draw_line(line, style, legend_label, legend_name=legend_name)
		self.zorder += 1

		## Labels
		if line_data.labels and line_style.label_style:
			# TODO: auto-rotate labels
			# See http://stackoverflow.com/questions/18780198/how-to-rotate-matplotlib-annotation-to-match-a-line
			# Add possibility to anchor label at start, end, middle or fraction of line length
			# and obtain line orientation for that anchor point for auto-rotation
			#label_points = MultiTextData([], [], labels=[])
			if isinstance(line_style.label_anchor, (str, unicode)):
				label_anchor = {"start": 0., "middle": 0.5, "end": 1.}.get(line_style.label_anchor, 0.5)
			else:
				label_anchor = line_style.label_anchor
			for line in line_data:
				if line.label:
					pt = line.get_point_at_fraction_of_length(label_anchor)
					lp = TextData(pt.lon, pt.lat, label=line.label)
					#label_points.lons.append(lp.lon)
					#label_points.lats.append(lp.lat)
					#label_points.labels.append(line.label)
					lp.style_params = line.style_params
					if line_style.label_style.rotation == "auto":
						label_style = line_style.label_style.copy()
						## Set rotation
						## Note: doesn't play nicely with horizontal and vertical
						## text alignment...
						if label_anchor < 0.95:
							pt2 = line.get_point_at_fraction_of_length(label_anchor + 0.25)
						else:
							pt2 = line.get_point_at_fraction_of_length(label_anchor - 0.25)
						display_x, display_y = self.lonlat_to_display_coordinates([pt.lon, pt2.lon], [pt.lat, pt2.lat])
						[dx], [dy] = np.diff(display_y), np.diff(display_x)
						label_style.rotation = np.degrees(np.arctan(dy/dx))
					else:
						label_style = line_style.label_style
					self._draw_texts(lp, label_style)
			#self._draw_texts(label_points, line_style.label_style)
			self.zorder += 1

		# Thematic legend
		if line_style.is_thematic and line_style.thematic_legend_style != None:
			legend_artists, legend_labels = [], []
			## Line color
			if isinstance(line_style.line_color, ThematicStyle) and line_style.line_color.add_legend:
				colorbar_style = line_style.line_color.colorbar_style
				if isinstance(line_style.line_color, ThematicStyleColormap) or colorbar_style:
					if colorbar_style is None:
						## interpret thematic_legend_style as colorbar_style
						colorbar_style = line_style.thematic_legend_style
					if colorbar_style:
						sm = line_style.line_color.to_scalar_mappable()
						if not isinstance(line_style.line_color, ThematicStyleColormap):
							if colorbar_style.ticks is None:
								colorbar_style.ticks = line_style.line_color.values
						self.draw_colorbar(sm, colorbar_style)
				if isinstance(line_style.line_color, (ThematicStyleIndividual,  ThematicStyleRanges)):
					legend_labels.extend(line_style.line_color.labels)
					for color in line_style.line_color.styles:
						ntl = line_style.get_non_thematic_style()
						ntl.line_color = color
						l = matplotlib.lines.Line2D([0,1], [0,1], **ntl.to_kwargs())
						legend_artists.append(l)
			## Line pattern
			if isinstance(line_style.line_pattern, (ThematicStyleIndividual, ThematicStyleRanges)):
				legend_labels.extend(line_style.line_pattern.labels)
				for line_pattern in line_style.line_pattern.styles:
					ntl = line_style.get_non_thematic_style()
					ntl.line_pattern = line_pattern
					l = matplotlib.lines.Line2D([0,1], [0,1], **ntl.to_kwargs())
					legend_artists.append(l)
			## Line width
			if isinstance(line_style.line_width, (ThematicStyleIndividual, ThematicStyleRanges, ThematicStyleGradient)):
				legend_labels.extend(line_style.line_width.labels)
				for line_width in line_style.line_width.styles:
					ntl = line_style.get_non_thematic_style()
					ntl.line_width = line_width
					l = matplotlib.lines.Line2D([0,1], [0,1], **ntl.to_kwargs())
					legend_artists.append(l)

			if line_style.thematic_legend_style and len(legend_artists) > 0:
				if isinstance(line_style.thematic_legend_style, LegendStyle):
					thematic_legend = ThematicLegend(legend_artists, legend_labels, line_style.thematic_legend_style)
					self.thematic_legends.append(thematic_legend)
				elif isinstance(line_style.thematic_legend_style, (str, unicode)):
					legend_title = line_style.thematic_legend_style
					tl_artists, tl_labels = self.get_thematic_legend_artists_and_labels(legend_title)
					tl_artists.extend(legend_artists)
					tl_labels.extend(legend_labels)

	def draw_point_layer(self, point_data, point_style, legend_label="_nolegend_"):
		legend_artists, legend_labels = [], []
		if isinstance(point_data, PointData):
			point_data = point_data.to_multi_point()
		if not isinstance(point_style.shape, ThematicStyle):
			if isinstance(point_style.thematic_legend_style, (str, unicode)):
				legend_name = point_style.thematic_legend_style
				#legend_artists, legend_labels = self.get_thematic_legend_artists_and_labels(legend_name)
			else:
				legend_name = ""
			self._draw_points(point_data, point_style, legend_label, legend_name=legend_name, thematic_legend_artists=legend_artists, thematic_legend_labels=legend_labels)
		else:
			## scatter does not support different markers, so we have to do this separately
			data_marker_shapes = np.array(point_style.shape(point_data.values))
			for i, marker_shape in enumerate(point_style.shape.styles):
				indexes = np.where(data_marker_shapes == marker_shape)[0]
				point_list = [point_data[index] for index in indexes]
				marker_shape_points = MultiPointData.from_points(point_list)
				marker_shape_style = PointStyle(shape=marker_shape, size=point_style.size, line_width=point_style.line_width, line_color=point_style.line_color, fill_color=point_style.fill_color, label_style=point_style.label_style, alpha=point_style.alpha, thematic_legend_style=point_style.thematic_legend_style)
				#legend_label = "_nolegend_"
				self._draw_points(marker_shape_points, marker_shape_style, legend_label, legend_name="", thematic_legend_artists=legend_artists, thematic_legend_labels=legend_labels)
				## Thematic legend
				ntl_style = point_style.get_non_thematic_style()
				ntl_style.shape = marker_shape
				l = matplotlib.lines.Line2D([0], [0], lw=0, ls="None", **ntl_style.to_kwargs())
				legend_artists.append(l)
				label = point_style.shape.labels[i]
				legend_labels.append(label)

		self.zorder += 1
		if point_data.labels and point_style.label_style:
			self._draw_texts(point_data, point_style.label_style)
			self.zorder += 1

		if point_style.is_thematic and point_style.thematic_legend_style != None:
			if point_style.thematic_legend_style and len(legend_artists) > 0:
				if isinstance(point_style.thematic_legend_style, LegendStyle):
					thematic_legend = ThematicLegend(legend_artists, legend_labels, point_style.thematic_legend_style)
					self.thematic_legends.append(thematic_legend)
				elif isinstance(point_style.thematic_legend_style, (str, unicode)):
					legend_title = point_style.thematic_legend_style
					tl_artists, tl_labels = self.get_thematic_legend_artists_and_labels(legend_title)
					tl_artists.extend(legend_artists)
					tl_labels.extend(legend_labels)

	def draw_composite_layer(self, point_data=[], point_style=None, line_data=[], line_style=None, polygon_data=[], polygon_style=None, text_data=[], text_style=None, legend_label={"points": "_nolegend_", "lines": "_nolegend_", "polygons": "_nolegend_"}):
		#print len(point_data), len(line_data), len(polygon_data)
		if polygon_data and len(polygon_data) > 0 and (polygon_style or line_style):
			if not polygon_style:
				polygon_style = line_style.to_polygon_style()
			try:
				label = legend_label.get("polygons", "")
			except AttributeError:
				label = legend_label
			self.draw_polygon_layer(polygon_data, polygon_style, label)
		if line_data and len(line_data) > 0 and (line_style or polygon_style):
			if not line_style:
				line_style = polygon_style.to_line_style()
			try:
				label = legend_label.get("lines", "")
			except AttributeError:
				label = legend_label
			self.draw_line_layer(line_data, line_style, label)
		if point_data and len(point_data) > 0 and point_style:
			try:
				label = legend_label.get("points", "")
			except AttributeError:
				label = legend_label
			self.draw_point_layer(point_data, point_style, label)
		if text_data and len(text_data) > 0 and text_style:
			self._draw_texts(text_data, text_style)

	def draw_gis_layer(self, gis_data, gis_style, legend_label={"points": "_nolegend_", "lines": "_nolegend_", "polygons": "_nolegend_"}):
		point_style = line_style = polygon_style = None
		if isinstance(gis_style, CompositeStyle):
			point_style = gis_style.point_style
			line_style = gis_style.line_style
			polygon_style = gis_style.polygon_style
		elif isinstance(gis_style, PointStyle):
			point_style = gis_style
		elif isinstance(gis_style, LineStyle):
			line_style = gis_style
		elif isinstance(gis_style, PolygonStyle):
			polygon_style = gis_style

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

		## Remove column names that correspond to joined attribute names
		joined_attribute_names = set(gis_data.joined_attributes.keys())
		point_value_colnames = point_value_colnames.difference(joined_attribute_names)
		line_value_colnames = line_value_colnames.difference(joined_attribute_names)
		polygon_value_colnames = polygon_value_colnames.difference(joined_attribute_names)

		point_data, line_data, polygon_data = gis_data.get_data(point_value_colnames,
										line_value_colnames, polygon_value_colnames)

		self.draw_composite_layer(point_data=point_data, point_style=point_style, line_data=line_data, line_style=line_style, polygon_data=polygon_data, polygon_style=polygon_style, legend_label=legend_label)

	def draw_circles(self, circle_data, circle_style, legend_label="_nolegend_"):
		## Note: we could also use the tissot method, but then we would have
		## to code the thematic styling again
		import mapping.geo.geodetic as geodetic
		circles = MultiPolygonData([], [], interior_lons=[], interior_lats=[], values=[], labels=[])
		for i in range(len(circle_data)):
			center = (circle_data.lons[i], circle_data.lats[i])
			radius = circle_data.radii[i]
			lons, lats = [], []
			for azimuth in np.arange(0., 361., circle_data.azimuthal_resolution):
				lon, lat = geodetic.get_point_at(center, radius, azimuth)
				lons.append(lon)
				lats.append(lat)
			circles.append(PolygonData(lons, lats))
		circles.values = circle_data.values
		circles.labels = circle_data.values
		if isinstance(circle_style, PolygonStyle):
			self.draw_polygon_layer(circles, circle_style, legend_label)
		elif isinstance(circle_style, LineStyle):
			self.draw_line_layer(circles, circle_style, legend_label)

	def draw_great_circles(self, gc_data, gc_style, legend_label="_nolegend_"):
		"""
		Draw great circles

		:param gc_data:
			instance of :class:`GreatCircleData`
		:param gc_style:
			instance of :class:`LineStyle` or :class:`PointStyle`
			Note that thematic styles are currently not supported!
		:param legend_label:
			str, label to put in legend for this data set
			(default: "_nolegend_", will not add entry in legend)
		"""
		for (start_lon, start_lat, end_lon, end_lat) in gc_data:
			self.map.drawgreatcircle(start_lon, start_lat, end_lon, end_lat, del_s=gc_data.resolution, **gc_style.to_kwargs())

	def draw_grid_layer(self, grid_data, grid_style, legend_label=""):
		# TODO: add ax=self.ax to plot functions??

		# TODO: Note that pcolor(mesh), if the dimensions or X and Y are the same as C, then the last row and column of C will be ignored
		# Is this the case for contourf as well?? No!
		from cm.norm import PiecewiseLinearNorm

		## Projected center and edge coordinates of grid cells
		xc, yc = self.map(grid_data.center_lons, grid_data.center_lats)
		xe, ye = self.map(grid_data.edge_lons, grid_data.edge_lats)

		if grid_style.color_map_theme:
			cmap = grid_style.color_map_theme.color_map
			norm = grid_style.color_map_theme.norm
			vmin = grid_style.color_map_theme.vmin
			vmax = grid_style.color_map_theme.vmax
			alpha = grid_style.color_map_theme.alpha
			grid_style.color_map_theme.alpha = 1.
		else:
			cmap = None

		## Note: vmin and vmax will control range shown in colorbar
		## However, this doesn't work if color_gradient is continuous
		## and norm is a matplotlib.colors.Normalize instance
		## (norm is reset with vmin and vmax passed to pcolor method)
		## I think this is a bug in pcolor, as it does not occur with contourf

		if cmap:
			if isinstance(cmap, str):
				#cmap_obj = getattr(matplotlib.cm, cmap)
				cmap_obj = matplotlib.cm.get_cmap(cmap)
			else:
				cmap_obj = cmap
			if grid_style.color_gradient == "discontinuous":
				if isinstance(norm, PiecewiseLinearNorm):
					norm = norm.to_piecewise_constant_norm()

			if grid_style.color_gradient == "discontinuous" and grid_style.pixelated == False:
				cs = self.map.contourf(xc, yc, grid_data.values, levels=grid_style.contour_levels, cmap=cmap_obj, norm=norm, vmin=vmin, vmax=vmax, extend="both", alpha=alpha, zorder=self.zorder)
			else:
				shading = {True: 'flat', False: 'gouraud'}[grid_style.pixelated]
				if shading == 'gouraud':
					## Data must have same size as X and Y
					x, y = xc, yc
				else:
					## Length of X and Y should be one more than data size
					x, y = xe, ye
				if alpha < 1:
					## pcolor needs edge coordinates, pcolormesh needs center coordinates
					x, y = xe, ye
				if grid_style.hillshade_style:
					## Source: http://rnovitsky.blogspot.com.es/2010/04/using-hillshade-image-as-intensity.html
					# TODO: there is also a hillshade function in matplotlib
					# TODO: find a way to add hillshade from another grid
					# (e.g., to add topographic shading to ground-motion map)
					data = grid_data.values
					azimuth = grid_style.hillshade_style.azimuth
					elevation_angle = grid_style.hillshade_style.elevation_angle
					scale = grid_style.hillshade_style.scale

					hillshade = grid_data.calc_hillshade(azimuth, elevation_angle, scale)
					#ny, nx = xe.shape
					## Get RGB of normalized data based on cmap
					#data_min, data_max = data.min(), data.max()
					#rgba = cmap_obj((data - data_min) / float(data_max - data_min))
					rgba = grid_style.color_map_theme(data)
					rgb = rgba[:,:,:3]
					## Form an RGB eqvivalent of shade
					d = hillshade.repeat(3)
					d = d.reshape(rgb.shape)
					## Simulate illumination based on pegtop algorithm
					rgba[:,:,:3] = np.minimum(1., (2 * d * rgb + (rgb*rgb) * (1 - 2 * d)))

					## Hillshade in matplotlib, doesn't work yet
					"""
					from matplotlib.colors import LightSource
					ls = LightSource(azdeg=azimuth, altdeg=elevation_angle)
					dx = x[1,0] - x[0,0]
					dy = y[0,1] - y[0,0]
					#rgba = ls.shade(data, cmap=cmap_obj, blend_mode="overlay",
					#				vert_exag=scale, dx=dx, dy=dy)
					rgba = ls.shade(data, cmap=cmap_obj)
					"""

					## From http://stackoverflow.com/questions/29232439/plotting-an-irregularly-spaced-rgb-image-in-python
					color_tuple = rgba.reshape((rgba.shape[0]*rgba.shape[1], rgba.shape[2]))

					## pcolormesh is more efficient than pcolor, but if alpha
					## is less than zero, it produces ugly gridlines that cannot
					## be removed.
					if alpha == 1:
						## Note: omit alpha parameter or else nodata grid cells
						## will be opaque!
						cs = self.map.pcolormesh(x, y, data, facecolor=color_tuple, shading=shading, linewidth=0, rasterized=True, zorder=self.zorder)
					else:
						#print("Warning: Due to a bug in matplotlib, gridlines are visible when alpha < 1!")
						cs = self.map.pcolor(x, y, data, facecolor=color_tuple, shading=shading, linewidth=0, rasterized=True, alpha=alpha, zorder=self.zorder)

					## This removes default cmap coloring, but colorbar crashes
					cs.set_array(None)
					## Note: nothing helps to remove the gridlines
					#cs.set_rasterized(True)
					#cs.set_edgecolor("face")
					#cs.set_edgecolor('none')
					#cs.set_linewidth(0)
					#cs._is_stroked = False
					## Set alpha of quadmesh faces
					#for i in cs.get_facecolors():
					#	i[3] = alpha
					#for i in cs.get_edgecolors():
					#	i = [1,1,1,0]
						#i[3] = 0
					## Use scalarmappable as cs for colorbar, vmin and vmax must be set
					grid_style.color_map_theme.vmin = (vmin if vmin is not None else data.min())
					grid_style.color_map_theme.vmax = (vmax if vmax is not None else data.max())
					cs = grid_style.color_map_theme.to_scalar_mappable()
				else:
					if alpha == 1:
						## Note: omit alpha parameter or else nodata grid cells
						## will be opaque!
						cs = self.map.pcolormesh(x, y, grid_data.values, cmap=cmap_obj, norm=norm, vmin=vmin, vmax=vmax, shading=shading, linewidth=0, rasterized=True, zorder=self.zorder)
					else:
						cs = self.map.pcolor(x, y, grid_data.values, cmap=cmap_obj, norm=norm, vmin=vmin, vmax=vmax, shading=shading, linewidth=0, rasterized=True, alpha=alpha, zorder=self.zorder)

			self.zorder += 1

		elif grid_style.hillshade_style:
			## Plot hillshading only
			shading = {True: 'flat', False: 'gouraud'}[grid_style.pixelated]
			if shading == 'gouraud':
				x, y = xc, yc
			else:
				x, y = xe, ye
			## Note: do not use variable name 'cmap' here!
			hillshade_cmap = grid_style.hillshade_style.color_map
			if alpha == 1:
				## Note: omit alpha parameter or else nodata grid cells
				## will be opaque!
				self.map.pcolormesh(x, y, grid_data.values, cmap=hillshade_cmap, shading=shading, zorder=self.zorder)
			else:
				self.map.pcolor(x, y, grid_data.values, cmap=hillshade_cmap, shading=shading, alpha=alpha, zorder=self.zorder)
			self.zorder += 1

		if grid_style.line_style:
			line_style = grid_style.line_style
			if not grid_style.color_gradient and cmap:
				## Draw colored contour lines
				cl = self.map.contour(xc, yc, grid_data.values, levels=grid_style.contour_levels, colors=None, cmap=cmap, norm=norm, linewidths=line_style.line_width, alpha=line_style.alpha, zorder=self.zorder)
			else:
				cl = self.map.contour(xc, yc, grid_data.values, levels=grid_style.contour_levels, colors=line_style.line_color, linewidths=line_style.line_width, alpha=line_style.alpha, zorder=self.zorder)
			label_style = line_style.label_style
			if label_style:
				## other font properties do not seem to be supported
				self.ax.clabel(cl, colors='k', inline=True, fontsize=label_style.font_size, fmt=grid_style.label_format, alpha=label_style.alpha, zorder=self.zorder)
			self.zorder += 1

		## Draw color bar
		if cmap:
			colorbar_style = grid_style.colorbar_style
			if colorbar_style:
				if colorbar_style.ticks is None or len(colorbar_style.ticks) == 0:
					if grid_style.contour_levels != []:
						colorbar_style.ticks = grid_style.contour_levels
				if not colorbar_style.format:
					colorbar_style.format = grid_style.label_format
				if not colorbar_style.title:
					colorbar_style.title = legend_label
				colorbar_style.alpha = alpha
				if grid_style.color_gradient:
					self.draw_colorbar(cs, colorbar_style)

	def draw_grid_image_layer(self, grid_data, image_style):
		img_ar = grid_data.warp_to_map(self, **image_style.to_kwargs())
		img_ar = np.rollaxis(img_ar, 0, 3)
		self.map.imshow(img_ar, ax=self.ax, zorder=self.zorder, alpha=image_style.alpha)
		self.zorder += 1

	def draw_image_layer(self, image_data, image_style):
		img_ar = pylab.imread(image_data.filespec)
		lon, lat = image_data.lon, image_data.lat
		[x], [y] = self.lonlat_to_display_coordinates([lon], [lat])
		width = image_style.width or img_ar.shape[1]
		aspect = img_ar.shape[1] / float(img_ar.shape[0])
		height = image_style.height or int(round(width / aspect))
		if image_style.horizontal_alignment == 'left':
			x0, x1 = x, x + width
		elif image_style.horizontal_alignment == 'center':
			x0, x1 = int(round((x - width/2.))), int(round(x + width/2.))
		elif image_style.horizontal_alignment == 'right':
			x0, x1 = x - width, x
		if image_style.vertical_alignment == 'top':
			y0, y1 = y - height, y
		elif image_style.vertical_alignment == 'center':
			y0, y1 = int(round((y - height/2.))), int(round(y + height/2.))
		elif image_style.vertical_alignment == 'bottom':
			y0, y1 = y, y + height
		X, Y = self.map_from_display_coordinates([x0,x1], [y0,y1])
		extent = X + Y
		## Note: self.map.imshow always plots image over entire map region!
		self.ax.imshow(img_ar, extent=extent, zorder=self.zorder, alpha=image_style.alpha)
		self.zorder += 1

	def draw_grid_vector_layer(self, vector_data, vector_style, legend_label=""):
		# TODO: thematic legend with size of vector! (pylab.quiverkey)
		try:
			x, y = vector_data.grdx.get_mesh_coordinates("center")
		except AttributeError:
			x, y = vector_data.grdx.lons, vector_data.grdx.lats
		u, v = vector_data.grdx.values, vector_data.grdy.values
		Q = self.map.quiver(x, y, u, v, latlon=True, zorder=self.zorder, **vector_style.to_kwargs())
		if vector_style.thematic_legend_style:
			# TODO: find mechanism to pass arrow scale and label
			length = 1
			qk = pylab.quiverkey(Q, -1, -1, length, label="", coordinates='axes', labelpos='E')
			label = "%s (%s %s)" % (legend_label, length, vector_data.unit)

			if isinstance(vector_style.thematic_legend_style, (str, unicode)):
				legend_name = vector_style.thematic_legend_style
				legend_artists, legend_labels = self.get_thematic_legend_artists_and_labels(legend_name)
				legend_artists.append(qk)
				legend_labels.append(label)
			else:
				thematic_legend = ThematicLegend([qk], [label], vector_style.thematic_legend_style)
				self.thematic_legends.append(thematic_legend)
		self.zorder == 1

	def draw_colorbar(self, sm, style):
		"""
		sm: scalarmappable
		"""
		# TODO: limit ticks to interval between norm.vmin and norm.vmax,
		# but then we need to pass norm as well...
		if self.cax == "fig":
			cbar = self.map.colorbar(sm, ax=None, fig=self.fig, **style.to_kwargs())
		elif self.cax:
			if style.location in ("top", "bottom"):
				orientation = "horizontal"
			else:
				orientation = "vertical"
			cbar = pylab.colorbar(sm, ax=None, cax=self.cax, orientation=orientation,
						extend=style.extend, spacing=style.spacing,
						ticks=style.ticks, format=style.format, drawedges=style.drawedges,
						alpha=style.alpha)
		else:
			cbar = self.map.colorbar(sm, ax=self.ax, fig=self.fig, **style.to_kwargs())
		# TODO: do set_label and set_ticklabels accept font kwargs?
		cbar.set_label(style.title, size=style.label_size)
		if style.tick_labels:
			cbar.set_ticklabels(style.tick_labels)
		cbar.ax.tick_params(labelsize=style.tick_label_size)
		## Hack to get rid of grid lines if style.alpha is less than 1
		if len(cbar.solids.get_edgecolors()) < 20:
			cbar.solids.set_edgecolor("face")
		else:
			cbar.solids.set_edgecolor("none")
		#for i in cbar.solids.get_edgecolors():
		#	i[3] = style.alpha

		# TODO: implement plotting of colorbar inside map.
		# See: http://stackoverflow.com/questions/18211967/position-colorbar-inside-figure

		# TODO: implement full label_style for both colorbar title and ticks

	def draw_continents(self, continent_style):
		if hasattr(continent_style, "bg_color"):
			## Draw oceans as map background
			self.map.drawmapboundary(fill_color=continent_style.bg_color, color="None", linewidth=0, zorder=-1)
			# Note: zorder not respected by drawlsmask
			#self.map.drawlsmask(land_color=continent_style.fill_color, ocean_color=continent_style.bg_color, lakes=True, resolution=self.resolution, zorder=self.zorder)
		if getattr(continent_style, "fill_color", None):
			lake_color = getattr(continent_style, "bg_color", "None")
			self.map.fillcontinents(color=continent_style.fill_color, lake_color=lake_color, zorder=self.zorder, alpha=continent_style.alpha)
		self.zorder += 1
		if continent_style.line_color:
			self.draw_coastlines(continent_style.to_line_style())

	def draw_coastlines(self, coastline_style):
		self.map.drawcoastlines(linewidth=coastline_style.line_width, color=coastline_style.line_color, linestyle=coastline_style.line_pattern, zorder=self.zorder)
		self.zorder += 1

	def draw_countries(self, style):
		if style.line_color:
			self.map.drawcountries(linewidth=style.line_width, color=style.line_color, linestyle=style.line_pattern, zorder=self.zorder)
			self.zorder += 1

	def draw_rivers(self, style):
		if style.line_color:
			self.map.drawrivers(linewidth=style.line_width, color=style.line_color, linestyle=style.line_pattern, zorder=self.zorder)
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
		#num_points = 10.
		#num_pixels = num_points * self.dpi
		num_pixels = 100.
		display_x0, display_y0 = self.map_to_display_coordinates([x0], [y0])
		display_x1 = display_x0[0] + num_pixels
		x1, y1 = self.map_from_display_coordinates([display_x1], display_y0)
		conv_factor = float(x1[0] - x0) / num_pixels
		#conv_factor = float(x1[0] - x0) * self.dpi / 120 / num_pixels / num_points

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

		## Handle offset
		if focmec_data.style_params.has_key('offset') or focmec_style.offset:
			offsets = focmec_data.style_params.get('offset') or [focmec_style.offset] * len(focmec_data)
			offsets = np.array(offsets)
			offset_coord_frame = focmec_style.offset_coord_frame
			## Compute offset in map units
			if offset_coord_frame == "offset points":
				## Offset in points
				# TODO: this should probably be pixels instead of points
				display_x, display_y = self.lonlat_to_display_coordinates(focmec_data.lons, focmec_data.lats)
				display_x = np.array(display_x) + offsets[:,0]
				display_y = np.array(display_y) + offsets[:,1]
				x, y = self.map_from_display_coordinates(display_x, display_y)
			elif offset_coord_frame == "geographic":
				## Offsets correspond to lon, lat coordinates
				x, y = self.map(offsets[:,0], offsets[:,1])
				#for (lon, lat) in zip(x, y):
				#	print "%s, %s" % (lon, lat)
			elif offset_coord_frame == "data":
				## Offsets correspond to data
				x, y = offsets[:,0], offsets[:,1]
			else:
				raise Exception("offset_coord_frame %s not supported!" % offset_coord_frame)

			## Draw lines between focmec and its original position
			x0, y0 = self.map(focmec_data.lons, focmec_data.lats)
			arrowprops = {"lw": focmec_style.line_width,
						"color": focmec_style.line_color,
						"arrowstyle": "-"}
			for i in range(len(focmec_data)):
				if not np.allclose(offsets[i], 0):
					self.ax.annotate("", (x0[i], y0[i]), xytext=(x[i], y[i]),
							textcoords="data", arrowprops=arrowprops,
							zorder=self.zorder, axes=self.ax)
		else:
			## No offset specified
			x, y = self.map(focmec_data.lons, focmec_data.lats)

		## Draw focal mechanisms
		for i in range(len(focmec_data)):
			## Convert width in pixels to width in map units, normalized to 120 dpi
			width = sizes[i] * conv_factor * self.dpi / 120.
			style = FocmecStyle(size=width, line_width=line_widths[i], line_color=line_colors[i], fill_color=fill_colors[i], bg_color=focmec_style.bg_color, alpha=focmec_style.alpha)
			style = focmec_data.get_overriding_style(style, i)
			b = Beach(focmec_data.sdr[i], xy=(x[i], y[i]), **style.to_kwargs())
			b.set_zorder(self.zorder)
			self.ax.add_collection(b)
		self.zorder += 1

		# Add thematic legend
		if focmec_style.is_thematic:
			legend_artists, legend_labels = [], []
			## Fill color
			if isinstance(focmec_style.fill_color, ThematicStyle) and focmec_style.fill_color.add_legend:
				colorbar_style = focmec_style.fill_color.colorbar_style
				if isinstance(focmec_style.fill_color, ThematicStyleColormap) or colorbar_style:
					if colorbar_style is None and isinstance(focmec_style.thematic_legend_style, ColorbarStyle):
						## interpret thematic_legend_style as colorbar_style
						colorbar_style = focmec_style.thematic_legend_style
					sm = focmec_style.fill_color.to_scalar_mappable()
					self.draw_colorbar(sm, colorbar_style)
				elif isinstance(focmec_style.fill_color, (ThematicStyleIndividual,  ThematicStyleRanges)):
					legend_labels.extend(focmec_style.fill_color.labels)
					for color in focmec_style.fill_color.styles:
						ntl = focmec_style.get_non_thematic_style()
						ntl.fill_color = color
						ntl.size = 10
						## Legend does not support <matplotlib.collections.PatchCollection object
						#b = Beach(focmec_data.sdr[0], xy=(0, 0), **ntl.to_kwargs())
						## Circle patches show up as rectangles in legend...
						#b = matplotlib.patches.Circle((0,0), radius=1, fill=1, fc=color, ec=ntl.line_color, lw=ntl.line_width, alpha=ntl.alpha)
						b = matplotlib.lines.Line2D([0], [0], ls="None", lw=0, **ntl.to_point_style().to_kwargs())
						legend_artists.append(b)
			## Line color
			if isinstance(focmec_style.line_color, ThematicStyle) and focmec_style.line_color.add_legend:
				colorbar_style = focmec_style.line_color.colorbar_style
				if isinstance(focmec_style.line_color, ThematicStyleColormap) or colorbar_style:
					if colorbar_style is None and isinstance(focmec_style.thematic_legend_style, ColorbarStyle):
						## interpret thematic_legend_style as colorbar_style
						colorbar_style = focmec_style.thematic_legend_style
					sm = focmec_style.line_color.to_scalar_mappable()
					self.draw_colorbar(sm, colorbar_style)
				elif isinstance(focmec_style.line_color, (ThematicStyleIndividual,  ThematicStyleRanges)):
					legend_labels.extend(focmec_style.line_color.labels)
					for color in focmec_style.line_color.styles:
						ntl = focmec_style.get_non_thematic_style()
						ntl.line_color = color
						ntl.size = 10
						#ntl.fill_color = "none"
						b = matplotlib.lines.Line2D([0], [0], ls="None", lw=0, **ntl.to_point_style().to_kwargs())
						legend_artists.append(b)
			## Marker size
			if isinstance(focmec_style.size, (ThematicStyleIndividual, ThematicStyleRanges, ThematicStyleGradient)) and focmec_style.size.add_legend:
				legend_labels.extend(focmec_style.size.labels)
				for size in focmec_style.size.styles:
					ntl = focmec_style.get_non_thematic_style()
					ntl.size = size
					b = matplotlib.lines.Line2D([0], [0], ls="None", lw=0, **ntl.to_point_style().to_kwargs())
					legend_artists.append(b)
			## Line width
			if isinstance(focmec_style.line_width, (ThematicStyleIndividual, ThematicStyleRanges, ThematicStyleGradient)) and focmec_style.line_width.add_legend:
				legend_labels.extend(focmec_style.line_width.labels)
				for line_width in focmec_style.line_width.styles:
					ntl = focmec_style.get_non_thematic_style()
					ntl.line_width = line_width
					b = matplotlib.lines.Line2D([0], [0], ls="None", lw=0, **ntl.to_point_style().to_kwargs())
					legend_artists.append(b)

			if focmec_style.thematic_legend_style and len(legend_artists) > 0:
				if isinstance(focmec_style.thematic_legend_style, LegendStyle):
					thematic_legend = ThematicLegend(legend_artists, legend_labels, focmec_style.thematic_legend_style)
					self.thematic_legends.append(thematic_legend)
				elif isinstance(focmec_style.thematic_legend_style, (str, unicode)):
					legend_title = focmec_style.thematic_legend_style
					tl_artists, tl_labels = self.get_thematic_legend_artists_and_labels(legend_title)
					tl_artists.extend(legend_artists)
					tl_labels.extend(legend_labels)

	def draw_wms_layer(self, wms_data, wms_style):
		self.map.wmsimage(wms_data.url, layers=wms_data.layers, verbose=wms_data.verbose, zorder=self.zorder, axes=self.ax, **wms_style.to_kwargs())
		self.zorder += 1

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
		## Not used for the moment
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

		cmap = matplotlib.cm.get_cmap("binary")
		cmap._init()
		cmap._lut[1:,3] = 0
		self.map.imshow(mask, cmap=cmap, zorder=self.zorder)
		self.zorder += 1

	def draw_layers(self):
		## Note: start with zorder = 1, to allow place for map border
		self.zorder = 1
		for l, layer in enumerate(self.layers):
			if isinstance(layer.data, BuiltinData):
				# TODO: legend for builtin data
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
			elif isinstance(layer.data, MultiTextData):
				self._draw_texts(layer.data, layer.style)
			elif isinstance(layer.data, FocmecData):
				self.draw_focmecs(layer.data, layer.style)
			elif isinstance(layer.data, CircleData):
				self.draw_circles(layer.data, layer.style, layer.legend_label)
			elif isinstance(layer.data, GreatCircleData):
				self.draw_great_circles(layer.data, layer.style, layer.legend_label)
			elif isinstance(layer.data, MaskData):
				self.draw_mask(layer.data.polygon, layer.style, layer.data.outside)
			elif isinstance(layer.data, (PointData, MultiPointData)):
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
				if not isinstance(layer.legend_label, dict):
					legend_label = {"points": layer.legend_label, "lines": layer.legend_label, "polygons": layer.legend_label}
				else:
					legend_label = layer.legend_label
				self.draw_composite_layer(point_data=point_data, point_style=point_style, line_data=line_data, line_style=line_style, polygon_data=polygon_data, polygon_style=polygon_style, text_data=text_data, text_style=text_style, legend_label=legend_label)
			elif isinstance(layer.data, MeshGridVectorData):
				self.draw_grid_vector_layer(layer.data, layer.style, layer.legend_label)
			elif isinstance(layer.data, GridData):
				if isinstance(layer.style, GridStyle):
					self.draw_grid_layer(layer.data, layer.style, layer.legend_label)
				elif isinstance(layer.style, GridImageStyle):
					self.draw_grid_image_layer(layer.data, layer.style)
			elif isinstance(layer.data, ImageData):
				self.draw_image_layer(layer.data, layer.style)
			elif isinstance(layer.data, WMSData):
				self.draw_wms_layer(layer.data, layer.style)

	def draw_decoration(self):
		self.draw_graticule()
		self.draw_scalebar()
		self.draw_legend()
		self.draw_title()
		self.draw_map_border()

	def draw_legend(self):
		## Thematic legends
		for thematic_legend in self.thematic_legends:
			if thematic_legend.style:
				title = thematic_legend.style.title
				if isinstance(title, str):
					title = title.decode('iso-8859-1')
				title_style = thematic_legend.style.title_style

				tl = self.ax.legend(thematic_legend.artists, thematic_legend.labels, handler_map=self.legend_handler_map, **thematic_legend.style.to_kwargs())
				tl.set_title(title, prop=title_style.to_font_props())
				## Align title to center...
				ha = getattr(title_style, 'horizontal_alignment', 'center')
				if ha != 'left':
					ttl = tl.get_title()
					ttl.set_ha(ha)
					renderer = self.fig.canvas.get_renderer()
					shift = ttl.get_window_extent(renderer).width
					# Note: fig.dpi must be set at final rendering value for this to work !
					if ha == 'center':
						ttl.set_position((shift/2., 0))
					if ha == 'right':
						ttl.set_position((shift, 0))
				## Set frame color and linewidth
				frame = tl.get_frame()
				frame.set_edgecolor(thematic_legend.style.frame_color)
				frame.set_facecolor(thematic_legend.style.fill_color)
				frame.set_linewidth(thematic_legend.style.frame_width)

				tl.set_zorder(self.zorder)
				self.ax.add_artist(tl)

		## Main legend
		if self.legend_style and len(self.legend_artists):
			title = self.legend_style.title
			if isinstance(title, str):
				title = title.decode('iso-8859-1')
			title_style = self.legend_style.title_style

			#ml = self.ax.legend(loc=loc+1, prop=label_style.to_font_props(), markerscale=marker_scale, frameon=frame_on, fancybox=fancy_box, shadow=shadow, ncol=ncol, borderpad=border_pad, labelspacing=label_spacing, handlelength=handle_length, handleheight=handle_height, handletextpad=handle_text_pad, borderaxespad=border_axes_pad, columnspacing=column_spacing, numpoints=numpoints)
			ml = self.ax.legend(self.legend_artists, self.legend_labels, handler_map=self.legend_handler_map, **self.legend_style.to_kwargs())
			if ml:
				ml.set_title(title, prop=title_style.to_font_props())
				## Align title to center...
				ha = getattr(title_style, 'horizontal_alignment', 'center')
				if ha != 'left':
					ttl = ml.get_title()
					ttl.set_ha(ha)
					renderer = self.fig.canvas.get_renderer()
					shift = ttl.get_window_extent(renderer).width
					if ha == 'center':
						ttl.set_position((shift/2.,0))
					if ha == 'right':
						ttl.set_position((shift,0))
					ml.set_zorder(self.zorder)
				## Set frame color and linewidth
				frame = ml.get_frame()
				frame.set_edgecolor(self.legend_style.frame_color)
				frame.set_facecolor(self.legend_style.fill_color)
				frame.set_linewidth(self.legend_style.frame_width)

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
		if self.graticule_style:
			#if abs(self.region[1] - self.region[0]) == 360:
			#	labelstyle = "+/-"
			#else:
			#	labelstyle = ""
			if self.dlon != None:
				meridian_style = self.graticule_style.copy()
				meridian_style.annot_axes = meridian_style.annot_axes.replace('W', '').replace('E', '')
				first_meridian = np.ceil(self.region[0] / self.dlon) * self.dlon
				last_meridian = np.floor(self.region[1] / self.dlon) * self.dlon + self.dlon
				meridians = np.arange(first_meridian, last_meridian, self.dlon)
				self.map.drawmeridians(meridians, zorder=self.zorder, **meridian_style.to_kwargs())
			if self.dlat != None:
				parallel_style = self.graticule_style.copy()
				parallel_style.annot_axes = parallel_style.annot_axes.replace('N', '').replace('S', '')
				first_parallel = np.ceil(self.region[2] / self.dlat) * self.dlat
				last_parallel = np.floor(self.region[3] / self.dlat) * self.dlat + self.dlat
				parallels = np.arange(first_parallel, last_parallel, self.dlat)
				self.map.drawparallels(parallels, zorder=self.zorder, **parallel_style.to_kwargs())
			self.zorder += 1

	def draw_scalebar(self):
		if self.scalebar_style:
			lon0, lat0 = self.lon_0, self.lat_0
			self.map.drawmapscale(lon0=lon0, lat0=lat0, zorder=self.zorder, **self.scalebar_style.to_kwargs())
			self.zorder += 1

	def draw_map_border(self):
		if self.border_style:
			## Note: zorder left to default
			## High zorder values don't work with global projections
			self.map.drawmapboundary(zorder=None, ax=self.ax, **self.border_style.to_kwargs())

	def draw(self):
		## Note: We call draw_map_border twice, once at the beginning
		## and once at the end (in draw_decoration).
		## The former is necessary to ensure correct drawing of frontlines
		## which depends on ax.transData being correctly set
		self.draw_map_border()
		self.draw_layers()
		self.draw_decoration()
		self.is_drawn = True

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

	def lonlat_to_map_coordinates(self, lons, lats):
		return self.map(lons, lats)

	def lonlat_to_projected_coordinates(self, lons, lats):
		"""
		Convert geographic to projected coordinates using ogr.
		For some projections, this gives another result than meth:`lonlat_to_map_coordinates`
		"""
		from mapping.geo.coordtrans import transform_array_coordinates, wgs84
		x, y = transform_array_coordinates(wgs84, self.get_srs(), lons, lats)
		return (x, y)

	def projected_to_lonlat_coordinates(self, x, y):
		from mapping.geo.coordtrans import transform_array_coordinates, wgs84
		lons, lats = transform_coordinates(self.get_srs(), wgs84, x, y)
		return (lons, lats)

	def map_to_display_coordinates(self, x, y):
		return zip(*self.ax.transData.transform(zip(x, y)))

	def map_to_lonlat_coordinates(self, x, y):
		return self.map(x, y, inverse=True)

	def lonlat_from_display_coordinates(self, display_x, display_y):
		## Convert display coordinates to lon, lat
		x, y = self.map_from_display_coordinates(display_x, display_y)
		return self.map(x, y, inverse=True)

	def map_from_display_coordinates(self, display_x, display_y):
		return zip(*self.ax.transData.inverted().transform(zip(display_x, display_y)))

	def get_srs(self):
		import osr
		srs = osr.SpatialReference()
		srs.ImportFromProj4(self.map.proj4string)
		return srs

	def get_srs_wkt(self):
		srs = self.get_srs()
		return srs.ExportToWkt()

	def plot(self, fig_filespec=None, fig_width=0, dpi=None):
		"""
		:param fig_filespec:
			str, full path to output file or None (plot on screen)
			or "hold" (do not show plot)
		"""
		#fig = pylab.figure()
		#subplot = fig.draw_subplot(111)
		#subplot.set_axes(self.ax)
		if dpi:
			if fig_filespec:
				default_figsize = pylab.rcParams['figure.figsize']
				if fig_width:
					fig_width /= 2.54
					dpi = dpi * (fig_width / default_figsize[0])
			if dpi != self.dpi:
				self.fig.set_dpi(dpi)
		if not self.is_drawn:
			self.draw()
		if fig_filespec == "hold":
			return
		elif fig_filespec:
			pylab.savefig(fig_filespec, dpi=dpi)
			pylab.clf()
		else:
			pylab.show()
		## Reset dpi to original value
		self.fig.set_dpi(self.dpi)

	def get_map_image(self, dpi=120):
		"""
		Get image corresponding to map area, cropped to map frame.
		Note that map is supposed to be rectangular, and that title and tick
		labels will be removed.

		:param dpi:
			int, image resolution (default: 120)

		:return:
			instance of :class:`PIL.Image`
		"""
		from PIL import Image

		if dpi and dpi != self.dpi:
			self.fig.set_dpi(dpi)
		if not self.is_drawn:
			self.draw()
		self.fig.canvas.draw()
		subplot = self.fig.add_subplot(111)
		#subplot.set_axes(self.ax)
		subplot.axes = self.ax

		lons = [self.llcrnrlon, self.urcrnrlon]
		lats = [self.llcrnrlat, self.urcrnrlat]

		x, y = self.lonlat_to_display_coordinates(lons, lats)
		left, right = map(int, np.round(x))
		lower, upper = map(int, np.round(y))

		buf, size = self.fig.canvas.print_to_buffer()
		image = Image.frombuffer('RGBA', size, buf, 'raw', 'RGBA', 0, 1)
		image = image.crop((left, lower, right, upper))

		## Reset dpi to original value
		self.fig.set_dpi(self.dpi)

		return image

	def export_geotiff(self, out_filespec, dpi=120, verbose=False):
		"""
		Export map to GeoTiff.
		May only work if map area is rectangular.

		:param out_filespec:
			str, full path to output file
		:param dpi:
			int, image resolution (default: 120)
		"""
		from mapping.geo.geotiff import write_multi_band_geotiff

		img = self.get_map_image(dpi=dpi)
		if verbose:
			print img.size
			png_filespec = os.path.splitext(out_filespec)[0] + ".png"
			print png_filespec
			img.save(png_filespec, format='png', dpi=(dpi, dpi))

		srs = self.get_srs()

		lons = [self.llcrnrlon, self.urcrnrlon]
		lats = [self.llcrnrlat, self.urcrnrlat]
		# TODO: understand why some projections work with map coordinates,
		# some with projected coordinates, and some not at all
		if self.projection in ("merc", "cyl", "lcc", "laea", "cass", "poly", "eqdc", "aea", "gall", "mill"):
			x, y = self.lonlat_to_projected_coordinates(lons, lats)
		elif self.projection in ("tmerc", "cea", "aeqd", "stere"):
			x, y = self.lonlat_to_map_coordinates(lons, lats)
		else:
			raise Exception("Projection %s not supported!" % self.projection)
		extent = (x[0], x[1], y[0], y[1])
		if verbose:
			print("Extent: %s" % (extent,))
			print srs.ExportToWkt()

		write_multi_band_geotiff(out_filespec, img, extent, srs, cell_registration="corner", north_up=True)

	def move_layer(self, cur_index_or_name, new_index):
		"""
		Move layer to another position

		:param cur_index_or_name:
			int, current layer index (may be negative)
			or str, layer name
		:param new_index:
			int, target layer index (may be negative)
		"""
		if not isinstance(cur_index_or_name, int):
			cur_index = self.get_named_layer_index(cur_index_or_name)
		else:
			cur_index = cur_index_or_name

		if cur_index < 0:
			cur_index = len(self.layers) + cur_index
		if new_index < 0:
			new_index = len(self.layers) + new_index
		layer = self.layers.pop(cur_index)
		self.layers.insert(new_index, layer)

	def move_layer_up(self, cur_index_or_name):
		"""
		Move layer one position upward

		:param cur_index_or_name:
			int, current layer index (may be negative)
			or str, layer name
		"""
		self.move_layer(cur_index_or_name, cur_index+1)

	def move_layer_down(self, cur_index_or_name):
		"""
		Move layer one position downward

		:param cur_index_or_name:
			int, current layer index (may be negative)
			or str, layer name
		"""
		self.move_layer(cur_index_or_name, cur_index-1)

	def move_layer_top(self, cur_index_or_name):
		"""
		Move layer to top

		:param cur_index_or_name:
			int, current layer index (may be negative)
			or str, layer name
		"""
		self.move_layer(cur_index_or_name, len(self.layers))

	def move_layer_bottom(self, cur_index_or_name):
		"""
		Move layer to bottom

		:param cur_index_or_name:
			int, current layer index (may be negative)
			or str, layer name
		"""
		self.move_layer(cur_index_or_name, 0)

	def get_layer_names(self):
		"""
		Obtain list of layer names

		:return:
			list of strings
		"""
		return [layer.name for layer in self.layers]

	def get_named_layer_index(self, layer_name):
		"""
		Obtain index of named layer

		:param layer_name:
			str, layer name

		:return:
			int, layer index
		"""
		return self.get_layer_names().index(layer_name)

	def get_layer_by_name(self, layer_name):
		"""
		Fetch layer with given name

		:param layer_name:
			str, layer name

		:return:
			instance of :class:`MapLayer`
		"""
		return self.layers[self.get_named_layer_index(layer_name)]



if __name__ == "__main__":
	import os

	region = (0,8,49,52)
	projection = "tmerc"
	title = "Test"
	resolution = "h"
	graticule_interval = (2, 1)

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
	thematic_legend_style = LegendStyle(title="Area sources", location=2, shadow=True, fancy_box=True, label_spacing=0.4)
	label_style = TextStyle()
	line_style = LineStyle(line_width=2, label_style=label_style)
	fill_color = ThematicStyleIndividual(["SLZ", "RVG"], ["green", "orange"], value_key="ShortName")
	polygon_style = PolygonStyle(line_width=2, fill_color=fill_color, alpha=0.5, label_style=label_style, thematic_legend_style=thematic_legend_style)
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
	colorbar_style = ColorbarStyle(format='%.2f')
	grid_style = GridStyle(color_map_theme, color_gradient="continuous", line_style=LineStyle(label_style=TextStyle()), contour_levels=contour_levels, colorbar_style=colorbar_style)
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
	thematic_legend_style = LegendStyle(title="Magnitude", location=3, shadow=True, fancy_box=True, label_spacing=0.7)
	colorbar_style = ColorbarStyle(title="Depth", location="bottom", format="%d")
	thematic_size = ThematicStyleGradient([1,6], [2, 24], value_key="magnitude")
	#thematic_color = ThematicStyleColormap(value_key="depth")
	thematic_color = ThematicStyleRanges([0,1,10,25,50], ['red', 'orange', 'yellow', 'green'], value_key="depth", colorbar_style=colorbar_style)
	#thematic_color = ThematicStyleRanges([1350,1910,2050], ['green', (1,1,1,0)], value_key="year")
	#point_style = PointStyle(shape='+', size=thematic_size, fill_color='k', line_color=thematic_color, line_width=0.5)
	point_style = PointStyle(shape='o', size=thematic_size, line_color='k', fill_color=thematic_color, line_width=0.5, thematic_legend_style=thematic_legend_style)
	layer = MapLayer(point_data, point_style, legend_label="ROB Catalog")
	layers.append(layer)

	## Point data: NPP sites
	point_data = MultiPointData([4.259, 5.274], [51.325, 50.534], values=["Doel", "Tihange"], labels=["Doel", "Tihange"])
	thematic_shape = ThematicStyleIndividual(["Doel", "Tihange"], ['o', 's'])
	thematic_legend_style = LegendStyle(title="NPP", location=1)
	point_style = PointStyle(shape=thematic_shape, fill_color='w', label_style=TextStyle(color='w', horizontal_alignment="left", offset=(10,0)), thematic_legend_style=thematic_legend_style)
	layer = MapLayer(point_data, point_style, legend_label="NPP")
	layers.append(layer)

	## Focal mechanisms
	thematic_size = ThematicStyleGradient([3,4,5,6,7], [20,30,40,50,60], value_key="magnitude")
	thematic_color = ThematicStyleIndividual(["normal", "reverse"], ['g', "b"], value_key="sof")
	focmecs = FocmecData([4.5, 6.0], [51., 49.5], sdr=[[135, 60, -90], [0, 30, 90]], values={"magnitude": [4,6], "sof": ["normal", "reverse"]})
	focmec_style = FocmecStyle(size=thematic_size, fill_color=thematic_color)
	layer = MapLayer(focmecs, focmec_style)
	layers.append(layer)

	#layers = []
	legend_style = LegendStyle(location=0)
	title_style = DefaultTitleTextStyle
	title_style.color = "red"
	title_style.weight = "bold"
	map = LayeredBasemap(layers, title, projection, region=region, title_style=title_style, graticule_interval=graticule_interval, resolution=resolution, legend_style=legend_style)
	mask_polygon = PolygonData([2,3,4,4,3,2,2], [50,50,50,51,51,51,50])
	map.draw_mask(mask_polygon, outside=False)

	#fig_filespec = r"C:\Temp\layeredbasemap.png"
	fig_filespec = None
	map.draw()
	map.plot(fig_filespec=fig_filespec)

