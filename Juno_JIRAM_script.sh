#!/bin/bash
# conda activate isis3


# perijove is the orbit number
# IMAGE_NAME is the central image of the summed image

PERIJOVE="PJ32"
IMAGE_NAME="JIR_IMG_RDR_2021052T203921_V01"
DIRECTORY="/Users/perry/Dropbox/Io/Juno/$PERIJOVE/$IMAGE_NAME"

CLAT="-40.565"

# 360 - SUB_SPACECRAFT_LONGITUDE .  Like a lot of IR astronomers, JIRAM use 
# E longitude
CLON="8.884"
CLON=$(echo "360-${CLON}" | bc -l)

# HORIZONTAL_PIXEL_SCALE divided by 20
RES="120500.797"
RES=$(echo "${RES}/20" | bc -l)

# use TARGET_ALTITUDE
DISTANCE="506802.026"

mkdir $DIRECTORY
cd $DIRECTORY
maptemplate map=$IMAGE_NAME.map targopt=user targetname=Io clat=$CLAT clon=$CLON dist=$DISTANCE londir=POSITIVEWEST projection=POINTPERSPECTIVE resopt=MPP resolution=$RES rngopt=user minlat=-90 maxlat=90 minlon=0 maxlon=360
map2map from=~/Dropbox/Io/Io_GalileoSSI-Voyager_Global_Mosaic_1km.cub to=$IMAGE_NAME.map.cub map=$IMAGE_NAME.map pixres=map defaultrange=map
isis2std from=$IMAGE_NAME.map.cub to=$IMAGE_NAME.map.tif format=tiff bittype=U16BIT stretch=manual minimum=0 maximum=1


