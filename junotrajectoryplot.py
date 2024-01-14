from __future__ import print_function
from builtins import input
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import spiceypy
import spiceypy.utils.support_types as stypes
import PIL

# this script plots the orbits of Juno between two dates

metakr = '/Users/perry/Dropbox/Io/Juno/kernels/juno_latest.tm'
sclkid = -61
scname = 'JUNO'
target = 'IO'
tarfrm = 'IAU_IO'
abcorr = 'LT+S'
tdbfmt = 'YYYY MON DD HR:MN:SC.### TDB ::TDB'
xlsxmt = 'MM/DD/YYYY HR:MN:SC.###'
maxivl = 1000
maxwin = 2 * maxivl
relate = 'ABSMIN'
jrmfrm = 'JUNO_JIRAM_I'
jirmid = -61410
method = 'Intercept/Ellipsoid'
iobasemap = 'Io_GalileoSSI-Voyager_Global_Mosaic_ClrMerge_2km_180W.jpg'

#
# The adjustment value only applies to absolute extrema
# searches; simply give it an initial value of zero
# for this inequality search.
#
adjust = 0.0
    
spiceypy.furnsh( metakr )

step = 8000
# we are going to get positions between these two dates
utc = ['12/30/2023 08:31:00.869', '12/30/2023 08:41:00.869']

# get et values one and two, we could vectorize str2et
etOne = spiceypy.str2et(utc[0])
etTwo = spiceypy.str2et(utc[1])
print("ET One: {}, ET Two: {}".format(etOne, etTwo))

# get times
times = [x*(etTwo-etOne)/step + etOne for x in range(step)]

# check first few times:
print(times[0:3])

#Run spkpos as a vectorized function
positions, lightTimes = spiceypy.spkpos(scname, times, 'J2000', 'NONE', target)

# altplot = []
# for time in times:
# 	[spoint, trgepc, srfvec] = spiceypy.subpnt( method, target, time, tarfrm, abcorr, scname )
# 	alt = spiceypy.vnorm(srfvec)
# 	altplot.append(alt)
	
# Positions is a 3xN vector of XYZ positions
print("Positions: ")
print(positions[0])

# Light times is a N vector of time
print("Light Times: ")
print(lightTimes[0])

# Clean up the kernels
spiceypy.kclear()

# load bluemarble with PIL
# bm = PIL.Image.open(iobasemap)
# it's big, so I'll rescale it, convert to array, and divide by 256 to get RGB values that matplotlib accept 
# bm = np.array(bm.resize((2048,1024)))/256.

theta = np.linspace(0, 2.*np.pi, 100)
phi = np.linspace(0, np.pi, 100)

# Convert to Cartesian coordinates
x = 1830. * np.outer(np.cos(theta), np.sin(phi))
y = 1818.7 * np.outer(np.sin(theta), np.sin(phi))
z = 1815.3 * np.outer(np.ones(np.size(theta)), np.cos(phi))


positions = positions.T # positions is shaped (4000, 3), let's transpose to (3, 4000) for easier indexing
fig = plt.figure(figsize=(9, 9))
ax  = fig.add_subplot(111, projection='3d')
# Adjust aspect ratio
ax.set_box_aspect([1,1,1])

ax.set_xlim(-20000, 20000)
ax.set_ylim(-20000, 20000)
ax.set_zlim(-20000, 20000)
ax.plot(positions[0], positions[1], positions[2])
ax.plot_surface(x, y, z,  rstride=4, cstride=4, color='y')
# ax.plot_surface(x, y, z, facecolors = bm)
plt.title('Juno trajectory during PJ57 +/- 5 minutes')
plt.show()
