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

####################
### SCRIPT START ###
####################

# initialize spice files
spiceypy.furnsh( metakr )

# open file dialog. Select one or more label files as input.

inputFile = fd.askopenfilename(title='Select Image', filetypes=(('ISIS cubes', '*.cub'), ('All files', '*.*')))
numFiles = len(inputFile)
utctim = input( 'Input UTC Observation Time: ' )

if numFiles == 0:
	sys.exit()


et = spiceypy.str2et( utctim )

	
# setup output files
# first generate the file names for each parameter CSV file
root = os.path.dirname(inputFile)
name = os.path.basename(inputFile)
productID = os.path.basename(inputFile).split('.')[0]
fileBase = root + '/' + productID
fileName = fileBase + '.cub'
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
	
# obtain cartesian coordinates for sub-spacecraft point at the time of closest approach
[spoint, trgepc, subsrfvec] = spiceypy.subpnt( method, target, et, tarfrm, abcorr, scname )

[shape, frame, bsight, nbounds, bounds] = spiceypy.getfov(srufrm, 20)

#possible source of error
dy = np.abs((bounds[0,2]-bounds[1,2]) / 512)
dx = np.abs((bounds[0,1]-bounds[3,1]) / 512)

# generate numpy arrays of radian pixel locations for both the X and Y directions
xp = np.arange(0.5,511.51,1)*dx + bounds[1,1]
yp = bounds[3,2] - np.arange(0.5,511.51,1)*dy
zp = bounds[0,0]

# get center lat and lon
# print(bsight)
# dvec = [bsight[1],bsight[2],bsight[0]]
# [spoint, trgepc, srfvec, found] = spiceypy.sincpt(method2, target, et, tarfrm, abcorr, scname, frame, dvec)
# print(lon * spiceypy.dpr())
# print(lat * spiceypy.dpr())

for i in range(0,512):
	# initialize each line so as to clear the previous line
	latitudeLine = ""
	longitudeLine = ""
	altitudeLine = ""
	emissionLine = ""
	phaseLine = ""
	incidenceLine = ""
	for j in range(0,512):
		# vector for pixel in radians
		dvec=[zp,xp[i],yp[j]]
		# print(dvec)
		# ensures the script won't break on pixels that don't intersect Io
		with spiceypy.no_found_check():
			[spoint, trgepc, srfvec, found] = spiceypy.sincpt(method2, target, et, tarfrm, abcorr, scname, frame, dvec)
			if found:
				[lon, lat, alti] = spiceypy.recpgr(target, spoint, radii[0], (radii[0]-radii[2])/radii[0])
				lon = lon * spiceypy.dpr()
				lat = lat * spiceypy.dpr()
				alt = spiceypy.vnorm( srfvec )
				[trgepc, srfvec, phase, solar, emissn] = spiceypy.ilumin(method2, target, et, tarfrm, abcorr, scname, spoint)
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

latitudeFile.close()
longitudeFile.close()
altitudeFile.close()
emissionFile.close()
phaseFile.close()
incidenceFile.close()

##################################
######## CUBE GENERATION #########
##################################

# generate cubes files for each backplane using the backplanecubegen function
latitudeCube = fileBase + '.' + 'latitude' + '.cub'
longitudeCube = fileBase + '.' + 'longitude' + '.cub'
altitudeCube = fileBase + '.' + 'altitude' + '.cub'
emissionCube = fileBase + '.' + 'emission' + '.cub'
incidenceCube = fileBase + '.' + 'incidence' + '.cub'
phaseCube = fileBase + '.' + 'phase' + '.cub'

latitudeFile = fileBase + '_latitude.csv'
longitudeFile = fileBase + '_longitude.csv'
altitudeFile = fileBase + '_altitude.csv'
emissionFile = fileBase + '_emission.csv'
incidenceFile = fileBase + '_incidence.csv'
phaseFile = fileBase + '_phase.csv'

isis.ascii2isis(from_=latitudeFile, to_=latitudeCube, order_="bsq", samples_=512, lines_=512, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
isis.ascii2isis(from_=longitudeFile, to_=longitudeCube, order_="bsq", samples_=512, lines_=512, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
isis.ascii2isis(from_=altitudeFile, to_=altitudeCube, order_="bsq", samples_=512, lines_=512, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
isis.ascii2isis(from_=emissionFile, to_=emissionCube, order_="bsq", samples_=512, lines_=512, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
isis.ascii2isis(from_=incidenceFile, to_=incidenceCube, order_="bsq", samples_=512, lines_=512, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)
isis.ascii2isis(from_=phaseFile, to_=phaseCube, order_="bsq", samples_=512, lines_=512, bands_=1, skip_=0, setnullrange_="true", nullmin_=-2000, nullmax_=-1000)

# create merged product
fromlist_path = isis.fromlist.make([fileName, latitudeCube, longitudeCube, altitudeCube, phaseCube, incidenceCube, emissionCube])
geomCub = fileBase + '.geom.cub'
isis.cubeit(fromlist=fromlist_path, to_=geomCub, proplab_=fileName)

# clean up extraneous cube files
os.system(str("/bin/rm " + latitudeCube))
os.system(str("/bin/rm " + longitudeCube))
os.system(str("/bin/rm " + altitudeCube))
os.system(str("/bin/rm " + emissionCube))
os.system(str("/bin/rm " + incidenceCube))
os.system(str("/bin/rm " + phaseCube))


#############################
######## SCRIPT END #########
#############################
spiceypy.unload( metakr )

