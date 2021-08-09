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

conda activate base
python ~/Documents/scripts/cassini_processing/junocam_png_to_img.py -p JNCE_2021158_34C00001_V01-raw.png -m 10629-Metadata.json -d -f

# don't freak out about all the errors. Those are expected
# you should have a raw file and a lbl file

# now get into ISIS and convert the raw image to IMG
# use label to get size
raw2isis from=JNCE_2021158_34C00001_V01-raw.raw to=JNCE_2021158_34C00001_V01-raw.cub samples=1648 lines=10752 bittype=REAL byteorder=LSB
isis2pds from=JNCE_2021158_34C00001_V01-raw.cub to=JNCE_2021158_34C00001_V01-raw-adjusted.img labtype=FIXED bittype=32BIT pdsversion=PDS3

mkdir disk
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

# import framelets into ISIS
junocam2isis from=JNCE_2021158_34C00001_V01-raw-adjusted.lbl to=initial/JNCE_2021158_34C00001_V01.cub
cd initial
ls -1 *.cub | sed s/.cub// > image_name.lis

# need to trim off the top and bottom by 4 pixels
# may need to trim off left and right depending on camera settings
trim from=\$1.cub to=\$1.trim.cub top=4 bottom=4 left=25 right=17 -batchlist=image_name.lis
spiceinit from=\$1.trim.cub ckpredicted=true spkpredicted=true attach=true -batchlist=image_name.lis

ls -1 *.trim.cub > JNCE_2021158_34C00001_V01.disk.lis

# jigsaw process
ls -1 *.cub | sed s/.trim.cub// > image_name.lis
footprintinit from=\$1 -batchlist=JNCE_2021158_34C00001_V01.disk.lis
findimageoverlaps from=JNCE_2021158_34C00001_V01.disk.lis overlaplist=overlaps.txt
autoseed fromlist=JNCE_2021158_34C00001_V01.disk.lis overlaplist=overlaps.txt deffile=../autoseed_strip.def onet=autoseed_strip.net errors=autoseed_grid.err networkid=34C00001.1 pointid=34C00001.\?\?\?\?\?\?\? description="34C00001 grid1"
jigsaw fromlist=JNCE_2021158_34C00001_V01.disk.lis cnet=autoseed_strip.net onet=jigsaw_net.net model1=none twist=yes file_prefix=34C00001.js sigma0=1.0e-3 maxits=200 update=no observations=yes camera_angles_sigma=10 spsolve=positions SPACECRAFT_POSITION_SIGMA=600000
jigsaw fromlist=JNCE_2021158_34C00001_V01.disk.lis cnet=autoseed_strip.net onet=jigsaw_net.net model1=none twist=yes file_prefix=34C00001.js sigma0=1.0e-3 maxits=200 update=no observations=yes camera_angles_sigma=10

# no update
jigsaw fromlist=JNCE_2021158_34C00001_V01.disk.lis cnet=PJ34_Ganymede.net \
    onet=jigsaw_net.net model1=none twist=yes file_prefix=34C00001.js \
    sigma0=1.0e-3 maxits=200 update=no observations=yes camera_angles_sigma=10 \
    spsolve=positions SPACECRAFT_POSITION_SIGMA=600000
jigsaw fromlist=JNCE_2021158_34C00001_V01.disk.lis cnet=PJ34_Ganymede.net onet=jigsaw_net.net model1=none twist=yes file_prefix=34C00001.js sigma0=1.0e-3 maxits=200 update=no observations=yes camera_angles_sigma=10

# update
jigsaw fromlist=JNCE_2021158_34C00001_V01.disk.lis cnet=PJ34_Ganymede.net \
    onet=jigsaw_net.net model1=none twist=yes file_prefix=34C00001.js \
    sigma0=1.0e-3 maxits=200 update=yes observations=yes camera_angles_sigma=10 \
    spsolve=positions SPACECRAFT_POSITION_SIGMA=600000
jigsaw fromlist=JNCE_2021158_34C00001_V01.disk.lis cnet=PJ34_Ganymede.net onet=jigsaw_net.net model1=none twist=yes file_prefix=34C00001.js sigma0=1.0e-3 maxits=200 update=yes observations=yes camera_angles_sigma=10

ckwriter fromlist=JNCE_2021158_34C00001_V01.disk.lis to=PJ34_Ganymede.ck overlap=warning
spkwriter fromlist=JNCE_2021158_34C00001_V01.disk.lis to=PJ34_Ganymede.bsp overlap=warning


# use Qview to find images that have the disk in it and delete those that don't
cam2map from=\$1 to=../projected/\$1 map=../JNCE_2021158_34C00001_V01.map \
pixres=map -batchlist=JNCE_2021158_34C00001_V01.disk.lis
cam2map from=\$1 to=../projected/\$1 map=../JNCE_2021158_34C00001_V01.map \
pixres=map -batchlist=34C00001.lis

cd ../projected
ls -1 *_GREEN_* > GREEN_images.lis
ls -1 *_RED_* > RED_images.lis
ls -1 *_BLUE_* > BLUE_images.lis
automos fromlist=BLUE_images.lis mosaic=../mosaic/JNCE_2021158_34C00001_V01_BLUE.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=GREEN_images.lis mosaic=../mosaic/JNCE_2021158_34C00001_V01_GREEN.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
automos fromlist=RED_images.lis mosaic=../mosaic/JNCE_2021158_34C00001_V01_RED.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 


# try histeq to get better quality images
cd ../mosaic
histeq from=JNCE_2021158_34C00001_V01_BLUE.cub+1 to=JNCE_2021158_34C00001_V01_BLUE.histeq.cub minper=0.0 maxper=100
histeq from=JNCE_2021158_34C00001_V01_GREEN.cub+1 to=JNCE_2021158_34C00001_V01_GREEN.histeq.cub minper=0.0 maxper=100
histeq from=JNCE_2021158_34C00001_V01_RED.cub+1 to=JNCE_2021158_34C00001_V01_RED.histeq.cub minper=0.0 maxper=100

ls -1 *histeq.cub > images.lis
cubeit fromlist=images.lis to=JNCE_2021158_34C00001_V01_RGB.cub
isis2std red=JNCE_2021158_34C00001_V01_RED.histeq.cub green=JNCE_2021158_34C00001_V01_GREEN.histeq.cub blue=JNCE_2021158_34C00001_V01_BLUE.histeq.cub to=JNCE_2021158_34C00001_V01_RGB.png mode=RGB stretch=manual rmin=-32418.7 rmax=1040 gmin=-32433 gmax=997 bmin=-32413.6 bmax=1073 quality=80
isis2std red=JNCE_2021158_34C00001_V01_RED.cub+1 green=JNCE_2021158_34C00001_V01_GREEN.cub+1 blue=JNCE_2021158_34C00001_V01_BLUE.cub+1 to=JNCE_2021158_34C00001_V01_RGB_stretch.png mode=RGB stretch=manual rmin=738 rmax=3387 gmin=981 gmax=3542 bmin=821 bmax=3514 quality=80

isis2std from=JNCR_2017192_07C00060_V01_GREEN_0008.cub to=JNCE_2021158_34C00001_V01_GREEN_0008.tif format=TIFF bittype=U16BIT stretch=linear minpercent=0.01 maxpercent=99.99


# for non-histogram stretched images
ls -1 *.cub > images.lis
cubeit fromlist=images.lis to=JNCE_2021158_34C00001_V01_RGB.cub
isis2std red=JNCE_2021158_34C00001_V01_RED.cub+1 green=JNCE_2021158_34C00001_V01_GREEN.cub+1 blue=JNCE_2021158_34C00001_V01_BLUE.cub+1 to=JNCE_2021158_34C00001_V01_RGB.png mode=RGB stretch=manual rmin=50 rmax=2620 gmin=50 gmax=2620 bmin=50 bmax=2620 quality=80

# cam2map test
cp JNCE_2021158_34C00001_V01_GREEN_0018.trim.cub ../mosaic
map2cam from=JNCE_2021158_34C00001_V01_RED.cub match=JNCE_2021158_34C00001_V01_GREEN_0018.trim.cub to=JNCE_2021158_34C00001_V01_RED.cam.cub
map2cam from=JNCE_2021158_34C00001_V01_GREEN.cub match=JNCE_2021158_34C00001_V01_GREEN_0018.trim.cub to=JNCE_2021158_34C00001_V01_GREEN.cam.cub
map2cam from=JNCE_2021158_34C00001_V01_BLUE.cub match=JNCE_2021158_34C00001_V01_GREEN_0018.trim.cub to=JNCE_2021158_34C00001_V01_BLUE.cam.cub

ls -1 *cam.cub > images3.lis
cubeit fromlist=images3.lis to=JNCE_2021158_34C00001_V01_RGB3.cub




cam2map from=\$1 to=../34C00001/projected/\$1 map=../JNCE_2021158_34C00001_V01.map pixres=map -batchlist=34C00001.lis
cd ../34C00001/projected/
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


ls -1 JNCE_2021158_34C00002_V01*cub > 34C00002.lis
cam2map from=\$1 to=../34C00002/projected/\$1 map=../JNCE_2021158_34C00002_V01.map pixres=map -batchlist=34C00002.lis
cd ../34C00002/projected/
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

# photometric processing

ls -1 *34C00001_V01_GREEN_* | sed s/.trim.cub// > image_name.lis
mkdir projected
mkdir mosaic
photomet from=\$1.trim.cub to=\$1.photomet.cub frompvl=../ganymede.pvl maxemission=80 maxincidence=85 \
phtname=LUNARLAMBERTEMPIRICAL \
PhaseList = "0.,10.,20.,30.,40.,50.,60.,70.,80.,90.,100.,110.,120.,130.,140.,150.,160.,170.,180." \
LList = "0.866,0.697,0.580,0.493,0.410,0.326,0.241,0.161,0.090,0.032,-0.012,-0.040,-0.052,-0.055,-0.052,-0.047,-0.037,-0.014,0.000" \
PhaseCurveList = "1.000,1.011,0.995,0.960,0.915,0.865,0.816,0.768,0.719,0.666,0.607,0.538,0.458,0.376,0.295,0.219,0.145,0.064,0.000" \
normname=mixed incref=0 incmat=45 albedo=1.0 thresh=30 \
-batchlist=image_name.lis

cam2map from=\$1.photomet.cub to=../projected/\$1.map.cub map=../JNCE_2021158_34C00001_V01.map pixres=map -batchlist=image_name.lis
cd ../projected
ls -1 *_GREEN_* > GREEN_images.lis
automos fromlist=GREEN_images.lis mosaic=../mosaic/JNCE_2021158_34C00002_V01_GREEN.cub grange=user minlat=-90 maxlat=90 minlon=0 maxlon=360 priority=average 
map2map from=JNCE_2021158_34C00002_V01_GREEN.cub to=JNCE_2021158_34C00002_V01_GREEN.map.cub \
map=/Volumes/TouchT7/data/basemaps/ganymede/Ganymede_Voyager_GalileoSSI_global_mosaic_1km.cub \
matchmap=true
isis2std from=JNCE_2021158_34C00002_V01_GREEN.map.cub+1 to=JNCE_2021158_34C00001_V01_map.png stretch=manual minimum=0 maximum=4300 quality=80
