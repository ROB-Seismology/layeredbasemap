"""
Styles for vector geometries
"""

from __future__ import absolute_import, division, print_function, unicode_literals


from .base import BasemapStyle
from .thematic import ThematicStyle
#from .decoration import LegendStyle


__all__ = ['PointStyle', 'LineStyle', 'PolygonStyle', 'CompositeStyle']


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
							fill_color="none", dash_pattern=self.dash_pattern,
							label_style=self.label_style, label_anchor=self.label_anchor,
							alpha=self.alpha,
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
	def __init__(self, line_pattern="solid", line_width=1, line_color='k', fill_color='w', fill_hatch=None, hatch_color='k', dash_pattern=[], label_style=None, label_anchor="centroid", alpha=1., thematic_legend_style=None):
		self.line_pattern = {'-': 'solid', '--': 'dashed', ':': 'dotted', '-.': 'dashdot'}.get(line_pattern, line_pattern)
		self.line_width = line_width
		self.line_color = line_color
		self.fill_color = fill_color
		self.fill_hatch = fill_hatch
		self.hatch_color = hatch_color
		self.dash_pattern = dash_pattern
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
							fill_hatch, self.hatch_color, self.dash_pattern, self.label_style,
							self.label_anchor, self.alpha, self.thematic_legend_style)

	def to_line_style(self):
		"""
		Convert to line style.

		:return:
			instance of :class:`LineStyle`
		"""
		return LineStyle(self.line_pattern, self.line_width, self.line_color,
						label_style=self.label_style, label_anchor=self.label_anchor,
						dash_pattern=self.dash_pattern, alpha=self.alpha,
						thematic_legend_style=self.thematic_legend_style)

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
		if self.dash_pattern:
			d["dashes"] = self.dash_pattern
		else:
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
