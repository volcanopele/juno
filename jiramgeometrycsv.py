from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy
from tkinter import filedialog as fd
import tkinter as tk
import os, sys, getopt

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
jirmid = -61410


# various parameters for the script
adjust = 0.0
method = 'Intercept/Ellipsoid'
method2 = 'ELLIPSOID'
maxivl = 1000
maxwin = 2 * maxivl
relate = 'ABSMIN'
tdbfmt = 'YYYY MON DD HR:MN:SC.### TDB ::TDB'
xlsxmt = 'MM/DD/YYYY HR:MN:SC.###'
useLabel = False

# initialize functions

# fileParse takes an input JIRAM label file and pulls out pieces of information 
# that will be used by the script, outputting as a tuple the image mid-time, 
# product ID, orbit number, and target name

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
		if 'TARGET_NAME' in line:
			targetName = line
			targetNames = targetName.split(" ")
			targetNames = sorted(targetNames, reverse=True)
			targetName = targetNames[2]
			
			targetNames = targetName.split('"')
			targetName = targetNames[1]
		if 'START_TIME' in line:
			startTime = line
			startTimes = startTime.split(" ")
			startTimes = sorted(startTimes, reverse=True)
			startTime = startTimes[2]
		elif 'STOP_TIME' in line:
			stopTime = line
			stopTimes = stopTime.split(" ")
			stopTimes = sorted(stopTimes, reverse=True)
			stopTime = stopTimes[2]
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
	etStart = spiceypy.str2et(startTime)
	etStop = spiceypy.str2et(stopTime)
	# Image mid-time calculated
	et = (etStart+etStop)/2
	orbit = "PJ%s"%(orbit)
	
	# close file
	file.close()
	
	# tuple with image mid-time, product ID, and orbit output by function
	return [et, productID, orbit, targetName]
	

	
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

# based on whether a file was selected or not, the observation mid-time is converted to 
# seconds after J2000. Other variables are set to be used when outputting a text file, 
# including product ID, orbit number, and the time in a string meant for Excel
if numFiles > 0:
	# if an odd number of labels are selected, the middle label is used for calculations
	# by this script. Otherwise, else will select the middle two labels. The observation
	# mid-time will be the average of the two individual image mid-times. This time is
	# used by most of the script to calculate geometric values except for north clock
	# angle, which will use the first of the two middle labels. Product ID also uses this 
	# label.
	outputFile = open( 'test.csv', 'w' )
	print('Perijove,Observation,Image Mid-Time (UTC),"SC Distance (Io, km)","SC Altitude (Io, km)","SC Latitude (Io IAU, deg)","SC W Longitude (Io IAU, deg)","Sub-Solar Latitude (Io IAU, deg)","Sub-Solar W Longitude (Io IAU, deg)",Phase Angle,JIRAM scale (m/pixel),JunoCAM scale (m/pixel),North Clock Angle,PS North Clock Angle', file = outputFile)
	
	for file in inputFiles:
		parseTuple = fileParse(file)
		
		# check to see if image is of Io
		targetName = parseTuple[3]
		if targetName == target:
			et = parseTuple[0]
			timstr = spiceypy.timout( et, xlsxmt )
			productID = parseTuple[1]
			orbit = parseTuple[2]
		
			# Compute the apparent state of Io as seen from JUNO in the IAU_IO frame.  
			# All of the ephemeris readers return states in units of kilometers and
			# kilometers per second.
			[state, ltime] = spiceypy.spkezr( target, et, tarfrm, abcorr, scname )

			# Compute the distance between the body centers in kilometers.
			dist = spiceypy.vnorm( state )

			# obtain cartesian coordinates for sub-spacecraft point at the time of closest approach
			[spoint, trgepc, srfvec] = spiceypy.subpnt( method, target, et, tarfrm, abcorr, scname )

			# convert cartesian coordinates of lat/lon
			[radius, lon, lat] = spiceypy.reclat( spoint )

			# convert longitude domain from -180-180 E longitude to 0-360 W longitude
			lon = lon * spiceypy.dpr()
			if lon <= 0.0:
				lon = math.fabs(lon)
			else:
				lon = 360.0 - lon
	
			  
			# compute altitude
			alt = spiceypy.vnorm( srfvec )

			# camera resolution
			jncamres = alt * 0.6727
			jiramres = alt * 0.237767

			[trgepc, srfvec, phase, incdnc, emissn, visibl, lit] = spiceypy.illumf(
						  method2, target, 'SUN', et, tarfrm, abcorr, scname, spoint )

			# calculating subsolar point
			[spoint_slr, trgepc_slr, srfvec_slr] = spiceypy.subslr( method, target, et, tarfrm, abcorr, scname )
			[radius_slr, lon_slr, lat_slr] = spiceypy.reclat( spoint_slr )
			lon_slr = lon_slr * spiceypy.dpr()
			if lon_slr <= 0.0:
				lon_slr = math.fabs(lon_slr)
			else:
				lon_slr = 360.0 - lon_slr

			# calculate angle separation between center of JIRAM FOV and Io center
			[jishape, jiframe, jibsight, jin, jivbounds] = spiceypy.getfov(jirmid, 25, 20, 4)

			# NORTH CLOCK ANGLE CALCULATION
			# Find position vector of Io center in JIRAM reference frame
			[pos,ltime] = spiceypy.spkpos(target, et, jrmfrm, abcorr, scname)

			sep = spiceypy.convrt(spiceypy.vsep(jibsight, pos), 'RADIANS', 'DEGREES')

			# Find position vector of Io north pole in JIRAM reference frame
			[pos_np,ltime_np] = spiceypy.spkpos('-501001', et, jrmfrm, abcorr, scname)

			# normalize angle to North pole so that the distance matches the distance to Io center
			# north pole position projected on to detector this way
			xangle = math.atan2(pos_np[0], pos_np[2])
			yangle = math.atan2(pos_np[1], pos_np[2])

			# calculate north pole projection distance
			[dim, radii] = spiceypy.bodvrd(target, 'RADII', 3)
			normznp = math.sqrt(pow(pos[2],2) + pow(radii[2],2))

			normxnp = math.tan(xangle) * normznp
			normynp = math.tan(yangle) * normznp

			# find difference between previous two vectors (Io center to Io North Pole vector 
			# in JIRAM reference frame. units in km)
			xsub = normxnp - pos[0]
			ysub = normynp - pos[1]

			# clock angle calculation (-180 to 180, clockwise. 0 degrees is up)
			raw_clock_angle = math.degrees(math.atan2(ysub, xsub))

			# north clock angle now in 0 to 360, clockwise, with 0 degrees up
			if raw_clock_angle < 0.0:
				northclockangle = 360 + raw_clock_angle
			else:
				northclockangle = raw_clock_angle

			# OUTPUT CSV LINE

			print(orbit + ',' + productID + ',' + timstr + ',' + '{:.3f}'.format(dist) + ',' + '{:.3f}'.format(alt) + ',' + '{:.3f}'.format(lat * spiceypy.dpr()) + ',' + '{:.3f}'.format(lon) + ',' + '{:.3f}'.format(lat_slr * spiceypy.dpr()) + ',' + '{:.3f}'.format(lon_slr) + ',' + '{:.3f}'.format(phase*spiceypy.dpr()) + ',' + '{:.3f}'.format(jiramres) + ',' + '{:.3f}'.format(jncamres) + ',' + '{:.3f}'.format(northclockangle) + ',' + '{:.3f}'.format(raw_clock_angle), file = outputFile)
else:
	print("No files entered")

spiceypy.unload( metakr )
spiceypy.unload( 'io_north_pole.bsp' )
