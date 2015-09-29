"""
Example demonstrating how to get a grid from a WCS server
"""

import numpy as np
import gdal
from owslib.wcs import WebCoverageService
import pylab


url = 'http://seishaz.oma.be:8080/geoserver/wcs'
wcs = WebCoverageService(url, version='1.0.0')
print wcs.contents

layer_name = 'ngi:DTM10k'
coverage = wcs[layer_name]

#width, height = 500, 500
width, height = None, None
#resx, resy = None, None
resx, resy = 200, 200
# Note: bbox (llx, lly, urx, ury)
bbox = coverage.boundingboxes[0]['bbox']
crs = coverage.supportedCRS[0]
format = "GeoTIFF"
response = wcs.getCoverage(identifier=layer_name, width=width, height=height, resx=resx, resy=resy, bbox=bbox, format=format, crs=crs)

ds = gdal.Open(response.geturl())
print ds.RasterXSize, ds.RasterYSize, ds.RasterCount

band = ds.GetRasterBand(1)
nodata = band.GetNoDataValue()
ar = band.ReadAsArray()
ar[ar == nodata] = np.nan
pylab.imshow(ar, cmap=pylab.cm.gray_r)
pylab.show()
