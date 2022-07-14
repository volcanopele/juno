# juno
Python and Shell scripts for my Juno work. Most of these are called independently, but some do dovetail into each other (for example, the reprojected map file generated in junogeometryinfo.py can be used in jiramReprojection.py to reproject the original JIRAM image.

## Dependencies
These scripts require the following to be installed on the system running these scripts:
### Anaconda
### ISIS - https://github.com/USGS-Astrogeology/ISIS3
### in the ISIS conda environment, also install the kalasiris and matplotlib python packages

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

### jiramReprojection.py
Using an ISIS level 3 cube, reprojects JIRAM images. This is useful for summing images.
