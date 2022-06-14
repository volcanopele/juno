from __future__ import print_function
from builtins import input
import math
import spiceypy
from tkinter import filedialog as fd
import tkinter as tk
import os, sys, getopt
import numpy as np
import kalasiris as isis

#######################
###### VARIABLES ######
#######################

# edit metakr to point to your Juno metakernel
metakr = '/Users/perry/Dropbox/Io/Juno/kernels/juno_latest.tm'
sclkid = -61
scname = 'JUNO'
target = 'IO'
tarfrm = 'IAU_IO'
abcorr = 'LT+S'
jirmid = -61410
jrmfrm = 'JUNO_JIRAM_I'
lbandfrm = -61411
lbndnm = 'JUNO_JIRAM_I_LBAND'
mbandfrm = -61412
mbndnm = 'JUNO_JIRAM_I_MBAND'
specfrm = -61420
specnm = 'JUNO_JIRAM_S'

# various parameters for the script
method = 'Intercept/Ellipsoid'
method2 = 'ELLIPSOID'
tdbfmt = 'YYYY MON DD HR:MN:SC.### TDB ::TDB'
xlsxmt = 'MM/DD/YYYY HR:MN:SC.###'
datefmt = 'YYYY-MM-DD'
timefmt = 'HR:MN:SC.###'


#################
#### TESTING ####
#################

# initialize spice files
spiceypy.furnsh( metakr )

encounters = []
encounters.append(('I1', '07/18/2035 03:26:49.371'))
encounters.append(('I2', '11/20/2035 17:57:07.271'))
encounters.append(('I3', '01/21/2036 16:00:22.124'))
encounters.append(('I4', '04/10/2036 06:34:50.993'))
encounters.append(('I5', '06/09/2036 10:07:20.979'))
encounters.append(('I6', '09/18/2036 06:08:57.277'))
encounters.append(('I7', '11/13/2036 20:50:00.418'))
encounters.append(('I8', '12/28/2036 02:19:31.769'))
encounters.append(('I9', '02/22/2037 17:01:42.541'))
encounters.append(('I10', '06/10/2037 14:55:48.067'))
encounters.append(('I11', '08/16/2037 20:18:34.150'))
encounters.append(('I12', '10/08/2037 22:02:55.126'))
encounters.append(('I13', '12/18/2037 16:23:04.858'))
encounters.append(('I14', '02/11/2038 12:37:21.839'))
encounters.append(('I15', '05/23/2038 08:51:55.522'))
encounters.append(('I16', '08/18/2038 01:25:21.280'))
encounters.append(('I17', '11/10/2038 23:27:50.806'))
encounters.append(('I18', '01/13/2039 15:57:38.356'))
encounters.append(('I19', '02/26/2039 21:25:10.736'))
encounters.append(('I20', '04/28/2039 01:01:35.621'))

spkbounds = []
spkbounds.append(('2035 JUL 18 01:27:58.555', '2035 JUL 18 05:27:58.555'))
spkbounds.append(('2035 NOV 20 15:58:16.454', '2035 NOV 20 19:58:16.454'))
spkbounds.append(('2036 JAN 21 14:01:31.309', '2036 JAN 21 18:01:31.309'))
spkbounds.append(('2036 APR 10 04:36:01.123', '2036 APR 10 08:36:04.843'))
spkbounds.append(('2036 JUN 09 08:08:30.164', '2036 JUN 09 12:08:30.164'))
spkbounds.append(('2036 SEP 18 04:10:05.483', '2036 SEP 18 08:10:05.483'))
spkbounds.append(('2036 NOV 13 18:51:09.600', '2036 NOV 13 22:51:09.600'))
spkbounds.append(('2036 DEC 28 00:20:40.952', '2036 DEC 28 04:20:40.952'))
spkbounds.append(('2037 FEB 22 15:02:51.727', '2037 FEB 22 19:02:51.727'))
spkbounds.append(('2037 JUN 10 12:56:57.252', '2037 JUN 10 16:56:57.252'))
spkbounds.append(('2037 AUG 16 18:19:43.333', '2037 AUG 16 22:19:43.333'))
spkbounds.append(('2037 OCT 08 20:04:04.308', '2037 OCT 09 00:04:04.308'))
spkbounds.append(('2037 DEC 18 14:24:14.041', '2037 DEC 18 18:24:14.041'))
spkbounds.append(('2038 FEB 11 10:38:31.024', '2038 FEB 11 14:38:31.024'))
spkbounds.append(('2038 MAY 23 06:53:04.707', '2038 MAY 23 10:53:04.707'))
spkbounds.append(('2038 AUG 17 23:26:30.463', '2038 AUG 18 03:26:30.463'))
spkbounds.append(('2038 NOV 10 21:28:59.989', '2038 NOV 11 01:28:59.989'))
spkbounds.append(('2039 JAN 13 13:58:47.540', '2039 JAN 13 17:58:47.540'))
spkbounds.append(('2039 FEB 26 19:26:19.921', '2039 FEB 26 23:26:19.921'))
spkbounds.append(('2039 APR 27 23:02:44.807', '2039 APR 28 03:02:44.807'))

for i in range(0,19):
	encounters[i] = encounters[i] + spkbounds[i]
	print(encounters[i])
	
print(encounters[12])

for encounter in encounters:
	print(encounter)

spiceypy.unload( metakr )

