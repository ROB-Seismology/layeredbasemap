from __future__ import absolute_import, division, print_function, unicode_literals


import numpy as np
import matplotlib

from .norm import PiecewiseLinearNorm


usgs_rgb = np.array([(255, 255, 255),
			(230, 230, 230),
			(200, 200, 200),
			(231, 255, 255),
			(215, 255, 255),
			(198, 255, 255),
			(151, 255, 241),
			(151, 254, 199),
			(200, 255, 153),
			(202, 254, 83),
			(251, 250, 100),
			(255, 238, 0),
			(254, 225, 1),
			(255, 200, 1),
			(255, 94, 0),
			(254, 0, 2),
			(200, 121, 20),
			(151, 74, 20)], dtype='f')
usgs_rgb /= 255.

usgs_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("USGS_hazard", usgs_rgb)
usgs_norm = PiecewiseLinearNorm([0., 0.02, 0.06, 0.14, 0.30, 0.90])

"""
share_rgb = np.array([(255, 255, 255),
			(219, 237, 222),
			(147, 208, 206),
			(42, 176, 185),
			(76, 180, 137),
			(124, 192, 125),
			(152, 200, 116),
			(177, 208, 110),
			(201, 216, 104),
			(214, 220, 88),
			(224, 223, 67),
			(230, 225, 47),
			(236, 227, 35),
			(240, 230, 27),
			(243, 231, 28),
			(244, 232, 33),
			(250, 230, 21),
			(254, 212, 22),
			(252, 192, 22),
			(249, 175, 23),
			(245, 156, 23),
			(242, 140, 22),
			(239, 122, 20),
			(236, 104, 27),
			(234, 88, 26),
			(232, 72, 30),
			(231, 58, 29),
			(230, 42, 31),
			(229, 32, 32),
			(228, 24, 28),
			(227, 13, 19),
			(217, 13, 21),
			(200, 21, 23),
			(181, 24, 23),
			(164, 25, 23),
			(155, 25, 23),
			(148, 25, 23),
			(139, 24, 22),
			(129, 23, 23),
			(121, 22, 22),
			(111, 20, 25),
			(101, 18, 32),
			(91, 15, 37),
			(84, 13, 41),
			(80, 12, 43),
			(76, 12, 46),
			(70, 14, 48),
			(64, 16, 50),
			(60, 18, 52),
			(56, 20, 55)], dtype='f')
share_rgb /= 255.

share_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("SHARE_hazard", share_rgb)
#share_norm = matplotlib.colors.Normalize(vmin=0.0, vmax=0.5)
share_norm = PiecewiseLinearNorm([0., 0.5])
"""

share_rgb = np.array([(255, 255, 255),
			(146, 212, 208),
			(177, 220, 108),
			(246, 248, 22),
			(255, 212, 0),
			(255, 123, 0),
			(255, 29, 0),
			(200, 10, 12),
			(139, 15, 20),
			(91, 11, 36),
			(67, 9, 50),
			(48, 6, 47)], dtype='f')
share_rgb /= 255.

share_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("SHARE_hazard", share_rgb)
share_norm = PiecewiseLinearNorm([0., 0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5])


gshap_rgb = np.array([(255, 255, 255),
			(131, 247, 47),
			(48, 228, 0),
			(255, 255, 1),
			(245, 171, 8),
			(245, 76, 116),
			(231, 0, 88),
			(243, 0, 0),
			(165, 51, 0)], dtype='f')
gshap_rgb /= 255.

gshap_cmap = matplotlib.colors.LinearSegmentedColormap.from_list("GSHAP_hazard", gshap_rgb)
gshap_norm = PiecewiseLinearNorm([0., 0.02, 0.04, 0.08, 0.16, 0.24, 0.32, 0.40, 0.48])
