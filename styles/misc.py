"""
Miscellaneous styles
"""

from __future__ import absolute_import, division, print_function, unicode_literals


from .base import BasemapStyle
from .decoration import LegendStyle


__all__ = ['FocmecStyle', 'FrontStyle', 'PiechartStyle', 'ArrowStyle']


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
	def __init__(self, size=50, line_width=1, line_color='k', fill_color='k',
				bg_color='w', offset=(0,0), offset_coord_frame="offset points",
				alpha=1., thematic_legend_style=None):
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
	:param labels:
		list of labels for the different pie chart categories
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
	:param thematic_legend_style:
		instance of :class:`LegendStyle` or str, title of thematic legend
		labels will be added to (e.g., "main")
		(default: None)
	"""
	def __init__(self, fill_colors, labels, line_color='k', line_width=1,
				start_angle=0, alpha=1., thematic_legend_style=None):
		self.fill_colors = fill_colors
		self.labels = labels
		#self.size = size
		self.line_color = line_color
		self.line_width = line_width
		self.start_angle = start_angle
		self.alpha = alpha
		self.thematic_legend_style = thematic_legend_style

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


class ArrowStyle(BasemapStyle):
	"""
	Style defining how arrows (e.g., in vector grids) are plotted
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
