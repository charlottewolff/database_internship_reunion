########################################################### 
# Computation new index on the images already doawnloaded #
###########################################################

INDEX_NAME='new_index_name'








##



##########################################################################################
# INDEX DEFINITION
##########################################################################################
INDEX_computation(){
	B04=$(find ./ -name '*B04_10m.jp2')
	B08=$(find ./ -name '*B08_10m.jp2')
	name=${B08:(-38):19}	
	
	#index definition
	echo '************************ '$INDEX_NAME' computation ************************'
	otbcli_BandMath -il $B04 $B08 -out indice.tif  -exp "ndvi(im1b1,im2b1)"
	gdalwarp -ot Float32 -t_srs EPSG:4326 -r near -of GTiff -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 indice.tif $2/$3'_'$1'_'$4'.tif'   
	rm indice.tif 		
}
##########################################################################################



##








######################    FONCTIONS DEFINITION
cd ..
mainPath="$PWD"

parameters() {
#Process to read parameters information
    line14=14
    DATA=`sed -n ${line14}p $mainPath/parametres.txt`
}
parameters

# index folder mkdir
mkdir $DATA/$INDEX_NAME


cd $DATA/rawData

tiles=$(find ./ -type d -name 'T*')


for tileName in $tiles
do
	out=$DATA/$INDEX_NAME/$tileName	
	mkdir $out
	cd $tileName	
	for tileDate in $(ls -D)
	do
		cd $tileDate				
		INDEX_computation $INDEX_NAME $out $tileName $tileDate
		cd .. 
	done
	cd ..
done
