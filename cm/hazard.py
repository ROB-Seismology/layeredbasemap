import numpy as np
import matplotlib


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
			(151, 74, 20)])
usgs_rgb /= 255.

usgs = matplotlib.colors.LinearSegmentedColormap.from_list("USGS_hazard", usgs_rgb)

# TODO: SHARE color map
