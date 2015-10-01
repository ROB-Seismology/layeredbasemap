#
# Empty file necessary for python to recognise directory as package
#

import os



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

def from_cpt(cpt_filespec):
	"""
	Convert GMT CPT file to matplotlib colormap
	Modified from the cookbook at SciPy.org
	(http://www.scipy.org/Wiki/Cookbook/Matplotlib/Loading_a_colormap_dynamically)

	:param cpt_filespec:
		str, full path to CPT file

	:return:
		(cmap, norm) tuple
	"""
	import colorsys
	import numpy as np
	from matplotlib.colors import LinearSegmentedColormap
	from norm import PiecewiseLinearNorm

	if not os.path.splitext(cpt_filespec)[-1]:
		cpt_filespec += ".cpt"

	x, r, g, b = [], [], [], []
	r_under, r_over, r_bad = None, None, None
	colorModel = "RGB"
	discrete = True
	with open(cpt_filespec) as fd:
		for line in fd:
			cols = line.split()
			if cols:
				if line[0] == "#":
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

	## Append last color for continuous cpt palettes
	x.append(x2)
	if not (r2 == r[-1] and g2 == g[-1] and b2 == b[-1]):
		discrete = False
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

	name = os.path.splitext(os.path.split(cpt_filespec)[1])[0]
	colors = np.asarray(zip(r, g, b))
	cmap = LinearSegmentedColormap.from_list(name, colors)

	if r_under != None:
		cmap.set_under((r_under, g_under, b_under))
	if r_over != None:
		cmap.set_over((r_over, g_over, b_over))
	if r_bad != None:
		cmap.set_bad((r_bad, g_bad, b_bad))

	return (cmap, norm)

def from_cpt_city(rel_path):
	"""
	Convert cpt_city color palette to matplotlib colormap

	See http://soliton.vm.bytemark.co.uk/pub/cpt-city/
	and http://docs.idldev.com/mglib/vis/color/cptcity_catalog.html

	:param rel_path:
		str, relative path in cpt_city folder

	:return:
		(cmap, norm) tuple
	"""
	base_folder = os.path.split(__file__)[0]
	cpt_filespec = os.path.join(base_folder, "cpt-city", rel_path)
	return from_cpt(cpt_filespec)

