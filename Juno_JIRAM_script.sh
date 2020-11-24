#!/bin/bash
# conda activate isis3


# perijove is the orbit number
# IMAGE_NAME is the central image of the summed image

PERIJOVE="PJ25"
IMAGE_NAME="JIR_IMG_RDR_2020048T130532_V01"
CLAT="56.187"

# 360 - SUB_SPACECRAFT_LONGITUDE .  Like a lot of IR astronomers, JIRAM use 
# E longitude
CLON="95.5713"
CLON=$(echo "360-${CLON}" | bc -l)

# HORIZONTAL_PIXEL_SCALE divided by 20
RES="48269.58"
RES=$(echo "${RES}/20" | bc -l)

# use TARGET_CENTER_DISTANCE
DISTANCE="205185.1777"

mkdir $PERIJOVE/$IMAGE_NAME
maptemplate map=$PERIJOVE/$IMAGE_NAME/$IMAGE_NAME.map targopt=user targetname=Io clat=$CLAT clon=$CLON dist=$DISTANCE londir=POSITIVEWEST projection=POINTPERSPECTIVE resopt=MPP resolution=$RES rngopt=user minlat=-90 maxlat=90 minlon=0 maxlon=360
map2map from=~/Dropbox/Io/Io_GalileoSSI-Voyager_Global_Mosaic_1km.cub to=$PERIJOVE/$IMAGE_NAME/$IMAGE_NAME.map.cub map=$PERIJOVE/$IMAGE_NAME/$IMAGE_NAME.map pixres=map defaultrange=map
isis2std from=$PERIJOVE/$IMAGE_NAME/$IMAGE_NAME.map.cub to=$PERIJOVE/$IMAGE_NAME/$IMAGE_NAME.map.tif format=tiff bittype=U16BIT stretch=manual minimum=0 maximum=1


