cam2map from=\$1 to=../projected/\$1 map=../JNCE_2021158_34C00002_V01.map pixres=map -batchlist=34C00002.lis

cd ../projected
ls -1 *_GREEN_* > GREEN_images.lis
ls -1 *_RED_* > RED_images.lis
ls -1 *_BLUE_* > BLUE_images.lis
automos fromlist=BLUE_images.lis mosaic=../mosaic/JNCE_2021158_34C00002_V01_BLUE.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=GREEN_images.lis mosaic=../mosaic/JNCE_2021158_34C00002_V01_GREEN.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=RED_images.lis mosaic=../mosaic/JNCE_2021158_34C00002_V01_RED.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 

cd ../mosaic
ls -1 *.cub > images.lis
cubeit fromlist=images.lis to=JNCE_2021158_34C00002_V01_RGB.cub
isis2std red=JNCE_2021158_34C00002_V01_RED.cub+1 green=JNCE_2021158_34C00002_V01_GREEN.cub+1 blue=JNCE_2021158_34C00002_V01_BLUE.cub+1 to=JNCE_2021158_34C00002_V01_RGB.png mode=RGB stretch=manual rmin=50 rmax=2077 gmin=50 gmax=2077 bmin=50 bmax=2077 quality=80

ckwriter fromlist=JNCE_2021158_34C00001_V01.disk.lis to=PJ34_Ganymede.ck overlap=warning
spkwriter fromlist=JNCE_2021158_34C00001_V01.disk.lis to=PJ34_Ganymede.bsp overlap=warning

ls -1 *.cub | sed s/.noise.cub// >> image_name.lis

IMAGE_NAME=21ISCOLOR_01
cam2map from=\$1.noise.cub to=../projected/\$1.simp.cub map=../${IMAGE_NAME}.map pixres=map -batchlist=image_name.lis


python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021158_34C00001_V01-raw.png -m 10629-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021158_34C00002_V01-raw.png -m 10630-Metadata.json -d

raw2isis from=JNCE_2021158_34C00001_V01-raw.raw to=JNCE_2021158_34C00001_V01-raw.cub samples=1648 lines=10752 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021158_34C00001_V01-raw.cub to=JNCE_2021158_34C00001_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3

raw2isis from=JNCE_2021158_34C00002_V01-raw.raw to=JNCE_2021158_34C00002_V01-raw.cub samples=1648 lines=10752 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021158_34C00002_V01-raw.cub to=JNCE_2021158_34C00002_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3


========

junocam2isis from=JNCE_2021158_34C00001_V01-raw-adjusted.lbl to=initial/JNCE_2021158_34C00001_V01.cub
cd initial
/bin/rm JNCE_2021158_34C00001_V01_BLUE_0003* JNCE_2021158_34C00001_V01_BLUE_0001* JNCE_2021158_34C00001_V01_BLUE_0002* 
/bin/rm JNCE_2021158_34C00001_V01_BLUE_0024* JNCE_2021158_34C00001_V01_BLUE_0025* JNCE_2021158_34C00001_V01_BLUE_0026* 
/bin/rm JNCE_2021158_34C00001_V01_BLUE_0027* JNCE_2021158_34C00001_V01_BLUE_0028*
/bin/rm JNCE_2021158_34C00001_V01_GREEN_0001* JNCE_2021158_34C00001_V01_GREEN_0002* JNCE_2021158_34C00001_V01_GREEN_0028*
/bin/rm JNCE_2021158_34C00001_V01_GREEN_0022* JNCE_2021158_34C00001_V01_GREEN_0023* JNCE_2021158_34C00001_V01_GREEN_0024* 
/bin/rm JNCE_2021158_34C00001_V01_GREEN_0025* JNCE_2021158_34C00001_V01_GREEN_0026* JNCE_2021158_34C00001_V01_GREEN_0027*
/bin/rm JNCE_2021158_34C00001_V01_RED_0021* JNCE_2021158_34C00001_V01_RED_0022* JNCE_2021158_34C00001_V01_RED_0023* 
/bin/rm JNCE_2021158_34C00001_V01_RED_0024* JNCE_2021158_34C00001_V01_RED_0025* JNCE_2021158_34C00001_V01_RED_0026* 
/bin/rm JNCE_2021158_34C00001_V01_RED_0027* JNCE_2021158_34C00001_V01_RED_0028* 
ls -1 *.cub | sed s/.cub// > image_name.lis
ls -1 *BLUE*cub | sed s/.cub// > BLUE_image_name.lis
ls -1 *GREEN*cub | sed s/.cub// > GREEN_image_name.lis
ls -1 *RED*cub | sed s/.cub// > RED_image_name.lis

ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_BLUE_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=BLUE_image_name.lis
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_GREEN_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=GREEN_image_name.lis
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_RED_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=RED_image_name.lis

ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_BLUE_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=BLUE_image_name.lis
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_GREEN_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=GREEN_image_name.lis
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/scratch/mask/cubes2/JNCE_RED_flat_gany.cub \
    to=\$1.flat.cub -batchlist=RED_image_name.lis

trim from=\$1.flat.cub to=\$1.trim.cub top=4 bottom=4 left=25 right=17 -batchlist=image_name.lis
spiceinit from=\$1.trim.cub ckpredicted=true spkpredicted=true attach=true -batchlist=image_name.lis
cp *trim.cub /Volumes/TouchT7/scratch/pj34/jigsaw

junocam2isis from=JNCE_2021158_34C00002_V01-raw-adjusted.lbl to=initial/JNCE_2021158_34C00002_V01.cub
cd initial
/bin/rm JNCE_2021158_34C00002_V01_BLUE_0021* JNCE_2021158_34C00002_V01_BLUE_0001* JNCE_2021158_34C00002_V01_BLUE_0002* 
/bin/rm JNCE_2021158_34C00002_V01_BLUE_0022* JNCE_2021158_34C00002_V01_BLUE_0023*
/bin/rm JNCE_2021158_34C00002_V01_BLUE_0024* JNCE_2021158_34C00002_V01_BLUE_0025* JNCE_2021158_34C00002_V01_BLUE_0026* 
/bin/rm JNCE_2021158_34C00002_V01_BLUE_0027* JNCE_2021158_34C00002_V01_BLUE_0028*
/bin/rm JNCE_2021158_34C00002_V01_GREEN_0001* JNCE_2021158_34C00002_V01_GREEN_0020* JNCE_2021158_34C00002_V01_GREEN_0028*
/bin/rm JNCE_2021158_34C00002_V01_GREEN_0022* JNCE_2021158_34C00002_V01_GREEN_0023* JNCE_2021158_34C00002_V01_GREEN_0024* 
/bin/rm JNCE_2021158_34C00002_V01_GREEN_0025* JNCE_2021158_34C00002_V01_GREEN_0026* JNCE_2021158_34C00002_V01_GREEN_0027*
/bin/rm JNCE_2021158_34C00002_V01_GREEN_0021*
/bin/rm JNCE_2021158_34C00002_V01_RED_0021* JNCE_2021158_34C00002_V01_RED_0022* JNCE_2021158_34C00002_V01_RED_0023* 
/bin/rm JNCE_2021158_34C00002_V01_RED_0024* JNCE_2021158_34C00002_V01_RED_0025* JNCE_2021158_34C00002_V01_RED_0026* 
/bin/rm JNCE_2021158_34C00002_V01_RED_0027* JNCE_2021158_34C00002_V01_RED_0028* JNCE_2021158_34C00002_V01_RED_0019*
/bin/rm JNCE_2021158_34C00002_V01_RED_0020*
ls -1 *.cub | sed s/.cub// > image_name.lis
ls -1 *BLUE*cub | sed s/.cub// > BLUE_image_name.lis
ls -1 *GREEN*cub | sed s/.cub// > GREEN_image_name.lis
ls -1 *RED*cub | sed s/.cub// > RED_image_name.lis

ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_BLUE_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=BLUE_image_name.lis
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_GREEN_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=GREEN_image_name.lis
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_RED_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=RED_image_name.lis
    
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_BLUE_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=BLUE_image_name.lis
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_GREEN_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=GREEN_image_name.lis
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/scratch/mask/cubes2/JNCE_RED_flat_gany.cub \
    to=\$1.flat.cub -batchlist=RED_image_name.lis

    
trim from=\$1.cub to=\$1.trim.cub top=4 bottom=4 left=25 right=17 -batchlist=image_name.lis
spiceinit from=\$1.trim.cub ckpredicted=true spkpredicted=true attach=true -batchlist=image_name.lis

cp *trim.cub /Volumes/TouchT7/scratch/jigsaw

ls -1 *.cub | sed s/.trim.cub// > image_name.lis
footprintinit from=\$1 -batchlist=JNCE_2021158_34C00001_V01.disk.lis
findimageoverlaps from=JNCE_2021158_34C00001_V01.disk.lis overlaplist=overlaps.txt
jigsaw fromlist=JNCE_2021158_34C00001_V01.disk.lis cnet=PJ34_Ganymede.net \
    onet=jigsaw_net.net model1=none twist=yes file_prefix=34C00001.js \
    sigma0=1.0e-3 maxits=200 update=yes observations=yes camera_angles_sigma=10 \
    spsolve=positions SPACECRAFT_POSITION_SIGMA=600000

cp JNCE_2021158_34C00001_V01*trim.cub /Volumes/TouchT7/scratch/34C00001/test/jigsawed
cp JNCE_2021158_34C00002_V01*trim.cub /Volumes/TouchT7/scratch/34C00002/jigsawed

cam2map from=\$1 to=../projected/\$1 map=../JNCR_2021158_34C00001_V01.map \
    pixres=map -batchlist=34C00001.lis
cd ../projected
ls -1 *_GREEN_* > GREEN_images.lis
ls -1 *_RED_* > RED_images.lis
ls -1 *_BLUE_* > BLUE_images.lis
automos fromlist=BLUE_images.lis mosaic=../mosaic/JNCE_2021158_34C00001_V01_BLUE.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=GREEN_images.lis mosaic=../mosaic/JNCE_2021158_34C00001_V01_GREEN.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=RED_images.lis mosaic=../mosaic/JNCE_2021158_34C00001_V01_RED.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
cd ../mosaic
ls -1 *.cub > images.lis
cubeit fromlist=images.lis to=JNCE_2021158_34C00001_V01_RGB.cub
isis2std red=JNCE_2021158_34C00001_V01_RED.cub+1 green=JNCE_2021158_34C00001_V01_GREEN.cub+1 blue=JNCE_2021158_34C00001_V01_BLUE.cub+1 to=JNCE_2021158_34C00001_V01_RGB.png mode=RGB stretch=manual rmin=50 rmax=2620 gmin=50 gmax=2620 bmin=50 bmax=2620 quality=80

cam2map from=\$1 to=../projected/\$1 map=../JNCE_2021158_34C00002_V01.map \
    pixres=map -batchlist=34C00002.lis
cd ../projected
ls -1 *_GREEN_* > GREEN_images.lis
ls -1 *_RED_* > RED_images.lis
ls -1 *_BLUE_* > BLUE_images.lis
automos fromlist=BLUE_images.lis mosaic=../mosaic/JNCE_2021158_34C00002_V01_BLUE.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=GREEN_images.lis mosaic=../mosaic/JNCE_2021158_34C00002_V01_GREEN.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=RED_images.lis mosaic=../mosaic/JNCE_2021158_34C00002_V01_RED.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
cd ../mosaic
ls -1 *.cub > images.lis
cubeit fromlist=images.lis to=JNCE_2021158_34C00002_V01_RGB.cub
isis2std red=JNCE_2021158_34C00002_V01_RED.cub+1 green=JNCE_2021158_34C00002_V01_GREEN.cub+1 blue=JNCE_2021158_34C00002_V01_BLUE.cub+1 to=JNCE_2021158_34C00001_V01_RGB.png mode=RGB stretch=manual rmin=50 rmax=2077 gmin=50 gmax=2077 bmin=50 bmax=2077 quality=80


cubeit fromlist=JNCE_2021158_34C00001_V01_BLUE.lis to=JNCE_2021158_34C00001_V01_BLUE_cubeit.cub
cubeavg from=JNCE_2021158_34C00001_V01_BLUE_cubeit.cub to=JNCE_2021158_34C00001_V01_BLUE_cubeavg.cub
cubeit fromlist=JNCE_2021158_34C00001_V01_GREEN.lis to=JNCE_2021158_34C00001_V01_GREEN_cubeit.cub
cubeavg from=JNCE_2021158_34C00001_V01_GREEN_cubeit.cub to=JNCE_2021158_34C00001_V01_GREEN_cubeavg.cub
cubeit fromlist=JNCE_2021158_34C00001_V01_RED.lis to=JNCE_2021158_34C00001_V01_RED_cubeit.cub
cubeavg from=JNCE_2021158_34C00001_V01_RED_cubeit.cub to=JNCE_2021158_34C00001_V01_RED_cubeavg.cub

mask from=JNCE_2021158_34C00001_V01_BLUE_0010.cub to=JNCE_2021158_34C00001_V01_BLUE_0010.mask.cub \
    mask=/Volumes/TouchT7/scratch/JNCE_2021158_34C00001_V01_BLUE_mask.cub
lowpass from=JNCE_2021158_34C00001_V01_BLUE_0010.mask.cub to=JNCE_2021158_34C00001_V01_BLUE_0010.filter.cub \
    samples=5 lines=5 filter=outside null=yes hrs=no his=no lrs=no replacement=center
trim from=JNCE_2021158_34C00001_V01_BLUE_0010.filter.cub to=JNCE_2021158_34C00001_V01_BLUE_0010.trim.cub top=4 bottom=4 left=25 right=17


====
mask generation

conda activate base
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021202_35C00060_V01-raw.png -m 11050-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021202_35C00059_V01-raw.png -m 11049-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021202_35C00058_V01-raw.png -m 11048-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021202_35C00057_V01-raw.png -m 11047-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021159_34C00061_V01-raw.png -m 10660-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021159_34C00060_V01-raw.png -m 10659-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021159_34C00059_V01-raw.png -m 10658-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021159_34C00058_V01-raw.png -m 10657-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021159_34C00056_V01-raw.png -m 10655-Metadata.json -d

raw2isis from=JNCE_2021202_35C00060_V01-raw.raw to=JNCE_2021202_35C00060_V01-raw.cub samples=1648 lines=16128 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021202_35C00060_V01-raw.cub to=JNCE_2021202_35C00060_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021202_35C00059_V01-raw.raw to=JNCE_2021202_35C00059_V01-raw.cub samples=1648 lines=16128 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021202_35C00059_V01-raw.cub to=JNCE_2021202_35C00059_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021202_35C00058_V01-raw.raw to=JNCE_2021202_35C00058_V01-raw.cub samples=1648 lines=16128 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021202_35C00058_V01-raw.cub to=JNCE_2021202_35C00058_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021202_35C00057_V01-raw.raw to=JNCE_2021202_35C00057_V01-raw.cub samples=1648 lines=16128 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021202_35C00057_V01-raw.cub to=JNCE_2021202_35C00057_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021159_34C00061_V01-raw.raw to=JNCE_2021159_34C00061_V01-raw.cub samples=1648 lines=16128 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021159_34C00061_V01-raw.cub to=JNCE_2021159_34C00061_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021159_34C00060_V01-raw.raw to=JNCE_2021159_34C00060_V01-raw.cub samples=1648 lines=16128 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021159_34C00060_V01-raw.cub to=JNCE_2021159_34C00060_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021159_34C00059_V01-raw.raw to=JNCE_2021159_34C00059_V01-raw.cub samples=1648 lines=16128 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021159_34C00059_V01-raw.cub to=JNCE_2021159_34C00059_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021159_34C00058_V01-raw.raw to=JNCE_2021159_34C00058_V01-raw.cub samples=1648 lines=16128 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021159_34C00058_V01-raw.cub to=JNCE_2021159_34C00058_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021159_34C00056_V01-raw.raw to=JNCE_2021159_34C00056_V01-raw.cub samples=1648 lines=16128 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021159_34C00056_V01-raw.cub to=JNCE_2021159_34C00056_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3

junocam2isis from=JNCE_2021202_35C00060_V01-raw-adjusted.lbl to=initial/JNCE_2021202_35C00060_V01.cub
junocam2isis from=JNCE_2021202_35C00059_V01-raw-adjusted.lbl to=initial/JNCE_2021202_35C00059_V01.cub
junocam2isis from=JNCE_2021202_35C00058_V01-raw-adjusted.lbl to=initial/JNCE_2021202_35C00058_V01.cub
junocam2isis from=JNCE_2021202_35C00057_V01-raw-adjusted.lbl to=initial/JNCE_2021202_35C00057_V01.cub
junocam2isis from=JNCE_2021159_34C00061_V01-raw-adjusted.lbl to=initial/JNCE_2021159_34C00061_V01.cub
junocam2isis from=JNCE_2021159_34C00060_V01-raw-adjusted.lbl to=initial/JNCE_2021159_34C00060_V01.cub
junocam2isis from=JNCE_2021159_34C00059_V01-raw-adjusted.lbl to=initial/JNCE_2021159_34C00059_V01.cub
junocam2isis from=JNCE_2021159_34C00058_V01-raw-adjusted.lbl to=initial/JNCE_2021159_34C00058_V01.cub
junocam2isis from=JNCE_2021159_34C00056_V01-raw-adjusted.lbl to=initial/JNCE_2021159_34C00056_V01.cub

cubeit fromlist=BLUE_image_list.lis to=JNCE_BLUE_cubeit.cub
cubeavg from=JNCE_BLUE_cubeit.cub to=JNCE_BLUE_cubeavg.cub
cp JNCE_BLUE_cubeavg.cub JNCE_BLUE_mask.cub
cubeit fromlist=GREEN_image_list.lis to=JNCE_GREEN_cubeit.cub
cubeavg from=JNCE_GREEN_cubeit.cub to=JNCE_GREEN_cubeavg.cub
cp JNCE_GREEN_cubeavg.cub JNCE_GREEN_mask.cub
cubeit fromlist=RED_image_list.lis to=JNCE_RED_cubeit.cub
cubeavg from=JNCE_RED_cubeit.cub to=JNCE_RED_cubeavg.cub
cp JNCE_RED_cubeavg.cub JNCE_RED_mask.cub

cp JNCE_RED_* JNCE_GREEN_* JNCE_BLUE_* ../cubes2

reduce from=JNCE_BLUE_mask.cub to=JNCE_BLUE_grad1.cub mode=total ons=1648 onl=1
enlarge from=JNCE_BLUE_grad1.cub to=JNCE_BLUE_grad2.cub mode=total ons=1648 onl=128
ratio numerator=JNCE_BLUE_cubeavg.cub denominator=JNCE_BLUE_grad2.cub to=JNCE_BLUE_flat.cub

reduce from=JNCE_GREEN_mask.cub to=JNCE_GREEN_grad1.cub mode=total ons=1648 onl=1
enlarge from=JNCE_GREEN_grad1.cub to=JNCE_GREEN_grad2.cub mode=total ons=1648 onl=128
ratio numerator=JNCE_GREEN_cubeavg.cub denominator=JNCE_GREEN_grad2.cub to=JNCE_GREEN_flat.cub

/bin/rm *GREEN_grad* JNCE_GREEN_flat.cub

reduce from=JNCE_RED_mask.cub to=JNCE_RED_grad1.cub mode=total ons=1648 onl=1
enlarge from=JNCE_RED_grad1.cub to=JNCE_RED_grad2.cub mode=total ons=1648 onl=128
ratio numerator=JNCE_RED_cubeavg.cub denominator=JNCE_RED_grad2.cub to=JNCE_RED_flat.cub

/bin/rm *RED_grad* JNCE_RED_flat.cub

python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021159_34C00062_V01-raw.png -m 10730-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021159_34C00055_V01-raw.png -m 10654-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021159_34C00054_V01-raw.png -m 10653-Metadata.json -d
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021159_34C00053_V01-raw.png -m 10652-Metadata.json -d

raw2isis from=JNCE_2021159_34C00062_V01-raw.raw to=JNCE_2021159_34C00062_V01-raw.cub samples=1648 lines=16128 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021159_34C00062_V01-raw.cub to=JNCE_2021159_34C00062_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021159_34C00055_V01-raw.raw to=JNCE_2021159_34C00055_V01-raw.cub samples=1648 lines=15360 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021159_34C00055_V01-raw.cub to=JNCE_2021159_34C00055_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021159_34C00054_V01-raw.raw to=JNCE_2021159_34C00054_V01-raw.cub samples=1648 lines=15360 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021159_34C00054_V01-raw.cub to=JNCE_2021159_34C00054_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3
raw2isis from=JNCE_2021159_34C00053_V01-raw.raw to=JNCE_2021159_34C00053_V01-raw.cub samples=1648 lines=15360 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021159_34C00053_V01-raw.cub to=JNCE_2021159_34C00053_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3

/bin/rm JNCE_2021159_34C00062_V01-raw.cub JNCE_2021159_34C00062_V01-raw-adjusted.img
/bin/rm JNCE_2021159_34C00055_V01-raw.cub JNCE_2021159_34C00055_V01-raw-adjusted.img
/bin/rm JNCE_2021159_34C00054_V01-raw.cub JNCE_2021159_34C00054_V01-raw-adjusted.img
/bin/rm JNCE_2021159_34C00053_V01-raw.cub JNCE_2021159_34C00053_V01-raw-adjusted.img

junocam2isis from=JNCE_2021159_34C00062_V01-raw-adjusted.lbl to=initial/JNCE_2021159_34C00062_V01.cub
junocam2isis from=JNCE_2021159_34C00055_V01-raw-adjusted.lbl to=initial/JNCE_2021159_34C00055_V01.cub
junocam2isis from=JNCE_2021159_34C00054_V01-raw-adjusted.lbl to=initial/JNCE_2021159_34C00054_V01.cub
junocam2isis from=JNCE_2021159_34C00053_V01-raw-adjusted.lbl to=initial/JNCE_2021159_34C00053_V01.cub

ls -1 *BLUE*cub > BLUE_image_list.lis
ls -1 *GREEN*cub > GREEN_image_list.lis
ls -1 *RED*cub > RED_image_list.lis

cubeit fromlist=BLUE_image_list.lis to=JNCE_BLUE_cubeit.cub
cubeavg from=JNCE_BLUE_cubeit.cub to=JNCE_BLUE_cubeavg.cub
cp JNCE_BLUE_cubeavg.cub JNCE_BLUE_mask.cub
cubeit fromlist=GREEN_image_list.lis to=JNCE_GREEN_cubeit.cub
cubeavg from=JNCE_GREEN_cubeit.cub to=JNCE_GREEN_cubeavg.cub
cp JNCE_GREEN_cubeavg.cub JNCE_GREEN_mask.cub
cubeit fromlist=RED_image_list.lis to=JNCE_RED_cubeit.cub
cubeavg from=JNCE_RED_cubeit.cub to=JNCE_RED_cubeavg.cub
cp JNCE_RED_cubeavg.cub JNCE_RED_mask.cub

mv JNCE_RED_* JNCE_GREEN_* JNCE_BLUE_* ../cubes
ratio numerator=JNCE_2021159_34C00061_V01_BLUE_0020.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_BLUE_flat_PJ3435_v2.cub \
    to=JNCE_2021159_34C00061_V01_BLUE_0020.flat.cub
ratio numerator=JNCE_2021202_35C00057_V01_GREEN_0017.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_GREEN_flat_PJ3435_v2.cub \
    to=JNCE_2021202_35C00057_V01_GREEN_0017.flat.cub
ratio numerator=JNCE_2021159_34C00061_V01_RED_0019.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_RED_flat_PJ3435_v2.cub \
    to=JNCE_2021159_34C00061_V01_RED_0019.flat.cub

===

fx f1=JNCE_RED_flat_trim1.cub to=JNCE_RED_flat_fx1.cub \
equation="\(f1+((1-f1)*0.41))"

fx f1=JNCE_RED_flat_trim2.cub to=JNCE_RED_flat_fx2.cub \
equation="\(f1-((1-f1)*0.41))"
cp JNCE_RED_flat.cub JNCE_RED_flat_gany.cub
handmos from=JNCE_RED_flat_fx1.cub mosaic=JNCE_RED_flat_gany.cub
handmos from=JNCE_RED_flat_fx2.cub mosaic=JNCE_RED_flat_gany.cub

fx f1=JNCE_GREEN_flat_trim.cub to=JNCE_GREEN_flat_fx.cub \
equation="\(f1-((1-f1)*0.41))"
cp JNCE_GREEN_flat.cub JNCE_GREEN_flat_gany.cub
handmos from=JNCE_GREEN_flat_fx.cub mosaic=JNCE_GREEN_flat_gany.cub

ratio numerator=JNCE_2021158_34C00001_V01_RED.cub denominator=JNCE_2021158_34C00001_V01_BLUE.cub \
    to=JNCE_2021158_34C00001_V01_RBratio.cub
