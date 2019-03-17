"""
Styles used in LayeredBasemap
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



## Import submodules

## base (no internal dependencies)
if not reloading:
	from . import base
else:
	reload(base)

## thematic (depends on base)
if not reloading:
	from . import thematic
else:
	reload(thematic)
from .thematic import *

## text (depends on base)
if not reloading:
	from . import text
else:
	reload(text)
from .text import *

## decoration (depends on text)
if not reloading:
	from . import decoration
else:
	reload(decoration)
from .decoration import *

## misc (depends on decoration)
if not reloading:
	from . import misc
else:
	reload(misc)
from .misc import *

## vector (depends on decoration, thematic)
if not reloading:
	from . import vector
else:
	reload(vector)
from .vector import *

## grid (depends on thematic)
if not reloading:
	from . import grid
else:
	reload(grid)
from .grid import *
