"""
Styles used in LayeredBasemap
"""

from __future__ import absolute_import, division, print_function, unicode_literals


"""
IDEA: Refactor as follows:

base:
	BasemapStyle

text:
	FontStyle
	TextStyle
	DefaultTitleTextStyle

thematic:
	ThematicStyle
	ThematicStyleIndividual
	ThematicStyleRanges
	ThematicStyleGradient
	ThematicStyleColormap

shape:
	PointStyle
	LineStyle
	PolygonStyle
	CompositeStyle?

grid:
	GridStyle
	GridImageStyle
	VectorStyle?
	ImageStyle
	HillshadeStyle
	WMSStyle

other:
	FocmecStyle
	FrontStyle
	PiechartStyle

decoration:
	ColorbarStyle
	LegendStyle
	ScalebarStyle
	MapBorderStyle
	GraticuleStyle
"""

try:
	## Python 2
	basestring
	PY2 = True
except:
	## Python 3
	PY2 = False
	basestring = str


import numpy as np
import matplotlib
import matplotlib.cm


__all__ = ['FontStyle', 'TextStyle', 'DefaultTitleTextStyle', 'PointStyle',
			'LineStyle', 'PolygonStyle', 'FocmecStyle', 'CompositeStyle',
			'ThematicStyleIndividual', 'ThematicStyleRanges', 'ThematicStyleGradient',
			'ThematicStyleColormap', 'ColorbarStyle', 'GridStyle', 'LegendStyle',
			'ScalebarStyle', 'MapBorderStyle', 'GraticuleStyle', 'GridImageStyle',
			'ImageStyle', 'HillshadeStyle', 'WMSStyle', 'FrontStyle', 'VectorStyle',
			'PiechartStyle']


class BasemapStyle(object):
	"""
	Base class for most Basemap styles, containing common methods
	"""
	@classmethod
	def from_dict(cls, style_dict):
		"""
		Construct style from dictionary.

		:param style_dict:
			dictionary containing style properties as keys.
			Note that an error will be raised if style_dict contains keys
			that are not properties of the style!

		:return:
			instance of :class:`BasemapStyle` or derived class
		"""
		## Note: it is not currently possible to check if all keys in style_dict
		## are properties of the particular style, and we can't instantiate
		## the style as some styles have positional arguments...
		return cls(**style_dict)

	def to_dict(self):
		"""
		Convert style to dictionary.

		:return:
			dict
		"""
		d = {}
		for attr in dir(self):
			if attr == "text_filter" or (not attr.startswith('__') and not callable(getattr(self, attr))):
				d[attr] = getattr(self, attr, None)
		return d

	def copy(self):
		"""
		Create a shallow copy of the current style.

		:return:
			instance of :class:`BasemapStyle` or derived class
		"""
		return self.from_dict(self.to_dict())

	def update(self, other):
		"""
		Update properties from another style.
		Properties (or keys) in the other style that are not
		properties of the current class are ignored.

		:param other:
			instance of :class:`BasemapStyle` or derived class
			or dict
		"""
		for attr in dir(self):
			if not attr.startswith('__') and not callable(getattr(self, attr)):
				if isinstance(other, dict):
					val = other.get(attr, None)
				else:
					val = getattr(other, attr, None)
				if not val is None:
					setattr(self, attr, val)


class FontStyle(BasemapStyle):
	"""
	Class representing matplotlib font properties
	Used in e.g., plot titles

	:param font_family:
		string, font family or font name
		("serif" | "sans-serif" | "cursive" | "fantasy" | "monospace")
		or the name of a TrueType font in system font path (e.g. Calibri)
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

	def to_font_props_dict(self):
		"""
		Return dictionary with keyword arguments accepted by mpl's
		FontProperties initializer
		"""
		d = {}
		d['family'] = self.font_family
		d['style'] = self.font_style
		d['variant'] = self.font_variant
		d['stretch'] = self.font_stretch
		d['weight'] = self.font_weight
		d['size'] = self.font_size

		if not self.font_family in ("serif", "sans-serif", "cursive", "fantasy", "monospace"):
			fp = matplotlib.font_manager.FontProperties(**d)
			fname = matplotlib.font_manager.findfont(fp)
		else:
			fname = None
		d['fname'] = fname
		return d

	def to_font_props(self):
		"""
		Return instance of :class:`FontProperties`
		"""
		fp = matplotlib.font_manager.FontProperties(**self.to_font_props_dict())
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
		(default: 1.25)
	:param rotation:
		Float, angle in degrees, or string ("vertical" | "horizontal" | "auto")
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
	:param border_color:
		matplotlib color spec, line color of surrounding box
		(default: "None")
	:param border_width:
		float, line width of surrounding box
		(default: 0.5)
	:param border_pad:
		float, padding between text and surrounding box (in fraction of
		font size)
		(default: 0.2)
	:param border_shape:
		str, shape of surrounding box. Available shapes:
		circle, darrow, larrow, rarrow, round, round4, roundtooth,
		sawtooth, square
		(default: "square")
	:param offset:
		tuple, horizontal and vertical offset in points (default: (0, 0))
	:param offset_coord_frame:
		str, coordinate frame for :prop:`offset`:
		"figure points", "figure pixels", "figure fraction", "axes points",
		"axes pixels", "axes fraction", "data", "offset points" or "polar"
		Note: Ignored if coord_frame property of (Multi)TextData is not
		set to "geographic" !
		(default: "offset points")
	:param clip_on:
		bool, whether or not text should be clipped to the axes bounding box
		(default: True)
	:param text_filter:
		func returning string, filter function to be applied to text
		(default: None)
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	"""
	def __init__(self,
				font_family="sans-serif",
				font_style="normal",
				font_variant="normal",
				font_stretch="normal",
				font_weight="normal",
				font_size=12,
				color='k',
				background_color="None",
				line_spacing=1.25,
				rotation=0,
				horizontal_alignment="center",
				vertical_alignment="center",
				multi_alignment="center",
				border_color="None",
				border_width=0.5,
				border_pad=0.2,
				border_shape="square",
				offset=(0,0),
				offset_coord_frame="offset points",
				clip_on=True,
				text_filter=None,
				alpha=1.):
		super(TextStyle, self).__init__(font_family, font_style, font_variant, font_stretch, font_weight, font_size)
		self.color = color
		self.background_color = background_color
		self.line_spacing = line_spacing
		self.rotation = rotation
		self.horizontal_alignment = horizontal_alignment
		self.vertical_alignment = vertical_alignment
		self.multi_alignment = multi_alignment
		self.border_color = border_color
		self.border_width = border_width
		self.border_pad = border_pad
		self.border_shape = border_shape
		self.offset = offset
		self.offset_coord_frame = offset_coord_frame
		self.clip_on = clip_on
		self.text_filter = text_filter
		self.alpha = alpha

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the text and annotate functions
		"""
		d = {}
		#d["family"] = self.font_family
		#d["size"] = self.font_size
		#d["weight"] = self.font_weight
		#d["style"] = self.font_style
		#d["stretch"] = self.font_stretch
		#d["variant"] = self.font_variant
		d["fontproperties"] = self.to_font_props()
		d["color"] = self.color
		#d["backgroundcolor"] = self.background_color
		d["linespacing"] = self.line_spacing
		d["rotation"] = self.rotation
		d["ha"] = self.horizontal_alignment
		d["va"] = self.vertical_alignment
		d["multialignment"] = self.multi_alignment
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		d["bbox"] = dict(facecolor=self.background_color, lw=self.border_width,
						edgecolor=self.border_color,
						boxstyle="%s, pad=%s" % (self.border_shape, self.border_pad))
		#bbox=dict(facecolor='none', edgecolor='black', boxstyle='round,pad=1')
		return d

	def get_text(self, text):
		"""
		Modify given text according to style's text filter

		:param text:
			str, input text for :param:`text_filter`

		:return:
			str, text generated by applying :param:`text_filter`
		"""
		if self.text_filter:
			return self.text_filter(text)
		else:
			return text


DefaultTitleTextStyle = TextStyle(font_size="large", horizontal_alignment="center", vertical_alignment="bottom")


class PointStyle(BasemapStyle):
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
		instance of :class:`LegendStyle` or str, title of thematic legend
		labels will be added to (e.g., "main")
		(default: None)

	Note: only one of line_color / fill_color may be a thematic style.
	Markers like '+' can only take thematic line_color
	Markers like 'o' can take thematic fill_color or line_color;
	if fill_color is thematic, a fixed line_color may be specified, but
	if line_color is thematic, fill_color is currently ignored.
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
		if isinstance(self.size, ThematicStyle) and isinstance(self.thematic_legend_style, LegendStyle):
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
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d


class FrontStyle(BasemapStyle):
	"""
	Style defining how "fronts" are plotted in matplotlib

	:param shape:
		str, shape of front marker,
		one of ("polygon", "star", "asterisk", "circle", "arc",
		"arrow", "ellipse", "rectangle").
		Polygons, stars, asterisks and circles are implemented as
		matplotlib markers; arcs, arrows, ellipses and rectangles as
		matplotlib patches.
		marker_style may also be a matplotlib patch instance, , in that
		case, it is recommended to set lower left coordinate at (0, 0).
	:param size:
		int, size of front marker in points.
		(default: 10)
	:param interval:
		int, str or array-like, interval of front marker along line
		- positive int: interval between markers in points
		- negative int (or zero): number of markers along line
		- str: marker interval will be rounded to closest value that
			results in even spacing along the line
		- array-like: distances along line, in range [0,1].
		(default: 24)
	:param offset:
		int, offset of front marker with respect to line.
		(default: 0)
	:param angle:
		float, angle in degrees of front marker with respect to line.
		Does not apply to circles.
		(default: 0)
	:param alternate_sides:
		bool, whether or not front markers should alternate between
		two sides of line.
		(default: False)
	:param line_width:
		int, line width of front marker in points.
		If None, will take line width of parent line.
		(default: 1)
	:param line_color:
		matplotlib color definition for line color of front marker.
		If None, will take line color of parent line.
		(default: 'k')
	:param fill_color:
		matplotlib color definition for fill color of front marker.
		If None, will take line color of parent line.
		(default: 'k')
	:param num_sides:
		int, number of sides of front marker. Only applies to polygons, stars,
		and asterisks.
		(default: 3)
	:param aspect_ratio:
		float, aspect ratio of width (direction perpendicular to line)
		to length (direction along line) of front marker. Only applies
		to arcs, arrows, ellipses and rectangles.
		(default: 1.)
	:param theta1:
		float, starting angle in degrees. Only applies to arcs.
		(default: 0)
	:param theta2:
		float, ending angle in degrees. Only applies to arcs.
		(default: 180)
	:param arrow_shape:
		str, arrow shape, one of ["full", "left", "right"].
		Only applies to arrows.
		(default: "full")
	:param arrow_overhang:
		float, fraction that the arrow is swept back (0 means triangular shape).
		Can be negative or greater than one. Only applies to arrows.
		(default: 0.)
	:param arrow_length_includes_head:
		bool, True if head is to be counted in calculating arrow length.
		Only applies to arrows.
		(default: False)
	:param arrow_head_starts_at_zero:
		bool, if True, arrow head starts being drawn at coordinate 0 instead of
		ending at coordinate 0. Only applies to arrows.
		(default: False)
	:param alpha:
		float, alpha transparency for front marker.
		(default: 1)
	"""
	def __init__(self, shape, size=10, interval=20, offset=0, angle=0,
				alternate_sides=False, line_width=1, line_color='k', fill_color='k',
				num_sides=3, aspect_ratio=1, theta1=0, theta2=180,
				arrow_shape="full", arrow_overhang=0, arrow_length_includes_head=False,
				arrow_head_starts_at_zero=False, alpha=1.):
		self.shape = shape
		self.size = size
		self.interval = interval
		self.offset = offset
		self.angle = angle
		self.alternate_sides = alternate_sides
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.num_sides = num_sides
		self.aspect_ratio = aspect_ratio
		self.theta1 = theta1
		self.theta2 = theta2
		self.arrow_shape = arrow_shape
		self.arrow_length_includes_head = arrow_length_includes_head
		self.arrow_overhang = arrow_overhang
		self.arrow_head_starts_at_zero = arrow_head_starts_at_zero
		self.alpha = alpha

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the plot function
		"""
		d = {}
		d["marker_shape"] = self.shape
		d["marker_size"] = self.size
		d["marker_interval"] = self.interval
		d["marker_offset"] = self.offset
		d["marker_angle"] = self.angle
		d["marker_alternate_sides"] = self.alternate_sides
		d["marker_edge_width"] = self.line_width
		d["marker_edge_color"] = self.line_color
		d["marker_face_color"] = self.fill_color
		d["marker_num_sides"] = self.num_sides
		d["marker_aspect_ratio"] = self.aspect_ratio
		d["marker_theta1"] = self.theta1
		d["marker_theta2"] = self.theta2
		d["marker_arrow_shape"] = self.arrow_shape
		d["marker_arrow_overhang"] = self.arrow_overhang
		d["marker_arrow_length_includes_head"] = self.arrow_length_includes_head
		d["marker_arrow_head_starts_at_zero"] = self.arrow_head_starts_at_zero
		d["marker_alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d


class LineStyle(BasemapStyle):
	"""
	Style defining how lines are plotted in matplotlib.

	:param line_pattern:
		String, line pattern format string, or instance of :class:`ThematicStyle`
		"-" | "--" | "-." | ":"
		or "solid" | "dashed" | "dashdot" | "dotted"
		(default: "solid")
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
	:param label_anchor:
		float, fraction of length where label should be anchored
		or str, one of "start", "end" or "middle"
		(default: 0.5)
	:param front_style:
		instance of :class:`FrontStyle`. If None, no fronts will be plotted
		(default: None)
	:param dash_pattern:
		list of on/off dash lengths in points
		(default: [])
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	:param thematic_legend_style:
		instance of :class:`LegendStyle` or str, title of thematic legend
		labels will be added to (e.g., "main")
		(default: None)
	"""
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', solid_capstyle="butt", solid_joinstyle="round", dash_capstyle="butt", dash_joinstyle="round", label_style=None, label_anchor=0.5, front_style=None, dash_pattern=[], alpha=1., thematic_legend_style=None):
		self.line_pattern = line_pattern
		self.line_width = line_width
		self.line_color = line_color
		self.solid_capstyle = solid_capstyle
		self.solid_joinstyle = solid_joinstyle
		self.dash_capstyle = dash_capstyle
		self.dash_joinstyle = dash_joinstyle
		self.front_style = front_style
		self.label_style = label_style
		self.label_anchor = label_anchor
		self.dash_pattern = dash_pattern
		self.alpha = alpha
		self.thematic_legend_style = thematic_legend_style
		# TODO: drawstyle

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
		return LineStyle(line_pattern, line_width, line_color, self.solid_capstyle,
						self.solid_joinstyle, self.dash_capstyle, self.dash_joinstyle,
						self.label_style, self.label_anchor, self.front_style,
						self.dash_pattern, self.alpha, self.thematic_legend_style)

	def to_line_style(self):
		"""
		no-op
		"""
		return self

	def to_polygon_style(self):
		"""
		Convert to polygon style.

		:return:
			instance of :class:`PolygonStyle`
		"""
		return PolygonStyle(self.line_pattern, self.line_width, self.line_color,
							fill_color="none", label_style=self.label_style,
							label_anchor=self.label_anchor, alpha=self.alpha,
							thematic_legend_style=self.thematic_legend_style)

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the fill function or PolygonPatch object
		"""
		d = {}
		d["lw"] = self.line_width
		d["color"] = self.line_color
		d["solid_capstyle"] = self.solid_capstyle
		d["solid_joinstyle"] = self.solid_joinstyle
		d["dash_capstyle"] = self.dash_capstyle
		d["dash_joinstyle"] = self.dash_joinstyle
		if self.dash_pattern:
			d["dashes"] = self.dash_pattern
		else:
			d["ls"] = self.line_pattern
			#d["dashes"] = (None, None)
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d


class PolygonStyle(BasemapStyle):
	"""
	Style defining how polygons are plotted in matplotlib.

	:param line_pattern:
		String, line pattern format string, or instance of :class:`ThematicStyle`
		"solid" | "dashed" | "dashdot" | "dotted"
		(default: "solid")
		Note: the character formats "-" | "--" | "-." | ":" are supported
		as well, but they are automatically converted to the corresponding
		long names
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
		"/" | "\\" | "|" | "-" | "+" | "x" | "o" | "O" | "." | "*"
		Note: repeat pattern format to increase density, e.g. "//"
		or "..."
		May also be instance of :class:`ThematicStyleRanges` or of
		:class:`ThematicStyleIndividual`

	:param hatch_color:
		matplotlib color spec, color of hatch pattern.
		Only used if :prop:`line_color` is not set.
		(default: 'k')
	:param label_style:
		instance of :class:`TextStyle`. If None, no labels will be plotted
		(default: None)
	:param label_anchor:
		str, one of "centroid", "west", "east", "south" or "north"
		(default: "centroid")
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	:param thematic_legend_style:
		instance of :class:`LegendStyle` or str, title of thematic legend
		labels will be added to (e.g., "main")
		(default: None)
	"""
	# TODO: add dash_pattern as well!
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', fill_color='w', fill_hatch=None, hatch_color='k', label_style=None, label_anchor="centroid", alpha=1., thematic_legend_style=None):
		self.line_pattern = {'-': 'solid', '--': 'dashed', ':': 'dotted', '-.': 'dashdot'}.get(line_pattern, line_pattern)
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.fill_hatch = fill_hatch
		self.hatch_color = hatch_color
		self.label_style = label_style
		self.label_anchor = label_anchor
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
		return PolygonStyle(line_pattern, line_width, line_color, fill_color,
							fill_hatch, self.hatch_color, self.label_style,
							self.label_anchor, self.alpha, self.thematic_legend_style)

	def to_line_style(self):
		"""
		Convert to line style.

		:return:
			instance of :class:`LineStyle`
		"""
		return LineStyle(self.line_pattern, self.line_width, self.line_color,
						label_style=self.label_style, label_anchor=self.label_anchor,
						alpha=self.alpha, thematic_legend_style=self.thematic_legend_style)

	def to_polygon_style(self):
		"""
		no-op
		"""
		return self

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
		if self.fill_hatch:
			if not self.hatch_color in (None, "None", "none"):
				## override ec
				d["ec"] = self.hatch_color
				if self.line_color in (None, "None", "none"):
					d["lw"] = 0
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d


class FocmecStyle(BasemapStyle):
	"""
	Style defining how focal mechanisms are plotted in Basemap

	:param size:
		int, size (width) of beach ball in pixels @ 120 dpi
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
	:param offset:
		tuple, horizontal and vertical offset in points (default: (0, 0))
		Note: ignored when offsets property of FocmecData is set.
	:param offset_coord_frame:
		str, coordinate frame for :prop:`offset`:
		"offset points", "geographic" or "data"
		(default: "offset points")
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	:param thematic_legend_style:
		instance of :class:`LegendStyle` or str, title of thematic legend
		labels will be added to (e.g., "main")
		(default: None)
	"""
	def __init__(self, size=50, line_width=1, line_color='k', fill_color='k', bg_color='w', offset=(0,0), offset_coord_frame="offset points", alpha=1., thematic_legend_style=None):
		self.size = size
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.bg_color = bg_color
		self.offset = offset
		self.offset_coord_frame = offset_coord_frame
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
			#fill_color = 'k'
			fill_color = self.bg_color
		else:
			fill_color = self.fill_color
		bg_color = self.bg_color
		return FocmecStyle(size, line_width, line_color, fill_color, bg_color, self.offset, self.alpha, self.thematic_legend_style)

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
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d


class PiechartStyle():
	"""
	Style defining how pie charts should be plotted

	:param fill_colors:
		list of matplotlib color specifications for the different
		pie chart categories
	:param line_color:
		matplotlib color specification for pie outlines
		(default: 'k')
	:param line_width:
		float, line width of pie outlines
		(default: 1)
	:param start_angle:
		float, angle at which first category starts  (in degrees
		counterclockwise from the X-axis)
		(default: 0)
	:param alpha:
		float in the range 0 - 1, opacity (default: 1.)
	"""
	def __init__(self, fill_colors, line_color='k', line_width=1, start_angle=0,
				alpha=1.):
		self.fill_colors = fill_colors
		#self.size = size
		self.line_color = line_color
		self.line_width = line_width
		self.start_angle = start_angle
		self.alpha = alpha

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the plot function
		"""
		d = {}
		#d["ms"] = self.size
		d["linewidths"] = self.line_width
		d["edgecolors"] = self.line_color
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
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
	:param text_style:
		instance of :class:`TextStyle`
	"""
	def __init__(self, point_style=None, line_style=None, polygon_style=None, text_style=None):
		self.point_style = point_style
		self.line_style = line_style
		self.polygon_style = polygon_style
		self.text_style = text_style

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
	:param style_under:
		style corresponding to data values lower than range in :param:`values`
		(default: None)
	:param style_over:
		style corresponding to data values higher than range in :param:`values`
		(default: None)
	:param style_bad:
		style corresponding to 'bad' data values (NaN)
		(default: None)
	"""
	def __init__(self, value_key=None, add_legend=True, colorbar_style=None,
				style_under=None, style_over=None, style_bad=None):
		self.value_key = value_key
		self.add_legend = add_legend
		self.colorbar_style = colorbar_style
		self.style_under = style_under
		self.style_over = style_over
		self.style_bad = style_bad

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
		values are defined, or lists grouping data values
		Values should of course be unique
	:param styles:
		list of style values (numbers or matplotlib colors) corresponding
		to given data values
	:param labels:
		labels corresponding to data classes, and which will be used in
		the thematic legend or color bar
		(default: [], will use :param:`values`)
	:param value_key:
	:param add_legend:
	:param colorbar_style:
		see :class:`ThematicStyle`
	:param style_under:
		style corresponding to data values lower than range in :param:`values`
		(only applies if values are numbers and monotonically increasing)
		(default: None)
	:param style_over:
		(only applies if values are numbers and monotonically increasing)
		style corresponding to data values higher than range in :param:`values`
		(default: None)
	:param style_bad:
		style corresponding to 'bad' data values (NaN)
		(default: None)
	"""
	def __init__(self, values, styles, labels=[], value_key=None, add_legend=True,
				colorbar_style=None, style_under=None, style_over=None, style_bad=None):
		super(ThematicStyleIndividual, self).__init__(value_key, add_legend, colorbar_style,
													style_under, style_over, style_bad)
		self.values = values
		if isinstance(styles, (list, tuple, np.ndarray)):
			assert len(values) == len(styles)
			self.set_styles(styles)
		elif isinstance(styles, basestring) and styles[:12] == "random_color":
			if ',' in styles:
				random_seed = int(styles.split(',')[-1])
			else:
				random_seed = None
			self.set_styles_from_random_colors(random_seed)
		elif isinstance(styles, (basestring, matplotlib.colors.Colormap)):
			self.set_styles_from_colormap(styles)
		if not (labels is None or labels == []):
			self.labels = labels
		else:
			self.labels = []
			for val in self.values:
				if PY2 and isinstance(val, str):
					val = val.decode('iso-8859-1')
				if isinstance(val, basestring):
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

	def is_numeric(self):
		return np.array([not isinstance(self.values[idx], basestring)
						for idx in range(len(self.values))]).any()

	def is_monotonously_increasing(self):
		if self.is_numeric():
			sign_diff = np.sign(np.diff(self.values))
			return np.all(sign_diff == sign_diff[0])

	def set_styles(self, styles):
		self.styles = styles
		self.style_dict = {}
		for value, style in zip(self.values, self.styles):
			if isinstance(value, (list, tuple)):
				for val in value:
					self.style_dict[val] = style
			else:
				self.style_dict[value] = style

	def set_styles_from_colormap(self, color_map):
		if isinstance(color_map, (str)):
			color_map = matplotlib.cm.get_cmap(color_map)
		N = len(self.values)
		norm  = matplotlib.colors.Normalize(vmin=0, vmax=N-1)
		sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=color_map)
		styles = [sm.to_rgba(i) for i in range(N)]
		self.set_styles(styles)
		self.style_under = color_map._rgba_under
		self.style_over = color_map._rgba_over
		self.style_bad = color_map._rgba_bad

	def set_styles_from_random_colors(self, random_seed=None):
		import random
		from itertools import cycle

		N = len(self.values)
		rnd = random.Random()
		rnd.seed(random_seed)
		named_colors = matplotlib.colors.cnames.keys()
		rnd.shuffle(named_colors)
		named_colors = cycle(named_colors)
		styles = [named_colors.next() for i in range(N)]
		self.set_styles(styles)

	def __call__(self, values):
		"""
		Convert data values to style values

		:param values:
			list or array of data values (numbers or strings)

		:return:
			float or rgba array
		"""
		values = self.apply_value_key(values)
		out_styles = [self.style_dict.get(val) for val in values]
		if self.is_monotonously_increasing():
			if self.style_under:
				for idx in np.where(values < self.values[0])[0]:
					out_styles[idx] = self.style_under
			if self.style_over:
				for idx in np.where(values > self.values[-1])[0]:
					out_styles[idx] = self.style_over
			if self.style_bad:
				for idx in np.where(np.isnan(values))[0]:
					out_styles[idx] = self.style_bad
		return out_styles

	def to_colormap(self):
		"""
		Get corresponding Colormap object. Only applicable if :param:`styles`
		contains matplotlib colors
		"""
		if self.is_color_style():
			cmap = matplotlib.colors.ListedColormap(self.styles, name=self.value_key)
			if self.style_under:
				cmap.set_under(self.style_under)
			if self.style_over:
				cmap.set_over(self.style_over)
			if self.style_bad:
				cmap.set_bad(self.style_bad)
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

	def to_scalar_mappable(self, values=None):
		"""
		Get corresponding Scalarmappable object. Only applicable if
		:param:`styles` contains matplotlib colors

		:param values:
			list or array, data values
			(default: None)

		:return:
			instance of :class:`matplotlib.cm.ScalarMappable`
		"""
		if self.is_color_style():
			norm = self.get_norm()
			cmap = self.to_colormap()
			sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
			if values is None:
				if isinstance(self.values[0], (int, float)):
					sm.set_array(self.values)
				else:
					sm.set_array(np.arange(len(self.values)))
			else:
				sm.set_array(values)
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
		labels corresponding to breakpoints, and which will be used in
		the thematic legend or color bar
		(default: [], will use :param:`values`)
	:param value_key:
	:param add_legend:
	:param colorbar_style:
		see :class:`ThematicStyle`
	:param style_under:
		style corresponding to data values lower than range in :param:`values`
		(default: None)
	:param style_over:
		style corresponding to data values higher than range in :param:`values`
		(default: None)
	:param style_bad:
		style corresponding to 'bad' data values (NaN)
		(default: None)
	"""
	def __init__(self, values, styles, labels=[], value_key=None, add_legend=True,
				colorbar_style=None, style_under=None, style_over=None, style_bad=None):
		super(ThematicStyleRanges, self).__init__(value_key, add_legend, colorbar_style,
													style_under, style_over, style_bad)
		self.values = np.array(values, dtype='f')
		if isinstance(styles, (list, tuple, np.ndarray)):
			assert len(values) == len(styles) + 1
			self.set_styles(styles)
		elif isinstance(styles, basestring) and styles[:12] == "random_color":
			if ',' in styles:
				random_seed = int(styles.split(',')[-1])
			else:
				random_seed = None
			self.set_styles_from_random_colors(random_seed)
		elif isinstance(styles, (str, matplotlib.colors.Colormap)):
			self.set_styles_from_colormap(styles)
		if not (labels is None or labels == []):
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

	def set_styles(self, styles):
		self.styles = styles

	def set_styles_from_colormap(self, color_map):
		if isinstance(color_map, (str)):
			color_map = matplotlib.cm.get_cmap(color_map)
		N = len(self.values) - 1
		norm  = matplotlib.colors.Normalize(vmin=0, vmax=N-1)
		sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=color_map)
		styles = [sm.to_rgba(i) for i in range(N)]
		self.set_styles(styles)
		self.style_under = color_map._rgba_under
		self.style_over = color_map._rgba_over
		self.style_bad = color_map._rgba_bad

	def set_styles_from_random_colors(self, random_seed=None):
		import random
		from itertools import cycle

		N = len(self.values)
		rnd = random.Random()
		rnd.seed(random_seed)
		named_colors = matplotlib.colors.cnames.keys()
		rnd.shuffle(named_colors)
		named_colors = cycle(named_colors)
		styles = [named_colors.next() for i in range(N)]
		self.set_styles(styles)

	def __call__(self, values):
		"""
		Convert data values to style values

		:param values:
			list or array of floats, data values

		:return:
			float or rgba array
		"""
		values = self.apply_value_key(values)
		bin_indexes = np.digitize(values, self.values) - 1
		bin_indexes = np.clip(bin_indexes, 0, len(self.styles) - 1)
		out_styles = [self.styles[bi] for bi in bin_indexes]
		if self.style_under:
			for idx in np.where(values < self.values[0])[0]:
				out_styles[idx] = self.style_under
		if self.style_over:
			for idx in np.where(values > self.values[-1])[0]:
				out_styles[idx] = self.style_over
		if self.style_bad:
			for idx in np.where(np.isnan(values))[0]:
				out_styles[idx] = self.style_bad
		return out_styles

	def to_colormap(self):
		"""
		Get corresponding Colormap object. Only applicable if :param:`styles`
		contains matplotlib colors
		"""
		if self.is_color_style():
			cmap = matplotlib.colors.ListedColormap(self.styles, name=self.value_key)
			if self.style_under:
				cmap.set_under(self.style_under)
			if self.style_over:
				cmap.set_over(self.style_over)
			if self.style_bad:
				cmap.set_bad(self.style_bad)
			return cmap

	def get_norm(self):
		"""
		Get corresponding Normalize object
		"""
		return matplotlib.colors.BoundaryNorm(self.values, len(self.styles))

	def to_scalar_mappable(self, values=None):
		"""
		Get corresponding Scalarmappable object. Only applicable if
		:param:`styles` contains matplotlib colors

		:param values:
			list or array, data values
			(default: None)

		:return:
			instance of :class:`matplotlib.cm.ScalarMappable`
		"""
		if self.is_color_style():
			#cmap, norm = matplotlib.colors.from_levels_and_colors(self.values, self.styles)
			cmap = self.to_colormap()
			norm = self.get_norm()
			sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
			if values is None:
				sm.set_array(self.values)
			else:
				sm.set_array(values)
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
		labels corresponding to breakpoints, and which will be used in
		the thematic legend or color bar
		(default: [], will use :param:`values`)
	:param value_key:
	:param add_legend:
	:param colorbar_style:
		see :class:`ThematicStyle`
	:param style_under:
		style corresponding to data values lower than range in :param:`values`
		(default: None)
	:param style_over:
		style corresponding to data values higher than range in :param:`values`
		(default: None)
	:param style_bad:
		style corresponding to 'bad' data values (NaN)
		(default: None)
	"""
	def __init__(self, values, styles, labels=[], value_key=None, add_legend=True,
				colorbar_style=None, style_under=None, style_over=None, style_bad=None):
		super(ThematicStyleGradient, self).__init__(value_key, add_legend, colorbar_style,
													style_under, style_over, style_bad)
		self.values = np.array(values, dtype='f')
		if isinstance(styles, (list, tuple, np.ndarray)):
			assert len(values) == len(styles)
			self.set_styles(styles)
		elif isinstance(styles, basestring) and styles[:12] == "random_color":
			if ',' in styles:
				random_seed = int(styles.split(',')[-1])
			else:
				random_seed = None
			self.set_styles_from_random_colors(random_seed)
		elif isinstance(styles, (basestring, matplotlib.colors.Colormap)):
			self.set_styles_from_colormap(styles)
		#TODO: assert len(values) = len(styles)
		if not (labels is None or labels == []):
			self.labels = labels
		else:
			#self.labels = map(str, self.values)
			self.labels = []
			for i in range(len(self.values) - 1):
				self.labels.append("[%s - %s[" % (self.values[i], self.values[i+1]))
			self.labels.append("[%s -" % self.values[-1])

		## Override colorbar default ticks and tick_labels
		if self.colorbar_style and self.is_color_style():
			if self.colorbar_style.ticks is None:
				sm = self.to_scalar_mappable()
				self.colorbar_style.ticks = sm.get_array()
			if self.colorbar_style.tick_labels is None and labels:
				self.colorbar_style.tick_labels = labels

	def set_styles(self, styles):
		self.styles = styles

	def set_styles_from_colormap(self, color_map):
		if isinstance(color_map, (str)):
			color_map = matplotlib.cm.get_cmap(color_map)
		N = len(self.values)
		norm  = matplotlib.colors.Normalize(vmin=0, vmax=N-1)
		sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=color_map)
		styles = [sm.to_rgba(i) for i in range(N)]
		self.set_styles(styles)
		self.style_under = color_map._rgba_under
		self.style_over = color_map._rgba_over
		self.style_bad = color_map._rgba_bad

	def set_styles_from_random_colors(self, random_seed=None):
		import random
		from itertools import cycle

		N = len(self.values)
		rnd = random.Random()
		rnd.seed(random_seed)
		named_colors = matplotlib.colors.cnames.keys()
		rnd.shuffle(named_colors)
		named_colors = cycle(named_colors)
		styles = [named_colors.next() for i in range(N)]
		self.set_styles(styles)

	def __call__(self, values):
		"""
		Convert data values to style values

		:param values:
			list or array of floats, data values

		:return:
			float or rgba array
		"""
		values = self.apply_value_key(values)
		try:
			out_styles = np.interp(values, self.values, self.styles)
		except:
			sm = self.to_scalar_mappable()
			#return sm.to_rgba(self.apply_value_key(values), alpha=self.alpha)
			return sm.to_rgba(values)
		else:
			if self.style_under:
				out_styles[values < self.values[0]] = self.style_under
			if self.style_over:
				out_styles[values > self.values[-1]] = self.style_over
			if self.style_bad:
				out_styles[np.isnan(values)] = self.style_bad
			return out_styles

	def to_colormap(self):
		"""
		Get corresponding Colormap object. Only applicable if :param:`styles`
		contains matplotlib colors
		"""
		if self.is_color_style():
			#x = self.values / self.values.max()
			x = np.linspace(0., 1., len(self.values))
			cmap = matplotlib.colors.LinearSegmentedColormap.from_list(self.value_key, list(zip(x, self.styles)))
			cmap._init()
			if self.style_under:
				cmap.set_under(self.style_under)
			if self.style_over:
				cmap.set_over(self.style_over)
			if self.style_bad:
				cmap.set_bad(self.style_bad)
			return cmap

	def get_norm(self):
		"""
		Get corresponding Normalize object
		"""
		from .cm.norm import PiecewiseLinearNorm
		return PiecewiseLinearNorm(self.values)
		#return matplotlib.colors.Normalize(vmin=self.values.min(), vmax=self.values.max())

	def to_scalar_mappable(self, values=None):
		"""
		Get corresponding Scalarmappable object. Only applicable if
		:param:`styles` contains matplotlib colors

		:param values:
			list or array, data values
			(default: None)

		:return:
			instance of :class:`matplotlib.cm.ScalarMappable`
		"""
		if self.is_color_style():
			norm = self.get_norm()
			cmap = self.to_colormap()
			sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
			if values is None:
				sm.set_array(self.values)
			else:
				sm.set_array(values)
			return sm


class ThematicStyleColormap(ThematicStyle):
	"""
	Thematic style feature corresponding to a matplotlib colormap.

	:param color_map:
		string or matplotlib colormap (default: "jet")
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
	# TODO: add param labels too?
	# TODO: add bad_rgba, over_rgba, under_rgba
	# TODO: style_under, style_over, style_bad?
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

	def to_scalar_mappable(self, values=None):
		"""
		Convert colormap and norm to a Scalarmappable object

		:param values:
			list or array, data values
			(default: None)

		:return:
			instance of :class:`matplotlib.cm.ScalarMappable`
		"""
		norm = self.get_norm()
		sm = matplotlib.cm.ScalarMappable(norm=norm, cmap=self.color_map)
		if values is None:
			sm.set_array(self.values)
		else:
			sm.set_array(values)
		return sm

	def scale_hls(self, hue_factor=1.0, lightness_factor=1.0, saturation_factor=1.0):
		"""
		Scale hue, lightness and/or saturation of entire colormap.
		If factor is positive, it will be simply multiplied.
		If factor is negative, scaling is applied to the inverse property:
			1 - scale_factor * (1 - property)
		E.g., if ligthness factor is -0.6, the result would be to make
		the colormap 60% less dark, which is not the same as making it
		60% lighter.

		:param hue_factor:
			float, hue scaling factor
			(default: 1.0)
		:param lightness_factor:
			float, lightness scaling factor
			(default: 1.0)
		:param saturation_factor:
			float, saturation scaling factor
			(default: 1.0)
		"""
		# TODO: combine with adjust_cmap_luminosity and adjust_cmap_saturation
		# functions in cm submodule.
		import colorsys
		num_colors = self.color_map._lut.shape[0]
		#self.color_map._lut[,:3] *= factor
		for i in range(num_colors):
			rgb = self.color_map._lut[i,:3]
			hls = np.array(colorsys.rgb_to_hls(*rgb))
			#rgb = colorsys.hls_to_rgb(hls[0], 1 - lightness_factor * (1 - hls[1]), hls[2])
			#hls *= np.array([hue_factor, lightness_factor, saturation_factor])
			if hue_factor >= 0:
				hls[0] *= hue_factor
			else:
				hls[0] = 1 - np.abs(hue_factor) * (1 - hls[0])
			if lightness_factor >= 0:
				hls[1] *= lightness_factor
			else:
				hls[1] = 1 - np.abs(lightness_factor) * (1 - hls[1])
			if saturation_factor >= 0:
				hls[2] *= saturation_factor
			else:
				hls[2] = 1 - np.abs(saturation_factor) * (1 - hls[2])
			hls = np.maximum(0, np.minimum(1, hls))
			rgb = colorsys.hls_to_rgb(*hls)
			self.color_map._lut[i,:3] = rgb


class ColorbarStyle(BasemapStyle):
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
	:param label_size:
		int, font size of colorbar label (default: 14)
	:param tick_label_size:
		int, font size of colorbar tick labels (default: 10)
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	"""
	def __init__(self, title="", location="bottom", size='5%', pad='10%', extend="neither", spacing="uniform", ticks=None, tick_labels=None, format="%s", drawedges=False, label_size=14, tick_label_size=10, alpha=1.):
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
		self.label_size = label_size
		self.tick_label_size = tick_label_size
		self.alpha = alpha

		# TODO: implement other font style parameters for label and tick labels

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
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d

	@classmethod
	def from_dict(self, style_dict):
		"""
		Construct colorbar style from dictionary.

		:param style_dict:
			dictionary containing colorbarstyle properties as keys

		:return:
			instance of :class:`ColorbarStyle`
		"""
		colorbarstyle = ColorbarStyle()
		for key in style_dict.keys():
			if hasattr(colorbarstyle, key):
				setattr(colorbarstyle, key, style_dict[key])
		return colorbarstyle


class GridStyle(BasemapStyle):
	"""
	Class defining how a regular grid is plotted in matplotlib

	:param color_map_theme:
		instance of :class:`ThematicStyleColormap`
	:param color_gradient:
		string, "continuous", "discontinuous" or None.
		Defines if color_gradient should be continuous or discontinuous.
		If None, only contour lines will be plotted.
		(default: "continuous")
	:param pixelated:
		bool, whether grid cells should have a flat color (True) or
		shaded (False).
		(default: False)
	:param line_style:
		instance of :class:`LineStyle`, defining how contour lines will
		be plotted
	:param contour_levels:
		list or array, defining contour-line values
		(default: None, will be determined automatically by matplotlib)
	:param colorbar_style:
		instance of :class:`ColorbarStyle`, will override colorbar_style
		property of color_map_theme
	:param hillshade_style:
		instance of :class:`HillShadeStyle` to apply hill shading
		(default: None)
	:param fill_hatches:
		list of chars, hatch pattern format string for different contour
		levels: "/" | "\\" | "|" | "-" | "+" | "x" | "o" | "O" | "." | "*"
		Note: repeat pattern format to increase density, e.g. "//"
		or "..."

	Note: format of contour labels is determined by format property
	of colorbar_style.
	"""
	def __init__(self, color_map_theme=ThematicStyleColormap("jet"), color_gradient="continuous", pixelated=False, line_style=None, contour_levels=None, colorbar_style=None, hillshade_style=None, fill_hatches=[]):
		self.color_map_theme = color_map_theme
		self.color_gradient = color_gradient
		self.pixelated = pixelated
		self.line_style = line_style
		self.contour_levels = contour_levels
		if colorbar_style:
			self.color_map_theme.colorbar_style = colorbar_style
		self.hillshade_style = hillshade_style
		self.fill_hatches = fill_hatches
	# TODO: would it be more logical to define fill_hatches elsewhere
	# (as it is related to contours)

	@property
	def colorbar_style(self):
		if self.color_map_theme:
			return self.color_map_theme.colorbar_style
		else:
			return None

	@property
	def label_format(self):
		if self.color_map_theme and self.color_map_theme.colorbar_style:
			return self.color_map_theme.colorbar_style.format
		else:
			return "%s"


class HillshadeStyle(BasemapStyle):
	"""
	:param azimuth:
		float, azimuth of light source in degrees
	:param elevation_angle:
		float, elevation angle of light source in degrees
	:param scale:
		float, multiplication factor to apply (default: 1.)
	:param color_map:
		string or matplotlib colormap to be used if only hillshade
		map is plotted
		(default: "gray")
	:param blend_mode:
		str, type of blending used to combine colormapped data values
		with illumination intensity, one of "pegtop", "hsv", "overlay"
		or "soft"
		(default: "pegtop")
	:param elevation_grid:
		instance of :class:`MeshGridData`
		alternative grid to get hillshading from
		(default: None)
	"""
	def __init__(self, azimuth, elevation_angle, scale=1., color_map="gray",
				blend_mode="pegtop", elevation_grid=None):
		self.azimuth = azimuth
		self.elevation_angle = elevation_angle
		self.scale = scale
		self.color_map = color_map
		self.blend_mode = blend_mode
		self.elevation_grid = elevation_grid


class VectorStyle(BasemapStyle):
	"""
	Style defining how vectors are plotted
	"""
	def __init__(self,
			units="dots",
			angles="uv",
			scale=None,
			scale_units="dots",
			width=None,
			head_width=3,
			head_length=5,
			head_axis_length=4.5,
			min_shaft=1,
			min_length=1,
			pivot='tail',
			color='k',
			alpha=1.,
			thematic_legend_style=None):
		self.units = units
		self.angles = angles
		self.scale = scale
		self.scale_units = scale_units
		self.width = width
		self.head_width = head_width
		self.head_length = head_length
		self.head_axis_length = head_axis_length
		self.min_shaft = min_shaft
		self.min_length = min_length
		self.pivot = pivot
		self.color = color
		self.alpha = alpha
		self.thematic_legend_style = thematic_legend_style

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the colorbar function
		"""
		d = {}
		d["units"] = self.units
		d["angles"] = self.angles
		d["scale"] = self.scale
		d["scale_units"] = self.scale_units
		d["width"] = self.width
		d["headwidth"] = self.head_width
		d["headlength"] = self.head_length
		d["headaxislength"] = self.head_axis_length
		d["minshaft"] = self.min_shaft
		d["minlength"] = self.min_length
		d["pivot"] = self.pivot
		d["color"] = self.color
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d


class LegendStyle(BasemapStyle):
	"""
	Style defining how to plot basemap legend

	:param title:
		String, legend title (default: "")
	:param location:
		String or Int: location of legend (matplotlib location code):
			"best" 	0
			"upper right" 	1
			"upper left" 	2
			"lower left" 	3
			"lower right" 	4
			"right" 	5
			"center left" 	6
			"center right" 	7
			"lower center" 	8
			"upper center" 	9
			"center" 	10
		(default: 0)
	:param label_style:
		instance of :class:`FontStyle` or :class:`TextStyle`, font style of legend labels
		Note: use TextStyle if you want to control horizontal alignment
		(default: FontStyle())
	:param title_style:
		instance of :class:`FontStyle`, font style of legend title
		(default: FontStyle(font_weight='bold'))
	:param marker_scale:
		Float, relative size of legend markers with respect to map
		(default: None)
	:param frame_on:
		Bool, whether or not to draw a frame around the legend
		(default: True)
	:param fancy_box:
		Bool, whether or not to draw a frame with a round fancybox
		(default: False)
	:param shadow:
		Bool, whether or not to draw a shadow behind legend
		(default: False)
	:param ncol:
		Int, number of legend columns (default: 1)
	:param border_pad:
		Float, fractional whitespace inside the legend border
		(default: None)
	:param label_spacing:
		Int (or Float?), vertical space between the legend entries
		(default: None)
	:param handle_length:
		Int (or Float?), length of the legend handles (default: None)
	:param handle_height:
		Int (or Float?), height of the legend handles (default: None)
	:param handle_text_pad:
		Float, pad between the legend handle and text (default: None)
	:param border_axes_pad:
		Float, pad between the axes and legend border (default: None)
	:param column_spacing:
		Float (or Int?), spacing between columns (default: None)
	:param num_points:
		Int, number of points in the legend for line (default: 1)
	:param num_scatter_points:
		Int, number of points in the legend for scatter plot (default: 3)
	:param alpha:
		Float, alpha value for the frame (default: 1.)
	"""
	def __init__(self, title="", location=0, label_style=FontStyle(), title_style=FontStyle(font_weight='bold'), marker_scale=None, frame_on=True, frame_color='k', frame_width=1, fill_color='w', fancy_box=False, shadow=False, ncol=1, border_pad=None, label_spacing=None, handle_length=None, handle_height=None, handle_text_pad=None, border_axes_pad=None, column_spacing=None, num_points=1, num_scatter_points=3, alpha=1.):
		self.title = title
		self.location = location
		self.label_style = label_style
		self.title_style = title_style
		self.marker_scale = marker_scale
		self.frame_on = frame_on
		self.frame_color = frame_color
		self.frame_width = frame_width
		self.fill_color = fill_color
		self.fancy_box = fancy_box
		self.shadow = shadow
		self.ncol = ncol
		self.border_pad = border_pad
		self.label_spacing = label_spacing
		self.handle_length = handle_length
		self.handle_height = handle_height
		self.handle_text_pad = handle_text_pad
		self.border_axes_pad = border_axes_pad
		self.column_spacing = column_spacing
		self.num_points = num_points
		self.num_scatter_points = num_scatter_points
		self.alpha = alpha

	def to_kwargs(self):
		"""
		Return a dictionary with keys corresponding to matplotlib parameter names,
		and which can be passed to the legend function
		"""
		## Note: frame_color, fill_color and frame_width are passed differently!
		d = {}
		d["loc"] = self.location
		d["prop"] = self.label_style.to_font_props()
		d["markerscale"] = self.marker_scale
		d["frameon"] = self.frame_on
		d["fancybox"] = self.fancy_box
		d["shadow"] = self.shadow
		d["ncol"] = self.ncol
		d["borderpad"] = self.border_pad
		d["labelspacing"] = self.label_spacing
		d["handlelength"] = self.handle_length
		d["handleheight"] = self.handle_height
		d["handletextpad"] = self.handle_text_pad
		d["borderaxespad"] = self.border_axes_pad
		d["columnspacing"] = self.column_spacing
		d["numpoints"] = self.num_points
		d["scatterpoints"] = self.num_scatter_points
		d["framealpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d


class ScalebarStyle(BasemapStyle):
	"""
	Style defining how to plot scale bar

	:param center:
		(lon, lat) tuple: position of scale bar in geographic coordinates
	:param length:
		float, distance represented by scale bar
	:param units:
		str, units of :param:`length` (default: 'km')
	:param bar_style:
		str, style of scale bar, either "simple" or "fancy"
		(default: "simple")
	:param yoffset:
		float, controls how tall the scale bar is, and how far the
		annotations are offset from the scale bar.
		(default: None, corresponds to 0.02 times the height of the map)
	:param label_style:
		str, either "simple" or "default", or False. If False, label
		will be empty (default: "simple")
	:param font_size:
		int, font size for map scale annotations (default: 9)
	:param font_color:
		matplotlib color spec, color for map scale annotations (default: 'k')
	:param format:
		str, string formatter to format numeric values
	:param fill_color1:
	:param fill_color2:
		matplotlib color spec, colors of the alternating filled regions
		for "fancy" barstyle (default: 'w' and 'k')
	:param line_color:
		matplotlib color spec, color of the scale
		(default: 'k')
	:pram line_width:
		float, line width
		(default: 1)
	"""
	def __init__(self, center, length, units='km', bar_style='simple', yoffset=None, label_style='simple', font_size=9, font_color='k', format='%d', fill_color1='w', fill_color2='k', line_color='k', line_width=1):
		self.center = center
		self.length = length
		self.units = units
		self.bar_style = bar_style
		self.yoffset = yoffset
		self.label_style = label_style
		self.font_size = font_size
		self.font_color = font_color
		self.format = format
		self.fill_color1 = fill_color1
		self.fill_color2 = fill_color2
		self.line_color = line_color
		self.line_width = line_width

	@property
	def lon(self):
		return self.center[0]

	@property
	def lat(self):
		return self.center[1]

	def to_kwargs(self):
		d = {}
		d["lon"] = self.lon
		d["lat"] = self.lat
		d["length"] = self.length
		d["units"] = self.units
		d["barstyle"] = self.bar_style
		d["yoffset"] = self.yoffset
		d["labelstyle"] = self.label_style
		d["fontsize"] = self.font_size
		d["fontcolor"] = self.font_color
		d["fillcolor1"] = self.fill_color1
		d["fillcolor2"] = self.fill_color2
		d["linecolor"] = self.line_color
		d["linewidth"] = self.line_width
		return d


class MapBorderStyle(BasemapStyle):
	"""
	Style defining how to plot map border

	:param line_width:
		float, line width of map border (default: 1)
	:param line_color:
		matplotlib color spec, color of border line (default: 'k')
	:param fill_color:
		matplotlib color spec, color for map region background
		(default: None)
	"""
	def __init__(self, line_width=1, line_color="k", fill_color="w"):
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color or "none"

	def to_kwargs(self):
		d = {}
		d["linewidth"] = self.line_width
		d["color"] = self.line_color
		d["fill_color"] = self.fill_color
		return d


class GraticuleStyle(BasemapStyle):
	"""
	Style defining how to plot graticule

	:param line_style:
		instance of :class:`LineStyle`, style for meridians and parallels
		Note: only color, line_width and dash_pattern are taken into account
		(default: LineStyle(dash_pattern=[1,1]))
	:param label_style:
		instance of :class:`TextStyle`, style for longitude and latitude
		labels
		(default: TextStyle())
	:param annot_axes:
		str, containing 'N', 'E', 'S' and/or 'W' characters, denoting which
		side(s) of the map grid lines should be annotated
		(default: "SE")
	:param annot_style:
		str, annotation style. if set to '+/-', east and west longitudes
		are labelled with '+' and '-', otherwise they are labelled with
		'E' and 'W'
		(default: "")
	:param annot_format:
		str, format string to format the meridian labels
		or a function that takes a longitude value in degrees as it's only
		argument and returns a formatted string
		(default '%g')
	:param label_offset:
		(xoffset, yoffset) tuple specifying label offset from edge of map
		in x- and y-direction (in map projection coordinates?)
		(default: (None, None))
	:param lat_max:
		float, absolute value of latitude to which meridians are drawn
		(default: 80)
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	"""
	# TODO: check label_offset units
	# TODO: add parameter to control plotting of meridian labels left and right
	# and parallel labels top and bottom (something like annot_strict)
	def __init__(self, line_style=LineStyle(dash_pattern=[1,1]), label_style=TextStyle(), annot_axes="SE",
				annot_style="", annot_format='%g', label_offset=(None, None), lat_max=80,
				alpha=1.):
		self.line_style = line_style
		self.label_style = label_style
		self.annot_axes = annot_axes
		self.annot_style = annot_style
		self.annot_format = annot_format
		self.label_offset = label_offset
		self.lat_max = lat_max
		self.alpha = alpha

	def to_kwargs(self):
		d = {}
		d["color"] = self.line_style.line_color
		d["linewidth"] = self.line_style.line_width
		d["dashes"] = self.line_style.dash_pattern
		d["labels"] = [c in self.annot_axes for c in "WENS"]
		d["labelstyle"] = self.annot_style
		d["fmt"] = self.annot_format
		d["xoffset"] = self.label_offset[0]
		d["yoffset"] = self.label_offset[1]
		d["latmax"] = self.lat_max
		text_kwargs = self.label_style.to_kwargs()
		del text_kwargs["alpha"]
		d.update(text_kwargs)
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d


class GridImageStyle(BasemapStyle):
	"""
	Style defining how to plot grid image

	:param masked:
		bool, whether or not region outside grid image should be masked
		(default: True)
	:param interpolation_method:
		str, one of "nearest neighbor", "bilinear" or "cubic spline"
		(default: "bilinear")
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	"""
	def __init__(self, masked=True, interpolation_method="bilinear", alpha=1.):
		self.masked = masked
		self.interpolation_method = interpolation_method
		self.alpha = alpha

	def get_order(self, interpolation_method):
		method_order_dict = {"nearest neighbor": 0, "bilinear": 1, "cubic spline": 3}
		return method_order_dict[interpolation_method]

	def to_kwargs(self):
		d = {}
		d['masked'] = self.masked
		d['order'] = self.get_order(self.interpolation_method)
		#d['alpha'] = self.alpha
		return d


class ImageStyle(BasemapStyle):
	"""
	Style defining how to plot an image

	:param width:
		int, width of image in pixels
		(default: None, use original width of image)
	:param height:
		int, height of image in pixels
		(default: None, determine height from width keeping original aspect ratio)
	:param horizontal_alignment:
		str, one of 'left', 'center', 'right' or 'stretch' (= 'fill'),
		horizontal alignment with respect to image position
		(default: 'center')
	:param vertical_alignment:
		str, one of 'bottom', 'center', 'top' or 'stretch' (= 'fill'),
		vertical alignment with respect to image position
		(default: 'center')
	:param on_top:
		bool, whether or not to plot image on top of all other layers
		(including graticule)
		(default: False)
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	"""
	def __init__(self, width=None, height=None, horizontal_alignment='center',
				vertical_alignment='center', on_top=False, alpha=1.):
		self.width = width
		self.height = height
		self.horizontal_alignment = horizontal_alignment
		self.vertical_alignment = vertical_alignment
		self.on_top = on_top
		self.alpha = alpha


class WMSStyle(BasemapStyle):
	"""
	Style defining how to plot WMS image

	:param xpixels:
		int, requested number of image pixels in x-direction
		(default: 400)
	:param ypixels:
		int, requested number of image pixels in y-direction
		(default: None, will infer the number from from xpixels and the aspect
		ratio of the map projection region)
	:param format:
		str, image format, either 'png' or 'jpg'
		(default: 'png')
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	"""
	def __init__(self, xpixels=400, ypixels=None, format='png', alpha=1.):
		self.xpixels = xpixels
		self.ypixels = ypixels
		self.format = format
		self.alpha = alpha

	def to_kwargs(self):
		d = {}
		d["xpixels"] = self.xpixels
		d["ypixels"] = self.ypixels
		d["format"] = self.format
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d
