from __future__ import print_function
from builtins import input
import math
import os, sys, getopt

# script for processing the hotspot database
# usage
# sample command
# python hotspot_DB_process.py -i /Users/perry/Dropbox/Io/Juno/Hotspot_table_JIRAM_table.csv -o /Users/perry/Dropbox/Io/Juno/test/db_processing/test.csv -e 70

# i is the input CSV file
# o is the output CSV file
# e is the emission angle limit (defaults to 90 to use all detections)

########################
### ARGUMENT PARSING ###
########################

infile = ''
outfile = ''
emissionLimit = 90
argv = sys.argv[1:]

try:
	opts, args = getopt.getopt(argv, 'i:o:e:', ['infile', 'outfile', 'emission'])
	for opt, arg in opts:
		if opt in ("-i", "--infile"):
			inputCSV = arg
		if opt in ("-o", "--outfile"):
			outputCSV = arg
		if opt in ("-e", "--emission"):
			emissionLimit = float(arg)
		
except getopt.GetoptError:
	print('jiramReprojection.py -i <infile> -o <outfile> -e <emission>')
	sys.exit(2)

####################
### SCRIPT START ###
####################

outputFile = open( outputCSV, 'w' )
inputFile = open(inputCSV)

hotspotNums = 267
datafile = inputFile.readlines()

# array setup
radiance = []
nosatradiance = []

print("Source, Source Name, Source Latitude, Source Longitude, Maximum, Max unsat, average unsat, Minmum unsat", file = outputFile)

for i in range(1,hotspotNums):
	hotspotID = "JRM"+ f'{i:03}'
	radiance = []
	nosatradiance = []
	note = ""
	name = ""
	latitude = ""
	longitude = ""
	maxnosatradiance = ""
	maxradiance = ""
	avg = ""
	minradiance = ""
	sum = 0
	for line in datafile:
		if hotspotID in line:
			lines = line.split(",")
			emi = float(lines[18])
			specRad = float(lines[15])
			saturation = lines[13]
			name = str(lines[4])
			latitude = str(lines[5])
			longitude = str(lines[6])
			if emi < emissionLimit:
				radiance.append(specRad)
				if saturation == "No":
					nosatradiance.append(specRad)
	radiance.sort(reverse=True)
	nosatradiance.sort(reverse=True)
	# check to see if the full list of radiances at < 80 degrees emission is not empty
	if len(radiance) > 0:
		maxradiance = str(radiance[0])
		# let's get no sat statistics, check to see if it has more than 2
		# can run average without max and min
		if len(nosatradiance) > 2:
			maxnosatradiance = str(nosatradiance[0])
			minradiance = str(nosatradiance[-1])
			nosatradiance.pop(0)
			nosatradiance.pop(-1)
			for ele in nosatradiance:
				sum += ele
			strlen = len(nosatradiance)
			avg = sum / strlen
			avg = str(avg)
		# okay, let's check to see if that list of non-saturated radiances has 1 or 2 detections
		elif len(nosatradiance) > 0:
			for ele in nosatradiance:
				sum += ele
			strlen = len(nosatradiance)
			avg = sum / strlen
			avg = str(avg)
			maxnosatradiance = str(nosatradiance[0])
			minradiance = str(nosatradiance[-1])
		# what to do if there are no unsaturated detections at emissions angles less than 80°
		else:
			minradiance = str(radiance[-1])
			maxradiance = str(radiance[0])
			maxnosatradiance = str(radiance[0])
			note = "No unsaturated detections below " + str(emissionLimit) + " deg emission"
			# check to see if there are more than 2 detections
			# if so you can remove max and min
			if len(radiance) > 2:
				radiance.pop(0)
				radiance.pop(-1)
				for ele in radiance:
					sum += ele
				avg = sum / len(radiance)
				avg = str(avg)
			# we know there is 1 or 2 detections
			else:
				strlen = len(radiance)
				for ele in radiance:
					sum += ele
				avg = sum / len(radiance)
				avg = str(avg)
	# if there are no detections below 80 degrees emission, we need to use all detections
	else:
		radiance = []
		nosatradiance = []
		maxnosatradiance = ""
		maxradiance = ""
		avg = ""
		minradiance = ""
		# parse through database again, but this time without using emission limit
		for line in datafile:
			if hotspotID in line:
				lines = line.split(",")
				# emi = float(lines[18])
				specRad = float(lines[15])
				saturation = lines[13]
				name = str(lines[4])
				latitude = str(lines[5])
				longitude = str(lines[6])
				radiance.append(specRad)
				if saturation == "No":
					nosatradiance.append(specRad)
		radiance.sort(reverse=True)
		nosatradiance.sort(reverse=True)
		if len(radiance) > 0:
			maxradiance = str(radiance[0])
			# check to see if non-saturated radiances have 3 or more detections
			if len(nosatradiance) > 2:
				maxnosatradiance = str(nosatradiance[0])
				minradiance = str(nosatradiance[-1])
				nosatradiance.pop(0)
				nosatradiance.pop(-1)
				for ele in nosatradiance:
					sum += ele
				avg = sum / len(nosatradiance)
				avg = str(avg)
				
			# okay, let's check to see if that list of non-saturated radiances has 1 or 2 detections
			elif len(nosatradiance) > 0:
				for ele in nosatradiance:
					sum += ele
				avg = sum / len(nosatradiance)
				avg = str(avg)
				maxnosatradiance = str(nosatradiance[0])
				minradiance = str(nosatradiance[-1])
			# what to do if there are no unsaturated detections at emissions angles less than 80°
			else:
				minradiance = str(radiance[-1])
				maxradiance = str(radiance[0])
				# check to see if there are more than 2 detections
				# if so you can remove max and min
				if len(radiance) > 2:
					radiance.pop(0)
					radiance.pop(-1)
					for ele in radiance:
						sum += ele
					avg = sum / len(radiance)
					avg = str(avg)
				# we know there is 1 or 2 detections
				else:
					for ele in radiance:
						sum += ele
					avg = sum / len(radiance)
					avg = str(avg)
			note = "No detections below " + str(emissionLimit) + " deg emission"
			
	print(hotspotID + ',' + name + ',' + latitude + ',' + longitude + ',' + maxradiance + ',' + maxnosatradiance + ',' + minradiance + ',' + avg + ',' + note, file = outputFile)

	