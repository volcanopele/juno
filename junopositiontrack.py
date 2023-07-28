from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy
import matplotlib.pyplot as plt
import numpy as np

############
# This script produces CSV files for each Juno encounter with Io
# with information about Juno's position WRT Io every half second
# with viewing geometry information for Io
# script also produces a map of Io showing the ground track of each encounter
# with color dependent on phase angle, and width depending on altitude
# This script takes no input from the user
############

# initialize variables

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
adjust = 0.0
method = 'Intercept/Ellipsoid'
method2 = 'ELLIPSOID'
stepsz = 1.0
step = 4800
iobasemap = 'Io_GalileoSSI-Voyager_Global_Mosaic_ClrMerge_2km_180W.jpg'

spiceypy.furnsh( metakr )

encounters = []
encounters.append(('PJ53', '07/31/2023 04:57:16.869'))
encounters.append(('PJ55', '10/15/2023 06:47:21.331'))
encounters.append(('PJ57', '12/30/2023 08:36:00.681'))
encounters.append(('PJ58', '02/03/2024 17:48:35.743'))
encounters.append(('PJ60', '04/09/2024 04:58:03.679'))

latplot = []
lonplot = []
phaseplot = []
altplot = []
altmathplot = []
calatplot = []
calonplot = []
caphaseplot = []
caaltplot = []
perijoveplot = []

for encounter in encounters:
	perijove = encounter[0]
	file_name = perijove + '.csv'
	sourceFile = open(file_name, 'w')
	utc = encounter[1]

	et = spiceypy.str2et(utc)

	# get et values one and two, we could vectorize str2et
	etOne = et - 1200
	etTwo = et + 1200

	print("ET One: {}, ET Two: {}".format(etOne, etTwo))

	times = [x*(etTwo-etOne)/step + etOne for x in range(step)]

	print(times[0:3])

	print( 'Perijove', 'Time (UTC)', 'SC Range to Io (km)', 'SC Altitude (km)', 'SC Latitude (deg)', 'SC W Longitude (deg)', 'Subsolar Latitude (deg)', 'Subsolar W Longitude (deg)', 'Sun-Io-SC Angle (deg)', 'JIRAM scale (km/pixel)', 'JunoCAM scale (km/pixel)', sep=',', file = sourceFile)

	for time in times:
		timstr = spiceypy.timout( time, xlsxmt )
	
		# calculate sub-S/C point and altitude
		[spoint, trgepc, srfvec] = spiceypy.subpnt( method, target, time, tarfrm, abcorr, scname )
		[radius, lon, lat] = spiceypy.reclat( spoint )
		[trgepc, srfvec, phase, incdnc, emissn, visibl, lit] = spiceypy.illumf(method2, target, 'SUN', time, tarfrm, abcorr, scname, spoint )
	
		# calculate distance to center of Io, altitude, and JunoCAM and JIRAM resolution
		[state, ltime] = spiceypy.spkezr( target, time, tarfrm, abcorr, scname )
		dist = spiceypy.vnorm( state )
		alt = spiceypy.vnorm(srfvec)
		jiramres = alt * 0.000237767
		jncamres = alt * 0.0006727
	
		# convert longitude domain from -180-180 E longitude to 0-360 W longitude
		lon = lon * spiceypy.dpr()
		if lon <= 0.0:
			lon = math.fabs(lon)
		else:
			lon = 360.0 - lon
		
		lat = lat * spiceypy.dpr()
		phase = phase * spiceypy.dpr()	
	
		# calculating subsolar point
		[spoint_slr, trgepc_slr, srfvec_slr] = spiceypy.subslr( method, target, time, tarfrm, abcorr, scname )
		[radius_slr, lon_slr, lat_slr] = spiceypy.reclat( spoint_slr )
		lon_slr = lon_slr * spiceypy.dpr()
		if lon_slr <= 0.0:
			lon_slr = math.fabs(lon_slr)
		else:
			lon_slr = 360.0 - lon_slr
	
		print( '{:s}'.format(perijove), '{:s}'.format(timstr), '{:0.4f}'.format(dist), '{:0.4f}'.format(alt), '{:0.4f}'.format(lat), '{:0.4f}'.format(lon), '{:0.4f}'.format(lat_slr * spiceypy.dpr()), '{:0.4f}'.format(lon_slr), '{:0.4f}'.format(phase), '{:0.4f}'.format(jiramres), '{:0.4f}'.format(jncamres), sep=',', file = sourceFile)
		
		# add points to plot if alitude is less than 20000 km
		if alt <= 30000:
			latplot.append(lat)
			lonplot.append(lon)
			phaseplot.append(phase)
			altplot.append(alt)
			altmath = 30000 - alt
			altmath = altmath / 4000
			altmath = math.exp(altmath)
			altmath = altmath + 0.1
			altmathplot.append(altmath)

	# find geometry information for the C/A point and add that to arrays for that Info
	# for the plot
	
	[spoint, trgepc, srfvec] = spiceypy.subpnt( method, target, et, tarfrm, abcorr, scname )
	[radius, lon, lat] = spiceypy.reclat( spoint )
	[trgepc, srfvec, phase, incdnc, emissn, visibl, lit] = spiceypy.illumf(method2, target, 'SUN', et, tarfrm, abcorr, scname, spoint )
	alt = spiceypy.vnorm(srfvec)
	lon = lon * spiceypy.dpr()
	if lon <= 0.0:
		lon = math.fabs(lon)
	else:
		lon = 360.0 - lon
	
	lat = lat * spiceypy.dpr()
	phase = phase * spiceypy.dpr()
	lat = round(lat, 1)
	lon = round(lon, 1)
	phase = round(phase, 1)
	alt = round(alt, 1)
	calatplot.append(lat)
	calonplot.append(lon)
	caphaseplot.append(phase)
	caaltplot.append(alt)
	perijoveplot.append(perijove)


# creates graph of the ground plots for all encounters
# load map as background image
img = plt.imread(iobasemap)

# initialize plot
fig, ax = plt.subplots()

# define area covered by map
ax.imshow(img, extent=[360, 0, -90, 90])

# sets color gradient to use in scatter plot
cmap = plt.get_cmap('gnuplot_r')

# creates scatter plot with the longitude on the x-axis, latitude as the y-axis, and uses the phase angle 
# to define the color
plt.scatter(lonplot, latplot, c = phaseplot, s = 10, cmap = cmap, vmin=0, vmax=180)

# adds points to plot for the c/a points for each encounter
plt.scatter(calonplot, calatplot, c = 'w', s = 5)

# create close approach point labels
# could do this as a for loop, but need to adjust text alignment for each one
ax.text(calonplot[0], calatplot[0], perijoveplot[0] + '\n' + str(caaltplot[0]) + ' km\n' + str(caphaseplot[0]) + '° phase', verticalalignment='top', horizontalalignment='right', fontweight = 'bold', c = 'w')
ax.text(calonplot[1], calatplot[1], perijoveplot[1] + '\n' + str(caaltplot[1]) + ' km\n' + str(caphaseplot[1]) + '° phase', verticalalignment='bottom', horizontalalignment='left', fontweight = 'bold', c = 'w')
ax.text(calonplot[2], calatplot[2], perijoveplot[2] + '\n' + str(caaltplot[2]) + ' km\n' + str(caphaseplot[2]) + '° phase', horizontalalignment='right', fontweight = 'bold', c = 'w')
ax.text(calonplot[3], calatplot[3], perijoveplot[3] + '\n' + str(caaltplot[3]) + ' km\n' + str(caphaseplot[3]) + '° phase', horizontalalignment='right', fontweight = 'bold', c = 'w')
ax.text(calonplot[4], calatplot[4], perijoveplot[4] + '\n' + str(caaltplot[4]) + ' km\n' + str(caphaseplot[4]) + '° phase', horizontalalignment='right', fontweight = 'bold', c = 'w')

# sets graph labels and axis markers
ax.set_xlabel('Longitude (°W)')
ax.set_ylabel('Latitude')
ax.set_title(scname + ' Groundtracks')
ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], minor = False)
ax.set_yticks([-75, -45, -15, 15, 45, 75], minor = True)
ax.set_xticks([0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360], minor = False)
ax.set_xticks([15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345], minor = True)

#create color bar for phase angle
mappable = ax.collections[0]
cbar = plt.colorbar(mappable=mappable)
cbar.set_label('Phase Angle', labelpad=+1)

# creates grid
# ax.grid(True)

# shows plot
plt.show()

spiceypy.unload( metakr )
