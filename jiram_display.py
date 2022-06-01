from __future__ import print_function
from builtins import input
import math
import spiceypy
from tkinter import filedialog as fd
import tkinter as tk
import os, sys, getopt
import numpy as np
import matplotlib.pyplot as plt

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

inputFile = fd.askopenfilename(title='Select Labels', filetypes=(('PDS Labels', '*.LBL'), ('All files', '*.*')))
label = open(inputFile)
datafile = label.readlines()
for line in datafile:
	if 'PRODUCT_ID ' in line:
		if line.startswith('PRODUCT_ID ', 0):
			productID = line
			productIDs = productID.split(" ")
			productIDs = sorted(productIDs, reverse=True)
			productID = productIDs[1]
	if 'STANDARD_DATA_PRODUCT_ID' in line:
		dataType = line
		dataTypes = dataType.split(" ")
		dataTypes = sorted(dataTypes, reverse=True)
		dataType = dataTypes[2]
		dataType = dataType.split('"')[1]

label.close()

if dataType == 'IMAGE':
	root = os.path.dirname(inputFile)
	name = os.path.basename(inputFile)
	imgFile = root + '/' + productID + '.IMG'

	img = np.fromfile(imgFile, dtype='float32')

	img_shape_2band = np.array([256,432])
	img = img.reshape(*img_shape_2band)
	img = np.flip(img,1)
elif dataType == 'SPECTRAL':
	root = os.path.dirname(inputFile)
	name = os.path.basename(inputFile)
	imgFile = root + '/' + productID + '.DAT'

	img = np.fromfile(imgFile, dtype='float32')

	spec_shape = np.array([256,336])
	img = img.reshape(*spec_shape)
	img = np.rot90(img,3)

plt.figure()
plt.imshow(img, interpolation='none', cmap='gist_heat')
plt.show()