"""
Color maps and norms for layeredbasemap
"""

from __future__ import absolute_import, division, print_function, unicode_literals


## Reloading mechanism
try:
	reloading
except NameError:
	## Module is imported for the first time
	reloading = False
else:
	## Module is reloaded
	reloading = True
	try:
		## Python 3
		from importlib import reload
	except ImportError:
		## Python 2
		pass


try:
	## Python 2
	basestring
	PY2 = True
except:
	## Python 3
	PY2 = False
	basestring = str


import os
import numpy as np


## norm submodule
if not reloading:
	from . import norm
else:
	reload(norm)


def get_cmap(category, name):
	"""
	Return a named colormap

	:param category:
		str, name of submodule corresponding to colormap category
	:param name:
		str, colormap name

	:return:
		matplotlib Colormap instance or None
	"""
	cmap_name = name.lower() + "_cmap"
	module = __import__(__name__ + ".%s" % category, fromlist=[category])
	try:
		return getattr(module, cmap_name)
	except:
		pass

def get_norm(category, name):
	"""
	Return a named colormap

	:param category:
		str, name of submodule corresponding to colormap category
	:param name:
		str, norm name

	:return:
		matplotlib Normalize instance or None
	"""
	norm_name = name.lower() + "_norm"
	module = __import__(__name__ + ".%s" % category, fromlist=[category])
	try:
		return getattr(module, norm_name)
	except:
		pass

def from_cpt(cpt_filespec, N=256, override_bad_color=True):
	"""
	Convert GMT CPT file to matplotlib colormap
	Modified from the cookbook at SciPy.org
	(http://www.scipy.org/Wiki/Cookbook/Matplotlib/Loading_a_colormap_dynamically)

	:param cpt_filespec:
		str, full path to CPT file, or file descriptor
	:param N:
		int, number of colors in resulting color palette
		If None, N will correspond to the number of actual colors
		(default: 256)
	:param override_bad_color:
		bool, whether or not to override the color specified for bad data
		with transparency
		(default: True)

	:return:
		(cmap, norm) tuple
	"""
	import colorsys
	import numpy as np
	from matplotlib.colors import LinearSegmentedColormap
	from .norm import PiecewiseLinearNorm

	if isinstance(cpt_filespec, basestring):
		if not os.path.splitext(cpt_filespec)[-1]:
			cpt_filespec += ".cpt"
		cpt_fd = open(cpt_filespec)
		cpt_name = os.path.splitext(os.path.split(cpt_filespec)[1])[0]
	else:
		cpt_fd = cpt_filespec
		cpt_name = "cpt"

	x, r, g, b = [], [], [], []
	r_under, r_over, r_bad = None, None, None
	colorModel = "RGB"
	discrete = True
	for line in cpt_fd:
		if not PY2 and isinstance(line, bytes):
			## zipfile's open function doesn't do unicode...
			line = line.decode('ascii')
		cols = line.split()
		if cols:
			if line[0] in "#":
				if cols[-1] == "HSV":
					colorModel = "HSV"
					continue
				else:
					continue
			if cols[0] == "B":
				r_under, g_under, b_under = map(float, cols[1:4])
			elif cols[0] == "F":
				r_over, g_over, b_over = map(float, cols[1:4])
			elif cols[0] == "N":
				r_bad, g_bad, b_bad = map(float, cols[1:4])
			else:
				x.append(float(cols[0]))
				r.append(float(cols[1]))
				g.append(float(cols[2]))
				b.append(float(cols[3]))
				x2 = float(cols[4])
				r2 = float(cols[5])
				g2 = float(cols[6])
				b2 = float(cols[7])
	cpt_fd.close()

	## Append last color for continuous cpt palettes
	if not (r2 == r[-1] and g2 == g[-1] and b2 == b[-1]):
		discrete = False
		x.append(x2)
		r.append(r2)
		g.append(g2)
		b.append(b2)

	x = np.array(x)
	r = np.array(r)
	g = np.array(g)
	b = np.array(b)

	if colorModel == "HSV":
		for i in range(r.shape[0]):
			r[i], g[i], b[i] = colorsys.hsv_to_rgb(r[i]/360., g[i], b[i])
		if r_under != None:
			r_under, g_under, b_under = colorsys.hsv_to_rgb(r_under/360., g_under, b_under)
		if r_over != None:
			r_over, g_over, b_over = colorsys.hsv_to_rgb(r_over/360., g_over, b_over)
		if r_bad != None:
			r_bad, g_bad, b_bad = colorsys.hsv_to_rgb(r_bad/360., g_bad, b_bad)
	elif colorModel == "RGB":
		r, g, b = r/255., g/255., b/255.
		if r_under != None:
			r_under, g_under, b_under = r_under / 255., g_under / 255., b_under / 255.
		if r_over != None:
			r_over, g_over, b_over = r_over / 255., g_over / 255., b_over / 255.
		if r_bad != None:
			r_bad, g_bad, b_bad = r_bad / 255., g_bad / 255., b_bad / 255.

	norm = PiecewiseLinearNorm(x)

	colors = np.asarray(list(zip(r, g, b)))
	if N is None:
		N = len(colors)
	cmap = LinearSegmentedColormap.from_list(cpt_name, colors, N=N)

	min_index, max_index = x.argmin(), x.argmax()
	if r_under is None:
		r_under, g_under, b_under = r[min_index], g[min_index], b[min_index]
	if r_over is None:
		r_over, g_over, b_over = r[max_index], g[max_index], b[max_index]
	if r_bad is None:
		r_bad, g_bad, b_bad = 0., 0., 0.

	cmap.set_under((r_under, g_under, b_under))
	cmap.set_over((r_over, g_over, b_over))
	## Override
	if override_bad_color:
		cmap.set_bad((0., 0., 0., 0.))
	else:
		cmap.set_bad((r_bad, g_bad, b_bad))

	return (cmap, norm)

def from_cpt_city(rel_path, override_bad_color=True):
	"""
	Convert cpt_city color palette to matplotlib colormap

	See http://soliton.vm.bytemark.co.uk/pub/cpt-city/
	and http://docs.idldev.com/mglib/vis/color/cptcity_catalog.html

	:param rel_path:
		str, relative path in cpt_city zip file
		Note: path should use forward slashes as separator, and .cpt
		extension may be omitted
	:param override_bad_color:
		bool, whether or not to override the color specified for bad data
		with transparency
		(default: True)

	:return:
		(cmap, norm) tuple
	"""
	import zipfile

	if not os.path.splitext(rel_path)[-1]:
		rel_path += ".cpt"

	base_folder = os.path.split(__file__)[0]
	for filename in os.listdir(base_folder):
		if filename[:8].lower() == "cpt-city" and filename[-4:].lower() == ".zip":
			zip_filename = filename
			break
	zip_filespec = os.path.join(base_folder, zip_filename)
	with zipfile.ZipFile(zip_filespec) as zf:
		cpt_fd = zf.open('cpt-city/' + rel_path)
		return from_cpt(cpt_fd, override_bad_color=override_bad_color)


def rgb_to_hls(rgb):
	"""
	Convert float rgb values (in the range [0, 1]), in a numpy array to
	hls values.
	"""
	import colorsys

	hls = np.zeros((len(rgb), 3))
	for i in range(len(rgb)):
		r, g, b = rgb[i]
		hls[i] = colorsys.rgb_to_hls(r, g, b)
	return hls


def hls_to_rgb(hls):
	"""
	Convert float hls values (in the range [0, 1]), in a numpy array to
	rgb values.
	"""
	import colorsys

	rgb = np.zeros((len(hls), 3))
	for i in range(len(hls)):
		h, l, s = hls[i]
		rgb[i] = colorsys.hls_to_rgb(h, l, s)
	return rgb


def scale_cmap_range(cmap, scale_factor):
	"""
	Scale colormap range by a fixed factor (RGB values are scaled with
	respect to the center value of 0.5).
	Note: no checking is performed to ensure that RGB values remain
	within the range 0-1!

	:param cmap:
		matplotlib Colormap object
	:param scale_factor:
		float, scale factor
	:return:
		matplotlib ListedColormap object
	"""
	from matplotlib.colors import ListedColormap

	rgba = cmap(np.arange(cmap.N))
	rgba[:, 0:3] = (rgba[:, 0:3] - 0.5) * np.abs(scale_factor) + 0.5
	return ListedColormap(rgba)


def scale_cmap(cmap, scale_factor):
	"""
	Scale colormap RGB values by a fixed factor.
	Note: no checking is performed to ensure that RGB values remain
	within the range 0-1!

	:param cmap:
		matplotlib Colormap object
	:param scale_factor:
		float, scale factor
	:return:
		matplotlib ListedColormap object
	"""
	rgba = cmap(np.arange(cmap.N))
	rgba[:, 0:3] *= np.abs(scale_factor)
	return ListedColormap(rgba)


def adjust_cmap_luminosity(cmap, dlight, colorspace='HLS'):
	"""
	Adjust the lightness or luminosity value (in HLS space) of colormap.
	In HLS, saturated colors have a luminosity of 0.5, in HSV 1.0

	:param cmap:
		matplotlib Colormap object
	:param dlight:
		float, luminosity value in range 0-1 to add or subtract
		Positive values will make colors lighter, negative values darker
	:param colorspace:
		str, one of 'HSV' or 'HLS'
		(default: 'HLS')

	:return:
		matplotlib ListedColormap object
	"""
	from matplotlib.colors import ListedColormap, rgb_to_hsv, hsv_to_rgb

	## In HSL, saturated colors have lightness 0.5
	## < 0.5 = darker, > 0.5 = lighter

	rgba = cmap(np.arange(cmap.N))

	if colorspace == 'HSV':
		hsv = rgb_to_hsv(rgba[:, 0:3])
		hsv[:, 2] += dlight
		hsv[:, 2] = np.maximum(0, hsv[:, 2])
		hsv[:, 2] = np.minimum(1, hsv[:, 2])
		rgba[:, 0:3] = hsv_to_rgb(hsv)
	elif colorspace == 'HLS':
		hls = rgb_to_hls(rgba[:, 0:3])
		hls[:, 1] += dlight
		hls[:, 1] = np.maximum(0, hls[:, 1])
		hls[:, 1] = np.minimum(1, hls[:, 1])
		rgba[:, 0:3] = hls_to_rgb(hls)

	return ListedColormap(rgba)


def adjust_cmap_saturation(cmap, dsat, colorspace='HSV'):
	"""
	Adjust the saturation of colormap.

	:param cmap:
		matplotlib Colormap object
	:param dsat:
		float, delta saturation in range 0-1
	:param colorspace:
		str, one of 'HSV' or 'HLS'
		(default: 'HSV')

	:return:
		matplotlib ListedColormap object
	"""
	from matplotlib.colors import ListedColormap, rgb_to_hsv, hsv_to_rgb

	rgba = cmap(np.arange(cmap.N))

	if colorspace == 'HSV':
		hsv = rgb_to_hsv(rgba[:, 0:3])
		hsv[:, 1] += dsat
		hsv[:, 1] = np.maximum(0, hsv[:, 1])
		hsv[:, 1] = np.minimum(1, hsv[:, 1])
		rgba[:, 0:3] = hsv_to_rgb(hsv)
	elif colorspace == 'HLS':
		hls = rgb_to_hls(rgba[:, 0:3])
		hls[:, 2] += dsat
		hls[:, 2] = np.maximum(0, hls[:, 2])
		hls[:, 2] = np.minimum(1, hls[:, 2])
		rgba[:, 0:3] = hls_to_rgb(hls)

	return ListedColormap(rgba)


def extract_partial_cmap(cmap, min_val=0.0, max_val=1.0, n=256):
	"""
	Extract a subset of a colormap as a new colormap.
	Note: colormap can also be reversed by specifying min_val > max_val

	Source: https://gist.github.com/denis-bz/8052855

	:param cmap:
		matplotlib Colormap object
	:param min_val:
		float (range 0-1): fraction of colormap to start new colormap with
		(default: 0.)
	:param max_val:
		float (range 0-1): fraction of colormap to end new colormap with
		(default: 1.)
	:param n:
		int, number of colors in output colormap

	:return:
		matplotlib Colormap object
	"""
	from matplotlib.colors import LinearSegmentedColormap
	#cmap = get_cmap(cmap)
	name = "%s-trunc-%.2g-%.2g" % (cmap.name, min_val, max_val)
	new_cmap = LinearSegmentedColormap.from_list(name,
					cmap(np.linspace(min_val, max_val, n)), N=n)
	return new_cmap
