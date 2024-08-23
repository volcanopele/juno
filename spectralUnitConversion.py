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

# TBD

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

####################
### SCRIPT START ###
####################

# initialize spice files
spiceypy.furnsh( metakr )

# open file dialog. Select one or more label files as input.

# inputFile = fd.askopenfilename(title='Select Labels', filetypes=(('CSV files', '*.csv'), ('All files', '*.*')))
inputFile = "/Users/perry/Dropbox/Io/Juno/inputcsv.csv"
root = os.path.dirname(inputFile)
outputFile = root + "/hs_output.csv"
outputFile = open( outputFile, 'w' )
if len(inputFile) == 0:
	sys.exit()

utctim = input( 'Input UTC Observation Time: ' )
	
# Convert utctim to ET.
et = spiceypy.str2et( utctim )

hotspotArray = pd.read_csv(inputFile, header=None, dtype=float)

for i in range(0,len(hotspotArray.index)):
	if pd.isnull(hotspotArray[2][i]):
		radiance = ""
		ema = ""
		alt = ""
		inc = ""
		pha = ""
	else:
		latitude = hotspotArray[0][i] * spiceypy.rpd()
		longitude = 360 - hotspotArray[1][i]
		longitude = longitude * spiceypy.rpd()
		
		spoint = spiceypy.srfrec(targid, longitude, latitude)
	
		(trgepc, srfvec, phase, incdnc, emissn) = spiceypy.ilumin(method2, target, et, tarfrm, abcorr, scname, spoint)
		ema = emissn * spiceypy.dpr()
		# if ema > 90:
# 			ema = 88
# 			emissn = ema * spiceypy.rpd()
		inc = incdnc * spiceypy.dpr()
		pha = phase * spiceypy.dpr()
			
		alt = spiceypy.vnorm( srfvec )
		
		scale = alt * 0.237767
		
		radiance = hotspotArray[2][i]
		radiance /= 0.4975
		radiance = radiance * math.pi
		radiance = radiance * math.pow(scale, 2)
		radiance = radiance / math.cos(emissn)
		radiance = radiance / 1000000000
	
	print(str(hotspotArray[0][i]) + "," + str(hotspotArray[1][i]) + "," + str(radiance) + "," + str(ema) + "," + str(alt) + "," + str(inc) + "," + str(pha), file = outputFile)
		
outputFile.close()