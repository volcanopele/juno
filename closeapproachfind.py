from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy

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


#
# The adjustment value only applies to absolute extrema
# searches; simply give it an initial value of zero
# for this inequality search.
#
adjust = 0.0
    
spiceypy.furnsh( metakr )

sourceFile = open('test.txt', 'w')
utcstarttime = input( 'Input UTC Start Time: ' )
utcendtime = input( 'Input UTC End Time: ' )
etstart = spiceypy.str2et( utcstarttime )
etend = spiceypy.str2et( utcendtime )


method = 'Intercept/Ellipsoid'
method2 = 'ELLIPSOID'
stepsz = 100.0

print( '\n{:s}\n'.format(
	   'Inputs for target visibility search:' ), file = sourceFile  )

print( '   Target                       = '
	   '{:s}'.format( target ), file = sourceFile  )
print( '   Spacecraft                   = '
	   '{:s}'.format( scname  ), file = sourceFile  )
print( '   Target\'s reference frame     = '
	   '{:s}'.format( tarfrm ), file = sourceFile  )
print( '   Aberration correction        = '
	   '{:s}'.format( abcorr ), file = sourceFile )
print( '   Step size (seconds)          = '
	   '{:f}'.format( stepsz ), file = sourceFile  )

btmstr = spiceypy.timout( etstart, tdbfmt )
print( '   Start time                   = '
	   '{:s}'.format(btmstr), file = sourceFile )
	   
etmstr = spiceypy.timout( etend, tdbfmt )
print( '   Stop time                    = '
	   '{:s}'.format(etmstr), file = sourceFile )

print( ' ', file = sourceFile )


#
# Initialize the "confinement" window with the interval
# over which we'll conduct the search.
#
cnfine = stypes.SPICEDOUBLE_CELL(2)
spiceypy.wninsd( etstart, etend, cnfine )

#
# In the call below, the maximum number of window
# intervals gfposc can store internally is set to MAXIVL.
# We set the cell size to MAXWIN to achieve this.
#
catim = stypes.SPICEDOUBLE_CELL( maxwin )

# search for the C/A time within user provided window

spiceypy.gfdist( target, abcorr, scname, relate, 0, adjust, stepsz, maxivl, cnfine, catim )

# convert time to excel format time
catimstr = spiceypy.timout( catim[0], xlsxmt )

# obtain cartesian coordinates for sub-spacecraft point at the time of closest approach

[spoint, trgepc, srfvec] = spiceypy.subpnt( method, target, catim[0], tarfrm, abcorr, scname )
						
# convert cartesian coordinates of lat/lon

[radius, lon, lat] = spiceypy.reclat( spoint )
[trgepc, srfvec, phase, solar, emissn, visibl, lit] = spiceypy.illumf(
					method2, target, 'SUN', catim[0], tarfrm, abcorr,
					scname, spoint )

# convert longitude domain from -180-180 E longitude to 0-360 W longitude
lon = lon * spiceypy.dpr()
if lon <= 0.0:
	lon = math.fabs(lon)
else:
	lon = 360.0 - lon
	
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

	
# print information about c/a to file: C/A time, distance, sub-spacecraft lat/lon, 
# and phase angle

print( '{0:s}\'s distance to {1:s} for this time period is: '.format( scname,
					 target ), file = sourceFile )
print( '   {:s}\n'.format( catimstr ), file = sourceFile )
print( '     ALT = {:16.3f}'.format(spiceypy.vnorm(srfvec)), file = sourceFile )
print( '     LAT = {:16.3f}'.format(lat * spiceypy.dpr() ), file = sourceFile )
print( '     LON = {:16.3f}'.format( lon ), file = sourceFile    )			   
print( '     VEL = {:16.3f}'.format( velocity ), file = sourceFile    )	
print( '     PHA = {:16.3f}'.format( phase*spiceypy.dpr() ), file = sourceFile )
print( '     OBA = {:16.3f}'.format( sep ), file = sourceFile )
print( ' ', file = sourceFile )


# calculate observation windows for Io


obswin = stypes.SPICEDOUBLE_CELL( maxwin )

spiceypy.gfposc( scname, 'JUNO_HGA', abcorr, target, 'RECTANGULAR', 'Z', '=', 90.0, 0.0,
				 stepsz, maxivl, cnfine, obswin )

# spiceypy.gftfov( jrmfrm, target, 'POINT', tarfrm,
# 				 abcorr, scname, stepsz, cnfine, obswin )

winsiz = spiceypy.wncard( obswin )

if winsiz == 0:
	print( 'No events were found.', file = sourceFile )
else:
	#
	# Display the visibility time periods.
	#
	print( 'Visibility times of {0:s} '
		   'as seen from {1:s}:\n'.format(
			target, jrmfrm ), file = sourceFile )
	for i in range(winsiz):
	     [intbeg, intend] = spiceypy.wnfetd( obswin, i )
	     timstr = spiceypy.timout( intbeg, xlsxmt )
	     print( 'Observation center time:          '
              '  {:s}'.format( timstr ), file = sourceFile  )
	     # calculate distance to center of Io and JunoCAM and JIRAM resolution
	     [state, ltime] = spiceypy.spkezr( target, intbeg, tarfrm, abcorr, scname )
	     dist = spiceypy.vnorm( state )
	     jiramres = dist * 0.000237767
	     jncamres = dist * 0.00061425
	     
	     # calculate sub-S/C point and altitude
	     [spoint, trgepc, srfvec] = spiceypy.subpnt( method, target, intbeg,
              tarfrm, abcorr, scname )
	     [radius, lon, lat] = spiceypy.reclat( spoint )
	     [trgepc, srfvec, phase, solar, emissn, visibl, lit] = spiceypy.illumf(
              method2, target, 'SUN', intbeg, tarfrm, abcorr, scname, spoint )
	     
	     # convert longitude domain from -180-180 E longitude to 0-360 W longitude
	     lon = lon * spiceypy.dpr()
	     if lon <= 0.0:
              lon = math.fabs(lon)
	     else:
              lon = 360.0 - lon
	     
	     print( '     ALT = {:16.3f}'.format(spiceypy.vnorm(srfvec)), file = sourceFile )
	     print( '     LAT = {:16.3f}'.format(lat * spiceypy.dpr() ), file = sourceFile )
	     print( '     LON = {:16.3f}'.format( lon ), file = sourceFile    )			   
	     print( '     PHA = {:16.3f}'.format( phase*spiceypy.dpr() ), file = sourceFile )   
	     print( '     JIRAM res = {:10.3f}'.format( jiramres ), file = sourceFile )
	     print( '     JunoCAM res = {:8.3f}'.format( jncamres ), file = sourceFile )
	     print( ' ', file = sourceFile )

spiceypy.unload( metakr )
