from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy
import matplotlib.pyplot as plt
import numpy as np
import csv
import pandas as pd

# initialize variables

metakr = '/Users/perry/Dropbox/Io/IVO/kernels/ivo_latest.tm'
sclkid = -150
scname = '-150'
target = 'IO'
tarfrm = 'IAU_IO'
abcorr = 'LT+S'
tdbfmt = 'YYYY MON DD HR:MN:SC.### TDB ::TDB'
xlsxmt = 'MM/DD/YYYY HR:MN:SC.###'
maxivl = 1000
maxwin = 2 * maxivl
relate = 'ABSMIN'
adjust = 0.0
method = 'Intercept/Ellipsoid'
method2 = 'ELLIPSOID'
stepsz = 1.0
step = 4800

file = '/Users/perry/Dropbox/Io/Juno/PJ27/PJ27_hotspots.csv'

csvarray = pd.read_csv(file, delimiter=',')
hotspots = [tuple(row) for row in csvarray.values]

latitude, longitude, value = zip(*hotspots)

# creates graph of the ground plots for all encounters
# load map as background image
img = plt.imread("Io_GalileoSSI-Voyager_Global_Mosaic_ClrMerge_2km_180W.jpg")

# initialize plot
fig, ax = plt.subplots()

# define area covered by map
ax.imshow(img, extent=[360, 0, -90, 90])

# sets color gradient to use in scatter plot
cmap = plt.get_cmap('inferno')

plt.scatter(longitude, latitude, c = value, s = 80, cmap = cmap)

# sets graph labels
ax.set_xlabel('Longitude (°W)')
ax.set_ylabel('Latitude')
ax.set_title(file)
ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], minor = False)
ax.set_yticks([-75, -45, -15, 15, 45, 75], minor = True)
ax.set_xticks([0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360], minor = False)
ax.set_xticks([15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345], minor = True)

#create color bar for phase angle
mappable = ax.collections[0]
cbar = plt.colorbar(mappable=mappable)

plt.show()