from __future__ import print_function
from builtins import input
import math
import spiceypy
from tkinter import filedialog as fd
import tkinter as tk
import os, sys, getopt
import numpy as np
import kalasiris as isis


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
		elif 'PRODUCT_CREATION_TIME' in line:
			productCreate = line
			productCreates = productCreate.split(" ")
			productCreates = sorted(productCreates, reverse=True)
			productCreate = productCreates[2]
		elif 'STANDARD_DATA_PRODUCT_ID' in line:
			dataType = line
			dataTypes = dataType.split(" ")
			dataTypes = sorted(dataTypes, reverse=True)
			dataType = dataTypes[2]
			dataType = dataType.split('"')[1]
		elif 'SEQUENCE_NUMBER' in line:
			sequenceNum = line
			sequenceNums = sequenceNum.split(" ")
			sequenceNums = sorted(sequenceNums, reverse=True)
			sequenceNum = sequenceNums[2]
		elif 'SEQUENCE_SAMPLES' in line:
			sequenceSam = line
			sequenceSams = sequenceSam.split(" ")
			sequenceSams = sorted(sequenceSams, reverse=True)
			sequenceSam = sequenceSams[2]
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
	return [et, productID, orbit, etStart, exposureTime, startTime, productCreate, sequenceNum, sequenceSam, dataType]


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
lines = int(isis.getkey(from_=mapInput, grpname_="Dimensions", objname_="Core", keyword_="Lines").stdout)
# convert JIRAM image to ISIS cube
parseTuple = fileParse(jiramInput)

root = os.path.dirname(jiramInput)
name = os.path.basename(jiramInput)
productID = parseTuple[1]
fileBase = root + '/' + productID
imageImg = fileBase + '.IMG'
imageCub = fileBase + '.cub'
mirrorCub = fileBase + '.mirror.cub'
outputText = root+ '/output.txt'

isis.raw2isis(from_=imageImg, to_=imageCub, samples_=432, lines_=256, bands_=1, bittype_="REAL")

# loop for each pixel (one loop for Y axis, nested loop for X axis)
# for i in range(1,lines):
# 	for j in range(1,samples):
# 		# determine lat and lon of pixel center
# 		isis.mappt(from_=mapInput, to_=outputText, format="pvl", append="false", type="image", sample_=j, line_=i)
# 		
# 		with open(outputText) as tempFile:
# 			if 'PlanetocentricLatitude' in tempFile.read():
# 			latitude=float(isis.getkey(from_=outputText, grpname_="Results", keyword_="PlanetocentricLatitude").stdout)
# 			longitude=float(isis.getkey(from_=outputText, grpname_="Results", keyword_="PositiveWest360Longitude").stdout)


for j in range(1,samples):
	# determine lat and lon of pixel center
	print(j)
	isis.mappt(from_=mapInput, to_=outputText, format="pvl", append="false", type="image", sample_=j, line_=1)
	
	# this bit is VERY slow, need to find a way to make this more efficient, like filtering out 
	# null pixels before hand
	
	with open(outputText) as tempFile:
		if 'PlanetocentricLatitude' in tempFile.read():
			latitude=float(isis.getkey(from_=outputText, grpname_="Results", keyword_="PlanetocentricLatitude").stdout)
			longitude=float(isis.getkey(from_=outputText, grpname_="Results", keyword_="PositiveWest360Longitude").stdout)
			print(latitude)
			print(longitude)


# in JIRAM image, find pixel for lat/lon center (careful, make sure that it is visible)
# obtain pixel value (ISIS?)
# paint pixel in ISIS cube pixel value from JIRAM image (or make CSV file?)


#############################
######## SCRIPT END #########
#############################
spiceypy.unload( metakr )

