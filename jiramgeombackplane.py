from __future__ import print_function
from builtins import input
import math
import spiceypy
from tkinter import filedialog as fd
import tkinter as tk
import os, sys, getopt
import numpy as np
import kalasiris as isis

###
# This script takes a time in UTC as input (either directly or via JIRAM 
# label file(s)) from the user
# It outputs geometry information for Juno WRT Io at that time
# Outputting test.csv with geometric information for each frame
###

###################################
###### LICENSE AND COPYRIGHT ######
###################################

# Copyright (C) 2020–2022 Arizona Board of Regents on behalf of the Planetary
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

metakr = '/Users/perry/Dropbox/Io/Juno/kernels/juno_latest.tm'
sclkid = -61
scname = 'JUNO'
target = 'IO'
tarfrm = 'IAU_IO'
abcorr = 'LT+S'
jrmfrm = 'JUNO_JIRAM_I'
lbandfrm = -61411
lbndnm = 'JUNO_JIRAM_I_LBAND'
mbandfrm = -61412
mbndnm = 'JUNO_JIRAM_I_MBAND'
jirmid = -61410


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
	return [et, productID, orbit, etStart, exposureTime, startTime, productCreate, sequenceNum, sequenceSam]

####################
### SCRIPT START ###
####################

# initialize spice files
spiceypy.furnsh( metakr )

# open file dialog. Select one or more label files as input. Hit cancel if you want to 
# manually input a time

inputFiles = fd.askopenfilenames(title='Select Labels', filetypes=(('PDS Labels', '*.LBL'), ('All files', '*.*')))
numFiles = len(inputFiles)
offsetInput = fd.askopenfilename(title='Select Offset CSV', filetypes=(('CSV Files', '*.csv'), ('All files', '*.*')))
numOffsetInput = len(offsetInput)

if numFiles > 0:
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
		
		# obtain cartesian coordinates for sub-spacecraft point at the time of closest approach
		[spoint, trgepc, subsrfvec] = spiceypy.subpnt( method, target, etStart, tarfrm, abcorr, scname )
		
		# get radii of Io from spice
		[num, radii] = spiceypy.bodvrd(target, 'RADII', 3)
		
		# obtain derived center pixel from derived file, if available
		if offsetInput != "":
			offsetFile = open(offsetInput)
			offsetInfo = offsetFile.readlines()
			for line in offsetInfo:
				if productID in line:
					derivedLine = line.split(",")
					derivedX = float(derivedLine[1])
					derivedY = float(derivedLine[2])
					break
			offsetFile.close()
		else:
			derivedY = ""
		
		##################################
		######## L-BAND BACKPLANE ########
		##################################
		
		[shape, frame, bsight, nbounds, bounds] = spiceypy.getfov(lbandfrm, 20)
		
		# calculation of the IFOV
		dy = np.abs((bounds[0,0]-bounds[2,0]) / 128)
		dx = np.abs((bounds[0,1]-bounds[2,1]) / 432)
		
		# IFOV from the IK
		# for now using this, but I can commment this out
		dx = 0.000237767
		dy = 0.000237767
		
		# calculate center pixel in the M-Band FOV
		xform = spiceypy.pxfrm2(tarfrm, lbndnm, trgepc, etStart)
		lbandsubvec = spiceypy.mxv(xform, subsrfvec)
		lbandsubvec[0] = lbandsubvec[0] / lbandsubvec[2]
		lbandsubvec[1] = lbandsubvec[1] / lbandsubvec[2]
		lbandsubvec[2] = lbandsubvec[2] / lbandsubvec[2]
		centerX = lbandsubvec[1] - bounds[3,1]
		centerX /= dx
		centerY = lbandsubvec[0] - bounds[3,0]
		centerY /= dx
		centerY *= -1
		
		# calculating offsets. probably still need this regardless of derivedY values
		if derivedY != "" and derivedY <= 128:
			offsetY = centerY - derivedY
			offsetY *= dy
			offsetX = centerX - derivedX
			offsetX *= dx
		else:
			offsetY = 0
			offsetX = 0
			
		# generate numpy arrays of radian pixel locations for both the X and Y directions
		xp = np.arange(0.5,431.51,1)*dx + bounds[3,1] + offsetX
		yp = bounds[3,0] - np.arange(0.5,127.51,1)*dy + offsetY
		zp = bounds[0,2]
		
		# initialize the arrays for different backplanes
		# don't even really need this!!!
		llon = np.zeros([432,128])
		llon.fill(-1024.0)
		llat = np.zeros([432,128])
		llat.fill(-1024.0)
		linc = np.zeros([432,128])
		linc.fill(-1024.0)
		lemm = np.zeros([432,128])
		lemm.fill(-1024.0)
		lpha = np.zeros([432,128])
		lpha.fill(-1024.0)
		lalt = np.zeros([432,128])
		lalt.fill(-1024.0)
		
		for i in range(0,128):
			# initialize each line so as to clear the previous line
			latitudeLine = ""
			longitudeLine = ""
			altitudeLine = ""
			emissionLine = ""
			phaseLine = ""
			incidenceLine = ""
			for j in range(0,432):
				dvec=[yp[i],xp[j],zp]
				with spiceypy.no_found_check():
					[spoint, trgepc, srfvec, found] = spiceypy.sincpt(method2, target, etStart, tarfrm, abcorr, scname, frame, dvec)
					if found:
						[loni, lati, alti] = spiceypy.recpgr(target, spoint, radii[0], (radii[0]-radii[2])/radii[0])
						llon[j,i] = loni * spiceypy.dpr()
						llat[j,i] = lati * spiceypy.dpr()
						lalt[j,i] = spiceypy.vnorm( srfvec )
						[trgepc, srfvec, phase, solar, emissn] = spiceypy.ilumin(method2,target, etStart, tarfrm, abcorr, scname, spoint)
						linc[j,i] = solar * spiceypy.dpr()
						lemm[j,i] = emissn * spiceypy.dpr()
						lpha[j,i] = phase * spiceypy.dpr()
				if latitudeLine == "":
					latitudeLine = str(llat[j,i])
					longitudeLine = str(llon[j,i])
					altitudeLine = str(lalt[j,i])
					emissionLine = str(lemm[j,i])
					phaseLine = str(lpha[j,i])
					incidenceLine = str(linc[j,i])
				else:
					latitudeLine = latitudeLine + "," + str(llat[j,i])
					longitudeLine = longitudeLine + "," + str(llon[j,i])
					altitudeLine = altitudeLine + "," + str(lalt[j,i])
					emissionLine = emissionLine + "," + str(lemm[j,i])
					phaseLine = phaseLine + "," + str(lpha[j,i])
					incidenceLine = incidenceLine + "," + str(linc[j,i])
			print(latitudeLine, file = latitudeFile)
			print(longitudeLine, file = longitudeFile)
			print(altitudeLine, file = altitudeFile)
			print(emissionLine, file = emissionFile)
			print(phaseLine, file = phaseFile)
			print(incidenceLine, file = incidenceFile)
		
		##################################
		######## M-BAND BACKPLANE ########
		##################################
		
		[shape, frame, bsight, nbounds, bounds] = spiceypy.getfov(mbandfrm, 20)
		
		# calculate the IFOV
		dy = np.abs((bounds[0,0]-bounds[2,0]) / 128)
		dx = np.abs((bounds[0,1]-bounds[2,1]) / 432)
		
		# IFOV from the IK
		# for now using this, but I can commment this out
		dx = 0.000237767
		dy = 0.000237767
		
		# calculate center pixel in the M-Band FOV
		xform = spiceypy.pxfrm2(tarfrm, mbndnm, trgepc, etStart)
		mbandsubvec = spiceypy.mxv(xform, subsrfvec)
		mbandsubvec[0] = mbandsubvec[0] / mbandsubvec[2]
		mbandsubvec[1] = mbandsubvec[1] / mbandsubvec[2]
		mbandsubvec[2] = mbandsubvec[2] / mbandsubvec[2]
		centerX = mbandsubvec[1] - bounds[3,1]
		centerX /= dx
		centerY = mbandsubvec[0] - bounds[3,0]
		centerY /= dx
		centerY *= -1
		centerY += 128
		
		# calculating X and Y offsets if derived information is available
		if derivedY != "" and derivedY >= 129:
			offsetY = centerY - derivedY
			offsetY *= dy
			offsetX = centerX - derivedX
			offsetX *= dx
		else:
			offsetY = 0
			offsetX = 0
		
		# generate numpy arrays for both the X and Y directions
		xp = np.arange(0.5,431.51,1)*dx + bounds[3,1] + offsetX
		yp = bounds[3,0] - np.arange(0.5,127.51,1)*dy - offsetY
		zp = bounds[0,2]
		
		# initialize the arrays for different backplanes
		mlon = np.zeros([432,128])
		mlon.fill(-1024.0)
		mlat = np.zeros([432,128])
		mlat.fill(-1024.0)
		minc = np.zeros([432,128])
		minc.fill(-1024.0)
		mema = np.zeros([432,128])
		mema.fill(-1024.0)
		mpha = np.zeros([432,128])
		mpha.fill(-1024.0)
		malt = np.zeros([432,128])
		malt.fill(-1024.0)
		
		for i in range(0,128):
			# initialize each line so as to clear the previous line
			latitudeLine = ""
			longitudeLine = ""
			altitudeLine = ""
			emissionLine = ""
			phaseLine = ""
			incidenceLine = ""
			for j in range(0,432):
				dvec=[yp[i],xp[j],zp]
				with spiceypy.no_found_check():
					[spoint, trgepc, srfvec, found] = spiceypy.sincpt(method2, target, etStart, tarfrm, abcorr, scname, frame, dvec)
					if found:
						[loni, lati, alti] = spiceypy.recpgr(target, spoint, radii[0], (radii[0]-radii[2])/radii[0])
						mlon[j,i] = loni * spiceypy.dpr()
						mlat[j,i] = lati * spiceypy.dpr()
						malt[j,i] = spiceypy.vnorm( srfvec )
						[trgepc, srfvec, phase, solar, emissn] = spiceypy.ilumin(method2,target, etStart, tarfrm, abcorr, scname, spoint)
						minc[j,i] = solar * spiceypy.dpr()
						mema[j,i] = emissn * spiceypy.dpr()
						mpha[j,i] = phase * spiceypy.dpr()
				if latitudeLine == "":
					latitudeLine = str(llat[j,i])
					longitudeLine = str(llon[j,i])
					altitudeLine = str(lalt[j,i])
					emissionLine = str(lemm[j,i])
					phaseLine = str(lpha[j,i])
					incidenceLine = str(linc[j,i])
				else:
					latitudeLine = latitudeLine + "," + str(mlat[j,i])
					longitudeLine = longitudeLine + "," + str(mlon[j,i])
					altitudeLine = altitudeLine + "," + str(malt[j,i])
					emissionLine = emissionLine + "," + str(mema[j,i])
					phaseLine = phaseLine + "," + str(mpha[j,i])
					incidenceLine = incidenceLine + "," + str(minc[j,i])
			print(latitudeLine, file = latitudeFile)
			print(longitudeLine, file = longitudeFile)
			print(altitudeLine, file = altitudeFile)
			print(emissionLine, file = emissionFile)
			print(phaseLine, file = phaseFile)
			print(incidenceLine, file = incidenceFile)
		
		
		latitudeFile.close()
		longitudeFile.close()
		altitudeFile.close()
		emissionFile.close()
		phaseFile.close()
		incidenceFile.close()
		
		# time to merge some of these products into ISIS files if the original image exists
		image = fileBase + '.IMG'
		if os.path.exists(image):
			imageCub = fileBase + '.cub'
			mirrorCub = fileBase + '.mirror.cub'
		
			# convert IMG to ISIS cube and mirror it (to match geometry)
			isis.raw2isis(from_=image, to_=imageCub, samples_=432, lines_=256, bands_=1, bittype_="REAL")
			isis.mirror(from_=imageCub, to_=mirrorCub)
		
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
			isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="PixelUnit", value="W/(m^2*sr)")
			isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="FiltersAvailable", value="L-BAND M-BAND")
			isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="FocalLengthUnit", value="M")
			isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="InstrumentType", value="INFRARED IMAGING SPECTROMETER")
			isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="DetectorDescription", value="2D Array")
			isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="PixelHeight", value=38.0)
			isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="PixelHeightUnit", value="MICRON")
			isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="PixelWidth", value=38.0)
			isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="PixelWidthUnit", value="MICRON")
			isis.editlab(from_=mirrorCub, option="addkey", grpname="Archive", keyword="OrbitNumber", value=orbit)
			isis.editlab(from_=mirrorCub, opt_="addg", grpname_="BandBin")
			isis.editlab(from_=mirrorCub, option="addkey", grpname="BandBin", keyword="FilterName", value="L-BAND")
			isis.editlab(from_=mirrorCub, option="addkey", grpname="BandBin", keyword="Center", value=3455)
			isis.editlab(from_=mirrorCub, option="addkey", grpname="BandBin", keyword="Width", value=290)
			isis.editlab(from_=mirrorCub, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=lbandfrm)
		
			# convert latitude file to cube
			latitudeFile = fileBase + '_latitude.csv'
			latitudeCube = fileBase + '.latitude.cub'
			isis.ascii2isis(from_=latitudeFile, to_=latitudeCube, order_="bsq", samples_=432, lines_=256, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
			isis.editlab(from_=latitudeCube, opt_="addg", grpname_="BandBin")
			isis.editlab(from_=latitudeCube, option="addkey", grpname="BandBin", keyword="FilterName", value="Latitude")
			isis.editlab(from_=latitudeCube, option="addkey", grpname="BandBin", keyword="Center", value=3455)
			isis.editlab(from_=latitudeCube, option="addkey", grpname="BandBin", keyword="Width", value=290)
			isis.editlab(from_=latitudeCube, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=lbandfrm)
		
			# convert longitude file to cube
			longitudeFile = fileBase + '_longitude.csv'
			longitudeCube = fileBase + '.longitude.cub'
			isis.ascii2isis(from_=longitudeFile, to_=longitudeCube, order_="bsq", samples_=432, lines_=256, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
			isis.editlab(from_=longitudeCube, opt_="addg", grpname_="BandBin")
			isis.editlab(from_=longitudeCube, option="addkey", grpname="BandBin", keyword="FilterName", value="Longitude")
			isis.editlab(from_=longitudeCube, option="addkey", grpname="BandBin", keyword="Center", value=3455)
			isis.editlab(from_=longitudeCube, option="addkey", grpname="BandBin", keyword="Width", value=290)
			isis.editlab(from_=longitudeCube, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=lbandfrm)
		
			# convert altitude file to cube
			altitudeFile = fileBase + '_altitude.csv'
			altitudeCube = fileBase + '.altitude.cub'
			isis.ascii2isis(from_=altitudeFile, to_=altitudeCube, order_="bsq", samples_=432, lines_=256, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
			isis.editlab(from_=altitudeCube, opt_="addg", grpname_="BandBin")
			isis.editlab(from_=altitudeCube, option="addkey", grpname="BandBin", keyword="FilterName", value="Altitude")
			isis.editlab(from_=altitudeCube, option="addkey", grpname="BandBin", keyword="Center", value=3455)
			isis.editlab(from_=altitudeCube, option="addkey", grpname="BandBin", keyword="Width", value=290)
			isis.editlab(from_=altitudeCube, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=lbandfrm)
		
			# convert emission file to cube
			emissionFile = fileBase + '_emission.csv'
			emissionCube = fileBase + '.emission.cub'
			isis.ascii2isis(from_=emissionFile, to_=emissionCube, order_="bsq", samples_=432, lines_=256, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
			isis.editlab(from_=emissionCube, opt_="addg", grpname_="BandBin")
			isis.editlab(from_=emissionCube, option="addkey", grpname="BandBin", keyword="FilterName", value="Emission Angle")
			isis.editlab(from_=emissionCube, option="addkey", grpname="BandBin", keyword="Center", value=3455)
			isis.editlab(from_=emissionCube, option="addkey", grpname="BandBin", keyword="Width", value=290)
			isis.editlab(from_=emissionCube, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=lbandfrm)
		
			# convert incidence file to cube
			incidenceFile = fileBase + '_incidence.csv'
			incidenceCube = fileBase + '.incidence.cub'
			isis.ascii2isis(from_=incidenceFile, to_=incidenceCube, order_="bsq", samples_=432, lines_=256, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
			isis.editlab(from_=incidenceCube, opt_="addg", grpname_="BandBin")
			isis.editlab(from_=incidenceCube, option="addkey", grpname="BandBin", keyword="FilterName", value="Incidence Angle")
			isis.editlab(from_=incidenceCube, option="addkey", grpname="BandBin", keyword="Center", value=3455)
			isis.editlab(from_=incidenceCube, option="addkey", grpname="BandBin", keyword="Width", value=290)
			isis.editlab(from_=incidenceCube, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=lbandfrm)
		
			# convert phase file to cube
			phaseFile = fileBase + '_phase.csv'
			phaseCube = fileBase + '.phase.cub'
			isis.ascii2isis(from_=phaseFile, to_=phaseCube, order_="bsq", samples_=432, lines_=256, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
			isis.editlab(from_=phaseCube, opt_="addg", grpname_="BandBin")
			isis.editlab(from_=phaseCube, option="addkey", grpname="BandBin", keyword="FilterName", value="Phase Angle")
			isis.editlab(from_=phaseCube, option="addkey", grpname="BandBin", keyword="Center", value=3455)
			isis.editlab(from_=phaseCube, option="addkey", grpname="BandBin", keyword="Width", value=290)
			isis.editlab(from_=phaseCube, option="addkey", grpname="BandBin", keyword="NaifIkCode", value=lbandfrm)
		
			# create merged product
			fromlist_path = isis.fromlist.make([mirrorCub, latitudeCube, longitudeCube, altitudeCube, phaseCube, incidenceCube, emissionCube])
			geomCub = fileBase + '.geom.cub'
			isis.cubeit(fromlist=fromlist_path, to_=geomCub, proplab_=mirrorCub)
		

spiceypy.unload( metakr )
