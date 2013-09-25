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
	Style defining how points are plotted in matplotlib.

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
		Determine whether point style has thematic style features

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
		Copy point style, replacing thematic style features with default values

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
		and which can be passed to the plot function
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
	"""
	Style defining how lines are plotted in matplotlib.

	:param line_pattern:
		String, line pattern format string, or instance of :class:`ThematicStyle`
		"-" | "--" | "-." | ":"
		or "solid" | "dashed" | "dashdot" | "dotted"
	:param line_width:
		Float, line width, or instance of :class:`ThematicStyle`
		(default: 1)
	:param line_color:
		matplotlib color spec or instance of :class:`ThematicStyle`
		(default: 'k')
	:param solid_capstyle:
		String, how the end of a solid line is drawn: "butt" | "round" |
		"projecting"
		(default: "butt")
	:param solid_joinstyle, how two solid lines meeting in a node should be drawn:
		"miter" | "round" | "bevel"
		(default: "round")
	:param dash_capstyle:
		String, how the end of a dashed line is drawn: "butt" | "round" |
		"projecting"
		(default: "butt")
	:param dash_joinstyle, how two dashed lines meeting in a node should be drawn:
		"miter" | "round" | "bevel"
		(default: "round")
	:param label_style:
		instance of :class:`TextStyle`. If None, no labels will be plotted
		(default: None)
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	:param thematic_legend_style:
		instance of :class:`LegendStyle`. If None, thematic legend labels
		will be added to main legend
		(default: None)
	"""
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', solid_capstyle="butt", solid_joinstyle="round", dash_capstyle="butt", dash_joinstyle="round", label_style=None, alpha=1., thematic_legend_style=None):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.solid_capstyle = solid_capstyle
		self.solid_joinstyle = solid_joinstyle
		self.dash_capstyle = dash_capstyle
		self.dash_joinstyle = dash_joinstyle
		self.label_style = label_style
		self.alpha = alpha
		self.thematic_legend_style = thematic_legend_style
		# TODO: dashes, drawstyle

	def is_thematic(self):
		"""
		Determine whether line style has thematic style features

		:return:
			Bool
		"""
		if (isinstance(self.line_pattern, ThematicStyle) or isinstance(self.line_width, ThematicStyle)
			or isinstance(self.line_color, ThematicStyle)):
			return True
		else:
			return False

	def get_non_thematic_style(self):
		"""
		Copy line style, replacing thematic style features with default values

		:return:
			instance of :class:`LineStyle`
		"""
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
		return LineStyle(line_pattern, line_width, line_color, self.solid_capstyle, self.solid_joinstyle, self.dash_capstyle, self.dash_joinstyle, self.label_style, self.alpha, self.thematic_legend_style)

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the fill function or PolygonPatch object
		"""
		d = {}
		d["ls"] = self.line_pattern
		d["lw"] = self.line_width
		d["color"] = self.line_color
		d["solid_capstyle"] = self.solid_capstyle
		d["solid_joinstyle"] = self.solid_joinstyle
		d["dash_capstyle"] = self.dash_capstyle
		d["dash_joinstyle"] = self.dash_joinstyle
		d["alpha"] = self.alpha
		return d


class PolygonStyle:
	"""
	Style defining how polygons are plotted in matplotlib.

	:param line_pattern:
		String, line pattern format string, or instance of :class:`ThematicStyle`
		"solid" | "dashed" | "dashdot" | "dotted"
		Note: in contrast to :class:`LineStyle`, the character formats
		"-" | "--" | "-." | ":" are NOT supported
	:param line_width:
		Float, line width, or instance of :class:`ThematicStyle`
		(default: 1)
	:param line_color:
		matplotlib color spec or instance of :class:`ThematicStyle`
		(default: 'k')
	:param fill_color:
		matplotlib color spec or instance of :class:`ThematicStyle`
		(default: 'w')
	:param fill_hatch:
		char, hatch pattern format string:
		"/" | "\" | "|" | "-" | "+" | "x" | "o" | "O" | "." | "*"
	:param label_style:
		instance of :class:`TextStyle`. If None, no labels will be plotted
		(default: None)
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	:param thematic_legend_style:
		instance of :class:`LegendStyle`. If None, thematic legend labels
		will be added to main legend
		(default: None)
	"""
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', fill_color='w', fill_hatch=None, label_style=None, alpha=1., thematic_legend_style=None):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.fill_hatch = fill_hatch
		self.label_style = label_style
		self.alpha = alpha
		self.thematic_legend_style = thematic_legend_style

	def is_thematic(self):
		"""
		Determine whether line style has thematic style features

		:return:
			Bool
		"""
		if (isinstance(self.line_pattern, ThematicStyle) or isinstance(self.line_width, ThematicStyle)
			or isinstance(self.line_color, ThematicStyle) or isinstance(self.fill_color, ThematicStyle)
			or isinstance(self.fill_hatch, ThematicStyle)):
			return True
		else:
			return False

	def get_non_thematic_style(self):
		"""
		Copy polygon style, replacing thematic style features with default values

		:return:
			instance of :class:`PolygonStyle`
		"""
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
		"""
		Convert to line style.

		:return:
			instance of :class:`LineStyle`
		"""
		return LineStyle(self.line_pattern, self.line_width, self.line_color, label_style=self.label_style, alpha=self.alpha, thematic_legend_style=self.thematic_legend_style)

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the plot function
		"""
		d = {}
		d["ls"] = self.line_pattern
		d["lw"] = self.line_width
		d["ec"] = self.line_color
		d["fc"] = self.fill_color
		d["hatch"] = self.fill_hatch
		d["alpha"] = self.alpha
		return d


class FocmecStyle:
	"""
	Style defining how focal mechanisms are plotted in Basemap

	:param size:
		int, size of beach ball in points
	:param line_width:
		Float, line width, or instance of :class:`ThematicStyle`
		(default: 1)
	:param line_color:
		matplotlib color spec or instance of :class:`ThematicStyle`
		(default: 'k')
	:param fill_color:
		matplotlib color spec or instance of :class:`ThematicStyle`,
		defining color of compressive quadrants
		(default: 'k')
	:param bg_color:
		matplotlib color spec or instance of :class:`ThematicStyle`,
		defining color of dilational quadrants
		(default: 'w')
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	:param thematic_legend_style:
		instance of :class:`LegendStyle`. If None, thematic legend labels
		will be added to main legend
		(default: None)
	"""
	def __init__(self, size=50, line_width=1, line_color='k', fill_color='k', bg_color='w', alpha=1., thematic_legend_style=None):
		self.size = size
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.bg_color = bg_color
		self.alpha = alpha
		self.thematic_legend_style = thematic_legend_style

	def is_thematic(self):
		"""
		Determine whether line style has thematic style features

		:return:
			Bool
		"""
		if (isinstance(self.size, ThematicStyle) or isinstance(self.line_width, ThematicStyle) or
			isinstance(self.line_color, ThematicStyle) or isinstance(self.fill_color, ThematicStyle)):
			return True
		else:
			return False

	def get_non_thematic_style(self):
		"""
		Copy focmec style, replacing thematic style features with default values

		:return:
			instance of :class:`FocmecStyle`
		"""
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

	def to_point_style(self):
		"""
		Convert to point style

		:return:
			instance of :class:`PointStyle`
		"""
		return PointStyle(shape='o', size=self.size, line_width=self.line_width, line_color=self.line_color, fill_color=self.fill_color, alpha=self.alpha, thematic_legend_style=self.thematic_legend_style)

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the plot function
		"""
		d = {}
		d["width"] = self.size
		d["linewidth"] = self.line_width
		d["edgecolor"] = self.line_color
		d["facecolor"] = self.fill_color
		d["bgcolor"] = self.bg_color
		d["alpha"] = self.alpha
		return d


class CompositeStyle:
	"""
	Class representing composite style, defining how an ensemble of
	points, lines and polygons are plotted in matplotlib.

	:param point_style:
		instance of :class:`PointStyle`
	:param line_style:
		instance of :class:`LineStyle`
	:param polygon_style:
		instance of :class:`PolygonStyle`
	"""
	def __init__(self, point_style=None, line_style=None, polygon_style=None):
		self.point_style = point_style
		self.line_style = line_style
		self.polygon_style = polygon_style

	def is_thematic(self):
		"""
		Determine whether line style has thematic style features

		:return:
			Bool
		"""
		if self.point_style.is_thematic() or self.line_style.is_thematic() or self.polygon_style.is_thematic():
			return True
		else:
			return False


class ThematicStyle(object):
	"""
	Base class for a thematic style feature.
	Themtatic style features may be:
	- point sizes
	- point shapes
	- line widths
	- line patterns
	- line colors
	- fill colors
	- fill hatches

	:param value_key:
		key of data value (value property of data object) that will be
		used to map data values to colors or other style features
		(default: None, supposes that data value is a single value
		rather than a dictionary)
	:param add_legend:
		bool, whether or not a legend should be added for this thematic
		style feature (default: True)
	:param colorbar_style:
		instance of :class:`ColorbarStyle`, determining the aspect of
		the colorbar, in case the thematic style feature is a color
		(default: None)
	"""
	def __init__(self, value_key=None, add_legend=True, colorbar_style=None):
		self.value_key = value_key
		self.add_legend = add_legend
		self.colorbar_style = colorbar_style

	def apply_value_key(self, values):
		"""
		Apply value key to a given set of values

		:param values:
			list or dictionary
		"""
		if self.value_key == None:
			return values
		else:
			return values[self.value_key]

	def is_color_style(self):
		"""
		Determine if thematic style feature is a matplotlib color

		:return:
			bool
		"""
		try:
			style = self.styles[0]
		except:
			## ThematicStyleColormap
			return True
		else:
			if isinstance(style, (int, float)):
				return False
			else:
				cc = matplotlib.colors.ColorConverter()
				try:
					cc.to_rgb(style)
				except:
					return False
				else:
					return True


class ThematicStyleIndividual(ThematicStyle):
	"""
	Thematic style feature corresponding to a property that is divided
	in different classes.

	:param values:
		list or array of floats or strings, data values for which style
		values are defined.
	:param styles:
		list of style values (numbers or matplotlib colors) corresponding
		to intervals between given data values
	:param labels:
		labels corresponding to data classes
		(default: [], will use :param:`values`)
	:param value_key:
	:param add_legend:
	:param colorbar_style:
		see :class:`ThematicStyle`
	"""
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

		## Override colorbar default ticks and tick_labels
		if self.colorbar_style and self.is_color_style():
			if self.colorbar_style.ticks is None:
				sm = self.to_scalar_mappable()
				self.colorbar_style.ticks = sm.get_array()
			if self.colorbar_style.tick_labels is None:
				self.colorbar_style.tick_labels = self.labels

	def __call__(self, values):
		"""
		Convert data values to style values

		:param values:
			list or array of data values (numbers or strings)

		:return:
			float or rgba array
		"""
		return [self.style_dict[val] for val in self.apply_value_key(values)]

	def to_colormap(self):
		"""
		Get corresponding Colormap object. Only applicable if :param:`styles`
		contains matplotlib colors
		"""
		if self.is_color_style():
			cmap = matplotlib.colors.ListedColormap(self.styles, name=self.value_key)
			return cmap

	def get_norm(self):
		"""
		Get corresponding Normalize object
		"""
		## The norm is constructed in such a way that, if classes are numbers,
		## they will be placed below the corresponding color in the colorbar
		if isinstance(self.values[0], (int, float)):
			values = np.array(self.values)
		else:
			values = np.arange(len(self.values))
		diff = values[1:] - values[:-1]
		boundaries = values[1:] - diff / 2.
		boundaries = np.concatenate([[values[0] - diff[0] / 2.], boundaries, [values[-1] + diff[-1] / 2.]])
		return matplotlib.colors.BoundaryNorm(boundaries, len(self.values))

	def to_scalar_mappable(self):
		"""
		Get corresponding Scalarmappable object. Only applicable if
		:param:`styles` contains matplotlib colors
		"""
		if self.is_color_style():
			norm = self.get_norm()
			cmap = self.to_colormap()
			sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
			if isinstance(self.values[0], (int, float)):
				sm.set_array(self.values)
			else:
				sm.set_array(np.arange(len(self.values)))
			return sm


class ThematicStyleRanges(ThematicStyle):
	"""
	Thematic style feature corresponding to a property that changes
	in discrete steps.

	:param values:
		list or array of floats, data values for which style values are
		defined (breakpoints).
		Must be monotonically increasing or decreasing. Styles for inter-
		vening values will be interpolated
	:param styles:
		list of style values (numbers or matplotlib colors) corresponding
		to intervals between given data values.
		Note that number of styles must be one less than number of values
	:param labels:
		labels corresponding to breakpoints
		(default: [], will use :param:`values`)
	:param value_key:
	:param add_legend:
	:param colorbar_style:
		see :class:`ThematicStyle`
	"""
	def __init__(self, values, styles, labels=[], value_key=None, add_legend=True, colorbar_style=None):
		super(ThematicStyleRanges, self).__init__(value_key, add_legend, colorbar_style)
		self.values = np.array(values, dtype='f')
		self.styles = styles
		if labels:
			self.labels = labels
		else:
			self.labels = []
			for i in range(len(self.styles)):
				self.labels.append("%s - %s" % (self.values[i], self.values[i+1]))

		## Override colorbar default ticks and tick_labels
		if self.colorbar_style and self.is_color_style():
			if self.colorbar_style.ticks is None:
				sm = self.to_scalar_mappable()
				self.colorbar_style.ticks = sm.get_array()
			if self.colorbar_style.tick_labels is None and labels:
				self.colorbar_style.tick_labels = labels

	def __call__(self, values):
		"""
		Convert data values to style values

		:param values:
			list or array of floats, data values

		:return:
			float or rgba array
		"""
		bin_indexes = np.digitize(self.apply_value_key(values), self.values) - 1
		bin_indexes = np.clip(bin_indexes, 0, len(self.styles) - 1)
		return [self.styles[bi] for bi in bin_indexes]

	def to_colormap(self):
		"""
		Get corresponding Colormap object. Only applicable if :param:`styles`
		contains matplotlib colors
		"""
		if self.is_color_style():
			cmap = matplotlib.colors.ListedColormap(self.styles, name=self.value_key)
			return cmap

	def get_norm(self):
		"""
		Get corresponding Normalize object
		"""
		return matplotlib.colors.BoundaryNorm(self.values, len(self.styles))

	def to_scalar_mappable(self):
		"""
		Get corresponding Scalarmappable object. Only applicable if
		:param:`styles` contains matplotlib colors
		"""
		if self.is_color_style():
			#cmap, norm = matplotlib.colors.from_levels_and_colors(self.values, self.styles)
			cmap = self.to_colormap()
			norm = self.get_norm()
			sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
			sm.set_array(self.values)
			return sm


class ThematicStyleGradient(ThematicStyle):
	"""
	Thematic style feature corresponding to a gradually changing property.
	Only applicable to point sizes, line widths, line colors, and fill
	colors. Not applicable to point shapes, line patterns, and fill
	hatches, as these cannot be interpolated.

	:param values:
		list or array of floats, data values for which style values are
		defined (breakpoints).
		Must be monotonically increasing or decreasing. Styles for inter-
		vening values will be interpolated
	:param styles:
		list of style values (numbers or matplotlib colors) corresponding
		to given data values
	:param labels:
		labels corresponding to breakpoints
		(default: [], will use :param:`values`)
	:param value_key:
	:param add_legend:
	:param colorbar_style:
		see :class:`ThematicStyle`
	"""
	def __init__(self, values, styles, labels=[], value_key=None, add_legend=True, colorbar_style=None):
		super(ThematicStyleGradient, self).__init__(value_key, add_legend, colorbar_style)
		self.values = np.array(values, dtype='f')
		self.styles = styles
		if labels:
			self.labels = labels
		else:
			self.labels = map(str, self.values)

		## Override colorbar default ticks and tick_labels
		if self.colorbar_style and self.is_color_style():
			if self.colorbar_style.ticks is None:
				sm = self.to_scalar_mappable()
				self.colorbar_style.ticks = sm.get_array()
			if self.colorbar_style.tick_labels is None and labels:
				self.colorbar_style.tick_labels = labels

	def __call__(self, values):
		"""
		Convert data values to style values

		:param values:
			list or array of floats, data values

		:return:
			float or rgba array
		"""
		try:
			return np.interp(self.apply_value_key(values), self.values, self.styles)
		except:
			sm = self.to_scalar_mappable()
			#return sm.to_rgba(self.apply_value_key(values), alpha=self.alpha)
			return sm.to_rgba(self.apply_value_key(values))

	def to_colormap(self):
		"""
		Get corresponding Colormap object. Only applicable if :param:`styles`
		contains matplotlib colors
		"""
		if self.is_color_style():
			#x = self.values / self.values.max()
			x = np.linspace(0., 1., len(self.values))
			cmap = matplotlib.colors.LinearSegmentedColormap.from_list(self.value_key, zip(x, self.styles))
			cmap._init()
			return cmap

	def get_norm(self):
		"""
		Get corresponding Normalize object
		"""
		from cm.norm import PiecewiseLinearNorm
		return PiecewiseLinearNorm(self.values)
		#return matplotlib.colors.Normalize(vmin=self.values.min(), vmax=self.values.max())

	def to_scalar_mappable(self):
		"""
		Get corresponding Scalarmappable object. Only applicable if
		:param:`styles` contains matplotlib colors
		"""
		if self.is_color_style():
			norm = self.get_norm()
			cmap = self.to_colormap()
			sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
			sm.set_array(self.values)
			return sm


class ThematicStyleColormap(ThematicStyle):
	"""
	Thematic style feature corresponding to a matplotlib colormap.

	:param color_map:
		string or matplotlib colormap
	:param norm:
		matplotlib Normalize object for scaling data values to the 0-1 range
		(default: None, will apply linear scaling between vmin and vmax)
	:param vmin:
		float, minimum value that will correspond to 0 (default: None)
	:param vmax:
		float, maximum value that will correspond to 1 (default: None)
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	:param value_key:
	:param add_legend:
	:param colorbar_style:
		see :class:`ThematicStyle`

	Note: if norm is specified, vmin and vmax will only determine the
	range shown in the colorbar; the norm itself will not be affected.
	"""
	def __init__(self, color_map="jet", norm=None, vmin=None, vmax=None, alpha=1.0, value_key=None, add_legend=True, colorbar_style=None):
		super(ThematicStyleColormap, self).__init__(value_key, add_legend, colorbar_style)
		if isinstance(color_map, matplotlib.colors.Colormap):
			self.color_map = color_map
		else:
			self.color_map = matplotlib.cm.get_cmap(color_map)
		if not self.color_map._isinit:
			self.color_map._init()
		self.norm = norm
		self.vmin = vmin
		self.vmax = vmax
		self.alpha = alpha
		self._set_cmap_alpha()

	@property
	def values(self):
		norm = self.get_norm()
		return np.array([norm.vmin, norm.vmax])

	def __call__(self, values):
		"""
		Convert data values to colors

		:param values:
			list or array of floats, data values

		:return:
			rgba array
		"""
		sm = self.to_scalar_mappable()
		return sm.to_rgba(self.apply_value_key(values), alpha=self.alpha)

	def _set_cmap_alpha(self):
		"""
		Private method to set alpha value in the color map
		"""
		self.color_map._lut[:-3,-1] = self.alpha

	def get_norm(self):
		"""
		Get the Normalize object. If not supplied, it will be
		constructed from vmin and vmax
		"""
		if not self.norm:
			norm = matplotlib.colors.Normalize(self.vmin, self.vmax)
		else:
			norm = self.norm
		return norm

	def to_colormap(self):
		"""
		Get the Colormap object
		"""
		return self.color_map

	def to_scalar_mappable(self):
		"""
		Convert colormap and norm to a Scalarmappable object
		"""
		norm = self.get_norm()
		return matplotlib.cm.ScalarMappable(norm=norm, cmap=self.color_map)


class ColorbarStyle:
	"""
	Class defining aspect of a color bar.

	:param title:
		str, title plotted alongside color bar (default: "")
	:param location:
		str, where to put colorbar: "left", "right", "bottom", "top"
		(default: "bottom")
	:param size:
		str, width (or height?) of colorbar, in percent (default: '5%')
	:param pad:
		str, padding between map and colorbar, in same units as :param:`size`
		(default: '10%')
	:param extend:
		str, how to extend colorbar with pointed ends for out-of-range values:
		"neither" | "both" | "min" | "max"
		(default: "neither")
	:param spacing:
		str, "uniform" | "proportional"
		Uniform spacing gives each discrete color the same space;
		proportional makes the space proportional to the data interval
		(default: "uniform")
	:param ticks:
		list of ticks or matplotlib Locator object
		If None, ticks are determined automatically (by matplotlib or by
		parent thematic style)
		(default: None)
	:param tick_labels:
		list of tick labels. If None, tick labels are determined
		automatically (by matplotlib or by parent thematic style)
		(default: None)
	:param format:
		str or matplotlib Formatter object
		(default: "%.2f")
	:param drawedges:
		bool, whether or not to draw lines at color boundaries
		(default: False)
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	"""
	def __init__(self, title="", location="bottom", size='5%', pad='10%', extend="neither", spacing="uniform", ticks=None, tick_labels=None, format=None, drawedges=False, alpha=1.):
		self.title = title
		self.location = location
		self.size = size
		self.pad = pad
		self.extend = extend
		self.spacing = spacing
		self.ticks = ticks
		self.tick_labels = tick_labels
		self.format = format
		self.drawedges = drawedges
		self.alpha = alpha

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the colorbar function
		"""
		d = {}
		d["location"] = self.location
		d["size"] = self.size
		d["pad"] = self.pad
		d["extend"] = self.extend
		d["spacing"] = self.spacing
		d["ticks"] = self.ticks
		d["format"] = self.format
		d["drawedges"] = self.drawedges
		d["alpha"] = self.alpha
		return d


class GridStyle:
	"""
	Class defining how a regular grid is plotted in matplotlib

	:param color_map_theme:
		instance of :class:`ThematicStyleColormap`
	:param color_gradient:
		string, "continuous", "discontinuous" or None.
		Defines if color_gradient should be continuous or discontinuous.
		If None, only contour lines will be plotted.
		(default: "continuous")
	:param line_style:
		instance of :class:`LineStyle`, defining how contour lines will
		be plotted
	:param contour_levels:
		list or array, defining contour-line values
		(default: None, will be determined automatically by matplotlib)
	:param colorbar_style:
		instance of :class:`ColorbarStyle`, will override colorbar_style
		property of color_map_theme

	Note: format of contour labels is determined by format property
	of colorbar_style.
	"""
	def __init__(self, color_map_theme=ThematicStyleColormap("jet"), color_gradient="continuous", line_style=None, contour_levels=None, colorbar_style=None):
		self.color_map_theme = color_map_theme
		self.color_gradient = color_gradient
		self.line_style = line_style
		self.contour_levels = contour_levels
		if colorbar_style:
			self.color_map_theme.colorbar_style = colorbar_style

	@property
	def colorbar_style(self):
		return self.color_map_theme.colorbar_style

	@property
	def label_format(self):
		if self.color_map_theme.colorbar_style:
			return self.color_map_theme.colorbar_style.format
		else:
			return "%.2f"


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

