"""
Decoration styles
"""

from __future__ import absolute_import, division, print_function, unicode_literals


from .base import BasemapStyle
from .text import FontStyle, TextStyle
from .vector import LineStyle


__all__ = ['ColorbarStyle', 'LegendStyle', 'ScalebarStyle',
			'MapBorderStyle', 'GraticuleStyle']


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
		if self.label_style:
			text_kwargs = self.label_style.to_kwargs()
			del text_kwargs["alpha"]
			d.update(text_kwargs)
		d["alpha"] = {True: None, False: self.alpha}[self.alpha == 1]
		return d
