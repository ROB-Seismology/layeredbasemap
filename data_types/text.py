"""
Text data
"""

from __future__ import absolute_import, division, print_function, unicode_literals


from .base import SingleData, MultiData
from .point import PointData


__all__ = ['TextData', 'MultiTextData']


class TextData(SingleData):
	"""
	Class representing single text label

	:param lon:
		float, longitude
	:param lat:
		float, latitude
	:param label:
		strings, label to be plotted
	:param coord_frame:
		str, matplotlib coordinate frame for lons, lats:
		"geographic" or one of the matplotlib coordinate frames:
		"figure points", "figure pixels", "figure fraction", "axes points",
		"axes pixels", "axes fraction", "data", "offset points" or "polar"
		(default: "geographic")
	:param style_params:
		dict, mapping style parameters to a value. These values will
		override the overall layer style
		(default: None --> {})
	"""
	def __init__(self, lon, lat, label, coord_frame="geographic", style_params=None):
		self.lon = lon
		self.lat = lat
		self.label = label
		self.coord_frame = coord_frame
		self.style_params = style_params or {}

	def to_multi_text(self):
		"""
		Convert to multi-text data

		:return:
			instance of :class:`MultiTextData`
		"""
		style_params = self._get_multi_values(self.style_params)
		return MultiTextData([self.lon], [self.lat], labels=[self.label],
						coord_frame=self.coord_frame, style_params=style_params)


class MultiTextData(MultiData):
	"""
	Class representing multiple text data.

	:param lons:
		list or array of floats, longitudes
	:param lats:
		list or array of floats, latitudes
	:param labels:
		list of strings, labels to be plotted
	:param coord_frame:
		str, matplotlib coordinate frame for lons, lats:
		"geographic" or one of the matplotlib coordinate frames:
		"figure points", "figure pixels", "figure fraction", "axes points",
		"axes pixels", "axes fraction", "data", "offset points" or "polar"
		(default: "geographic")
	:param style_params:
		dict, mapping style parameters to a list of values. These values
		will override the overall layer style.
		(default: None --> {})
	"""
	def __init__(self, lons, lats, labels, coord_frame="geographic", style_params=None):
		self.lons = lons
		self.lats = lats
		self.labels = labels
		self.coord_frame = coord_frame
		self.style_params = style_params or {}

	def __getitem__(self, index):
		lon = self.lons[index]
		lat = self.lats[index]
		label = self._get_label_at_index(index)
		style_params = self._get_style_params_at_index(index)
		return TextData(lon, lat, label=label, coord_frame=self.coord_frame,
						style_params=style_params)

	def append(self, pt_data):
		"""
		Append from single-value text data.
		Note: we don't check if :prop:`coord_frame` is consistent!

		:param pt_data:
			instance of :class:`PointData`
		"""
		#if getattr(pt_data, "coord_frame") != self.coord_frame:
		#	print("Warning: coord_frame not the same!")
		self.lons.append(pt_data.lon)
		self.lats.append(pt_data.lat)
		self.labels.append(pt_data.label or "")
		self._append_to_multi_values(self.style_params, pt_data.style_params)
