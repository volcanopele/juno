from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy
import matplotlib.pyplot as plt
import matplotlib
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
backgd = "Io_GalileoSSI-Voyager_Global_Mosaic_2km_180W.jpg"
backgd = "New_Io_photomosaic_2km_grey.jpg"
backgd = "/Users/perry/Dropbox/Io/Juno/publications/Paper5_Menagerie2/map/PJ60_coverage_map.jpg"

file = '/Users/perry/Dropbox/Io/Juno/max_brightness.csv'

csvarray = pd.read_csv(file, delimiter=',')
hotspots = [tuple(row) for row in csvarray.values]

latitude, longitude, value = zip(*hotspots)

perijove = csvarray.columns.values
perijove = perijove[2]

sizevalues = np.multiply(value, 100)
sizevalues = np.add(sizevalues, 10)

# creates graph of the ground plots for all encounters
# load map as background image
img = plt.imread(backgd)


# initialize plot
fig, ax = plt.subplots()
fig.set_size_inches(30,15)

# define area covered by map
ax.imshow(img, extent=[360, 0, -90, 90])

# sets color gradient to use in scatter plot
cmap = plt.get_cmap('inferno')

plt.scatter(longitude, latitude, c = value, s = 200, cmap = cmap, edgecolor='black', norm=matplotlib.colors.LogNorm(vmax=70.0, vmin=0.02), alpha=0.9)
# plt.scatter(longitude, latitude, c = value, s = sizevalues, cmap = cmap, edgecolor='black', norm=matplotlib.colors.LogNorm(), alpha=0.8)
# plt.scatter(longitude, latitude, c = value, s = 100, cmap = cmap, edgecolor='black', norm=matplotlib.colors.LogNorm(), alpha=0.8)

# sets graph labels
ax.set_xlabel('Longitude (°W)', fontsize=17)
ax.set_ylabel('Latitude', fontsize=17)
# ax.set_title('Io Hotspots seen by Juno - ' + perijove, fontsize=20, pad=10)
ax.set_title(perijove, fontsize=20, pad=10)
# ax.set_title('Io Hotspots seen by Juno - ' + '2017 – 2024 (Maximum Unsaturated Brightness)', fontsize=30, pad=20)
ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], minor = False)
ax.set_yticks([-75, -45, -15, 15, 45, 75], minor = True)
ax.set_xticks([0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360], minor = False)
ax.set_xticks([15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345], minor = True)
plt.yticks(fontsize=13)
plt.xticks(fontsize=13)


#create color bar for phase angle
mappable = ax.collections[0]
# cbar = plt.colorbar(mappable=mappable, shrink=0.75)
cbar = plt.colorbar(mappable=mappable)
cbar.ax.tick_params(labelsize=20)
cbar.set_label('M-band spectral radiance, GW/µm', labelpad=+3, fontsize=25)


plt.savefig('io_hotspots.png',dpi=150, format='png')

plt.show()