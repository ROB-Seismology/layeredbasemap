"""
Grid-related styles
"""

from __future__ import absolute_import, division, print_function, unicode_literals


from .base import BasemapStyle
from .thematic import ThematicStyleColormap
from .vector import LineStyle


__all__ = ['GridStyle', 'GridImageStyle', 'ImageStyle', 'HillshadeStyle',
			'WMSStyle']


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
	:param contour_labels:
		list or array, containing contour levels to be labeled
		(default: None)
	:param label_format:
		str, format of contour labels
		(default: None, will use format property of :param:`colorbar_style`)
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
	"""
	def __init__(self, color_map_theme=ThematicStyleColormap("jet"),
				color_gradient="continuous", pixelated=False, line_style=None,
				contour_levels=None, contour_labels=None, label_format=None,
				colorbar_style=None, hillshade_style=None, fill_hatches=[]):
		self.color_map_theme = color_map_theme
		self.color_gradient = color_gradient
		self.pixelated = pixelated
		self.line_style = line_style
		self.contour_levels = contour_levels
		self.contour_labels = contour_labels
		self._label_format = label_format
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
		if self._label_format is not None:
			return self._label_format
		elif self.color_map_theme and self.color_map_theme.colorbar_style:
			return self.color_map_theme.colorbar_style.format
		else:
			return "%E"


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
	:param border_width:
		int, width of border to draw around image (in pixels corresponding
		to the original image size)
		(default: 0)
	:param border_color:
		float, greyscale value or
		float array, RGB[A] values
		in the range 0 - 1
		(default: 1 = white)
	:param alpha:
		Float in the range 0 - 1, opacity (default: 1.)
	"""
	def __init__(self, width=None, height=None, horizontal_alignment='center',
				vertical_alignment='center', on_top=False,
				border_width=0, border_color=1, alpha=1.):
		self.width = width
		self.height = height
		self.horizontal_alignment = horizontal_alignment
		self.vertical_alignment = vertical_alignment
		self.on_top = on_top
		self.border_width = border_width
		self.border_color = border_color
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
