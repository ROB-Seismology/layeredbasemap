"""
Miscellaneous data types
"""

from __future__ import absolute_import, division, print_function, unicode_literals


import numpy as np

from .base import BasemapData
from .point import MultiPointData


__all__ = ['FocmecData', 'MaskData', 'PiechartData']


class FocmecData(MultiPointData):
	"""
	"""
	def __init__(self, lons, lats, sdr, z=None, values=None, labels=None, style_params=None):
		super(FocmecData, self).__init__(lons, lats, z, values, labels, style_params)
		self.sdr = sdr

	def sort(self, value_key=None, ascending=True):
		"""
		Sort focmec data in-place based on a value column

		:param value_key:
			str, name of value column to be used for sorting
			(default: None, assumes values is a single list or array)
		:param ascending:
			bool, whether sort order should be ascending (True)
			or descending (False)
			(default: True)

		:return:
			array with indexes representing sort order
		"""
		sorted_indexes = MultiPointData.sort(self, value_key=value_key, ascending=ascending)
		self.sdr = np.array(self.sdr)[sorted_indexes]
		return sorted_indexes


class MaskData(BasemapData):
	def __init__(self, polygon, outside=True):
		self.polygon = polygon
		self.outside = outside


class PiechartData(BasemapData):
	"""
	Class representing pie chart data

	:param lons:
		list or array of floats, longitudes
	:param lats:
		list or array of floats, latitudes
	:param ratios:
		nested list or 2-D array of ratios of different pie chart
		categories (need not sum to 1)
	:param sizes:
		list or array of floats, pie chart sizes
	"""
	def __init__(self, lons, lats, ratios, sizes):
		self.lons = np.asarray(lons)
		self.lats = np.asarray(lats)
		self.ratios = np.asarray(ratios)
		self.sizes = np.asarray(sizes)

	def __len__(self):
		return len(self.lons)

	def __getitem__(self, index):
		lon = self.lons[index]
		lat = self.lats[index]
		ratios = self.ratios[index]
		size = self.sizes[index]
		return (lon, lat, ratios, size)

	def __iter__(self):
		for i in range(len(self)):
			yield self.__getitem__(i)
