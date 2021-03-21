#!/bin/bash
# conda activate isis3


# perijove is the orbit number
# IMAGE_NAME is the central image of the summed image
COLORMAP=/Volumes/TouchT7/data/basemaps/io/merged_color_mosaic/Io_GalileoSSI-Voyager_Global_Mosaic_ClrMerge_1km.cub
GREYMAP=/Volumes/TouchT7/data/basemaps/io/Io_GalileoSSI-Voyager_Global_Mosaic_1km.cub

PERIJOVE="PJ58"

# 02/03/2024 17:55:30.602
IMAGE_NAME="JNCE_20240203T175601"
CLAT="11.411"

# W longitude
CLON="332.176"

# HORIZONTAL_PIXEL_SCALE
RES="7756.689"

# use TARGET_ALTITUDE
DISTANCE="11530.681"

SLAT="3.0873"
SLON="239.8903"

mkdir ~/Dropbox/Io/Juno/$PERIJOVE/preview
cd ~/Dropbox/Io/Juno/$PERIJOVE/preview
maptemplate map=$IMAGE_NAME.map targopt=user targetname=Io clat=$CLAT clon=$CLON dist=$DISTANCE londir=POSITIVEWEST projection=POINTPERSPECTIVE resopt=MPP resolution=$RES rngopt=user minlat=-90 maxlat=90 minlon=0 maxlon=360
maptemplate map=$IMAGE_NAME.subsolar.map targopt=user targetname=Io clat=$SLAT clon=$SLON londir=POSITIVEWEST projection=ORTHOGRAPHIC resopt=MPP resolution=1000 rngopt=user minlat=-90 maxlat=90 minlon=0 maxlon=360
map2map from=$COLORMAP to=$IMAGE_NAME.subsolar.cub map=$IMAGE_NAME.subsolar.map pixres=map defaultrange=map
map2map from=$IMAGE_NAME.subsolar.cub to=$IMAGE_NAME.map.cub map=$IMAGE_NAME.map pixres=map defaultrange=map
isis2std red=$IMAGE_NAME.map.cub+1 green=$IMAGE_NAME.map.cub+2 blue=$IMAGE_NAME.map.cub+3 to=$IMAGE_NAME.map.png mode=rgb format=png stretch=manual rmax=256 rmin=0 gmax=256 gmin=0 bmax=256 bmin=0 quality=80

# maptemplate map=$IMAGE_NAME.subjovian.map targopt=user targetname=Io clat=0 clon=0 londir=POSITIVEWEST projection=ORTHOGRAPHIC resopt=MPP resolution=1000 rngopt=user minlat=-90 maxlat=90 minlon=0 maxlon=360
# map2map from=$COLORMAP to=$IMAGE_NAME.subjovian.cub map=$IMAGE_NAME.subjovian.map pixres=map defaultrange=map
# map2map from=$IMAGE_NAME.subjovian.cub to=$IMAGE_NAME.jupshine.cub map=$IMAGE_NAME.map pixres=map defaultrange=map
# isis2std red=$IMAGE_NAME.jupshine.cub+1 green=$IMAGE_NAME.jupshine.cub+2 blue=$IMAGE_NAME.jupshine.cub+3 to=$IMAGE_NAME.jupshine.png mode=rgb format=png stretch=manual rmax=25600 rmin=0 gmax=25600 gmin=0 bmax=25600 bmin=0 quality=80


/bin/rm *.cub *.map *.prt *.pgw

