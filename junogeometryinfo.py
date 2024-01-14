from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy
from tkinter import filedialog as fd
import kalasiris as isis

###
# This script takes a time in UTC as input (either directly or via JIRAM 
# label file(s)) from the user
# It outputs geometry information for Juno WRT Io at that time
# Outputting test.txt with geometric information in human readable, 
# tab-delimited, and comma-delimited formats.
# Also outputs Juno_JIRAM_script2.sh, a shell script to be run in ISIS to 
# create basemaps
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
		if 'START_TIME' in line:
			startTime = line
			startTimes = startTime.split(" ")
			startTimes = sorted(startTimes, reverse=True)
			startTime = startTimes[2]
			if startTime[0] == '"':
				startTime = startTime[1:24]
		elif 'STOP_TIME' in line:
			stopTime = line
			stopTimes = stopTime.split(" ")
			stopTimes = sorted(stopTimes, reverse=True)
			stopTime = stopTimes[2]
			if stopTime[0] == '"':
				stopTime = stopTime[1:24]
		elif 'PRODUCT_ID ' in line:
			if line.startswith('PRODUCT_ID ', 0):
				productID = line
				productIDs = productID.split(" ")
				productIDs = sorted(productIDs, reverse=True)
				productID = productIDs[1]
				if productID == '=':
					productID = productIDs[2]
					productID = productID[1:26]
		elif 'ORBIT_NUMBER' in line:
			orbit = line
			orbits = orbit.split(" ")
			orbits = sorted(orbits, reverse=True)
			orbit = orbits[2]
			orbit = orbit[:2]
	# debug
	# print(startTime)
	# print(productID)
	# print(orbit)
	
	# start and stop time converted to seconds past J2000
	etStart = spiceypy.str2et(startTime)
	etStop = spiceypy.str2et(stopTime)
	# Image mid-time calculated
	et = (etStart+etStop)/2
	orbit = "PJ%s"%(orbit)
	
	# close file
	file.close()
	
	# tuple with image mid-time, product ID, and orbit output by function
	return [et, productID, orbit]
	
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
	useLabel = True
	# if an odd number of labels are selected, the middle label is used for calculations
	# by this script. Otherwise, else will select the middle two labels. The observation
	# mid-time will be the average of the two individual image mid-times. This time is
	# used by most of the script to calculate geometric values except for north clock
	# angle, which will use the first of the two middle labels. Product ID also uses this 
	# label.
	if numFiles & 1 == 1:
		file = numFiles / 2
		file = int(file)
		parseTuple = fileParse(inputFiles[file])
		et1 = parseTuple[0]
		et = et1
		timstr = spiceypy.timout( et, xlsxmt )
		productID = parseTuple[1]
		orbit = parseTuple[2]
	else:
		file = numFiles / 2
		file = int(file)
		parseTuple = fileParse(inputFiles[file])
		et2 = parseTuple[0]
		file = file - 1
		parseTuple = fileParse(inputFiles[file])
		et1 = parseTuple[0]
		et = (et1+et2)/2
		timstr = spiceypy.timout( et, xlsxmt )
		productID = parseTuple[1]
		orbit = parseTuple[2]
else:
	# ask user to input observation time
	utctim = input( 'Input UTC Observation Time: ' )
	
	# Convert utctim to ET.
	et = spiceypy.str2et( utctim )
	et1 = et
	
	# back to excel format
	timstr = spiceypy.timout( et, xlsxmt )

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
[pos,ltime] = spiceypy.spkpos(target, et1, jrmfrm, abcorr, scname)

sep = spiceypy.convrt(spiceypy.vsep(jibsight, pos), 'RADIANS', 'DEGREES')

# Find position vector of Io north pole in JIRAM reference frame
[pos_np,ltime_np] = spiceypy.spkpos('-501001', et1, jrmfrm, abcorr, scname)

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

# OUTPUT TEXT FILE

# initialize text file output
outputFile = open( 'test.txt', 'w' )

# Human readable portion
if useLabel:
	print( 'PRODUCT_ID               = {:s}'.format( productID ), file = outputFile )
	print( 'ORBIT                    = {:s}'.format( orbit ), file = outputFile )
print( 'OBSERVATION MID-TIME     = {:s}'.format( timstr ), file = outputFile )
print( 'DISTANCE                 = {:1.3f}'.format( dist ), file = outputFile )
print( 'ALTITUDE                 = {:1.3f}'.format( alt ), file = outputFile )
print( 'LATITUDE                 = {:1.3f}'.format(lat * spiceypy.dpr() ), file = outputFile )
print( 'LONGITUDE                = {:1.3f}'.format( lon ), file = outputFile )
print( 'SUB-SOLAR LATITUDE       = {:1.3f}'.format(lat_slr * spiceypy.dpr() ), file = outputFile )
print( 'SUB-SOLAR LONGITUDE      = {:1.3f}'.format( lon_slr ), file = outputFile )
print( 'PHASE_ANGLE              = {:1.3f}'.format( phase*spiceypy.dpr() ), file = outputFile )   
print( 'JIRAM PIXEL SCALE        = {:1.3f}'.format( jiramres ), file = outputFile )
print( 'JUNOCAM PIXEL SCALE      = {:1.3f}'.format( jncamres ), file = outputFile )
print( 'JIRAM ANGULAR SEPERATION = {:1.3f}'.format( sep ), file = outputFile )
print( 'NORTH CLOCK ANGLE        = {:1.3f}'.format( northclockangle ), file = outputFile )
print( 'PS NORTH CLOCK ANGLE     = {:1.3f}'.format( raw_clock_angle ), file = outputFile )
if useLabel:
	print( 'FRAMES                   = {:d}'.format( numFiles ), file = outputFile )
print( ' ', file = outputFile )

# tab-delimited format
if useLabel:
	print('Perijove\tObservation\tImage Mid-Time (UTC)\tNumber of Frames\tSC Distance (Io, km)\tSC Altitude (Io, km)\tSC Latitude (Io IAU, deg)\tSC W Longitude (Io IAU, deg)\tSub-Solar Latitude (Io IAU, deg)\tSub-Solar W Longitude (Io IAU, deg)\tPhase Angle\tJIRAM scale (m/pixel)\tJunoCAM scale (m/pixel)\tNorth Clock Angle\tPS North Clock Angle', file = outputFile)
	print(orbit + '\t' + productID + '\t' + timstr + '\t' + '{:d}'.format(numFiles) + '\t' + '{:.7f}'.format(dist) + '\t' + '{:.7f}'.format(alt) + '\t' + '{:.7f}'.format(lat * spiceypy.dpr()) + '\t' + '{:.7f}'.format(lon) + '\t' + '{:.7f}'.format(lat_slr * spiceypy.dpr()) + '\t' + '{:.7f}'.format(lon_slr) + '\t' + '{:.7f}'.format(phase*spiceypy.dpr()) + '\t' + '{:.7f}'.format(jiramres) + '\t' + '{:.7f}'.format(jncamres) + '\t' + '{:.7f}'.format(northclockangle) + '\t' + '{:.7f}'.format(raw_clock_angle), file = outputFile)
else:
	print('Image Mid-Time (UTC)\t\tSC Distance (Io, km)\tSC Altitude (Io, km)\tSC Latitude (Io IAU, deg)\tSC W Longitude (Io IAU, deg)\tSub-Solar Latitude (Io IAU, deg)\tSub-Solar W Longitude (Io IAU, deg)\tPhase Angle\tJIRAM scale (m/pixel)\tJunoCAM scale (m/pixel)\tNorth Clock Angle\tPS North Clock Angle', file = outputFile)
	print(timstr + '\t' + '{:.7f}'.format(dist) + '\t' + '{:.7f}'.format(alt) + '\t' + '{:.7f}'.format(lat * spiceypy.dpr()) + '\t' + '{:.7f}'.format(lon) + '\t' + '{:.7f}'.format(lat_slr * spiceypy.dpr()) + '\t' + '{:.7f}'.format(lon_slr) + '\t' + '{:.7f}'.format(phase*spiceypy.dpr()) + '\t' + '{:.7f}'.format(jiramres) + '\t' + '{:.7f}'.format(jncamres) + '\t' + '{:.7f}'.format(northclockangle) + '\t' + '{:.7f}'.format(raw_clock_angle), file = outputFile)

print( '', file = outputFile )

# comma-delimited format
if useLabel:
	print('Perijove,Observation,Image Mid-Time (UTC),Number of Frames,"SC Distance (Io, km)","SC Altitude (Io, km)","SC Latitude (Io IAU, deg)","SC W Longitude (Io IAU, deg)","Sub-Solar Latitude (Io IAU, deg)","Sub-Solar W Longitude (Io IAU, deg)",Phase Angle,JIRAM scale (m/pixel),JunoCAM scale (m/pixel),North Clock Angle,PS North Clock Angle', file = outputFile)
	print(orbit + ',' + productID + ',' + timstr + ',' + '{:d}'.format(numFiles) + ',' + '{:.7f}'.format(dist) + ',' + '{:.7f}'.format(alt) + ',' + '{:.7f}'.format(lat * spiceypy.dpr()) + ',' + '{:.7f}'.format(lon) + ',' + '{:.7f}'.format(lat_slr * spiceypy.dpr()) + ',' + '{:.7f}'.format(lon_slr) + ',' + '{:.7f}'.format(phase*spiceypy.dpr()) + ',' + '{:.7f}'.format(jiramres) + ',' + '{:.7f}'.format(jncamres) + ',' + '{:.7f}'.format(northclockangle) + ',' + '{:.7f}'.format(raw_clock_angle), file = outputFile)
else:
	print('Image Mid-Time (UTC),Number of Frames,"SC Distance (Io, km)","SC Altitude (Io, km)","SC Latitude (Io IAU, deg)","SC W Longitude (Io IAU, deg)","Sub-Solar Latitude (Io IAU, deg)","Sub-Solar W Longitude (Io IAU, deg)",Phase Angle,JIRAM scale (m/pixel),JunoCAM scale (m/pixel),North Clock Angle,PS North Clock Angle', file = outputFile)
	print(timstr + ',' + '{:.7f}'.format(dist) + ',' + '{:.7f}'.format(alt) + ',' + '{:.7f}'.format(lat * spiceypy.dpr()) + ',' + '{:.7f}'.format(lon) + ',' + '{:.7f}'.format(lat_slr * spiceypy.dpr()) + ',' + '{:.7f}'.format(lon_slr) + ',' + '{:.7f}'.format(phase*spiceypy.dpr()) + ',' + '{:.7f}'.format(jiramres) + ',' + '{:.7f}'.format(jncamres) + ',' + '{:.7f}'.format(northclockangle) + ',' + '{:.7f}'.format(raw_clock_angle), file = outputFile)

# OUTPUT ISIS script file

if useLabel:
	isisFile = open( 'Juno_JIRAM_script2.sh', 'w')
	print('#!/bin/bash', file = isisFile)
	print( '', file = isisFile)
	print('PERIJOVE="' + orbit + '"', file = isisFile)
	print('IMAGE_NAME="' + productID + '"', file = isisFile)
	print('DIRECTORY="/Users/perry/Dropbox/Io/Juno/$PERIJOVE/$IMAGE_NAME"', file = isisFile)
	print('BASEMAP="/Users/perry/Dropbox/Io/Io_GalileoSSI-Voyager_Global_Mosaic_1km.cub"', file = isisFile)
	print('CLAT="' + '{:.3f}'.format(lat * spiceypy.dpr()) + '"', file = isisFile)
	print('CLON="' + '{:.3f}'.format(lon) + '"', file = isisFile)
	print('RES="' + '{:.3f}'.format(jiramres) + '"', file = isisFile)
	print('RES=$(echo "${RES}/20" | bc -l)', file = isisFile)
	print('DISTANCE="' + '{:.3f}'.format(alt) + '"', file = isisFile)
	print('ROTATION="' + '{:.3f}'.format(northclockangle) + '"', file = isisFile)
	print( '', file = isisFile)
	print('mkdir $DIRECTORY', file = isisFile)
	print('cd $DIRECTORY', file = isisFile)
	print('maptemplate map=$IMAGE_NAME.map targopt=user targetname=Io clat=$CLAT clon=$CLON dist=$DISTANCE londir=POSITIVEWEST projection=POINTPERSPECTIVE resopt=MPP resolution=$RES rngopt=user minlat=-90 maxlat=90 minlon=0 maxlon=360', file = isisFile)
	print('map2map from=$BASEMAP to=$IMAGE_NAME.map.cub map=$IMAGE_NAME.map pixres=map defaultrange=map', file = isisFile)
	print('rotate from=$IMAGE_NAME.map.cub to=$IMAGE_NAME.rotate.cub degrees=$ROTATION', file = isisFile)
	print('isis2std from=$IMAGE_NAME.rotate.cub to=$IMAGE_NAME.map.tif format=tiff bittype=U16BIT stretch=manual minimum=0 maximum=1', file = isisFile)
	isis.maptemplate(map_='jncammap.map', targopt_="user", targetname_=target, clat_=format(lat * spiceypy.dpr()), clon_=lon, dist_=alt, londir_="POSITIVEWEST", projection_="POINTPERSPECTIVE", resopt_="MPP", resolution_=jncamres, rngopt_="user", minlat_=-90, maxlat_=90, minlon_=0, maxlon_=360)
	solarres = jncamres / 5
	isis.maptemplate(map_='solarmap.map', targopt_="user", targetname_=target, clat_=format(lat_slr * spiceypy.dpr()), clon_=lon_slr, londir_="POSITIVEWEST", projection_="ORTHOGRAPHIC", resopt_="MPP", resolution_=solarres, rngopt_="user", minlat_=-90, maxlat_=90, minlon_=0, maxlon_=360)
	
isis.maptemplate(map_='jncammap.map', targopt_="user", targetname_=target, clat_=format(lat * spiceypy.dpr()), clon_=lon, dist_=alt, londir_="POSITIVEWEST", projection_="POINTPERSPECTIVE", resopt_="MPP", resolution_=jncamres, rngopt_="user", minlat_=-90, maxlat_=90, minlon_=0, maxlon_=360)
spiceypy.unload( metakr )
spiceypy.unload( 'io_north_pole.bsp' )


