"""
Thematic styles
"""

from __future__ import absolute_import, division, print_function, unicode_literals


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

from .base import BasemapStyle


__all__ = ['ThematicStyleIndividual', 'ThematicStyleRanges',
			'ThematicStyleGradient', 'ThematicStyleColormap']


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
			if isinstance(style, (int, float, np.integer, np.floating)):
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
			self.labels = self.gen_labels()

		## Override colorbar default ticks and tick_labels
		if self.colorbar_style and self.is_color_style():
			if self.colorbar_style.ticks is None:
				sm = self.to_scalar_mappable()
				self.colorbar_style.ticks = sm.get_array()
			if self.colorbar_style.tick_labels is None:
				self.colorbar_style.tick_labels = self.labels

	def gen_labels(self, as_ranges=None):
		"""
		Generate labels from values

		:param as_ranges:
			dummy argument for compatibility with other ThematicStyle
			classes, has no effect

		:return:
			list of strings
		"""
		labels = []
		for val in self.values:
			if PY2 and isinstance(val, str):
				val = val.decode('iso-8859-1')
			if isinstance(val, basestring):
				labels.append(val)
			else:
				labels.append(str(val))
		return labels

	def is_numeric(self):
		return np.array([not isinstance(self.values[idx], (basestring, list))
						for idx in range(len(self.values))]).all()

	def is_monotonously_increasing(self):
		if self.is_numeric():
			sign_diff = np.sign(np.diff(self.values))
			return np.all(sign_diff == sign_diff[0])
		else:
			return False

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
		## Set style_under/_over/_bad if not set yet
		if not self.style_under:
			self.style_under = color_map._rgba_under
		if not self.style_over:
			self.style_over = color_map._rgba_over
		if not self.style_bad:
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
		if isinstance(self.values[0], (int, float, np.integer, np.floating)):
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
				if isinstance(self.values[0], (int, float, np.integer, np.floating)):
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
		self.values = np.asarray(values)
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
			self.labels = self.gen_labels()

		## Override colorbar default ticks and tick_labels
		if self.colorbar_style and self.is_color_style():
			if self.colorbar_style.ticks is None:
				sm = self.to_scalar_mappable()
				self.colorbar_style.ticks = sm.get_array()
			if self.colorbar_style.tick_labels is None and labels:
				self.colorbar_style.tick_labels = labels

	def gen_labels(self, as_ranges=True):
		"""
		Generate labels from values

		:param as_ranges:
			bool, whether or not to generate range labels
			(default: True)

		:return:
			list of strings
		"""
		if as_ranges:
			labels = []
			for i in range(len(self.styles)):
				labels.append("%s - %s" % (self.values[i], self.values[i+1]))
		else:
			labels = ["%s" % val for val in self.values]
		return labels

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
		## Set style_under/_over/_bad if not set yet
		if not self.style_under:
			self.style_under = color_map._rgba_under
		if not self.style_over:
			self.style_over = color_map._rgba_over
		if not self.style_bad:
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
		self.values = np.asarray(values)
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
			self.labels = self.gen_labels()

		## Override colorbar default ticks and tick_labels
		if self.colorbar_style and self.is_color_style():
			if self.colorbar_style.ticks is None:
				sm = self.to_scalar_mappable()
				self.colorbar_style.ticks = sm.get_array()
			if self.colorbar_style.tick_labels is None and labels:
				self.colorbar_style.tick_labels = labels

	def gen_labels(self, as_ranges=True):
		"""
		Generate labels from values

		:param as_ranges:
			bool, whether or not to generate range labels
			(default: True)

		:return:
			list of strings
		"""
		if as_ranges:
			labels = []
			for i in range(len(self.values) - 1):
				labels.append("[%s - %s[" % (self.values[i], self.values[i+1]))
			labels.append("[%s -" % self.values[-1])
		else:
			labels = ["%s" % val for val in self.values]
		return labels

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
		## Set style_under/_over/_bad if not set yet
		if not self.style_under:
			self.style_under = color_map._rgba_under
		if not self.style_over:
			self.style_over = color_map._rgba_over
		if not self.style_bad:
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
		from ..cm.norm import PiecewiseLinearNorm
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
	:param style_over:
		color corresponding to data values lower than :param:`vmin`
		(default: None)
	:param style_under:
		color corresponding to data values lower than :param:`vmax`
		(default: None)
	:param style_bad:
		color corresponding to invalid data values
		(default: None)

	Note: if norm is specified, vmin and vmax will only determine the
	range shown in the colorbar; the norm itself will not be affected.
	"""
	# TODO: add param labels too?
	# TODO: add bad_rgba, over_rgba, under_rgba
	# TODO: style_under, style_over, style_bad?
	def __init__(self, color_map="jet", norm=None, vmin=None, vmax=None, alpha=1.0,
				value_key=None, add_legend=True, colorbar_style=None,
				style_under=None, style_over=None, style_bad=None):
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

		## Override
		self.style_under = style_under
		if style_under:
			self.color_map.set_under(style_under)
		self.style_over = style_over
		if style_over:
			self.color_map.set_over(style_over)
		self.style_bad = style_bad
		if style_bad:
			self.color_map.set_bad(style_bad)

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
