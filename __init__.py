"""
layeredbasemap

Module to create maps with Basemap using the GIS layer philosophy,
where each layer is defined by a dataset and style.

Author: Kris Vanneste, Royal Observatory of Belgium
"""

from __future__ import absolute_import, division, print_function, unicode_literals


## Make relative imports work in Python 3
import importlib


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


## Test GDAL environment
import os
#gdal_keys = ["GDAL_DATA", "GDAL_DRIVER_PATH"]
gdal_keys = ["GDAL_DATA"]
for key in gdal_keys:
	if not key in os.environ.keys():
		print("Warning: %s environment variable not set. This may cause errors" % key)
	elif not os.path.exists(os.environ[key]):
		print("Warning: %s points to non-existing directory %s" % (key, os.environ[key]))


## Import submodules

## styles
if not reloading:
	styles = importlib.import_module('.styles', package=__name__)
else:
	reload(styles)
from .styles import *

## data_types
if not reloading:
	data_types = importlib.import_module('.data_types', package=__name__)
else:
	reload(data_types)
from .data_types import *

## cm
if not reloading:
	cm = importlib.import_module('.cm', package=__name__)
else:
	reload(cm)

## layered_basemap
if not reloading:
	layered_basemap = importlib.import_module('.layered_basemap', package=__name__)
else:
	reload(layered_basemap)
from .layered_basemap import *
