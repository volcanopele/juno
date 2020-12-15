from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy
import matplotlib.pyplot as plt
import numpy as np

# initialize variables

metakr = '/Applications/Cosmographia/JUNO/kernels/juno_latest.tm'
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
step = 2400

spiceypy.furnsh( metakr )

encounters = []
encounters.append(('PJ57', '12/30/2023 08:36:24.233'))
encounters.append(('PJ58', '02/03/2024 17:49:07.575'))

latplot = []
lonplot = []
phaseplot = []
altplot = []

for encounter in encounters:
	perijove = encounter[0]
	file_name = perijove + '.csv'
	sourceFile = open(file_name, 'w')
	utc = encounter[1]

	et = spiceypy.str2et(utc)

	# get et values one and two, we could vectorize str2et
	etOne = et - 600
	etTwo = et + 600

	print("ET One: {}, ET Two: {}".format(etOne, etTwo))

	times = [x*(etTwo-etOne)/step + etOne for x in range(step)]

	print(times[0:3])

	print( 'Perijove', 'Time (UTC)', 'SC Range to Io (km)', 'SC Altitude (km)', 'SC Latitude (deg)', 'SC W Longitude (deg)', 'Subsolar Latitude (deg)', 'Subsolar W Longitude (deg)', 'Sun-Io-SC Angle (deg)', 'JIRAM scale (km/pixel)', 'JunoCAM scale (km/pixel)', sep=',', file = sourceFile)

	for time in times:
		timstr = spiceypy.timout( time, xlsxmt )
	
		# calculate sub-S/C point and altitude
		[spoint, trgepc, srfvec] = spiceypy.subpnt( method, target, time, tarfrm, abcorr, scname )
		[radius, lon, lat] = spiceypy.reclat( spoint )
		[trgepc, srfvec, phase, solar, emissn, visibl, lit] = spiceypy.illumf(method2, target, 'SUN', time, tarfrm, abcorr, scname, spoint )
	
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
	
		latplot.append(lat)
		lonplot.append(lon)
		
	
		# calculating subsolar point
		[spoint_slr, trgepc_slr, srfvec_slr] = spiceypy.subslr( method, target, time, tarfrm, abcorr, scname )
		[radius_slr, lon_slr, lat_slr] = spiceypy.reclat( spoint_slr )
		lon_slr = lon_slr * spiceypy.dpr()
		if lon_slr <= 0.0:
			lon_slr = math.fabs(lon_slr)
		else:
			lon_slr = 360.0 - lon_slr
	
		print( '{:s}'.format(perijove), '{:s}'.format(timstr), '{:0.4f}'.format(dist), '{:0.4f}'.format(alt), '{:0.4f}'.format(lat), '{:0.4f}'.format(lon), '{:0.4f}'.format(lat_slr * spiceypy.dpr()), '{:0.4f}'.format(lon_slr), '{:0.4f}'.format(phase), '{:0.4f}'.format(jiramres), '{:0.4f}'.format(jncamres), sep=',', file = sourceFile)
		
		# add phase angle to plot
		phaseplot.append(phase)
		
		altplot.append(alt)

# creates graph of the ground plots for all encounters
# load map as background image
img = plt.imread("Io_GalileoSSI-Voyager_Global_Mosaic_ClrMerge_2km_180W.jpg")

# initialize plot
fig, ax = plt.subplots()

# define area covered by map
ax.imshow(img, extent=[360, 0, -90, 90])

# sets color gradient to use in scatter plot
cmap = plt.get_cmap('gnuplot_r')

sizevalues = [((17000-i)/12000)**13 for i in altplot]

# creates scatter plot with the longitude on the x-axis, latitude as the y-axis, and uses the phase angle 
# to define the color
plt.scatter(lonplot, latplot, c = phaseplot, s = sizevalues, cmap = cmap, vmin=0, vmax=180)

# sets graph labels
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title(scname + ' Groundtracks')
cbar = plt.colorbar()
cbar.set_label('Phase Angle', labelpad=+1)

# creates grid
# ax.grid(True)

# shows plot
plt.show()

spiceypy.unload( metakr )
