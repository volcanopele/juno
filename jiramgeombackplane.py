from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy
from tkinter import filedialog as fd
import tkinter as tk
import os, sys, getopt
import numpy as np

###
# This script takes a time in UTC as input (either directly or via JIRAM 
# label file(s)) from the user
# It outputs geometry information for Juno WRT Io at that time
# Outputting test.csv with geometric information for each frame
###

# initialize variables

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
useLabel = False

# initialize functions

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
	orbit = "PJ%s"%(orbit)
	
	# close file
	file.close()
	
	# tuple with image mid-time, product ID, and orbit output by function
	return [et, productID, orbit, etStart]

####################
### SCRIPT START ###
####################

# initialize spice files
spiceypy.furnsh( metakr )
spiceypy.furnsh( 'io_north_pole.bsp' )

# open file dialog. Select one or more label files as input. Hit cancel if you want to 
# manually input a time

inputFiles = fd.askopenfilenames(title='Select Labels', filetypes=(('PDS Labels', '*.LBL'), ('All files', '*.*')))
numFiles = len(inputFiles)
offsetFile = fd.askopenfilename(title='Select Offset CSV', filetypes=(('CSV Files', '*.LBL'), ('All files', '*.*')))
numOffsetFile = len(offsetFile)

if numFiles > 0:
	for file in inputFiles:
		parseTuple = fileParse(file)
		et = parseTuple[0]
		timstr = spiceypy.timout( et, xlsxmt )
		etStart = parseTuple[3]
		productID = parseTuple[1]
		orbit = parseTuple[2]
		
		# setup output file
		root = os.path.dirname(file)
		name = os.path.basename(file)
		fileBase = root + '/' + productID
		latitudeFile = fileBase + '_latitude.csv'
		longitudeFile = fileBase + '_longitude.csv'
		altitudeFile = fileBase + '_altitude.csv'
		emissionFile = fileBase + '_emission.csv'
		incidenceFile = fileBase + '_incidence.csv'
		phaseFile = fileBase + '_phase.csv'
		
		latitudeFile = open( latitudeFile, 'w' )
		longitudeFile = open( longitudeFile, 'w' )
		altitudeFile = open( altitudeFile, 'w' )
		emissionFile = open( emissionFile, 'w' )
		incidenceFile = open( incidenceFile, 'w' )
		phaseFile = open( phaseFile, 'w' )
		
		# may not even this part
		
		# calculate center spice pixel
		# obtain cartesian coordinates for sub-spacecraft point at the time of closest approach
		[spoint, trgepc, subsrfvec] = spiceypy.subpnt( method, target, etStart, tarfrm, abcorr, scname )
		print(subsrfvec)
		
		# get radii of Io from spice
		[num, radii] = spiceypy.bodvrd(target, 'RADII', 3)
		
		# convert cartesian coordinates of lat/lon
		[radius, lon, lat] = spiceypy.reclat( spoint )
		
		# convert lat and lon from radians to degrees
		lon = lon * spiceypy.dpr()
		lat = lat * spiceypy.dpr()
		
		# convert longitude domain from -180-180 E longitude to 0-360 W longitude
		if lon <= 0.0:
			lon = math.fabs(lon)
		else:
			lon = 360.0 - lon
		
		print(lat,lon)
		
		# L-band
		[shape, frame, bsight, nbounds, bounds] = spiceypy.getfov(lbandfrm, 20)
		
		dy = np.abs((bounds[0,0]-bounds[2,0]) / 128)
		dx = np.abs((bounds[0,1]-bounds[2,1]) / 432)

		xp = np.arange(0.5,431.51,1)*dx + bounds[3,1]
		yp = bounds[3,0] - np.arange(0.5,127.51,1)*dy
		zp = bounds[0,2]
		
		# calculate center pixel
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
		print(centerX)
		print(centerY)
		
		# initialize the arrays for different backplanes
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
		
		# M-band
		[shape, frame, bsight, nbounds, bounds] = spiceypy.getfov(mbandfrm, 20)
		
		# calculate the angle difference for one pixel in both X and Y
		dy = np.abs((bounds[0,0]-bounds[2,0]) / 128)
		dx = np.abs((bounds[0,1]-bounds[2,1]) / 432)

		xp = np.arange(0.5,431.51,1)*dx + bounds[3,1]
		yp = bounds[3,0] - np.arange(0.5,127.51,1)*dy
		zp = bounds[0,2]
		
		# calculate center pixel
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
		print(centerX)
		print(centerY)
		
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

spiceypy.unload( metakr )
spiceypy.unload( 'io_north_pole.bsp' )

# ascii2isis from=JIR_IMG_RDR_2021052T110632_V01.csv to=JIR_IMG_RDR_2021052T110632_V01.latstart.cub order=bsq samples=432 lines=256 bands=1 skip=0 setnullrange=yes nullmin=-2000 nullmax=-1000
# handmos from=JIR_IMG_RDR_2021052T110632_V01.latstart.cub mosaic=JIR_IMG_RDR_2021052T110632_V01.mirror.cub outband=2 null=true
# ascii2isis from=JIR_IMG_RDR_2021052T110632_V01_latitude.csv to=JIR_IMG_RDR_2021052T110632_V01.latitude.cub order=bsq samples=432 lines=256 bands=1 skip=0 setnullrange=yes nullmin=-2000 nullmax=-1000
# ascii2isis from=JIR_IMG_RDR_2021052T110632_V01_longitude.csv to=JIR_IMG_RDR_2021052T110632_V01.longitude.cub order=bsq samples=432 lines=256 bands=1 skip=0 setnullrange=yes nullmin=-2000 nullmax=-1000
# ascii2isis from=JIR_IMG_RDR_2021052T110632_V01_emission.csv to=JIR_IMG_RDR_2021052T110632_V01.emission.cub order=bsq samples=432 lines=256 bands=1 skip=0 setnullrange=yes nullmin=-2000 nullmax=-1000
# ascii2isis from=JIR_IMG_RDR_2021052T110632_V01_altitude.csv to=JIR_IMG_RDR_2021052T110632_V01.altitude.cub order=bsq samples=432 lines=256 bands=1 skip=0 setnullrange=yes nullmin=-2000 nullmax=-1000
