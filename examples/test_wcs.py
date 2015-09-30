"""
Example demonstrating how to get a grid from a WCS server
"""

import os
for key in os.environ:
	if "GDAL" in key or "OSR" in key:
		print key, os.environ[key]


import numpy as np
import gdal
from owslib.wcs import WebCoverageService
import pylab


url = 'http://seishaz.oma.be:8080/geoserver/wcs'
wcs = WebCoverageService(url, version='1.0.0')
print sorted(wcs.contents.keys())

layer_name = 'ngi:DTM10k'
coverage = wcs[layer_name]

#width, height = 500, 500
width, height = None, None
## resx, resy are resolution in CRS units, in this case m
#resx, resy = None, None
resx, resy = 200, 200
# Note: bbox (llx, lly, urx, ury)
bbox = coverage.boundingboxes[0]['bbox']
print bbox
crs = coverage.supportedCRS[0]
print crs
format = "GeoTIFF"
response = wcs.getCoverage(identifier=layer_name, width=width, height=height, resx=resx, resy=resy, bbox=bbox, format=format, crs=crs)
import urllib
print urllib.unquote(response.geturl())

#driver = gdal.GetDriverByName("Gtiff")
#ds = driver.CreateCopy('', response.read())
ds = gdal.Open(response.geturl())
print ds.RasterXSize, ds.RasterYSize, ds.RasterCount

band = ds.GetRasterBand(1)
nodata = band.GetNoDataValue()
ar = band.ReadAsArray()
ar[ar == nodata] = np.nan
pylab.imshow(ar, cmap=pylab.cm.gist_earth, vmin=0)
pylab.show()
