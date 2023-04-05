from __future__ import print_function
from builtins import input
import math
import spiceypy
from tkinter import filedialog as fd
import tkinter as tk
import os, sys, getopt
import kalasiris as isis
import pandas as pd


####################
###### README ######
####################

# Usage:

# python jiramReprojection.py 
	# -i <full path to label file> 
	# [-x <pixel offset>]
	# [-y <pixel offset>] 
	# [-m <full path to map file or cube file]

# i requires a JIRAM label file (extension .LBL) with a JIRAM image (extention .IMG) in the same directory
# m accepts both a map file for use in ISIS's map2map program or a reprojected ISIS cube file

# example use

# python jiramReprojection.py -i /Users/perry/Dropbox/Io/Juno/PJ17/M-band/JIR_IMG_RDR_2018355T122946_V01.LBL -x -1.25 -y 2.5 -z 0.25 -m /Users/perry/Dropbox/Io/Juno/PJ17/M-band/JIR_IMG_RDR_2018355T123147_V01.map.cub

# in this case, the label for the image to be reprojected is /Users/perry/Dropbox/Io/Juno/PJ17/M-band/JIR_IMG_RDR_2018355T122946_V01.LBL
# the spice geometry is to be offset by -1.25 pixels in the X direction and 2.5 pixels in the Y direction
# the JIRAM image is to be reprojected to match /Users/perry/Dropbox/Io/Juno/PJ17/M-band/JIR_IMG_RDR_2018355T123147_V01.map.cub

# if no offsets are included, the spice geometry will be used with no adjustment
# if no map file or cube file is specified, the script will generate one matching the geometry of the input JIRAM image but with 5x the pixel scale

# PREREQUISITES

# To run this script, ISIS 7.0.0 or higher is required. Installation 
# instructions are available at: 
# https://github.com/USGS-Astrogeology/ISIS3#installation
# The kalasiris python module is also required to generate ISIS cube files.
# It is not part of the standard ISIS installation. With the isis conda 
# environment active, run:

# conda install kalasiris

# this will add kalasiris to the isis conda environment. Kalasiris is a python
# wrapper for ISIS.

# output files are placed in the same directory as the input file.

# REMEMBER TO EDIT THE metakr VARIABLE in LINE 80 TO MATCH THE FULL PATH TO 
# YOUR JUNO METAKERNEL



###################################
###### LICENSE AND COPYRIGHT ######
###################################

# Copyright (C) 2022 Arizona Board of Regents on behalf of the Planetary
# Image Research Laboratory, Lunar and Planetary Laboratory at the
# University of Arizona.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

#######################
###### VARIABLES ######
#######################

# edit metakr to point to your Juno metakernel
metakr = '/Users/perry/Dropbox/Io/Juno/kernels/juno_latest.tm'
basemp = '/Users/perry/Dropbox/Io/map/Io_GalileoSSI-Voyager_Global_Mosaic_1km.cub'
sclkid = -61
scname = 'JUNO'
target = 'IO'
targid = 501
tarfrm = 'IAU_IO'
abcorr = 'LT+S'
jirmid = -61410
jrmfrm = 'JUNO_JIRAM_I'
lbandfrm = -61411
lbndnm = 'JUNO_JIRAM_I_LBAND'
mbandfrm = -61412
mbndnm = 'JUNO_JIRAM_I_MBAND'
specfrm = -61420
specnm = 'JUNO_JIRAM_S'

# various parameters for the script
method = 'Intercept/Ellipsoid'
method2 = 'ELLIPSOID'
tdbfmt = 'YYYY MON DD HR:MN:SC.### TDB ::TDB'
xlsxmt = 'MM/DD/YYYY HR:MN:SC.###'
datefmt = 'YYYY-MM-DD'
timefmt = 'HR:MN:SC.###'

delimiter=","

###########################
### INITALIZE FUNCTIONS ###
###########################

# fileParse takes an input JIRAM label file and pulls out pieces of information 
# that will be used by the script, outputting as a tuple the image mid-time, 
# product ID, and orbit number

def fileParse(inputs):
	# opens input file
	file = open(inputs)
	# converts input file into an array of lines
	datafile = file.readlines()
	# this for loop takes a look at each line in datafile and looks for four lines
	# with information needed for this script including the image start time, stop 
	# time, product ID, and orbit number. If found, the loop will parse the line by
	# split it by spaces then sorts the resulting array so that the value we need 
	# is at a consistent position.
	for line in datafile:
		if 'SPACECRAFT_CLOCK_START_COUNT' in line:
			startTime = line
			startTimes = startTime.split(" ")
			startTimes = sorted(startTimes, reverse=True)
			startTime = startTimes[2]
			startTime = startTime.split('"')[1]
			startTime = startTime.split('/')[1]
		elif 'SPACECRAFT_CLOCK_STOP_COUNT' in line:
			stopTime = line
			stopTimes = stopTime.split(" ")
			stopTimes = sorted(stopTimes, reverse=True)
			stopTime = stopTimes[2]
			stopTime = stopTime.split('"')[1]
			stopTime = stopTime.split('/')[1]
		elif 'PRODUCT_ID ' in line:
			if line.startswith('PRODUCT_ID ', 0):
				productID = line
				productIDs = productID.split(" ")
				productIDs = sorted(productIDs, reverse=True)
				productID = productIDs[1]
		elif 'ORBIT_NUMBER' in line:
			orbit = line
			orbits = orbit.split(" ")
			orbits = sorted(orbits, reverse=True)
			orbit = orbits[2]
		elif 'INSTRUMENT_MODE_ID' in line:
			instrumentMode = line
			instrumentModes = instrumentMode.split(" ")
			instrumentModes = sorted(instrumentModes, reverse=True)
			instrumentMode = instrumentModes[0]
			instrumentModes = instrumentMode.split("_")
			instrumentMode = instrumentModes[1]
	# start and stop time converted to seconds past J2000
	etStart = spiceypy.scs2e(-61999,startTime)
	etStop = spiceypy.scs2e(-61999,stopTime)
	# Image mid-time calculated
	et = (etStart+etStop)/2
	exposureTime = etStop - etStart
	
	# close file
	file.close()
	
	# tuple with image mid-time, product ID, and orbit output by function
	return [et, productID, orbit, etStart, exposureTime, startTime, instrumentMode]

def coordinates(frmcode, tarfrm, trgepc, etStart, srfvec, xOffset, yOffset):
	[shape, frame, bsight, nbounds, bounds] = spiceypy.getfov(frmcode, 20)
	dx = 0.000237767
	dy = 0.000237767
	xform = spiceypy.pxfrm2(tarfrm, frame, trgepc, etStart)
	xformvec = spiceypy.mxv(xform, srfvec)
	xformvec[0] = xformvec[0] / xformvec[2]
	xformvec[1] = xformvec[1] / xformvec[2]
	xformvec[2] = xformvec[2] / xformvec[2]
	X = xformvec[1] - bounds[3,1]
	X /= dx
	X += xOffset
	X = int(round(X,0))
	Y = xformvec[0] - bounds[3,0]
	Y /= dx
	Y *= -1
	Y += yOffset
	Y = int(round(Y,0))
	return X, Y

########################
### ARGUMENT PARSING ###
########################

mapfile = ''
outputfile = ''
jiramInput = ''
rotation = ''
xOffset = 0
yOffset = 0
argv = sys.argv[1:]

try:
	opts, args = getopt.getopt(argv, 'i:m:x:y:z:', ['mapfile', 'infile'])
	for opt, arg in opts:
		if opt in ("-m", "--mapfile"):
			mapfile = arg
		if opt in ("-i", "--infile"):
			jiramInput = arg
		if opt in ("-x"):
			xOffset = float(arg)
		if opt in ("-y"):
			yOffset = float(arg)
		if opt in ("-z"):
			rotation = float(arg)
except getopt.GetoptError:
	print('jiramReprojection.py -m <mapfile> -i <infile>')
	sys.exit(2)

   
####################
### SCRIPT START ###
####################

# initialize spice files
spiceypy.furnsh( metakr )

# Load JIRAM image if not loaded in command line
# check to make sure that the command line input is fine

if jiramInput != "":
	jiramfile_tub = os.path.splitext(jiramInput)
	if jiramfile_tub[1] == '.IMG':
		jiramInput = jiramfile_tub[0] + '.LBL'
	elif jiramfile_tub[1] == '.LBL':
		jiramInput = jiramInput
	else:
		print("Input file is not a valid JIRAM image or label")
		sys.exit()
else:
	jiramInput = fd.askopenfilename(title='Select JIRAM image label', filetypes=(('PDS Labels', '*.LBL'), ('All files', '*.*')))
# load map cube
# mapInput = fd.askopenfilename(title='Select Map Cube', filetypes=(('CUB Files', '*.cub'), ('All files', '*.*')))

# parse label file for information about cube
parseTuple = fileParse(jiramInput)
etStart =  parseTuple[3]
productID = parseTuple[1]
instrumentMode = parseTuple[6]
orbit = int(parseTuple[2])

# setup paths
root = os.path.dirname(jiramInput)
name = os.path.basename(jiramInput)
fileBase = root + '/' + productID

### REPROJECTED CUBE SETUP ###
mapCub = fileBase + '.map.cub'
mapPvl = fileBase + '.map'

if mapfile != "":
	mapfile_tub = os.path.splitext(mapfile)
	if mapfile_tub[1] == '.cub':
		mapCub = mapfile
	elif mapfile_tub[1] == '.map':
		mapPvl = mapfile
		isis.map2map(from_=basemp, to_=mapCub, map_=mapPvl, pixres_="map", defaultrange_="map")
	else:
		sys.exit()
else:
	[spoint, trgepc, subsrfvec] = spiceypy.subpnt( method, target, etStart, tarfrm, abcorr, scname )
	alt = spiceypy.vnorm( subsrfvec )
	[radius, lon, lat] = spiceypy.reclat( spoint )
	lon = lon * spiceypy.dpr()
	if lon <= 0.0:
		lon = math.fabs(lon)
	else:
		lon = 360.0 - lon
	lat = lat * spiceypy.dpr()
	res = alt * 0.237767
	if orbit == 41 or orbit == 43:
		magnify = 5
	else:
		magnify = 10
	res /= magnify
	isis.maptemplate(map_=mapPvl, targopt_="user", targetname_=target, clat_=lat, clon_=lon, dist_=alt, londir_="POSITIVEWEST", projection_="POINTPERSPECTIVE", resopt_="MPP", resolution_=res, rngopt_="user", minlat_=-90, maxlat_=90, minlon_=0, maxlon_=360)
	isis.map2map(from_=basemp, to_=mapCub, map_=mapPvl, pixres_="map", defaultrange_="map")
	print("map cube generated")

# determine size of map cube
samples = int(isis.getkey(from_=mapCub, grpname_="Dimensions", objname_="Core", keyword_="Samples").stdout)
arraySamples = samples
lines = int(isis.getkey(from_=mapCub, grpname_="Dimensions", objname_="Core", keyword_="Lines").stdout)
arrayLines = lines

# prepare file names
imageImg = fileBase + '.IMG'
imageCub = fileBase + '.cub'
mirrorCub = fileBase + '.mirror.cub'
lbandCub = fileBase + '.lband.cub'
mbandCub = fileBase + '.mband.cub'
lbandCsv = fileBase + '.lband.txt'
mbandCsv = fileBase + '.mband.txt'

mapCSV = fileBase + '.map.txt'
latitudeCub = fileBase + '.latitude.cub'
latitudeCSV = fileBase + '.latitude.txt'
longitudeCub = fileBase + '.longitude.cub'
longitudeCSV = fileBase + '.longitude.txt'
reprojectCSV = fileBase + '.reprojected.csv'
reprojectedCub = fileBase + '.reprojected.cub'

# create basemap image array
isis.isis2ascii(from_=mapCub, to_=mapCSV, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
mapPanda = pd.read_csv(mapCSV, header=None, dtype=float)

# create backplane arrays
isis.phocube(from_=mapCub, to_=latitudeCub, source="PROJECTION", longitude="false")
isis.isis2ascii(from_=latitudeCub, to_=latitudeCSV, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
latitudePanda = pd.read_csv(latitudeCSV, header=None, dtype=float)
isis.phocube(from_=mapCub, to_=longitudeCub, source="PROJECTION", latitude="false")
isis.isis2ascii(from_=longitudeCub, to_=longitudeCSV, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
longitudePanda = pd.read_csv(longitudeCSV, header=None, dtype=float)

# create JIRAM image arrays
if instrumentMode == "I1":
	lBandavailable = True
	mBandavailable = True
	imgLines = 256
elif instrumentMode == "I2":
	lBandavailable = False
	mBandavailable = True
	imgLines = 128
elif instrumentMode == "I3":
	lBandavailable = True
	mBandavailable = False
	imgLines = 128
else:
	print("Incorrect Image Mode")
	sys.exit()

isis.raw2isis(from_=imageImg, to_=imageCub, samples_=432, lines_=imgLines, bands_=1, bittype_="REAL")

isis.mirror(from_=imageCub, to_=mirrorCub)

if instrumentMode == "I1":
	isis.crop(from_=mirrorCub, to_=lbandCub, line_=1, nlines_=128)
	isis.crop(from_=mirrorCub, to_=mbandCub, line_=129, nlines_=128)
	isis.isis2ascii(from_=lbandCub, to_=lbandCsv, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
	lbandPanda = pd.read_csv(lbandCsv, header=None, dtype=float)
	isis.isis2ascii(from_=mbandCub, to_=mbandCsv, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
	mbandPanda = pd.read_csv(mbandCsv, header=None, dtype=float)
	print("Split PDS image into L-band and M-band images")
elif instrumentMode == "I2":
	mbandCub = mirrorCub
	isis.isis2ascii(from_=mbandCub, to_=mbandCsv, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
	mbandPanda = pd.read_csv(mbandCsv, header=None, dtype=float)
elif instrumentMode == "I3":
	lbandCub = mirrorCub
	isis.isis2ascii(from_=lbandCub, to_=lbandCsv, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
	lbandPanda = pd.read_csv(lbandCsv, header=None, dtype=float)


# camera variables
# dx = 0.000237767
# dy = 0.000237767
# [mshape, mframe, mbsight, mnbounds, mbounds] = spiceypy.getfov(mbandfrm, 20)
# [lshape, lframe, lbsight, lnbounds, lbounds] = spiceypy.getfov(lbandfrm, 20)

print("Setup Complete")

# loop for each pixel (one loop for Y axis, nested loop for X axis)
for i in range(0,arrayLines):
	for j in range(0,arraySamples):
		# determine lat and lon of pixel center
		if mapPanda.values[i][j] != -1024:
			latitude = latitudePanda.values[i][j]
			longitude = longitudePanda.values[i][j]
			# rectangular coordinate conversion
			latitude = latitude * spiceypy.rpd()
			longitude = longitude * spiceypy.rpd()
			spoint = spiceypy.srfrec(targid, longitude, latitude)
			(trgepc, srfvec, phase, incdnc, emissn) = spiceypy.ilumin(method2, target, etStart, tarfrm, abcorr, scname, spoint)
			
			# add one here to check to make sure that feature is on the visible face of Io
			emissndeg = emissn * spiceypy.dpr()
			if emissndeg <= 89.999:
				emissionGood = True
			else:
				emissionGood = False

			if instrumentMode == "I1":
				if emissionGood:
					X, Y = coordinates(lbandfrm, tarfrm, trgepc, etStart, srfvec, xOffset, yOffset)
					if Y > 127 or Y < 0 or X > 431 or X < 0:
						lbandVisible = False
					else:
						lbandVisible = True
				else:
					lbandVisible = False
				if emissionGood and lbandVisible == False:
					X, Y = coordinates(mbandfrm, tarfrm, trgepc, etStart, srfvec, xOffset, yOffset)
					if Y > 127 or Y < 0 or X > 431 or X < 0:
						mbandVisible = False
					else:
						mbandVisible = True
				else:
					mbandVisible = False
			elif instrumentMode == "I2":
				lbandVisible = False
				if emissionGood:
					X, Y = coordinates(mbandfrm, tarfrm, trgepc, etStart, srfvec, xOffset, yOffset)
					if Y > 127 or Y < 0 or X > 431 or X < 0:
						mbandVisible = False
					else:
						mbandVisible = True
				else:
					mbandVisible = False
			elif instrumentMode == "I3":
				if emissionGood:
					X, Y = coordinates(lbandfrm, tarfrm, trgepc, etStart, srfvec, xOffset, yOffset)
					if Y > 127 or Y < 0 or X > 431 or X < 0:
						lbandVisible = False
					else:
						lbandVisible = True
				else:
					lbandVisible = False
			
			# paint pixel in ISIS cube pixel value from JIRAM image (or make CSV file?)
			if mbandVisible:
				mapPanda.values[i][j] = mbandPanda.values[Y][X]
			elif lbandVisible:
				mapPanda.values[i][j] = lbandPanda.values[Y][X]
			else:
				mapPanda.values[i][j] = -1024
				
# Export CSV to ISIS image
mapPanda.to_csv(reprojectCSV, index=False, header=False)
isis.ascii2isis(from_=reprojectCSV, to_=reprojectedCub, order_="bsq", samples_=samples, lines_=lines, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=0.00002)

# rotate if requested
if rotation == "":
	isis.copylabel(from_=reprojectedCub, source_=mapCub, mapping="true")
else:
	rotatedCub = fileBase + '.rotate.cub'
	croppedCub = fileBase + '.crop.cub'
	isis.rotate(from_=reprojectedCub, to_=rotatedCub, degrees=rotation, interp="NEARESTNEIGHBOR")
	newsize = int(isis.getkey(from_=rotatedCub, grpname_="Dimensions", objname_="Core", keyword_="Samples").stdout)
	starting = newsize - samples
	starting /= 2
	starting += 1
	isis.crop(from_=rotatedCub, to=croppedCub, samp_=int(starting), line_=int(starting), nsamp_=samples, nline_=lines)
	isis.copylabel(from_=croppedCub, source_=mapCub, mapping="true")


#############################
######## SCRIPT END #########
#############################
# unload spice kernels
spiceypy.unload( metakr )

# clean up extraneous files
os.system(str("/bin/rm " + mapCSV))
os.system(str("/bin/rm " + latitudeCub))
os.system(str("/bin/rm " + latitudeCSV))
os.system(str("/bin/rm " + longitudeCub))
os.system(str("/bin/rm " + longitudeCSV))
os.system(str("/bin/rm " + imageCub))
os.system(str("/bin/rm " + mirrorCub))
os.system(str("/bin/rm " + mbandCsv))
os.system(str("/bin/rm " + reprojectCSV))
if lBandavailable:
	os.system(str("/bin/rm " + lbandCub))
	os.system(str("/bin/rm " + lbandCsv))
	os.system(str("/bin/rm " + mbandCub))
if rotation != "":
	os.system(str("/bin/rm " + rotatedCub))
