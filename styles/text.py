"""
Text-related styles
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import matplotlib

from .base import BasemapStyle


__all__ = ['FontStyle', 'TextStyle', 'DefaultTitleTextStyle']


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
	:param outline_color:
		matplotlib color spec, color of text outline
		(default: "w")
	:param outline_width:
		float, line width of text outline
		(default: 0)
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
				outline_color="w",
				outline_width=0,
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
		self.outline_color = outline_color
		self.outline_width = outline_width
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
