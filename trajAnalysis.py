from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy

###
# run as python trajAnalysis.py
# everything set in the script
###

# initialize variables


metakr = '/Users/perry/Dropbox/Io/Juno/kernels/juno_latest.tm'
gm_pck = '/Users/perry/Dropbox/Io/Juno/kernels/pck/gm_de440.tpc'
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

# number of hours +/- a satellite flyby we should be wary about imaging
fwindw = 6

starttime = '07/05/2016 04:00:00.000'
endtime = '09/28/2028 23:59:59.000'

#
# The adjustment value only applies to absolute extrema
# searches; simply give it an initial value of zero
# for this inequality search.
#
adjust = 0.0

spiceypy.furnsh( metakr )
spiceypy.furnsh( gm_pck )
orbitCSV = open('Juno_Io_encounters.csv', 'w')

etstart = spiceypy.str2et( starttime )
etstop = spiceypy.str2et( endtime )

method = 'Intercept/Ellipsoid'
method2 = 'ELLIPSOID'
stepsz = 100.0

cnfine = stypes.SPICEDOUBLE_CELL(2)
spiceypy.wninsd( etstart, etstop, cnfine )

#
# In the call below, the maximum number of window
# intervals gfposc can store internally is set to MAXIVL.
# We set the cell size to MAXWIN to achieve this.
#
pjtimes = stypes.SPICEDOUBLE_CELL( maxwin )

# find all the perijoves in the window
spiceypy.gfdist( 'JUPITER', abcorr, scname, 'LOCMIN', 0, adjust, stepsz, maxivl, cnfine, pjtimes )

# csv setup
priortime = 0.0
orbit = 0
flyby = ""
timedif = 0.0
fwindw = fwindw * 60 * 60

# csv headers
print( "Orbit", "Perijove Time (UTC)", "Io C/A Time (UTC)", "SC Altitude (Io km)", "SC Latitude (Io IAU deg)", "SC W Longitude (Io IAU deg)", "Vinf (Io km/s)", "Phase Angle", "Magnetic Latitude of Io (Jupiter System III deg)", "E Longitude of Io (Jupiter System III deg)", "True Anomaly of Io (deg)", "Separation Angle", file = orbitCSV, sep=',' )

for pjtime in pjtimes:
	timedif = pjtime - priortime
	if timedif >= 40000.0:
		orbit += 1
		# improve our perijove time
		winstart = pjtime - 10800
		winend = pjtime + 10800
		cnfine = stypes.SPICEDOUBLE_CELL(2)
		spiceypy.wninsd( winstart, winend, cnfine )
		pjtim = stypes.SPICEDOUBLE_CELL( maxwin )
		spiceypy.gfdist( 'JUPITER', abcorr, scname, relate, 0, adjust, stepsz, maxivl, cnfine, pjtim )
		pjtimestr = spiceypy.timout( pjtim[0], xlsxmt )
		window = 86400
		winstart = pjtime - window
		winend = pjtime + window
		cnfine = stypes.SPICEDOUBLE_CELL(2)
		spiceypy.wninsd( winstart, winend, cnfine )
		catim = stypes.SPICEDOUBLE_CELL( maxwin )
		# find Io C/A time
		spiceypy.gfdist( target, abcorr, scname, relate, 0, adjust, stepsz, maxivl, cnfine, catim )
		# convert time to excel format time
		catimstr = spiceypy.timout( catim[0], xlsxmt )

		# obtain cartesian coordinates for sub-spacecraft point at the time of closest approach
		
		[spoint, trgepc, srfvec] = spiceypy.subpnt( method, target, catim[0], tarfrm, abcorr, scname )
		
		alt = spiceypy.vnorm(srfvec)
								
		# convert cartesian coordinates of lat/lon
		
		[radius, lon, lat] = spiceypy.reclat( spoint )
		[trgepc, srfvec, phase, solar, emissn, visibl, lit] = spiceypy.illumf(
							method2, target, 'SUN', catim[0], tarfrm, abcorr,
							scname, spoint )
							
		phase = phase * spiceypy.dpr()
		
		
		# calculate resolutions
		jirres = alt * 0.000237767
		jcmres = alt * 0.0006727
		
		# convert longitude domain from -180-180 E longitude to 0-360 W longitude
		lon = lon * spiceypy.dpr()
		if lon <= 0.0:
			lon = math.fabs(lon)
		else:
			lon = 360.0 - lon
			
		lat = lat * spiceypy.dpr()

		# calculate velocity of Juno WRT Io at C/A
		[state, ltime] = spiceypy.spkezr( target, catim[0], tarfrm, abcorr, scname )
		vvector = spiceypy.vpack( state[3], state[4], state[5] )
		velocity = spiceypy.vnorm ( vvector )
		
		# calculating angular separation between Juno_HGA and Io
		#
		# Or alternatively we can work in the antenna
		# frame directly.
		#
		[pos, ltime] = spiceypy.spkpos( target, catim[0], 'JUNO_HGA', abcorr, scname )
		
		#
		# The antenna boresight is the Z-axis in the
		# JUNO_HGA frame.
		#
		bsight = [ 0.0, 0.0, 1.0 ]
		
		#
		# Lastly compute the angular separation.
		#
		sep =  spiceypy.convrt( spiceypy.vsep(bsight, pos), 'RADIANS', 'DEGREES' )
		if sep <= 90.0:
			sep = 90.0 - sep
		else:
			sep = sep - 90
		
		# calculating Jupiter System III position
		[jpoint, trgepc, srfvec2] = spiceypy.subpnt( method, "599", catim[0], "JUNO_MAG_VIP4", abcorr, "501" )
		[radius, jlon, jlat] = spiceypy.reclat( jpoint )
		[jpoint, trgepc, srfvec2] = spiceypy.subpnt( method, "599", catim[0], "IAU_JUPITER", abcorr, "501" )
		[radius, jlon, jlat2] = spiceypy.reclat( jpoint )
		
		jlon = jlon * spiceypy.dpr()
		if jlon <= 0.0:
			jlon = math.fabs(jlon)
		else:
			jlon = 360.0 - jlon
		
		jlon = 360.0 - jlon
		
		jlat = jlat * spiceypy.dpr()
		tabchar = "\t"
		
		# calculate true anomaly
		[state, ltime] = spiceypy.spkezr( target, catim[0], "J2000", "NONE", "JUPITER" )
		[dim, mu] = spiceypy.bodvrd("JUPITER", "GM", 1)
		elts = spiceypy.oscltx(state, catim[0], mu[0])
		trueanomaly = elts[8] * spiceypy.dpr()
		
		# print to csv
		print( orbit, pjtimestr, catimstr, '{:0.3f}'.format(alt), '{:0.3f}'.format(lat), '{:0.3f}'.format(lon), '{:0.3f}'.format(velocity), '{:0.3f}'.format(phase), '{:0.3f}'.format(jlat), '{:0.3f}'.format(jlon), '{:0.3f}'.format(trueanomaly), '{:0.3f}'.format(sep), file = orbitCSV, sep=',' )
		
		priortime = pjtime


spiceypy.unload( metakr )
spiceypy.unload( gm_pck )
