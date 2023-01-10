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

file = '/Users/perry/Dropbox/Io/Juno/max_brightness.csv'

csvarray = pd.read_csv(file, delimiter=',')
hotspots = [tuple(row) for row in csvarray.values]

latitude, longitude, value = zip(*hotspots)

perijove = csvarray.columns.values
perijove = perijove[2]

sizevalues = np.multiply(value, 100)
sizevalues = np.add(sizevalues, 10)

longitude2 = [x*spiceypy.rpd() for x in longitude]
print(longitude[200])
print(longitude2[200])
# creates graph of the ground plots for all encounters

maxlon = 360*spiceypy.rpd()
# initialize plot
fig = plt.figure()
ax = fig.add_subplot(projection='polar')

ax.set_rlim(-90,0)
ax.set_theta_direction(1)
ax.set_theta_zero_location(loc = "N")
# define area covered by map
# ax.imshow(img, extent=[360, 0, 0, 90])


# sets color gradient to use in scatter plot
cmap = plt.get_cmap('inferno')

plt.scatter(longitude2, latitude, c = value, s = 200, cmap = cmap, edgecolor='black', norm=matplotlib.colors.LogNorm(vmax=70.0, vmin=0.02), alpha=0.9)
# plt.scatter(longitude, latitude, c = value, s = sizevalues, cmap = cmap, edgecolor='black', norm=matplotlib.colors.LogNorm(), alpha=0.8)
# plt.scatter(longitude, latitude, c = value, s = 100, cmap = cmap, edgecolor='black', norm=matplotlib.colors.LogNorm(), alpha=0.8)

# sets graph labels
# ax.set_xlabel('Longitude (°W)', fontsize='xx-large')
# ax.set_ylabel('Latitude', fontsize='xx-large')
ax.set_title('Southern Hemisphere')
fig.suptitle('Io Hotspots seen by Juno - ' + '2017 – 2022 (Maximum Unsaturated Brightness)', fontsize=30)
# ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], minor = False)
# ax.set_yticks([-75, -45, -15, 15, 45, 75], minor = True)
ax.set_rgrids(radii = [-30, -60], labels = ['30°S', '60°S'], angle = 0)
ax.set_xticks([0*spiceypy.rpd(), 30*spiceypy.rpd(), 60*spiceypy.rpd(), 90*spiceypy.rpd(), 120*spiceypy.rpd(), 150*spiceypy.rpd(), 180*spiceypy.rpd(), 210*spiceypy.rpd(), 240*spiceypy.rpd(), 270*spiceypy.rpd(), 300*spiceypy.rpd(), 330*spiceypy.rpd()], minor = False)
# ax.set_xticks([15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345], minor = True)
# plt.yticks(fontsize='x-large')
plt.xticks(fontsize='x-large')


#create color bar for phase angle
mappable = ax.collections[0]
cbar = plt.colorbar(mappable=mappable)
cbar.ax.tick_params(labelsize='x-large')
cbar.set_label('Surface Radiance (GW/µm)', labelpad=+1, fontsize='xx-large')

plt.show()