# make sure the kernels for Juno are up-to-date for ISIS
# rerun the database generator so that spiceinit knows what kernel files to pick update_dyld_shared_cache

# not meant to be run automatically as a pipeline

kerneldbgen to='/Volumes/TouchT7/SPICE/juno/kernels/ck/kernels.????.db' \
type=ck predictdir=/Volumes/TouchT7/SPICE/juno/kernels/ck \
predictfilter='juno_sc_raw_??????_??????.bc;juno_sc_prl_??????_??????_jm????rp_v??.bc;juno_sc_prl_??????_??????_jm????a_v??.bc' \
recondir=/Volumes/TouchT7/SPICE/juno/kernels/ck \
reconfilter='juno_sc_rec_??????_??????_v??.bc' \
sclk=/Volumes/TouchT7/SPICE/juno/kernels/sclk/jno_sclkscet_00117.tsc \
lsk=/Volumes/TouchT7/SPICE/juno/kernels/lsk/naif0012.tls

kerneldbgen to='/Volumes/TouchT7/SPICE/juno/kernels/spk/kernels.????.db' \
type=SPK predictdir=/Volumes/TouchT7/SPICE/juno/kernels/spk \
predictfilter='juno_pre_??????_??????_??????_jm????.bsp' \
recondir='/Volumes/TouchT7/SPICE/juno/kernels/spk' \
reconfilter='juno_rec_??????_??????_??????.bsp;' \
lsk='/Volumes/TouchT7/SPICE/juno/kernels/lsk/naif0012.tls'

# useful to have three terminal tabs open
conda activate base
conda activate isis
conda activate spice

# don't start in ISIS, start in base conda and convert png file to raw
# also generates label file
# the -d option will decompound the image
conda activate base
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021158_34C00001_V01-raw.png -m 10629-Metadata.json -d

# don't freak out about all the errors. Those are expected
# you should have a raw file and a lbl file

# now get into ISIS and convert the raw image to IMG
# use label to get size
raw2isis from=JNCE_2021158_34C00001_V01-raw.raw to=JNCE_2021158_34C00001_V01-raw.cub \
    samples=1648 lines=10752 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021158_34C00001_V01-raw.cub to=JNCE_2021158_34C00001_V01-raw-adjusted.img \
    labtype=FIXED bittype=32BIT pdsversion=PDS3

mkdir initial
mkdir mosaic
mkdir projected
mkdir jigsaw

# use junogeometryinfo.py to get clat, clon, altitude (NOT DISTANCE TO CENTER), and JunoCAM resolution
# use the label file generated above to get the mid-image time
# be sure to edit targetname to be Ganymede for those images
maptemplate map=JNCE_2021158_34C00001_V01.map targopt=user targetname=Ganymede \
	clat=26.838 clon=34.284 dist=1306.554 londir=POSITIVEWEST \
	projection=POINTPERSPECTIVE resopt=MPP resolution=878.919 rngopt=user minlat=-90 \
	maxlat=90 minlon=0 maxlon=360

# Ganymede basemap at 
/Volumes/TouchT7/data/basemaps/ganymede
# Io basemap at 
/Volumes/TouchT7/data/basemaps/io

# import framelets into ISIS
junocam2isis from=JNCE_2021158_34C00001_V01-raw-adjusted.lbl to=initial/JNCE_2021158_34C00001_V01.cub
cd initial

# look through the images in qview to find those that lack any part of the disk
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

# need to trim off the top and bottom by 4 pixels
# may need to trim off left and right depending on camera settings
trim from=\$1.cub to=\$1.trim.cub top=4 bottom=4 left=25 right=17 -batchlist=image_name.lis
spiceinit from=\$1.trim.cub ckpredicted=true spkpredicted=true attach=true -batchlist=image_name.lis

# OPTIONAL
# before trimming, you can use a flatfield on framelets
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_BLUE_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=BLUE_image_name.lis
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_GREEN_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=GREEN_image_name.lis
ratio numerator=\$1.cub \
    denominator=/Volumes/TouchT7/data/juno/calibration/flats/JNCE_RED_flat_PJ3435_v2.cub \
    to=\$1.flat.cub -batchlist=RED_image_name.lis
trim from=\$1.flat.cub to=\$1.trim.cub top=4 bottom=4 left=25 right=17 -batchlist=image_name.lis
spiceinit from=\$1.trim.cub ckpredicted=true spkpredicted=true attach=true -batchlist=image_name.lis

cp *trim.cub ../jigsaw

# JIGSAW STEP

cd ../jigsaw

# this is for one observation, but it can be helpful to merge multiple observations in this step
# in scratch, just have a directory for each observation along with a directory for jigsaw
# also create a sub-directory in each observation directory called jigsawed

ls -1 *.trim.cub > image_list.lis
ls -1 *.cub | sed s/.trim.cub// > image_name.lis
footprintinit from=\$1 -batchlist=image_name.lis
findimageoverlaps from=image_name.lis overlaplist=overlaps.txt
autoseed fromlist=image_name.lis overlaplist=overlaps.txt deffile=../autoseed_strip.def \
	onet=autoseed_strip.net errors=autoseed_grid.err networkid=34C00001.1 \
	pointid=34C00001.\?\?\?\?\?\?\? description="34C00001 grid1"
# can also create the control network in qnet if you don't want to have a lot of unusable points

# no update - test network for solution
jigsaw fromlist=image_name.lis cnet=PJ34_Ganymede.net \
    onet=jigsaw_net.net model1=none twist=yes file_prefix=34C00001.js \
    sigma0=1.0e-3 maxits=200 update=no observations=yes camera_angles_sigma=10 \
    spsolve=positions SPACECRAFT_POSITION_SIGMA=600000

# update
jigsaw fromlist=image_name.lis cnet=PJ34_Ganymede.net \
    onet=jigsaw_net.net model1=none twist=yes file_prefix=34C00001.js \
    sigma0=1.0e-3 maxits=200 update=yes observations=yes camera_angles_sigma=10 \
    spsolve=positions SPACECRAFT_POSITION_SIGMA=600000

# create smithed c-kernel and spk though spk's may not actually work as of version 5.0.2 of ISIS
ls -1 *cub > image.lis
ckwriter fromlist=image.lis to=PJ34_Ganymede.ck overlap=warning
spkwriter fromlist=image.lis to=PJ34_Ganymede.bsp overlap=warning

# if using this with multiple observations you will need to copy the updated files to jigsawed
cp JNCE_2021158_34C00001_V01*trim.cub /Volumes/TouchT7/scratch/34C00001/jigsawed
cd /Volumes/TouchT7/scratch/34C00001/jigsawed
ls -1 *.trim.cub > image_list.lis

# reprojected each framelet
cam2map from=\$1 to=../projected/\$1 map=../JNCE_2021158_34C00001_V01.map \
    pixres=map -batchlist=image_list.lis

# create mosaic for each band
cd ../projected
ls -1 *_GREEN_* > GREEN_images.lis
ls -1 *_RED_* > RED_images.lis
ls -1 *_BLUE_* > BLUE_images.lis
automos fromlist=BLUE_images.lis mosaic=../mosaic/JNCE_2021158_34C00001_V01_BLUE.cub \
	grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=GREEN_images.lis mosaic=../mosaic/JNCE_2021158_34C00001_V01_GREEN.cub \
	grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=RED_images.lis mosaic=../mosaic/JNCE_2021158_34C00001_V01_RED.cub \
	grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 

# combine each band into one cube and create png version
# use qview to get stretch
cd ../mosaic
ls -1 *.cub > images.lis
cubeit fromlist=images.lis to=JNCE_2021158_34C00002_V01_RGB.cub
isis2std red=JNCE_2021158_34C00002_V01_RED.cub+1 green=JNCE_2021158_34C00002_V01_GREEN.cub+1 \
	blue=JNCE_2021158_34C00002_V01_BLUE.cub+1 to=JNCE_2021158_34C00001_V01_RGB.png mode=RGB \
	stretch=manual rmin=50 rmax=2077 gmin=50 gmax=2077 bmin=50 bmax=2077 quality=80

