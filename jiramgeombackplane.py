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


# This script takes a JIRAM label file or files and calculates the viewing and 
# illumination geometries for each pixel in the image associated with that 
# JIRAM file. This script exports that information as a set of CSV files, 
# where each pixel is represented by the appropriate value (latitude, 
# longitude, altitude, phase angle, incidence angle, and emission angle). An 
# ISIS cube file is also exported, containing a band for each of these values
# as well as one for the original image file.

# To run this script, ISIS 7.0.0 or higher is required. Installation 
# instructions are available at: 
# https://github.com/USGS-Astrogeology/ISIS3#installation
# The kalasiris python module is also required to generate ISIS cube files.
# It is not part of the standard ISIS installation. With the isis conda 
# environment active, run:

# conda install kalasiris

# this will add kalasiris to the isis conda environment. Kalasiris is a python
# wrapper for ISIS. Alternatively, if cubes files are not needed, you can 
# delete or comment out the Cube generation section (from the Cube generation
# header to the spiceypy.unload call at the very end of the script)

# To run this script, use the following command:

# python jiramgeombackplane.py

# A file picker dialog box will open. Select one or more JIRAM labels to 
# continue. If image data was selected, another file picker dialog box will 
# open, allowing the user to select a CSV file listing measured Io center 
# pixels, though this is optional! The script can work without one.

# output files are placed in the same directory as the input files.

# if you wish to split images into separate L- and M-band images, 
# add -split to the command line:

# python jiramgeombackplane.py -split

# REMEMBER TO EDIT THE metakr VARIABLE in LINE 83 TO MATCH THE FULL PATH TO 
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
	return [et, productID, orbit, etStart, exposureTime, startTime, productCreate, sequenceNum, sequenceSam, dataType, instrumentMode]

# backplanegen is used on JUNO_JIRAM_I data and generates CSV files containing
# geometric and illumination information for each pixel. The files generated are: 
# latitude, longitude, altitude (distance to the intercept point), incidence 
# angle, phase angle, and emission angle

def backplanegen(frmcode, derivedX, derivedY, trgepc):
	[shape, frame, bsight, nbounds, bounds] = spiceypy.getfov(frmcode, 20)
	
	# calculation of the IFOV
	dy = np.abs((bounds[0,0]-bounds[2,0]) / 128)
	dx = np.abs((bounds[0,1]-bounds[2,1]) / 432)
	
	# IFOV from the IK
	# for now using this, but I can commment this out
	dx = 0.000237767
	dy = 0.000237767
	
	
	# this script can check for a csv file listing the center pixel of Io
	# for each image, likely from performing a limb fit or calculating the 
	# brightest region of an image within a circle of Io's radius in pixels
	# this script calculates the center pixel according to spice then 
	# calculates the difference between the two points to be used as offsets 
	# for the image backplanes
	if derivedY != "":	
		# calculate center pixel
		xform = spiceypy.pxfrm2(tarfrm, frame, trgepc, etStart)
		xformsubvec = spiceypy.mxv(xform, subsrfvec)
		xformsubvec[0] = xformsubvec[0] / xformsubvec[2]
		xformsubvec[1] = xformsubvec[1] / xformsubvec[2]
		xformsubvec[2] = xformsubvec[2] / xformsubvec[2]
		centerX = xformsubvec[1] - bounds[3,1]
		centerX /= dx
		centerY = xformsubvec[0] - bounds[3,0]
		centerY /= dx
		centerY *= -1
		derivedY -= 0.5
		derivedX -= 0.5
	
		# calculating offsets. probably still need this regardless of derivedY values
		if derivedY <= 128:
			if frmcode == -61412:
				# include 10 pixel gap between L and M band portions of detector
				derivedY -= 10
				# center will be in M band coordinates so need to add 128 to match 
				# combined image coordinates
				offsetY = centerY + 128 - derivedY
			else:
				offsetY = centerY - derivedY
			offsetY *= dy
			offsetX = centerX - derivedX
			offsetX *= dx
		elif derivedY >= 129:
			if frmcode == -61411:
				# include 10 pixel gap between L and M band portions of detector
				derivedY += 10
				offsetY = centerY - derivedY
			else:
				# center will be in M band coordinates so need to add 128 to match 
				# combined image coordinates
				offsetY = centerY + 128 - derivedY
			offsetY *= dy
			offsetX = centerX - derivedX
			offsetX *= dx
	if offsetCSV:
		offsetFile = open(offsetInput)
		offsetInfo = offsetFile.readlines()
		for line in offsetInfo:
			if productID in line:
				derivedLine = line.split(",")
				offsetX = float(derivedLine[1])
				offsetY = float(derivedLine[2])
				offsetY *= dy
				offsetX *= dx
				offsetX *= -1
				offsetY *= -1
				break
		offsetFile.close()
	else:
		offsetY = 0
		offsetX = 0
		
	# generate numpy arrays of radian pixel locations for both the X and Y directions
	xp = np.arange(0.5,431.51,1)*dx + bounds[3,1] + offsetX
	yp = bounds[3,0] - np.arange(0.5,127.51,1)*dy - offsetY
	zp = bounds[0,2]
	
	for i in range(0,128):
		# initialize each line so as to clear the previous line
		latitudeLine = ""
		longitudeLine = ""
		altitudeLine = ""
		emissionLine = ""
		phaseLine = ""
		incidenceLine = ""
		for j in range(0,432):
			# vector for pixel in radians
			dvec=[yp[i],xp[j],zp]
			# ensures the script won't break on pixels that don't intersect Io
			with spiceypy.no_found_check():
				[spoint, trgepc, srfvec, found] = spiceypy.sincpt(method2, target, etStart, tarfrm, abcorr, scname, frame, dvec)
				if found:
					[lon, lat, alti] = spiceypy.recpgr(target, spoint, radii[0], (radii[0]-radii[2])/radii[0])
					lon = lon * spiceypy.dpr()
					lat = lat * spiceypy.dpr()
					alt = spiceypy.vnorm( srfvec )
					[trgepc, srfvec, phase, solar, emissn] = spiceypy.ilumin(method2, target, etStart, tarfrm, abcorr, scname, spoint)
					inc = solar * spiceypy.dpr()
					ema = emissn * spiceypy.dpr()
					pha = phase * spiceypy.dpr()
				# if pixel doesn't intersect Io, a default value of -1024.0 is used
				else:
					lon = -1024.0
					lat = -1024.0
					alt = -1024.0
					inc = -1024.0
					ema = -1024.0
					pha = -1024.0
			# a very verbose method of generating a CSV file, but the numpy savetxt method had 
			# issues with merging two of them
			if latitudeLine == "":
				latitudeLine = str(lat)
				longitudeLine = str(lon)
				altitudeLine = str(alt)
				emissionLine = str(ema)
				phaseLine = str(pha)
				incidenceLine = str(inc)
			else:
				latitudeLine = latitudeLine + "," + str(lat)
				longitudeLine = longitudeLine + "," + str(lon)
				altitudeLine = altitudeLine + "," + str(alt)
				emissionLine = emissionLine + "," + str(ema)
				phaseLine = phaseLine + "," + str(pha)
				incidenceLine = incidenceLine + "," + str(inc)
		
		print(latitudeLine, file = latitudeFile)
		print(longitudeLine, file = longitudeFile)
		print(altitudeLine, file = altitudeFile)
		print(emissionLine, file = emissionFile)
		print(phaseLine, file = phaseFile)
		print(incidenceLine, file = incidenceFile)

# specbackplanegen is used on JUNO_JIRAM_S data and generates CSV files containing
# geometric and illumination information for each pixel. The files generated are: 
# latitude, longitude, altitude (distance to the intercept point), incidence 
# angle, phase angle, and emission angle

def specbackplanegen():
	[shape, frame, bsight, nbounds, bounds] = spiceypy.getfov(specfrm, 20)
	
	# calculation of the IFOV
	dx = np.abs((bounds[0,1]-bounds[2,1]) / 256)
	
	# IFOV from the IK
	# for now using this, but I can commment this out
	dx = 0.000237767
	
	# generate numpy arrays of radian pixel locations for x
	# sensor array has 1 spatial and 1 spectral dimension, so Y and Z are one value
	xp = bounds[0,1] - np.arange(0.5,256.5,1)*dx
	yp = bsight[0]
	zp = bsight[2]
	for i in range(0,256):
		# initialize each line so as to clear the previous line
		latitudeLine = ""
		longitudeLine = ""
		altitudeLine = ""
		emissionLine = ""
		phaseLine = ""
		incidenceLine = ""
		
		# vector for pixel in radians
		dvec=[yp,xp[i],zp]
		# ensures the script won't break on pixels that don't intersect Io
		with spiceypy.no_found_check():
			[spoint, trgepc, srfvec, found] = spiceypy.sincpt(method2, target, etStart, tarfrm, abcorr, scname, frame, dvec)
			if found:
				[lon, lat, alti] = spiceypy.recpgr(target, spoint, radii[0], (radii[0]-radii[2])/radii[0])
				lon = lon * spiceypy.dpr()
				lat = lat * spiceypy.dpr()
				alt = spiceypy.vnorm( srfvec )
				[trgepc, srfvec, phase, solar, emissn] = spiceypy.ilumin(method2, target, etStart, tarfrm, abcorr, scname, spoint)
				inc = solar * spiceypy.dpr()
				ema = emissn * spiceypy.dpr()
				pha = phase * spiceypy.dpr()
			# if pixel doesn't intersect Io, a default value of -1024.0 is used
			else:
				lon = -1024.0
				lat = -1024.0
				alt = -1024.0
				inc = -1024.0
				ema = -1024.0
				pha = -1024.0
		latitudeLine = str(lat)
		longitudeLine = str(lon)
		altitudeLine = str(alt)
		emissionLine = str(ema)
		phaseLine = str(pha)
		incidenceLine = str(inc)
		# each line will have the same geometry values so just repeating this for all pixels in the line
		for j in range(0,335):
			latitudeLine = latitudeLine + "," + str(lat)
			longitudeLine = longitudeLine + "," + str(lon)
			altitudeLine = altitudeLine + "," + str(alt)
			emissionLine = emissionLine + "," + str(ema)
			phaseLine = phaseLine + "," + str(pha)
			incidenceLine = incidenceLine + "," + str(inc)
		
		print(latitudeLine, file = latitudeFile)
		print(longitudeLine, file = longitudeFile)
		print(altitudeLine, file = altitudeFile)
		print(emissionLine, file = emissionFile)
		print(phaseLine, file = phaseFile)
		print(incidenceLine, file = incidenceFile)
	
# backplanecubegen converts the CSV backplanes generated earlier into ISIS cube files
# using ascii2isis then adds band information with the name of the backplane parameter
# as the filter name and the NAIF code and wavelength information for the image.
# backplanecubegen returns the full path and name of the output cube file

def backplanecubegen(backplane, bpName):
	csvFile = fileBase + '_' + backplane + '.csv'
	cubFile = fileBase + '.' + backplane + '.cub'
	isis.ascii2isis(from_=csvFile, to_=cubFile, order_="bsq", samples_=samples, lines_=imgLines, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
	isis.editlab(from_=cubFile, opt_="addg", grpname_="BandBin")
	isis.editlab(from_=cubFile, option="addkey", grpname="BandBin", keyword="FilterName", value=bpName)
	isis.editlab(from_=cubFile, option="addkey", grpname="BandBin", keyword="Center", value=filterCenter)
	isis.editlab(from_=cubFile, option="addkey", grpname="BandBin", keyword="Width", value=filterWidth)
	isis.editlab(from_=cubFile, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=naifCode)
	return cubFile

###########################
### COMMAND LINE PARSER ###
###########################

splitimages = False
offsetCSV = False
for i in sys.argv:
	if i == '-split':
		splitimages = True
	elif i == '-offset':
		offsetCSV = True

####################
### SCRIPT START ###
####################

# initialize spice files
spiceypy.furnsh( metakr )

# open file dialog. Select one or more label files as input.

inputFiles = fd.askopenfilenames(title='Select Labels', filetypes=(('PDS Labels', '*.LBL'), ('All files', '*.*')))
numFiles = len(inputFiles)
offsetInput = fd.askopenfilename(title='Select Offset CSV', filetypes=(('CSV Files', '*.csv'), ('All files', '*.*')))
numOffsetInput = len(offsetInput)

if numFiles == 0:
	sys.exit()
	
for file in inputFiles:
	parseTuple = fileParse(file)
	et = parseTuple[0]
	timstr = spiceypy.timout( et, xlsxmt )
	etStart = parseTuple[3]
	exposureTime = parseTuple[4]
	sclkStart = parseTuple[5]
	productID = parseTuple[1]
	orbit = parseTuple[2]
	productCreate = parseTuple[6]
	sequenceNum = parseTuple[7]
	sequenceSam = parseTuple[8]
	dataType = parseTuple[9]
	instrumentMode = parseTuple[10]
	
	# setup output files
	# first generate the file names for each parameter CSV file
	root = os.path.dirname(file)
	name = os.path.basename(file)
	fileBase = root + '/' + productID
	latitudeFile = fileBase + '_latitude.csv'
	longitudeFile = fileBase + '_longitude.csv'
	altitudeFile = fileBase + '_altitude.csv'
	emissionFile = fileBase + '_emission.csv'
	incidenceFile = fileBase + '_incidence.csv'
	phaseFile = fileBase + '_phase.csv'
	
	# open each CSV file
	latitudeFile = open( latitudeFile, 'w' )
	longitudeFile = open( longitudeFile, 'w' )
	altitudeFile = open( altitudeFile, 'w' )
	emissionFile = open( emissionFile, 'w' )
	incidenceFile = open( incidenceFile, 'w' )
	phaseFile = open( phaseFile, 'w' )	
	
	# get radii of Io from spice
	[num, radii] = spiceypy.bodvrd(target, 'RADII', 3)
	
	if dataType == 'IMAGE':
		# obtain cartesian coordinates for sub-spacecraft point at the time of closest approach
		[spoint, trgepc, subsrfvec] = spiceypy.subpnt( method, target, etStart, tarfrm, abcorr, scname )

		# obtain derived center pixel from derived file, if available
		derivedY = ""
		derivedX = ""
		if offsetInput != "" and offsetCSV == False:
			offsetFile = open(offsetInput)
			offsetInfo = offsetFile.readlines()
			for line in offsetInfo:
				if productID in line:
					derivedLine = line.split(",")
					derivedX = float(derivedLine[1])
					derivedY = float(derivedLine[2])
					break
			offsetFile.close()
		elif offsetCSV:
			print("Yep, you want to use an offset file!")
		
		if instrumentMode == "I1":
			imgLines = 256
			filters = 'L-BAND M-BAND'
			filterName = 'L-BAND'
			filterCenter = 3455
			filterWidth = 290
			naifCode = lbandfrm
			backplanegen(lbandfrm, derivedX, derivedY, trgepc)
			backplanegen(mbandfrm, derivedX, derivedY, trgepc)
		elif instrumentMode == "I2":
			imgLines = 128
			filters = 'M-BAND'
			filterName = 'M-BAND'
			filterCenter = 4780
			filterWidth = 480
			naifCode = mbandfrm
			backplanegen(mbandfrm, derivedX, derivedY, trgepc)
		elif instrumentMode == "I3":
			imgLines = 128
			filters = 'L-BAND'
			filterName = 'L-BAND'
			filterCenter = 3455
			filterWidth = 290
			naifCode = lbandfrm
			backplanegen(lbandfrm, derivedX, derivedY, trgepc)
		else:
			print("Incorrect Image Mode")
			sys.exit()
		
		# these two lines actually do all the "real" work of generating backplane CSV files
		
	elif dataType == 'SPECTRAL':
		specbackplanegen()
	
	latitudeFile.close()
	longitudeFile.close()
	altitudeFile.close()
	emissionFile.close()
	phaseFile.close()
	incidenceFile.close()
		
	
	##################################
	######## CUBE GENERATION #########
	##################################
	
	# time to merge some of these products into ISIS files if the original image exists
	if dataType == 'IMAGE':
		image = fileBase + '.IMG'
		pixelUnit = 'W/(m^2*sr)'
		samples = 432
	elif dataType == 'SPECTRAL':
		image = fileBase + '.DAT'
		imageCSV = fileBase + '.csv'
		pixelUnit = 'W/(m^2*sr*micron)'
		filters = 'SPECTROMETER'
		filterName = 'SPECTROMETER'
		filterCenter = 3500
		filterWidth = 1500
		naifCode = specfrm
		samples = 336
		imgLines = 256
		
	if os.path.exists(image):
		imageCub = fileBase + '.cub'
		mirrorCub = fileBase + '.mirror.cub'
	
		# convert IMG to ISIS cube and mirror it (to match geometry)
		isis.raw2isis(from_=image, to_=imageCub, samples_=samples, lines_=imgLines, bands_=1, bittype_="REAL")
		if dataType == 'IMAGE':
			isis.mirror(from_=imageCub, to_=mirrorCub)
		else:
			mirrorCub = imageCub
	
		# add labels to the image file
		isis.editlab(from_=mirrorCub, opt_="addg", grpname_="Instrument")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Instrument", keyword="SpacecraftName", value=scname)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Instrument", keyword="InstrumentId", value="JIR")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Instrument", keyword="TargetName", value=target)
		startDate = spiceypy.timout( etStart, datefmt )
		startTime = spiceypy.timout( etStart, timefmt )
		startTime = startDate + "T" + startTime
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Instrument", keyword="StartTime", value=startTime)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Instrument", keyword="SpacecraftClockStartCount", value=sclkStart)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Instrument", keyword="ExposureDuration", value=exposureTime)
		isis.editlab(from_=mirrorCub, opt_="addg", grpname_="Archive")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="DataSetId", value="JNO-J-JIRAM-3-RDR-V1.0")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="ProductVersionId", value='"01"')
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="ProducerId", value="ISTITUTO NAZIONALE DI ASTROFISICA")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="ProductId", value=productID)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="ProducerName", value="A.ADRIANI - R.NOSCHESE")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="ProductCreationTime", value=productCreate)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="FileName", value=productID)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="FocalLength", value=0.1583)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="FNumber", value=3.7)	
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="SequenceNumber", value=sequenceNum)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="SequenceSample", value=sequenceSam)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="ExposureTimestamp", value=sclkStart)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="IFOV", value="2.378e-004")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="IFOVUnit", value="rad/px")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="PixelUnit", value=pixelUnit)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="FiltersAvailable", value=filters)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="FocalLengthUnit", value="M")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="InstrumentType", value="INFRARED IMAGING SPECTROMETER")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="StandardDataProductID", value=dataType)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="DetectorDescription", value="2D Array")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="PixelHeight", value=38.0)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="PixelHeightUnit", value="MICRON")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="PixelWidth", value=38.0)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="PixelWidthUnit", value="MICRON")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="OrbitNumber", value=orbit)
		isis.editlab(from_=mirrorCub, opt_="addg", grpname_="BandBin")
		isis.editlab(from_=mirrorCub, option="addkey", grpname="BandBin", keyword="FilterName", value=filterName)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="BandBin", keyword="Center", value=filterCenter)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="BandBin", keyword="Width", value=filterWidth)
		isis.editlab(from_=mirrorCub, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=naifCode)
		
		# split or rename files
		lbandCub = fileBase + '_lband.mirror.cub'
		mbandCub = fileBase + '_mband.mirror.cub'
		if instrumentMode == "I1" and dataType == 'IMAGE' and splitimages:
			isis.crop(from_=mirrorCub, to_=lbandCub, line=1, nlines=128)
			isis.crop(from_=mirrorCub, to_=mbandCub, line=129, nlines=128)
			filterName = 'L-BAND'
			isis.editlab(from_=lbandCub, option="MODKEY", grpname="BandBin", keyword="FilterName", value='L-BAND')
			imageCSV = fileBase + '_lband.csv'
			isis.isis2ascii(from_=lbandCub, to_=imageCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + imageCSV + ".txt " + imageCSV))
			filterName = 'M-BAND'
			filterCenter = 4780
			filterWidth = 480
			naifCode = mbandfrm
			isis.editlab(from_=lbandCub, option="modkey", grpname="BandBin", keyword="FilterName", value='L-BAND')
			isis.editlab(from_=lbandCub, option="modkey", grpname="BandBin", keyword="Center", value=filterCenter)
			isis.editlab(from_=lbandCub, option="modkey", grpname="BandBin", keyword="Width", value=filterWidth)
			isis.editlab(from_=lbandCub, option="modkey", grpname="BandBin", keyword="NaifIkCode", value=naifCode)
			imageCSV = fileBase + '_mband.csv'
			isis.isis2ascii(from_=mbandCub, to_=imageCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + imageCSV + ".txt " + imageCSV))
		
		
		# generate cubes files for each backplane using the backplanecubegen function
		latitudeCube = backplanecubegen("latitude", "Latitude")
		longitudeCube = backplanecubegen("longitude", "Longitude")
		altitudeCube = backplanecubegen("altitude", "Altitude")
		emissionCube = backplanecubegen("emission", "Emission Angle")
		incidenceCube = backplanecubegen("incidence", "Incidence Angle")
		phaseCube = backplanecubegen("phase", "Phase Angle")
	
		# create merged product
		fromlist_path = isis.fromlist.make([mirrorCub, latitudeCube, longitudeCube, altitudeCube, phaseCube, incidenceCube, emissionCube])
		geomCub = fileBase + '.geom.cub'
		isis.cubeit(fromlist=fromlist_path, to_=geomCub, proplab_=mirrorCub)
		
		# split or rename files
		lbandCub = fileBase + '_lband.geom.cub'
		mbandCub = fileBase + '_mband.geom.cub'
		if instrumentMode == "I1" and dataType == 'IMAGE' and splitimages:
			isis.crop(from_=geomCub, to_=lbandCub, line=1, nlines=128)
			isis.crop(from_=geomCub, to_=mbandCub, line=129, nlines=128)
			fromCube = str(lbandCub + "+2")
			toCSV = fileBase + '_lband_latitude.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			fromCube = str(lbandCub + "+3")
			toCSV = fileBase + '_lband_longitude.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			fromCube = str(lbandCub + "+4")
			toCSV = fileBase + '_lband_altitude.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			fromCube = str(lbandCub + "+5")
			toCSV = fileBase + '_lband_emission.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			fromCube = str(lbandCub + "+6")
			toCSV = fileBase + '_lband_incidence.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			fromCube = str(lbandCub + "+7")
			toCSV = fileBase + '_lband_phase.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			
			# now make mband csv files
			fromCube = str(mbandCub + "+2")
			toCSV = fileBase + '_mband_latitude.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			fromCube = str(mbandCub + "+3")
			toCSV = fileBase + '_mband_longitude.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			fromCube = str(mbandCub + "+4")
			toCSV = fileBase + '_mband_altitude.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			fromCube = str(mbandCub + "+5")
			toCSV = fileBase + '_mband_emission.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			fromCube = str(mbandCub + "+6")
			toCSV = fileBase + '_mband_incidence.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			fromCube = str(mbandCub + "+7")
			toCSV = fileBase + '_mband_phase.csv'
			isis.isis2ascii(from_=fromCube, to_=toCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + toCSV + ".txt " + toCSV))
			
			# remove the now extraneous csv files
			os.system(str('/bin/rm ' + fileBase + '_latitude.csv'))
			os.system(str('/bin/rm ' + fileBase + '_longitude.csv'))
			os.system(str('/bin/rm ' + fileBase + '_altitude.csv'))
			os.system(str('/bin/rm ' + fileBase + '_emission.csv'))
			os.system(str('/bin/rm ' + fileBase + '_incidence.csv'))
			os.system(str('/bin/rm ' + fileBase + '_phase.csv'))
		elif instrumentMode == "I2" and dataType == 'IMAGE' and splitimages:
			mbandCub = fileBase + '_mband.mirror.cub'
			imageCSV = fileBase + '_mband.csv'
			os.system(str("mv " + mirrorCub + " " + mbandCub))
			isis.isis2ascii(from_=mbandCub, to_=imageCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + imageCSV + ".txt " + imageCSV))
			mbandCub = fileBase + '_mband.geom.cub'
			os.system(str("mv " + geomCub + " " + mbandCub))
			os.system(str("mv " + fileBase + "_latitude.csv " + fileBase + "_mband_latitude.csv"))
			os.system(str("mv " + fileBase + "_longitude.csv " + fileBase + "_mband_longitude.csv"))
			os.system(str("mv " + fileBase + "_altitude.csv " + fileBase + "_mband_altitude.csv"))
			os.system(str("mv " + fileBase + "_emission.csv " + fileBase + "_mband_emission.csv"))
			os.system(str("mv " + fileBase + "_incidence.csv " + fileBase + "_mband_incidence.csv"))
			os.system(str("mv " + fileBase + "_phase.csv " + fileBase + "_mband_phase.csv"))
		elif instrumentMode == "I3" and dataType == 'IMAGE' and splitimages:
			lbandCub = fileBase + '_lband.mirror.cub'
			imageCSV = fileBase + '_lband.csv'
			os.system(str("mv " + mirrorCub + " " + lbandCub))
			isis.isis2ascii(from_=lbandCub, to_=imageCSV, header_="no", delimiter_=",", setpixelvalues="yes", nullvalue_=-1024, hrsvalue_=1)
			os.system(str("mv " + imageCSV + ".txt " + imageCSV))
			lbandCub = fileBase + '_lband.geom.cub'
			os.system(str("mv " + geomCub + " " + mbandCub))
			os.system(str("mv " + fileBase + "_latitude.csv " + fileBase + "_lband_latitude.csv"))
			os.system(str("mv " + fileBase + "_longitude.csv " + fileBase + "_lband_longitude.csv"))
			os.system(str("mv " + fileBase + "_altitude.csv " + fileBase + "_lband_altitude.csv"))
			os.system(str("mv " + fileBase + "_emission.csv " + fileBase + "_lband_emission.csv"))
			os.system(str("mv " + fileBase + "_incidence.csv " + fileBase + "_lband_incidence.csv"))
			os.system(str("mv " + fileBase + "_phase.csv " + fileBase + "_lband_phase.csv"))
		
		# clean up extraneous cube files
		os.system(str("/bin/rm " + latitudeCube))
		os.system(str("/bin/rm " + longitudeCube))
		os.system(str("/bin/rm " + altitudeCube))
		os.system(str("/bin/rm " + emissionCube))
		os.system(str("/bin/rm " + incidenceCube))
		os.system(str("/bin/rm " + phaseCube))
		if dataType == 'IMAGE':
			os.system(str("/bin/rm " + imageCub))
		

#############################
######## SCRIPT END #########
#############################
spiceypy.unload( metakr )

