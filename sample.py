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

