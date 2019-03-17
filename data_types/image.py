"""
Image data types
"""

from __future__ import absolute_import, division, print_function, unicode_literals


from .base import BasemapData


__all__ = ['ImageData', 'WMSData']


class ImageData(BasemapData):
	"""
	Class representing image

	:param filespec:
		str, full path to image file
	:param lon:
		float, longitude
	:param lat:
		float, latitude
	:param coord_frame:
		str, matplotlib coordinate frame for lons, lats:
		"geographic", "data" or "display"
		(default: "geographic")
	"""
	# TODO: should we also support display coordinates instead of lon, lat??
	def __init__(self, filespec, lon, lat, coord_frame="geographic"):
		self.filespec = filespec
		self.lon = lon
		self.lat = lat
		self.coord_frame = coord_frame


class WMSData(BasemapData):
	"""
	Class representing WMS image

	:param url:
		str, WMS server URL
	"""
	def __init__(self, url, layers, verbose=False):
		self.url = url
		self.layers = layers
		self.verbose = verbose
