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
srunm = 'JUNO_SRU1'
srufrm = -61071


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
	instrumentMode = ""
	exposureTime = ""
	targetName = ""
	
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
		elif 'TARGET_NAME' in line:
			targetName = line
			targetNames = targetName.split(" ")
			targetNames = sorted(targetNames, reverse=True)
			targetName = targetNames[2]
			targetName = targetName.split('"')
			targetName = targetName[1]
		elif 'STANDARD_DATA_PRODUCT_ID' in line:
			dataType = line
			dataTypes = dataType.split(" ")
			dataTypes = sorted(dataTypes, reverse=True)
			dataType = dataTypes[2]
			dataType = dataType.split('"')[1]
		elif 'PRODUCT_ID ' in line:
			if line.startswith('PRODUCT_ID ', 0):
				productID = line
				productIDs = productID.split(" ")
				productIDs = sorted(productIDs, reverse=True)
				productID = productIDs[2]
				productID = productID.split('"')
				productID = productID[1]
		elif 'ORBIT_NUMBER' in line:
			orbit = line
			orbits = orbit.split(" ")
			orbits = sorted(orbits, reverse=True)
			orbit = orbits[2]
		elif 'EXPOSURE_DURATION' in line:
			exposureTime = line
			exposureTimes = exposureTime.split(" ")
			exposureTimes = sorted(exposureTimes, reverse=True)
			exposureTime = float(exposureTimes[3])

	
	# start and stop time converted to seconds past J2000
	etStart = spiceypy.scs2e(-61999,startTime)
	etStop = spiceypy.scs2e(-61999,stopTime)
	# Image mid-time calculated
	et = (etStart+etStop)/2
	if exposureTime == "":
		exposureTime = etStop - etStart
	
	# close file
	file.close()
	
	# tuple with image mid-time, product ID, and orbit output by function
	return [et, productID, orbit, etStart, exposureTime, startTime, productCreate, dataType, targetName]
	
# backplanegen is used on JUNO_JIRAM_I data and generates CSV files containing
# geometric and illumination information for each pixel. The files generated are: 
# latitude, longitude, altitude (distance to the intercept point), incidence 
# angle, phase angle, and emission angle

def backplanegen(frmcode, Xoffset, Yoffset, trgepc):
	[shape, frame, bsight, nbounds, bounds] = spiceypy.getfov(frmcode, 20)
	
	# calculation of the IFOV
	dx = 0.000551562
	dy = 0.000551562
	
	Yoffset *= dy
	Xoffset *= dx
	
	for i in range(0,512):
		# initialize each line so as to clear the previous line
		latitudeLine = ""
		longitudeLine = ""
		altitudeLine = ""
		emissionLine = ""
		phaseLine = ""
		incidenceLine = ""
		for j in range(0,512):
			# defining variables
			line = i
			sample = j
			# sampleRadians = xp[j]
			# lineRadians = yp[i]
			
			# applying geometric correction
			tanxref = float((sample - 255.5) / 1760.21137)
			tanyref = float((line - 255.5) / 1760.21137)
			
			pixradi = math.sqrt(tanxref ** 2 + tanyref ** 2)
			radcorr = 0.999432579 + (-0.0295412410) * pixradi + 0.2733020107 * pixradi ** 2 + (-1.9368112951) * pixradi ** 4
			
			tanxref *= radcorr
			tanyref *= radcorr
			
			sample = tanxref * 1760.21137 + 255.5
			line = tanyref * 1760.21137 + 255.5
			
			sampleRadians = bounds[3,1] - (sample * dx)
			lineRadians = bounds[3,2] - (line * dy)
			
			# apply offset
			sampleRadians += Xoffset
			lineRadians += Yoffset
			
			# vector for pixel in radians
			dvec=[bounds[3,0],sampleRadians,lineRadians]
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

# backplanecubegen converts the CSV backplanes generated earlier into ISIS cube files
# using ascii2isis then adds band information with the name of the backplane parameter
# as the filter name and the NAIF code and wavelength information for the image.
# backplanecubegen returns the full path and name of the output cube file

def backplanecubegen(backplane, bpName):
	csvFile = fileBase + '_' + backplane + '.csv'
	cubFile = fileBase + '.' + backplane + '.cub'
	isis.ascii2isis(from_=csvFile, to_=cubFile, order_="bsq", samples_=512, lines_=512, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
	isis.editlab(from_=cubFile, opt_="addg", grpname_="BandBin")
	isis.editlab(from_=cubFile, option="addkey", grpname="BandBin", keyword="FilterName", value=bpName)
	isis.editlab(from_=cubFile, option="addkey", grpname="BandBin", keyword="Center", value=filterCenter)
	isis.editlab(from_=cubFile, option="addkey", grpname="BandBin", keyword="Width", value=filterWidth)
	isis.editlab(from_=cubFile, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=srufrm)
	return cubFile

###########################
### COMMAND LINE PARSER ###
###########################


mapfile = ''
outputfile = ''
jiramInput = ''
rotation = ''
offsetX = 0
offsetY = 0
argv = sys.argv[1:]
bandlimitation = "all"
saturation = "no"
spectral = False
bkgSubtract = False
flatfield = False

try:
	opts, args = getopt.getopt(argv, 'i:m:x:y:z:', ['mapfile', 'infile'])
	for opt, arg in opts:
		if opt in ("-m", "--mapfile"):
			mapfile = arg
		if opt in ("-i", "--infile"):
			jiramInput = arg
		if opt in ("-x"):
			offsetX = float(arg)
		if opt in ("-y"):
			offsetY = float(arg)
		if opt in ("-z"):
			rotation = float(arg)
			
except getopt.GetoptError:
	print('srugeombackplane.py -m <mapfile> -i <infile>')
	sys.exit(2)

####################
### SCRIPT START ###
####################

# initialize spice files
spiceypy.furnsh( metakr )

# open file dialog. Select one or more label files as input.

file = fd.askopenfilename(title='Select Labels', filetypes=(('PDS Labels', '*.LBL'), ('All files', '*.*')))
numFiles = len(file)

if numFiles == 0:
	sys.exit()

parseTuple = fileParse(file)
et = parseTuple[0]
timstr = spiceypy.timout( et, xlsxmt )
etStart = float(parseTuple[3])
exposureTime = float(parseTuple[4])
sclkStart = parseTuple[5]
productID = parseTuple[1]
orbit = int(parseTuple[2])
productCreate = parseTuple[6]
dataType = parseTuple[7]
target = parseTuple[8]

if target == "IO":
	tarfrm = 'IAU_IO'
elif target == "EUROPA":
	tarfrm = 'IAU_EUROPA'
elif target == "GANYMEDE":
	tarfrm = 'IAU_GANYMEDE'
else:
	target = 'IO'
	tarfrm = 'IAU_IO'

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
fitsFile = fileBase + '.FIT'
imageFile = fileBase + '.cub'

# open each CSV file
latitudeFile = open( latitudeFile, 'w' )
longitudeFile = open( longitudeFile, 'w' )
altitudeFile = open( altitudeFile, 'w' )
emissionFile = open( emissionFile, 'w' )
incidenceFile = open( incidenceFile, 'w' )
phaseFile = open( phaseFile, 'w' )	
	
# get radii of Io from spice
[num, radii] = spiceypy.bodvrd(target, 'RADII', 3)

# obtain cartesian coordinates for sub-spacecraft point at the time of closest approach
[spoint, trgepc, subsrfvec] = spiceypy.subpnt( method, target, et, tarfrm, abcorr, scname )

backplanegen(srufrm, offsetX, offsetY, trgepc)

latitudeFile.close()
longitudeFile.close()
altitudeFile.close()
emissionFile.close()
phaseFile.close()
incidenceFile.close()

##################################
######## CUBE GENERATION #########
##################################

filterName = 'IMAGE'
filterCenter = 716
filterWidth = 421

# csv files
latitudeFile = fileBase + '_latitude.csv'
longitudeFile = fileBase + '_longitude.csv'
altitudeFile = fileBase + '_altitude.csv'
emissionFile = fileBase + '_emission.csv'
incidenceFile = fileBase + '_incidence.csv'
phaseFile = fileBase + '_phase.csv'

# generate cubes files for each backplane using the backplanecubegen function
latitudeCube = backplanecubegen("latitude", "Latitude")
longitudeCube = backplanecubegen("longitude", "Longitude")
altitudeCube = backplanecubegen("altitude", "Altitude")
emissionCube = backplanecubegen("emission", "Emission Angle")
incidenceCube = backplanecubegen("incidence", "Incidence Angle")
phaseCube = backplanecubegen("phase", "Phase Angle")

# create image product
isis.fits2isis(from_=fitsFile, to_=imageFile)
trimcub = fileBase + '.' + 'trim' + '.cub'
isis.trim(from_=imageFile, to_=trimcub, top_=1, bottom_=2, left_=2, right_=1)

# add labels to the image file
isis.editlab(from_=latitudeCube, opt_="addg", grpname_="Instrument")
isis.editlab(from_=latitudeCube, option="addkey", grpname="Instrument", keyword="SpacecraftName", value=scname)
isis.editlab(from_=latitudeCube, option="addkey", grpname="Instrument", keyword="InstrumentId", value="SRU")
isis.editlab(from_=latitudeCube, option="addkey", grpname="Instrument", keyword="TargetName", value=target)
startDate = spiceypy.timout( etStart, datefmt )
startTime = spiceypy.timout( etStart, timefmt )
startTime = startDate + "T" + startTime
isis.editlab(from_=latitudeCube, option="addkey", grpname="Instrument", keyword="StartTime", value=startTime)
isis.editlab(from_=latitudeCube, option="addkey", grpname="Instrument", keyword="SpacecraftClockStartCount", value=sclkStart)
isis.editlab(from_=latitudeCube, option="addkey", grpname="Instrument", keyword="ExposureDuration", value=exposureTime)
isis.editlab(from_=latitudeCube, opt_="addg", grpname_="Archive")
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="DataSetId", value="JNO-J-SRU-EDR-2-L0-V1.0")
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="ProductVersionId", value='"01"')
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="ProducerId", value="JUNO_SRU_TEAM")
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="ProductId", value=productID)
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="ProductCreationTime", value=productCreate)
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="FileName", value=productID)	
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="ExposureTimestamp", value=sclkStart)
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="IFOV", value="5.51562e-004")
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="IFOVUnit", value="rad/px")
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="StandardDataProductID", value=dataType)
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="DetectorDescription", value="2D Array")
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="PixelHeight", value=17.0)
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="PixelHeightUnit", value="MICRON")
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="PixelWidth", value=17.0)
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="PixelWidthUnit", value="MICRON")
isis.editlab(from_=latitudeCube, option="addkey", grpname="Archive", keyword="OrbitNumber", value=orbit)

isis.editlab(from_=trimcub, opt_="addg", grpname_="BandBin")
isis.editlab(from_=trimcub, option="addkey", grpname="BandBin", keyword="FilterName", value=filterName)
isis.editlab(from_=trimcub, option="addkey", grpname="BandBin", keyword="Center", value=filterCenter)
isis.editlab(from_=trimcub, option="addkey", grpname="BandBin", keyword="Width", value=filterWidth)
isis.editlab(from_=trimcub, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=srufrm)

fromlist_path = isis.fromlist.make([trimcub, latitudeCube, longitudeCube, altitudeCube, phaseCube, incidenceCube, emissionCube])
geomCub = fileBase + '.geom.cub'
# need to use latitudeCube because imageFile is 16-bit
isis.cubeit(fromlist_=fromlist_path, to_=geomCub, proplab_=latitudeCube)

# clean up extraneous cube files
os.system(str("/bin/rm " + latitudeCube))
os.system(str("/bin/rm " + longitudeCube))
os.system(str("/bin/rm " + altitudeCube))
os.system(str("/bin/rm " + emissionCube))
os.system(str("/bin/rm " + incidenceCube))
os.system(str("/bin/rm " + phaseCube))

# clean up extraneous csv files
os.system(str("/bin/rm " + latitudeFile))
os.system(str("/bin/rm " + longitudeFile))
os.system(str("/bin/rm " + altitudeFile))
os.system(str("/bin/rm " + emissionFile))
os.system(str("/bin/rm " + incidenceFile))
os.system(str("/bin/rm " + phaseFile))

#############################
######## SCRIPT END #########
#############################
spiceypy.unload( metakr )

