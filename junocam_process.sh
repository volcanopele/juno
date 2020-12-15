junocam2isis from=JNCR_2017192_07C00060_V01.LBL to=disk/JNCR_2017192_07C00060_V01.cub
maptemplate map=JNCR_2017192_07C00060_V01.map targopt=user targetname=Jupiter clat=-22.323 clon=58.270 dist=10020.834 londir=POSITIVEWEST projection=POINTPERSPECTIVE resopt=MPP resolution=6741.015 rngopt=user minlat=-90 maxlat=90 minlon=0 maxlon=360
mv *cub *lis disk
spiceinit from=\$1 attach=true -batchlist=JNCR_2017192_07C00060_V01.lis

# use Qview to find images that have the disk in it and delete those that don't
ls -1 *cub > JNCR_2017192_07C00060_V01.disk.lis
cam2map from=\$1 to=../projected/\$1 map=../JNCR_2017192_07C00060_V01.map pixres=map -batchlist=JNCR_2017192_07C00060_V01.disk.lis

cd ../projected
ls -1 *_GREEN_* > GREEN_images.lis
ls -1 *_RED_* > RED_images.lis
ls -1 *_BLUE_* > BLUE_images.lis
automos fromlist=BLUE_images.lis mosaic=../mosaic/JNCR_2017192_07C00060_V01_BLUE.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=GREEN_images.lis mosaic=../mosaic/JNCR_2017192_07C00060_V01_GREEN.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=RED_images.lis mosaic=../mosaic/JNCR_2017192_07C00060_V01_RED.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 

cd ../mosaic
ls -1 *cub > images.lis
cubeit fromlist=images.lis to=JNCR_2017192_07C00060_V01_RGB.cub
isis2std red=JNCR_2017192_07C00060_V01_RED.cub+1 green=JNCR_2017192_07C00060_V01_GREEN.cub+1 blue=JNCR_2017192_07C00060_V01_BLUE.cub+1 to=JNCR_2017192_07C00060_V01_RGB.png mode=RGB stretch=manual rmin=3.6 rmax=3387 gmin=6.49 gmax=3542 bmin=9.47 bmax=3514 quality=80
isis2std red=JNCR_2017192_07C00060_V01_RED.cub+1 green=JNCR_2017192_07C00060_V01_GREEN.cub+1 blue=JNCR_2017192_07C00060_V01_BLUE.cub+1 to=JNCR_2017192_07C00060_V01_RGB_stretch.png mode=RGB stretch=manual rmin=738 rmax=3387 gmin=981 gmax=3542 bmin=821 bmax=3514 quality=80

isis2std from=JNCR_2017192_07C00060_V01_GREEN_0008.cub to=JNCR_2017192_07C00060_V01_GREEN_0008.tif format=TIFF bittype=U16BIT stretch=linear minpercent=0.01 maxpercent=99.99
