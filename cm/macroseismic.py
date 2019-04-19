from __future__ import absolute_import, division, print_function, unicode_literals


import numpy as np
import matplotlib

from .norm import PiecewiseLinearNorm


usgs_rgb = np.array([(225, 225, 225),
			(204, 212, 251),
			(151, 239, 253),
			(125, 253, 202),
			(180, 253, 88),
			(252, 234, 2),
			(255, 180, 3),
			(255, 77, 0),
			(234, 0, 0)], dtype='f')
usgs_rgb /= 255.

usgs_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("USGS_macroseismic",
															usgs_rgb, N=len(usgs_rgb))
usgs_cmap.set_under('w')
usgs_cmap.set_bad('w')
usgs_norm = PiecewiseLinearNorm(range(1, 10))


rob_rgb = np.array([(194, 202, 204),
			(40, 247, 255),
			(6, 251, 23),
			(248, 254, 24),
			(255, 128, 0),
			(249, 3, 16),
			(128, 0, 128)], dtype='f')
rob_rgb /= 255.

rob_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("ROB_macroseismic",
															rob_rgb, N=len(rob_rgb))
rob_cmap.set_under('w')
rob_cmap.set_bad('w')
rob_norm = PiecewiseLinearNorm(range(1, 8))
