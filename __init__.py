#
# Empty file necessary for python to recognise directory as package
#


## Test GDAL environment
import os
#gdal_keys = ["GDAL_DATA", "GDAL_DRIVER_PATH"]
gdal_keys = ["GDAL_DATA"]
for key in gdal_keys:
	if not key in os.environ.keys():
		print("Warning: %s environment variable not set. Functionality may be reduced" % key)
	elif not os.path.exists(os.environ[key]):
		print("Warning: %s points to non-existing directory %s" % (key, os.environ[key]))


import styles
reload(styles)

from styles import (FontStyle, TextStyle, DefaultTitleTextStyle, PointStyle,
					LineStyle, PolygonStyle, FocmecStyle, CompositeStyle,
					ThematicStyleIndividual, ThematicStyleRanges, ThematicStyleGradient,
					ThematicStyleColormap, ColorbarStyle, GridStyle, LegendStyle,
					ScalebarStyle, MapBorderStyle, GraticuleStyle, GridImageStyle,
					ImageStyle, HillshadeStyle, WMSStyle, FrontStyle)


import data_types
reload(data_types)

from data_types import (BuiltinData, PointData, MultiPointData, LineData, MultiLineData,
						PolygonData, MultiPolygonData, FocmecData, CircleData, MaskData,
						CompositeData, GridData, MeshGridData, UnstructuredGridData,
						GdalRasterData, GisData, GreatCircleData, ImageData, WMSData,
						WCSData)

import cm
reload(cm)


import LayeredBasemap
reload(LayeredBasemap)

from LayeredBasemap import (MapLayer, LayeredBasemap)
