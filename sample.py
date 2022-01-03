from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy
from tkinter import filedialog as fd
import os, sys, re

inputDir = fd.askdirectory(title='Open directory')
numDir = len(inputDir)

files = os.listdir(inputDir)
files = sorted(files)
lblFiles = []

for file in files:
	if re.search('.LBL', file):
		lblFiles += [file]

for file in lblFiles:
	fullFile = inputDir + "/" + file
	print(fullFile)

