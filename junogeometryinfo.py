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
target = 'IO'
tarfrm = 'IAU_IO'
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
spiceypy.furnsh( 'io_north_pole.bsp')

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

# calculate angle separation between center of JIRAM FOV and Io center
[jishape, jiframe, jibsight, jin, jivbounds] = spiceypy.getfov(jirmid, 25, 20, 4)

# NORTH CLOCK ANGLE CALCULATION
# Find position vector of Io center in JIRAM reference frame
[pos,ltime] = spiceypy.spkpos(target, et, jrmfrm, abcorr, scname)

sep = spiceypy.convrt(spiceypy.vsep(jibsight, pos), 'RADIANS', 'DEGREES')

# Find position vector of Io north pole in JIRAM reference frame
[pos_np,ltime_np] = spiceypy.spkpos('-501001', et, jrmfrm, abcorr, scname)

# normalize angle to North pole so that the distance matches the distance to Io center
# north pole position projected on to detector this way
xangle = math.atan2(pos_np[0], pos_np[2])
yangle = math.atan2(pos_np[1], pos_np[2])

# calculate north pole projection distance
[dim, radii] = spiceypy.bodvrd(target, 'RADII', 3)
normznp = math.sqrt(pow(pos[2],2) + pow(radii[2],2))

normxnp = math.tan(xangle) * normznp
normynp = math.tan(yangle) * normznp

# find difference between previous two vectors (Io center to Io North Pole vector 
# in JIRAM reference frame. units in km)
xsub = normxnp - pos[0]
ysub = normynp - pos[1]

# clock angle calculation (-180 to 180, clockwise. 0 degrees is up)
raw_clock_angle = math.degrees(math.atan2(ysub, xsub))

# north clock angle now in 0 to 360, clockwise, with 0 degrees up
if raw_clock_angle < 0.0:
	northclockangle = 360 + raw_clock_angle
else:
	northclockangle = raw_clock_angle

# OUTPUT TEXT FILE

print( 'Observation center time: {:s}'.format( timstr ), file = sourceFile )
print( '     ALT = {:16.3f}'.format( alt ), file = sourceFile )
print( '     DIST = {:16.3f}'.format( dist ), file = sourceFile )
print( '     LAT = {:16.3f}'.format(lat * spiceypy.dpr() ), file = sourceFile )
print( '     LON = {:16.3f}'.format( lon ), file = sourceFile )
print( '     Sub-Solar LAT = {:1.3f}'.format(lat_slr * spiceypy.dpr() ), file = sourceFile )
print( '     Sub-Solar LON = {:1.3f}'.format( lon_slr ), file = sourceFile )
print( '     PHA = {:16.3f}'.format( phase*spiceypy.dpr() ), file = sourceFile )   
print( '     JIRAM res = {:20.3f}'.format( jiramres ), file = sourceFile )
print( '     JunoCAM res = {:20.3f}'.format( jncamres ), file = sourceFile )
print( '     JIRAM angular seperation = {:1.3f}'.format( sep ), file = sourceFile )
print( '     North Clock Angle = {:14.3f}'.format( northclockangle ), file = sourceFile )
print( '     PS North Clock Angle = {:11.3f}'.format( raw_clock_angle ), file = sourceFile )
print( ' ', file = sourceFile )
print(timstr, tabchar, '{:0.3f}'.format(dist), tabchar, '{:0.3f}'.format(alt), tabchar, '{:0.3f}'.format(lat * spiceypy.dpr()), tabchar, '{:0.3f}'.format(lon), tabchar, '{:0.3f}'.format(lat_slr * spiceypy.dpr()), tabchar, '{:0.3f}'.format( lon_slr ), tabchar, '{:0.3f}'.format(phase*spiceypy.dpr()), tabchar, '{:0.3f}'.format(jiramres), tabchar, '{:0.3f}'.format(jncamres), tabchar, '{:0.3f}'.format(northclockangle), tabchar, '{:0.3f}'.format(raw_clock_angle), file = sourceFile)


spiceypy.unload( metakr )
spiceypy.unload( 'io_north_pole.bsp' )