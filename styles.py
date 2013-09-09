"""
Styles used in LayeredBasemap
"""

import numpy as np
import matplotlib



class FontStyle(object):
	"""
	Class representing matplotlib font properties
	Used in e.g., plot titles

	:param font_family:
		string, font family or font name
		("serif" | "sans-serif" | "cursive" | "fantasy" | "monospace")
		(default: "sans-serif")
	:param font_style:
		string, font style ("normal" | "italic" | "oblique")
		(default: "normal")
	:param font_variant:
		string, font variant ("normal" | "small-caps")
		(default: "normal")
	:param font_stretch:
		numeric value in range 0 - 1000 or string
		("ultra-condensed" | "extra-condensed" | "condensed" | "semi-condensed" |
		"normal" | "semi-expanded" | "expanded" | "extra-expanded" | "ultra-expanded")
		(default: "normal")
	:param font_weight:
		numeric value in range 0-1000 or string
		("ultralight" | "light" | "normal" | "regular" | "book" | "medium" |
		"roman" | "semibold" | "demibold" | "demi" | "bold" | "heavy" |
		"extra bold" | "black")
		(default: "normal")
	:param font_size:
		int, font size in points, or string ("xx-small" | "x-small" | "small" |
		"medium" | "large" | "x-large" | "xx-large")
		(default: 12)
	"""
	def __init__(self, font_family="sans-serif", font_style="normal", font_variant="normal", font_stretch="normal", font_weight="normal", font_size=12):
		self.font_family = font_family
		self.font_style = font_style
		self.font_variant = font_variant
		self.font_stretch = font_stretch
		self.font_weight = font_weight
		self.font_size = font_size

	def get_font_prop(self):
		"""
		Return instance of :class:`FontProperties`
		"""
		fp = matplotlib.font_manager.FontProperties(family=self.font_family, style=self.font_style, variant=self.font_variant, stretch=self.font_stretch, weight=self.font_weight, size=self.font_size)
		return fp


class TextStyle(FontStyle):
	"""
	Class defining how texts are plotted in matplotlib

	:param font_family:
	:param font_style:
	:param font_variant:
	:param font_stretch:
	:param font_weight:
	:param font_size:
		See :class:`FontStyle`
	:param color:
		matplotlib color specification (default: "k")
	:param background_color:
		matplotlib color specification (default: "None")
	:param line_spacing:
		Float, line spacing (multiple of font size)
		(default: 12)
	:param rotation:
		Float, angle in degrees, or string ("vertical" | "horizontal")
		(default: 0.)
	:param horizontal_alignment:
		string, where text will be horizontally aligned
		("center" | "right" | "left")
		(default: "center")
	:param vertical_alignment:
		string, where text will be vertically aligned
		("center" | "top" | "bottom" | "baseline")
		(default: "center")
	:param multi_alignment:
		String, how multiple lines of text will be aligned
		("left" | "right" | "center")
		(default: "center")
	:param offset:
		tuple, horizontal and vertical offset in points (default: (0, 0))
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	"""
	def __init__(self, font_family="sans-serif", font_style="normal", font_variant="normal", font_stretch="normal", font_weight="normal", font_size=12, color='k', background_color="None", line_spacing=12, rotation=0, horizontal_alignment="center", vertical_alignment="center", multi_alignment="center", offset=(0,0), alpha=1.):
		super(TextStyle, self).__init__(font_family, font_style, font_variant, font_stretch, font_weight, font_size)
		self.color = color
		self.background_color = background_color
		self.line_spacing = line_spacing
		self.rotation = rotation
		self.horizontal_alignment = horizontal_alignment
		self.vertical_alignment = vertical_alignment
		self.multi_alignment = multi_alignment
		self.offset = offset
		self.alpha = alpha

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the text and annotate functions
		"""
		d = {}
		d["family"] = self.font_family
		d["size"] = self.font_size
		d["weight"] = self.font_weight
		d["style"] = self.font_style
		d["stretch"] = self.font_stretch
		d["variant"] = self.font_variant
		d["color"] = self.color
		d["backgroundcolor"] = self.background_color
		d["linespacing"] = self.line_spacing
		d["rotation"] = self.rotation
		d["ha"] = self.horizontal_alignment
		d["va"] = self.vertical_alignment
		d["multialignment"] = self.multi_alignment
		d["alpha"] = self.alpha
		return d


DefaultTitleTextStyle = TextStyle(font_size="large", horizontal_alignment="center", vertical_alignment="bottom")


class PointStyle:
	"""
	:param shape:
		Char, marker shape format string, or instance of :class:`ThematicStyle`
		Available format strings:
			'.'	point marker
			','	pixel marker
			'o'	circle marker
			'v'	triangle_down marker
			'^'	triangle_up marker
			'<'	triangle_left marker
			'>'	triangle_right marker
			'1'	tri_down marker
			'2'	tri_up marker
			'3'	tri_left marker
			'4'	tri_right marker
			's'	square marker
			'p'	pentagon marker
			'*'	star marker
			'h'	hexagon1 marker
			'H'	hexagon2 marker
			'+'	plus marker
			'x'	x marker
			'D'	diamond marker
			'd'	thin_diamond marker
			'|'	vline marker
			'_'	hline marker
		(default: 'o')
	:param size:
		Int, marker size, or instance of :class:`ThematicStyle`
		(default: 10)
	:param line_width:
		Float, marker line width, or instance of :class:`ThematicStyle`
		(default: 1)
	:param line_color:
		matplotlib color spec or instance of :class:`ThematicStyle`
		(default: 'k')
	:param fill_color:
		matplotlib color spec or instance of :class:`ThematicStyle`
		(default: "None")
	:param fill_style:
		String, marker fill style ("full" | "left" | "right" | "bottom" |
		"top" | "none")
		(default: "full")
	:param label_style:
		instance of :class:`TextStyle`. If None, no labels will be plotted
		(default: None)
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	:param thematic_legend_style:
		instance of :class:`LegendStyle`. If None, thematic legend labels
		will be added to main legend
		(default: None)

	Note: only one of line_color / fill_color may be a thematic style.
	Thematic line_color only works for markers like '+'
	Thematic fill_color only works for markers like 'o'
	"""
	def __init__(self, shape='o', size=10, line_width=1, line_color='k', fill_color='None', fill_style="full", label_style=None, alpha=1., thematic_legend_style=None):
		self.shape = shape
		self.size = size
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.fill_style = fill_style
		self.label_style = label_style
		self.alpha = alpha
		self.thematic_legend_style = thematic_legend_style
		## Adjust label spacing of thematic legend to accommodate largest symbols
		if isinstance(self.size, ThematicStyle):
			max_size = max(size.styles)
			self.thematic_legend_style.label_spacing = max(max_size*0.5/10, self.thematic_legend_style.label_spacing)

	def is_thematic(self):
		"""
		Determine whether style has thematic style features

		:return:
			Bool
		"""
		if (isinstance(self.shape, ThematicStyle) or isinstance(self.size, ThematicStyle) or
			isinstance(self.line_width, ThematicStyle) or isinstance(self.line_color, ThematicStyle) or
			isinstance(self.fill_color, ThematicStyle)):
			return True
		else:
			return False

	def get_non_thematic_style(self):
		"""
		Copy style, replacing thematic style features with default values

		:return:
			instance of :class:`PointStyle`
		"""
		if isinstance(self.shape, ThematicStyle):
			shape = 'o'
		else:
			shape = self.shape
		if isinstance(self.size, ThematicStyle):
			size = 10
		else:
			size = self.size
		if isinstance(self.line_width, ThematicStyle):
			line_width = 1
		else:
			line_width = self.line_width
		if isinstance(self.line_color, ThematicStyle):
			line_color = 'k'
		else:
			line_color = self.line_color
		if isinstance(self.fill_color, ThematicStyle):
			fill_color = 'none'
		else:
			fill_color = self.fill_color
		return PointStyle(shape, size, line_width, line_color, fill_color, self.fill_style, self.label_style, self.alpha, self.thematic_legend_style)

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the text and annotate functions
		"""
		d = {}
		d["marker"] = self.shape
		d["ms"] = self.size
		d["mew"] = self.line_width
		d["mfc"] = self.fill_color
		d["mec"] = self.line_color
		d["fillstyle"] = self.fill_style
		d["alpha"] = self.alpha
		return d


class LineStyle:
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', label_style=None, alpha=1., thematic_legend_style=None):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.label_style = label_style
		self.alpha = alpha
		self.thematic_legend_style = thematic_legend_style
		# TODO: dash_capstyle, dash_joinstyle, dashes, drawstyle, solid_capstyle, solid_joinstyle

	def is_thematic(self):
		if (isinstance(self.line_pattern, ThematicStyle) or isinstance(self.line_width, ThematicStyle)
			or isinstance(self.line_color, ThematicStyle)):
			return True
		else:
			return False

	def get_non_thematic_style(self):
		if isinstance(self.line_pattern, ThematicStyle):
			line_pattern = '-'
		else:
			line_pattern = self.line_pattern
		if isinstance(self.line_width, ThematicStyle):
			line_width = 1
		else:
			line_width = self.line_width
		if isinstance(self.line_color, ThematicStyle):
			line_color = 'k'
		else:
			line_color = self.line_color
		return LineStyle(line_pattern, line_width, line_color, self.label_style, self.alpha, self.thematic_legend_style)

	def to_kwargs(self):
		d = {}
		d["ls"] = self.line_pattern
		d["lw"] = self.line_width
		d["color"] = self.line_color
		d["alpha"] = self.alpha
		return d


class PolygonStyle:
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', fill_color='w', fill_hatch=None, label_style=None, alpha=1., thematic_legend_style=None):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.fill_hatch = fill_hatch
		self.label_style = label_style
		self.alpha = alpha
		self.thematic_legend_style = thematic_legend_style
		# TODO: check line_patterns ('solid' versus '-' etc)

	def is_thematic(self):
		if (isinstance(self.line_pattern, ThematicStyle) or isinstance(self.line_width, ThematicStyle)
			or isinstance(self.line_color, ThematicStyle) or isinstance(self.fill_color, ThematicStyle)
			or isinstance(self.fill_hatch, ThematicStyle)):
			return True
		else:
			return False

	def get_non_thematic_style(self):
		if isinstance(self.line_pattern, ThematicStyle):
			line_pattern = 'solid'
		else:
			line_pattern = self.line_pattern
		if isinstance(self.line_width, ThematicStyle):
			line_width = 1
		else:
			line_width = self.line_width
		if isinstance(self.line_color, ThematicStyle):
			line_color = 'k'
		else:
			line_color = self.line_color
		if isinstance(self.fill_color, ThematicStyle):
			fill_color = 'w'
		else:
			fill_color = self.fill_color
		if isinstance(self.fill_hatch, ThematicStyle):
			fill_hatch = None
		else:
			fill_hatch = self.fill_hatch
		return PolygonStyle(line_pattern, line_width, line_color, fill_color, fill_hatch, self.label_style, self.alpha, self.thematic_legend_style)

	def to_line_style(self):
		return LineStyle(self.line_pattern, self.line_width, self.line_color, self.label_style, self.alpha, self.thematic_legend_style)

	def to_kwargs(self):
		d = {}
		d["ls"] = self.line_pattern
		d["lw"] = self.line_width
		d["ec"] = self.line_color
		d["fc"] = self.fill_color
		d["hatch"] = self.fill_hatch
		d["alpha"] = self.alpha
		return d


class FocmecStyle:
	def __init__(self, size=50, line_width=1, line_color='k', fill_color='k', bg_color='w', alpha=1., thematic_legend_style=None):
		self.size = size
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.bg_color = bg_color
		self.alpha = alpha
		self.thematic_legend_style = thematic_legend_style

	def is_thematic(self):
		if (isinstance(self.size, ThematicStyle) or isinstance(self.line_width, ThematicStyle) or
			isinstance(self.line_color, ThematicStyle) or isinstance(self.fill_color, ThematicStyle)):
			return True
		else:
			return False

	def get_non_thematic_style(self):
		if isinstance(self.size, ThematicStyle):
			size = 50
		else:
			size = self.size
		if isinstance(self.line_width, ThematicStyle):
			line_width = 1
		else:
			line_width = self.line_width
		if isinstance(self.line_color, ThematicStyle):
			line_color = 'k'
		else:
			line_color = self.line_color
		if isinstance(self.fill_color, ThematicStyle):
			fill_color = 'k'
		else:
			fill_color = self.fill_color
		bg_color = self.bg_color
		return FocmecStyle(size, line_width, line_color, fill_color, bg_color, self.alpha, self.thematic_legend_style)


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
	def __init__(self, value_key=None, add_legend=True, colorbar_style=None):
		self.value_key = value_key
		self.add_legend = add_legend
		self.colorbar_style = colorbar_style

	def apply_value_key(self, values):
		if self.value_key == None:
			return values
		else:
			return values[self.value_key]


class ThematicStyleIndividual(ThematicStyle):
	def __init__(self, values, styles, labels=[], value_key=None, add_legend=True, colorbar_style=None):
		super(ThematicStyleIndividual, self).__init__(value_key, add_legend, colorbar_style)
		self.values = values
		self.styles = styles
		self.style_dict = {}
		for value, style in zip(self.values, self.styles):
			self.style_dict[value] = style
		if labels:
			self.labels = labels
		else:
			self.labels = []
			for val in self.values:
				if isinstance(val, str):
					self.labels.append(val.decode('iso-8859-1'))
				elif isinstance(val, unicode):
					self.labels.append(val)
				else:
					self.labels.append(str(val))

	def __call__(self, values):
		"""
		values can be numbers or strings
		"""
		return [self.style_dict[val] for val in self.apply_value_key(values)]

	def to_colormap(self):
		try:
			cmap = matplotlib.colors.ListedColormap(self.styles, name=self.value_key)
		except:
			pass
		else:
			return cmap

	def get_norm(self):
		# TODO: can probably be replaced with matplotlib.colors.from_levels_and_colors
		# in newer versions of matplotlib
		if isinstance(self.values[0], (int, float)):
			values = np.array(self.values)
		else:
			values = np.arange(len(self.values))
		diff = values[1:] - values[:-1]
		boundaries = values[1:] - diff / 2.
		boundaries = np.concatenate([[values[0] - diff[0] / 2.], boundaries, [values[-1] + diff[-1] / 2.]])
		return matplotlib.colors.BoundaryNorm(boundaries, len(self.values))

	def to_scalar_mappable(self):
		norm = self.get_norm()
		cmap = self.to_colormap()
		return matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)


class ThematicStyleRanges(ThematicStyle):
	def __init__(self, values, styles, labels=[], value_key=None, add_legend=True, colorbar_style=None):
		"""
		values must be monotonically increasing or decreasing
		styles may be colors
		values contains one element less than styles
		"""
		super(ThematicStyleRanges, self).__init__(value_key, add_legend, colorbar_style)
		self.values = np.array(values, dtype='f')
		self.styles = styles
		if labels:
			self.labels = labels
		else:
			self.labels = []
			for i in range(len(self.styles)):
				self.labels.append("%s - %s" % (self.values[i], self.values[i+1]))

	def __call__(self, values):
		"""
		values must be numbers
		"""
		bin_indexes = np.digitize(self.apply_value_key(values), self.values) - 1
		return [self.styles[bi] for bi in bin_indexes]

	def to_colormap(self):
		# TODO: possible to check if a style spec is a matplotlib color spec?
		try:
			cmap = matplotlib.colors.ListedColormap(self.styles, name=self.value_key)
		except:
			pass
		else:
			return cmap

	def get_norm(self):
		return matplotlib.colors.BoundaryNorm(self.values, len(self.styles))

	def to_scalar_mappable(self):
		#cmap, norm = matplotlib.colors.from_levels_and_colors(self.values, self.styles)
		cmap = self.to_colormap()
		norm = self.get_norm()
		return matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)


class ThematicStyleGradient(ThematicStyle):
	def __init__(self, values, styles, labels=[], value_key=None, add_legend=True, colorbar_style=None):
		"""
		values must be monotonically increasing or decreasing
		styles must be numbers or colors
		"""
		super(ThematicStyleGradient, self).__init__(value_key, add_legend, colorbar_style)
		self.values = np.array(values, dtype='f')
		self.styles = styles
		if labels:
			self.labels = labels
		else:
			self.labels = map(str, self.values)

	def __call__(self, values):
		try:
			return np.interp(self.apply_value_key(values), self.values, self.styles)
		except:
			sm = self.to_scalar_mappable()
			return sm.to_rgba(self.apply_value_key(values), alpha=self.alpha)
			#cmap = self.to_colormap()
			#norm = self.get_norm()
			#return cmap(norm(self.apply_value_key(values)))

	def to_colormap(self):
		x = self.values.max()
		return matplotlib.colors.LinearSegmentedColormap.from_list(self.value_key, zip(x, self.styles))

	def get_norm(self):
		# TODO: use LevelNorm !
		return matplotlib.colors.Normalize(vmin=self.values.min(), vmax=self.values.max())

	def to_scalar_mappable(self):
		norm = self.get_norm()
		cmap = self.to_colormap()
		return matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)


class ThematicStyleColormap(ThematicStyle):
	def __init__(self, color_map="jet", norm=None, vmin=None, vmax=None, alpha=1.0, value_key=None, add_legend=True, colorbar_style=None):
		super(ThematicStyleColormap, self).__init__(value_key, add_legend, colorbar_style)
		self.color_map = color_map
		self.norm = norm
		self.vmin = vmin
		self.vmax = vmax
		self.alpha = alpha
		#TODO set alpha in self.color_map  ??

	@property
	def values(self):
		norm = self.get_norm()
		return np.array([norm.vmin, norm.vmax])

	def __call__(self, values):
		#from matplotlib.cm import ScalarMappable
		#sm = ScalarMappable(self.color_map, self.norm)
		#sm.set_clim(self.vmin, self.vmax)
		sm = self.to_scalar_mappable()
		return sm.to_rgba(self.apply_value_key(values), alpha=self.alpha)

	def get_norm(self):
		if not self.norm:
			norm = matplotlib.colors.Normalize(self.vmin, self.vmax)
		else:
			norm = self.norm
		return norm

	def to_colormap(self):
		return self.color_map

	def to_scalar_mappable(self):
		norm = self.get_norm()
		return matplotlib.cm.ScalarMappable(norm=norm, cmap=self.color_map)


class ColorbarStyle:
	def __init__(self, title="", location="bottom", size='5%', pad='10%', extend="neither", spacing="uniform", ticks=None, format=None, drawedges=False, alpha=1.):
		self.title = title
		self.location = location
		if location in ("top", "bottom"):
			self.orientation = "horizontal"
		else:
			self.orientation = "vertical"
		#self.orientation = orientation
		#self.fraction = fraction
		self.size = size
		self.pad = pad
		#if pad:
		#	self.pad = pad
		#else:
		#	if orientation == "horizontal":
		#		self.pad = 0.15
		#	else:
		#		self.pad = 0.05
		#self.shrink = shrink
		#self.aspect = aspect
		#self.anchor = anchor
		#if anchor:
		#	self.anchor = anchor
		#else:
		#	if orientation == "horizontal":
		#		self.anchor = (0.5, 1.0)
		#	if orientation == "vertical":
		#		self.anchor = (0.0, 0.5)
		#self.panchor = panchor
		#if panchor:
		#	self.panchor = panchor
		#else:
		#	if orientation == "horizontal":
		#		self.panchor = (0.5, 0.0)
		#	else:
		#		self.panchor = (1.0, 0.5)
		self.extend = extend
		#self.extendfrac = extendfrac
		#self.extendrect = extendrect
		self.spacing = spacing
		self.ticks = ticks
		self.format = format
		self.drawedges = drawedges
		self.alpha = alpha


class GridStyle:
	def __init__(self, color_map_theme=ThematicStyleColormap("jet"), continuous=True, line_style=None, contour_levels=[], label_format="%.2f", colorbar_style=ColorbarStyle()):
		self.color_map_theme = color_map_theme
		self.continuous = continuous
		self.line_style = line_style
		self.contour_levels = contour_levels
		self.label_format = label_format
		self.colorbar_style = colorbar_style


class LegendStyle:
	def __init__(self, title="", location=0, label_style=FontStyle(), title_style=FontStyle(font_weight='bold'), marker_scale=None, frame_on=True, fancy_box=False, shadow=False, ncol=1, border_pad=None, label_spacing=None, handle_length=None, handle_text_pad=None, border_axes_pad=None, column_spacing=None, num_points=1, alpha=1.):
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
		self.num_points = num_points
		self.alpha = alpha


