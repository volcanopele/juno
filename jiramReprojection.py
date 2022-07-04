from __future__ import print_function
from builtins import input
import math
import spiceypy
from tkinter import filedialog as fd
import tkinter as tk
import os, sys, getopt
import numpy as np
import kalasiris as isis


####################
###### README ######
####################

# to be completed

###################################
###### LICENSE AND COPYRIGHT ######
###################################

# Copyright (C) 2022 Arizona Board of Regents on behalf of the Planetary
# Image Research Laboratory, Lunar and Planetary Laboratory at the
# University of Arizona.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

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

###########################
### INITALIZE FUNCTIONS ###
###########################

####################
### SCRIPT START ###
####################

# initialize spice files
spiceypy.furnsh( metakr )

#############################
######## SCRIPT END #########
#############################
spiceypy.unload( metakr )

