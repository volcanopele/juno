# juno
Python and Shell scripts for my Juno work

## description of scripts in this repository

### junopositiontrack.py
Generates CSV files with geometric information every 0.5 seconds for each of Juno's close encounters with Io, including PJs 55, 57, 58, and 60

### closeapproachfind.py
Provides geometry information about the close approach point to Io for period ±8 hours from the time given with user input. Script will also find the center time for JIRAM observation opportunities in that time period

### junogeometryinfo.py
generates geometry information for the middle image of a given set of JIRAM label files. Also creates a shell script to be used in ISIS to create a base map

### jiramgeometrycsv.py
Similar to junogeometryinfo.py but instead of providing information for one time, this script generates a CSV file with geometry information for all the selected images

### jiramgeombackplane.py
Generates geometry and illumination backplanes for JIRAM images. Also generates ISIS cube files containing the JIRAM image and those backplanes as separate bands

### jiram_display.py
Interactive display of JIRAM images in python (supports imager and spectrometer data)
