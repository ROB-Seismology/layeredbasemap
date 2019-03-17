"""
base style
"""

from __future__ import absolute_import, division, print_function, unicode_literals



__all__ = []


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

		## Allow setting properties of substyles,
		## e.g. label_style in higher-order styles
		## (Not working at the moment in layered_basemap.py)
		if isinstance(other, dict):
			for attr in other.keys():
				if '.' in attr:
					main_attr, subattr = attr.split('.')
					val = other[attr]
					setattr(getattr(self, main_attr), subattr, val)
