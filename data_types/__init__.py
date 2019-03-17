"""
Data types used in LayeredBasemap
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


import osr, ogr, gdal
gdal.UseExceptions()

## Define WGS84 spatial reference system
WGS84 = osr.SpatialReference()
WGS84_EPSG = 4326
WGS84.ImportFromEPSG(WGS84_EPSG)


## Import submodules

## base (no internal dependencies)
if not reloading:
	from . import base
else:
	reload(base)
from .base import *

## point (depends on base)
if not reloading:
	from . import point
else:
	reload(point)
from .point import *

## line (depends on base, point)
if not reloading:
	from . import line
else:
	reload(line)
from .line import *

## polygon (depends on base, point, line)
if not reloading:
	from . import polygon
else:
	reload(polygon)
from .polygon import *

## text (depends on base, point)
if not reloading:
	from . import text
else:
	reload(text)
from .text import *

## circle (depends on point)
if not reloading:
	from . import circle
else:
	reload(circle)
from .circle import *

## vector (depends on base, point, line, polygon)
if not reloading:
	from . import vector
else:
	reload(vector)
from .vector import *

## misc (depends on base, point)
if not reloading:
	from . import misc
else:
	reload(misc)
from .misc import *

## image (depends on base)
if not reloading:
	from . import image
else:
	reload(image)
from .image import*

## grid (depends on base, point, line, polygon)
if not reloading:
	from . import grid
else:
	reload(grid)
from .grid import *
