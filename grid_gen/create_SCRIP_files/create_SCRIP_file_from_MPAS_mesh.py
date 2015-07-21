#!/usr/bin/env python
# Create a SCRIP file from an MPAS mesh.
# See for details: http://www.earthsystemmodeling.org/esmf_releases/public/ESMF_5_2_0rp1/ESMF_refdoc/node3.html#SECTION03024000000000000000

import sys
import netCDF4
import numpy as np

from optparse import OptionParser


print "== Gathering information.  (Invoke with --help for more details. All arguments are optional)"
parser = OptionParser()
parser.description = "This script takes an MPAS grid file and generates a SCRIP grid file."
parser.add_option("-m", "--mpas", dest="mpasFile", help="MPAS grid file name used as input.", default="grid.nc", metavar="FILENAME")
parser.add_option("-s", "--scrip", dest="scripFile", help="SCRIP grid file to output.", default="scrip.nc", metavar="FILENAME")
for option in parser.option_list:
	if option.default != ("NO", "DEFAULT"):
		option.help += (" " if option.help else "") + "[default: %default]"
options, args = parser.parse_args()

if not options.mpasFile:
	sys.exit('Error: MPAS input grid file is required.  Specify with -m command line argument.')
if not options.scripFile:
	sys.exit('Error: SCRIP output grid file is required.  Specify with -s command line argument.')

print '' # make a space in stdout before further output


# ===============================================

fin = netCDF4.Dataset(options.mpasFile, 'r')
fout = netCDF4.Dataset(options.scripFile, 'w')  # This will clobber existing files

# Get info from input file
latCell = fin.variables['latCell'][:]
lonCell = fin.variables['lonCell'][:]
latVertex = fin.variables['latVertex'][:]
lonVertex = fin.variables['lonVertex'][:]
verticesOnCell = fin.variables['verticesOnCell'][:]
nEdgesOnCell = fin.variables['nEdgesOnCell'][:]
nCells = len(fin.dimensions['nCells'])
maxVertices = len(fin.dimensions['maxEdges'])
areaCell = fin.variables['areaCell'][:]

# Write to output file
# Dimensions
fout.createDimension("grid_size", nCells)
fout.createDimension("grid_corners", maxVertices )
fout.createDimension("grid_rank", 1)

# Variables
grid_center_lat = fout.createVariable('grid_center_lat', 'f8', ('grid_size',))
grid_center_lat.units = 'degrees'
grid_center_lon = fout.createVariable('grid_center_lon', 'f8', ('grid_size',))
grid_center_lon.units = 'degrees'
grid_corner_lat = fout.createVariable('grid_corner_lat', 'f8', ('grid_size', 'grid_corners'))
grid_corner_lat.units = 'degrees'
grid_corner_lon = fout.createVariable('grid_corner_lon', 'f8', ('grid_size', 'grid_corners'))
grid_corner_lon.units = 'degrees'
grid_area = fout.createVariable('grid_area', 'f8', ('grid_size',))
grid_area.units = 'radian^2'
grid_imask = fout.createVariable('grid_imask', 'i4', ('grid_size',))
grid_imask.units = 'unitless'
grid_dims = fout.createVariable('grid_dims', 'i4', ('grid_rank',))

grid_center_lat[:] = latCell[:]*57.29577951308
grid_center_lon[:] = lonCell[:]*57.29577951308
grid_area[:] = areaCell[:]*0.24635127E-13
grid_imask[:] = 1  # For now, assume we don't want to mask anything out - but eventually may want to exclude certain cells from the input mesh during interpolation
grid_dims[:] = nCells

# grid corners:
grid_corner_lon_local = np.zeros( (nCells, maxVertices) )  # It is WAYYY faster to fill in the array entry-by-entry in memory than to disk.
grid_corner_lat_local = np.zeros( (nCells, maxVertices) )
for iCell in range(nCells):
	vertexMax = nEdgesOnCell[iCell]
	grid_corner_lat_local[iCell, 0:vertexMax] = latVertex[verticesOnCell[iCell, 0:vertexMax] - 1]
	grid_corner_lon_local[iCell, 0:vertexMax] = lonVertex[verticesOnCell[iCell, 0:vertexMax] - 1]
	if vertexMax < maxVertices:
    # repeat the last vertex location for any remaining, unused vertex indices
		grid_corner_lat_local[iCell, vertexMax:] = latVertex[verticesOnCell[iCell, vertexMax-1] - 1]
		grid_corner_lon_local[iCell, vertexMax:] = lonVertex[verticesOnCell[iCell, vertexMax-1] - 1]
grid_corner_lat[:] = grid_corner_lat_local[:]*57.29577951308
grid_corner_lon[:] = grid_corner_lon_local[:]*57.29577951308

#import matplotlib.pyplot as plt
#i=-1
#plt.plot(grid_center_lon[i], grid_center_lat[i], 'o')
#plt.plot(grid_corner_lon[i, 0], grid_corner_lat[i, 0], 'kx')
#plt.plot(grid_corner_lon[i, 1], grid_corner_lat[i, 1], 'bx')
#plt.plot(grid_corner_lon[i, 2], grid_corner_lat[i, 2], 'cx')
#plt.plot(grid_corner_lon[i, 3], grid_corner_lat[i, 3], 'gx')
#plt.plot(grid_corner_lon[i, 4], grid_corner_lat[i, 4], 'yx')
#plt.plot(grid_corner_lon[i, 5], grid_corner_lat[i, 5], 'rx')
#plt.show()

fin.close()
fout.close()
