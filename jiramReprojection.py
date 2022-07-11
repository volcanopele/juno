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

# to be completed

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
	# start and stop time converted to seconds past J2000
	etStart = spiceypy.scs2e(-61999,startTime)
	etStop = spiceypy.scs2e(-61999,stopTime)
	# Image mid-time calculated
	et = (etStart+etStop)/2
	exposureTime = etStop - etStart
	
	# close file
	file.close()
	
	# tuple with image mid-time, product ID, and orbit output by function
	return [et, productID, orbit, etStart, exposureTime, startTime]


####################
### SCRIPT START ###
####################

# initialize spice files
spiceypy.furnsh( metakr )

# things this script needs to do
# Load JIRAM image
jiramInput = fd.askopenfilename(title='Select JIRAM image label', filetypes=(('PDS Labels', '*.LBL'), ('All files', '*.*')))
# load map cube
mapInput = fd.askopenfilename(title='Select Map Cube', filetypes=(('CUB Files', '*.cub'), ('All files', '*.*')))

# determine size of map cube
samples = int(isis.getkey(from_=mapInput, grpname_="Dimensions", objname_="Core", keyword_="Samples").stdout)
arraySamples = samples
arraySamples -= 1
lines = int(isis.getkey(from_=mapInput, grpname_="Dimensions", objname_="Core", keyword_="Lines").stdout)
arrayLines = lines
arrayLines -= 1

# prepare file names
parseTuple = fileParse(jiramInput)

etStart =  parseTuple[3]

root = os.path.dirname(jiramInput)
name = os.path.basename(jiramInput)
productID = parseTuple[1]
fileBase = root + '/' + productID

imageImg = fileBase + '.IMG'
imageCub = fileBase + '.cub'
mirrorCub = fileBase + '.mirror.cub'
lbandCub = fileBase + '.lband.cub'
mbandCub = fileBase + '.mband.cub'
lbandCsv = fileBase + '.lband.txt'
mbandCsv = fileBase + '.mband.txt'

mapptCSV = root+ '/output.csv'
mapCSV = fileBase + '.map.txt'
latitudeCub = fileBase + '.latitude.cub'
latitudeCSV = fileBase + '.latitude.txt'
longitudeCub = fileBase + '.longitude.cub'
longitudeCSV = fileBase + '.longitude.txt'
reprojectCSV = fileBase + '.reprojected.csv'
reprojectedCub = fileBase + '.reprojected.cub'
delimiter=","

# create basemap image array
isis.isis2ascii(from_=mapInput, to_=mapCSV, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
mapPanda = pd.read_csv(mapCSV, header=None, dtype=float)

# create backplane arrays
isis.phocube(from_=mapInput, to_=latitudeCub, source="PROJECTION", longitude="false")
isis.isis2ascii(from_=latitudeCub, to_=latitudeCSV, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
latitudePanda = pd.read_csv(latitudeCSV, header=None, dtype=float)
isis.phocube(from_=mapInput, to_=longitudeCub, source="PROJECTION", latitude="false")
isis.isis2ascii(from_=longitudeCub, to_=longitudeCSV, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
longitudePanda = pd.read_csv(longitudeCSV, header=None, dtype=float)

# create JIRAM image arrays
isis.raw2isis(from_=imageImg, to_=imageCub, samples_=432, lines_=256, bands_=1, bittype_="REAL")
isis.mirror(from_=imageCub, to_=mirrorCub)
isis.crop(from_=mirrorCub, to_=lbandCub, line_=1, nlines_=128)
isis.crop(from_=mirrorCub, to_=mbandCub, line_=129, nlines_=128)
isis.isis2ascii(from_=lbandCub, to_=lbandCsv, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
lbandPanda = pd.read_csv(lbandCsv, header=None, dtype=float)
isis.isis2ascii(from_=mbandCub, to_=mbandCsv, header_="no", delimiter_=delimiter, setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
mbandPanda = pd.read_csv(mbandCsv, header=None, dtype=float)

# camera variables
dx = 0.000237767
dy = 0.000237767
[mshape, mframe, mbsight, mnbounds, mbounds] = spiceypy.getfov(mbandfrm, 20)
[lshape, lframe, lbsight, lnbounds, lbounds] = spiceypy.getfov(lbandfrm, 20)

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
			# in JIRAM image, find pixel for lat/lon center (careful, make sure that it is visible)
			
			# m-band (taken from center pixel calculation in jiramgeombackplane.py)
			# this is not providing an accurate position
			# it should be! This isn't the broken part!
			xform = spiceypy.pxfrm2(tarfrm, mframe, trgepc, etStart)
			xformvec = spiceypy.mxv(xform, srfvec)
			xformvec[0] = xformvec[0] / xformvec[2]
			xformvec[1] = xformvec[1] / xformvec[2]
			xformvec[2] = xformvec[2] / xformvec[2]
			X = xformvec[1] - mbounds[3,1]
			X /= dx
			X -= 1
			X = int(round(X,0))
			Y = xformvec[0] - mbounds[3,0]
			Y /= dx
			Y *= -1
			Y -= 1
			Y = int(round(Y,0))
			
			# obtain pixel value (ISIS?)
			
			# paint pixel in ISIS cube pixel value from JIRAM image (or make CSV file?)
			mapPanda.values[i][j] = mbandPanda.values[Y][X]



# obtain pixel value (ISIS?)



# Export CSV to ISIS image
mapPanda.to_csv(reprojectCSV, index=False, header=False)
isis.ascii2isis(from_=reprojectCSV, to_=reprojectedCub, order_="bsq", samples_=samples, lines_=lines, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
isis.copylabel(from_=reprojectedCub, source_=mapInput, mapping="true")

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
os.system(str("/bin/rm " + lbandCub))
os.system(str("/bin/rm " + mbandCub))
os.system(str("/bin/rm " + lbandCsv))
os.system(str("/bin/rm " + mbandCsv))
os.system(str("/bin/rm " + reprojectCSV))
