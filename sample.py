from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy
from tkinter import filedialog as fd
import os, sys, re

# inputDir = fd.askdirectory(title='Open directory')
inputFiles = fd.askopenfilenames(title='Select Labels', filetypes=(('PDS Labels', '*.LBL'), ('All files', '*.*')))
numFiles = len(inputFiles)

if numDir > 0:
	useLabel = True
	# if an odd number of labels are selected, the middle label is used for calculations
	# by this script. Otherwise, else will select the middle two labels. The observation
	# mid-time will be the average of the two individual image mid-times. This time is
	# used by most of the script to calculate geometric values except for north clock
	# angle, which will use the first of the two middle labels. Product ID also uses this 
	# label.
	if numDir & 1 == 1:
		file = numDir / 2
		file = int(file)
		parseTuple = fileParse(inputDir[file])
		et1 = parseTuple[0]
		et = et1
		timstr = spiceypy.timout( et, xlsxmt )
		productID = parseTuple[1]
		orbit = parseTuple[2]
	else:
		file = numDir / 2
		file = int(file)
		parseTuple = fileParse(inputDir[file])
		et2 = parseTuple[0]
		file = file - 1
		parseTuple = fileParse(inputDir[file])
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


files = os.listdir(inputDir)
files = sorted(files)
lblFiles = []

for file in files:
	if re.search('.LBL', file):
		lblFiles += [file]

if re.search('\\', inputDir):
	slash = '\\'
else:
	slash = '/'

for file in lblFiles:
	fullFile = inputDir + slash + file
	print(fullFile)

