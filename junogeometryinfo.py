from __future__ import print_function
from builtins import input
import math
import spiceypy.utils.support_types as stypes
import spiceypy

###
# This script takes a time in UTC as input from the user
# It outputs geometry information for Juno WRT Io at that time
# Outputting test.txt
###

# initialize variables

metakr = '/Users/perry/Dropbox/Io/Juno/kernels/juno_latest.tm'
sclkid = -61
scname = 'JUNO'
target = 'JUPITER'
tarfrm = 'IAU_JUPITER'
abcorr = 'LT+S'
jrmfrm = 'JUNO_JIRAM_I'
jirmid = -61410


# various parameters for the script
adjust = 0.0
method = 'Intercept/Ellipsoid'
method2 = 'ELLIPSOID'
maxivl = 1000
maxwin = 2 * maxivl
relate = 'ABSMIN'
tdbfmt = 'YYYY MON DD HR:MN:SC.### TDB ::TDB'
xlsxmt = 'MM/DD/YYYY HR:MN:SC.###'
    
spiceypy.furnsh( metakr )

# initialize text file output
sourceFile = open( 'test.txt', 'w' )

# ask user to input observation time
utctim = input( 'Input UTC Observation Time: ' )

# Convert utctim to ET.
et = spiceypy.str2et( utctim )

# back to excel format
timstr = spiceypy.timout( et, xlsxmt )

# Compute the apparent state of Io as seen from JUNO in the IAU_IO frame.  
# All of the ephemeris readers return states in units of kilometers and
# kilometers per second.
[state, ltime] = spiceypy.spkezr( target, et, tarfrm, abcorr, scname )

# Compute the distance between the body centers in kilometers.
dist = spiceypy.vnorm( state )

# obtain cartesian coordinates for sub-spacecraft point at the time of closest approach
[spoint, trgepc, srfvec] = spiceypy.subpnt( method, target, et, tarfrm, abcorr, scname )

# convert cartesian coordinates of lat/lon
[radius, lon, lat] = spiceypy.reclat( spoint )

# convert longitude domain from -180-180 E longitude to 0-360 W longitude
lon = lon * spiceypy.dpr()
if lon <= 0.0:
	lon = math.fabs(lon)
else:
	lon = 360.0 - lon
	
              
# compute altitude
alt = spiceypy.vnorm( srfvec )

# camera resolution
jncamres = alt * 0.6727
jiramres = alt * 0.237767

[trgepc, srfvec, phase, incdnc, emissn, visibl, lit] = spiceypy.illumf(
              method2, target, 'SUN', et, tarfrm, abcorr, scname, spoint )

# calculating subsolar point
[spoint_slr, trgepc_slr, srfvec_slr] = spiceypy.subslr( method, target, et, tarfrm, abcorr, scname )
[radius_slr, lon_slr, lat_slr] = spiceypy.reclat( spoint_slr )
lon_slr = lon_slr * spiceypy.dpr()
if lon_slr <= 0.0:
	lon_slr = math.fabs(lon_slr)
else:
	lon_slr = 360.0 - lon_slr
	
tabchar = "\t"

print( 'Observation center time: {:s}'.format( timstr ), file = sourceFile )
print( '     ALT = {:16.3f}'.format( alt ), file = sourceFile )
print( '     DIST = {:16.3f}'.format( dist ), file = sourceFile )
print( '     LAT = {:16.3f}'.format(lat * spiceypy.dpr() ), file = sourceFile )
print( '     LON = {:16.3f}'.format( lon ), file = sourceFile )
print( '     Sub-Solar LAT = {:1.3f}'.format(lat_slr * spiceypy.dpr() ), file = sourceFile )
print( '     Sub-Solar LON = {:1.3f}'.format( lon_slr ), file = sourceFile )
print( '     PHA = {:16.3f}'.format( phase*spiceypy.dpr() ), file = sourceFile )   
print( '     JIRAM res = {:10.3f}'.format( jiramres ), file = sourceFile )
print( '     JunoCAM res = {:8.3f}'.format( jncamres ), file = sourceFile )
print( ' ', file = sourceFile )
print(timstr, tabchar, tabchar, tabchar, '{:0.3f}'.format(lat * spiceypy.dpr()), tabchar, '{:0.3f}'.format(lon), tabchar, '{:0.3f}'.format(dist), tabchar, '{:0.3f}'.format(alt), tabchar, '{:0.3f}'.format(phase*spiceypy.dpr()), tabchar, '{:0.3f}'.format(jiramres), tabchar, '{:0.3f}'.format(jncamres), file = sourceFile)


spiceypy.unload( metakr )