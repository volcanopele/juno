# make sure the kernels for Juno are up-to-date for ISIS
# rerun the database generator so that spiceinit knows what kernel files to pick update_dyld_shared_cache

kerneldbgen to='/Volumes/TouchT7/SPICE/juno/kernels/ck/kernels.????.db' \
type=ck predictdir=/Volumes/TouchT7/SPICE/juno/kernels/ck \
predictfilter='juno_sc_raw_??????_??????.bc;juno_sc_prl_??????_??????_jm????a_v??.bc;juno_sc_prl_??????_??????_jm????rp_v??.bc' \
recondir=/Volumes/TouchT7/SPICE/juno/kernels/ck \
reconfilter='juno_sc_rec_??????_??????_v??.bc' \
sclk=/Volumes/TouchT7/SPICE/juno/kernels/sclk/jno_sclkscet_00113.tsc \
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

conda activate base
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021105_33C00028_V01-raw.png -m 10344-Metadata.json

# now get into ISIS and convert the raw image to IMG
# use label to get size
raw2isis from=JNCE_2021105_33C00028_V01-raw.raw to=JNCE_2021105_33C00028_V01-raw.cub samples=1648 lines=15360 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021105_33C00028_V01-raw.cub to=JNCE_2021105_33C00028_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3

mkdir disk
mkdir mosaic
mkdir projected

# use junogeometryinfo.py to get clat, clon, altitude (NOT DISTANCE TO CENTER), and JunoCAM resolution
maptemplate map=JNCE_2021105_33C00028_V01.map targopt=user targetname=Jupiter clat=40.963 clon=292.164 dist=6906.290 londir=POSITIVEWEST projection=POINTPERSPECTIVE resopt=MPP resolution=4645.861 rngopt=user minlat=-90 maxlat=90 minlon=0 maxlon=360

# import framelets into ISIS
junocam2isis from=JNCE_2021105_33C00028_V01-raw-adjusted.LBL to=disk/JNCE_2021105_33C00028_V01.cub
cd disk
ls -1 *.cub | sed s/.cub// > image_name.lis

# need to trim off the top and bottom by 4 pixels
# may need to trim off left and right depending on camera settings
trim from=\$1.cub to=\$1.trim.cub top=4 bottom=4 left=25 right=20 -batchlist=image_name.lis
spiceinit from=\$1.trim.cub ckpredicted=true spkpredicted=true -batchlist=image_name.lis

# use Qview to find images that have the disk in it and delete those that don't
ls -1 *.trim.cub > JNCE_2021105_33C00028_V01.disk.lis
cam2map from=\$1 to=../projected/\$1 map=../JNCE_2021105_33C00028_V01.map pixres=map -batchlist=JNCE_2021105_33C00028_V01.disk.lis

cd ../projected
ls -1 *_GREEN_* > GREEN_images.lis
ls -1 *_RED_* > RED_images.lis
ls -1 *_BLUE_* > BLUE_images.lis
automos fromlist=BLUE_images.lis mosaic=../mosaic/JNCE_2021105_33C00028_V01_BLUE.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=GREEN_images.lis mosaic=../mosaic/JNCE_2021105_33C00028_V01_GREEN.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=RED_images.lis mosaic=../mosaic/JNCE_2021105_33C00028_V01_RED.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 


# try histeq to get better quality images
cd ../mosaic
histeq from=JNCE_2021105_33C00028_V01_BLUE.cub+1 to=JNCE_2021105_33C00028_V01_BLUE.histeq.cub minper=0.0 maxper=100
histeq from=JNCE_2021105_33C00028_V01_GREEN.cub+1 to=JNCE_2021105_33C00028_V01_GREEN.histeq.cub minper=0.0 maxper=100
histeq from=JNCE_2021105_33C00028_V01_RED.cub+1 to=JNCE_2021105_33C00028_V01_RED.histeq.cub minper=0.0 maxper=100

ls -1 *histeq.cub > images.lis
cubeit fromlist=images.lis to=JNCE_2021105_33C00028_V01_RGB.cub
isis2std red=JNCE_2021105_33C00028_V01_RED.histeq.cub green=JNCE_2021105_33C00028_V01_GREEN.histeq.cub blue=JNCE_2021105_33C00028_V01_BLUE.histeq.cub to=JNCR_2017192_07C00060_V01_RGB.png mode=RGB stretch=manual rmin=-32418.7 rmax=1040 gmin=-32433 gmax=997 bmin=-32413.6 bmax=1073 quality=80
isis2std red=JNCR_2017192_07C00060_V01_RED.cub+1 green=JNCR_2017192_07C00060_V01_GREEN.cub+1 blue=JNCR_2017192_07C00060_V01_BLUE.cub+1 to=JNCR_2017192_07C00060_V01_RGB_stretch.png mode=RGB stretch=manual rmin=738 rmax=3387 gmin=981 gmax=3542 bmin=821 bmax=3514 quality=80

isis2std from=JNCR_2017192_07C00060_V01_GREEN_0008.cub to=JNCR_2017192_07C00060_V01_GREEN_0008.tif format=TIFF bittype=U16BIT stretch=linear minpercent=0.01 maxpercent=99.99


# for non-histogram stretched images
ls -1 *.cub > images.lis
cubeit fromlist=images.lis to=JNCE_2021105_33C00028_V01_RGB2.cub
isis2std red=JNCE_2021105_33C00028_V01_RED.cub+1 green=JNCE_2021105_33C00028_V01_GREEN.cub+1 blue=JNCE_2021105_33C00028_V01_BLUE.cub+1 to=JNCR_2017192_07C00060_V01_RGB2.png mode=RGB stretch=manual rmin=731 rmax=1067 gmin=744 gmax=1051 bmin=789 bmax=1136 quality=80

# cam2map test
cp JNCE_2021105_33C00028_V01_GREEN_0018.trim.cub ../mosaic
map2cam from=JNCE_2021105_33C00028_V01_RED.cub match=JNCE_2021105_33C00028_V01_GREEN_0018.trim.cub to=JNCE_2021105_33C00028_V01_RED.cam.cub
map2cam from=JNCE_2021105_33C00028_V01_GREEN.cub match=JNCE_2021105_33C00028_V01_GREEN_0018.trim.cub to=JNCE_2021105_33C00028_V01_GREEN.cam.cub
map2cam from=JNCE_2021105_33C00028_V01_BLUE.cub match=JNCE_2021105_33C00028_V01_GREEN_0018.trim.cub to=JNCE_2021105_33C00028_V01_BLUE.cam.cub

ls -1 *cam.cub > images3.lis
cubeit fromlist=images3.lis to=JNCE_2021105_33C00028_V01_RGB3.cub

