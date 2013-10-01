import numpy as np
import numpy.ma as ma
import matplotlib


def interpolate(xin, yin, xout):
	"""
	Wrapper for linear interpolation function
	"""
	## Scipy and numpy interpolation don't work if input values
	## are in decreasing order
	if np.all(np.diff(xin) <= 0):
		xin, yin = xin[::-1], yin[::-1]
	## SciPy
	## Does not support different fill values left and right...
	#from scipy.interpolate import interp1d
	#interpolator = interp1d(xin, yin, bounds_error=False)
	#yout = interpolator(xout)

	## Numpy
	## does not handle NaN correctly...
	yout = np.interp(xout, xin, yin, left=yin[0], right=yin[-1])
	yout[xout == np.nan] = np.nan

	return yout


class PiecewiseLinearNorm(matplotlib.colors.Normalize):
	"""
	Normalize a given value to the 0-1 range by piecewise linear
	interpolation between a number of breakpoints,
	for use in matplotlib plotting functions involving color maps.

	:param breakpoints:
		list or array, containing a number of breakpoints in ascending order,
		including the minimum and maximum value. These will be uniformly spaced
		in the color domain.
	"""
	def __init__(self, breakpoints):
		vmin = breakpoints[0]
		vmax = breakpoints[-1]
		self.breakpoints = np.array(breakpoints)
		matplotlib.colors.Normalize.__init__(self, vmin, vmax)

	def __call__(self, value, clip=None):
		breakpoint_values = np.linspace(0, 1, len(self.breakpoints))
		out_values = interpolate(self.breakpoints, breakpoint_values, value)
		try:
			mask = value.mask
		except:
			mask = None
		#else:
		out_values = ma.masked_array(out_values, mask)
		return out_values

	def to_piecewise_constant_norm(self):
		return PiecewiseConstantNorm(self.breakpoints)


class PiecewiseConstantNorm(matplotlib.colors.Normalize):
	def __init__(self, breakpoints):
		vmin = breakpoints[0]
		vmax = breakpoints[-1]
		self.breakpoints = np.array(breakpoints)
		matplotlib.colors.Normalize.__init__(self, vmin, vmax)

	def __call__(self, value, clip=None):
		breakpoint_values = np.linspace(0, 1, len(self.breakpoints))
		bin_indexes = np.digitize(value, self.breakpoints) - 1
		bin_indexes = bin_indexes.clip(0, len(self.breakpoints)-1)
		out_values = breakpoint_values[bin_indexes]
		out_values[value == np.nan] = np.nan
		try:
			mask = value.mask
		except:
			mask = None
		out_values = ma.masked_array(out_values, mask)
		return out_values
