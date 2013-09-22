#
# Empty file necessary for python to recognise directory as package
#



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
	module = __import__(__name__, fromlist=[category])
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
	module = __import__(__name__, fromlist=[category])
	try:
		return getattr(module, norm_name)
	except:
		pass

def from_cpt(self, cpt_filespec):
	# TODO
	pass
