from __future__ import print_function
from builtins import input
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import spiceypy
import spiceypy.utils.support_types as stypes

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

#
# The adjustment value only applies to absolute extrema
# searches; simply give it an initial value of zero
# for this inequality search.
#
adjust = 0.0
    
spiceypy.furnsh( metakr )

step = 8000
# we are going to get positions between these two dates
utc = ['Jul 1, 2023', 'Jul 1, 2024']

# get et values one and two, we could vectorize str2et
etOne = spiceypy.str2et(utc[0])
etTwo = spiceypy.str2et(utc[1])
print("ET One: {}, ET Two: {}".format(etOne, etTwo))

# get times
times = [x*(etTwo-etOne)/step + etOne for x in range(step)]

# check first few times:
print(times[0:3])

#Run spkpos as a vectorized function
positions, lightTimes = spiceypy.spkpos(scname, times, 'J2000', 'NONE', 'JUPITER BARYCENTER')

# Positions is a 3xN vector of XYZ positions
print("Positions: ")
print(positions[0])

# Light times is a N vector of time
print("Light Times: ")
print(lightTimes[0])

# Clean up the kernels
spiceypy.kclear()

positions = positions.T # positions is shaped (4000, 3), let's transpose to (3, 4000) for easier indexing
fig = plt.figure(figsize=(9, 9))
ax  = fig.add_subplot(111, projection='3d')
ax.plot(positions[0], positions[1], positions[2])
plt.title('SpiceyPy Juno Position Example from Jul 1, 2023 to Jul 1, 2024')
plt.show()
