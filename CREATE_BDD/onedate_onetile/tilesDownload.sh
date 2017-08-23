##################################################### 
#       Acquisition of one image at one date        #          bash tilesDownload.sh 2017-04-05 2017-05-05 T40KCB,T40KQV
#####################################################
cd ..
mainPath="$PWD"
cd onedate_onetile



##







##########################################################################################
# INDEX DEFINITION
##########################################################################################
INDEX_computation(){
	B04=$(find ./ -name '*B04_10m.jp2')
	B08=$(find ./ -name '*B08_10m.jp2')
	name=${B08:(-38):19}	
	
	#index definition
	echo '************************ NDVI computation ************************'
	indiceName='ndvi'
	otbcli_BandMath -il $B04 $B08 -out indice.tif -exp "ndvi(im1b1,im2b1)"
	gdalwarp -ot Float32 -t_srs EPSG:4326 -r near -of GTiff -co COMPRESS=DEFLATE -co PREDICTOR=1 -co ZLEVEL=6 indice.tif $1/$indiceName/$2/$2'_'$indiceName'_'$3'.tif'
	rm indice.tif

}
##########################################################################################








##










######################    FONCTIONS DEFINITION
parameters() {
#Process to read parameters information
    line2=2
    line4=4
    line6=6
    line8=8
    line10=10
    line14=14
    lonmin=`sed -n ${line2}p $mainPath/parametres.txt`
    lonmax=`sed -n ${line4}p $mainPath/parametres.txt`
    latmin=`sed -n ${line6}p $mainPath/parametres.txt`
    latmax=`sed -n ${line8}p $mainPath/parametres.txt`
    tile=`sed -n ${line10}p $mainPath/parametres.txt`
    tiles=$(echo $tile | tr "," "\n")
    DATA=`sed -n ${line14}p $mainPath/parametres.txt`
}
parameters


sen2corCorrection() {
#Process to correct the images et collect them in a new folder
echo '************************ Downloaded folders unzip ************************'
listZIP=$(find ./ -name '*.zip') 
for file in $listZIP
do
        unzip $file
        rm -r $file
done

echo '************************ Sen2cor correction ************************'
listUNZIP=$(find ./ -name '*.SAFE')
for file in $listUNZIP
do
	source L2A_Bashrc        
	L2A_Process $file
	rm -r $file	
done
}




treatment2017(){
cd acquisition
#correction
sen2corCorrection
#raw data
listL2A=$(find ./ -name '*.SAFE')
for file in $listL2A
do
	cd $file
#find raw data
	tileName=${file:(-27):6}
	tileDate=${file:(-20):8}
	mkdir $DATA/rawData/$tileName/$tileDate
	R10bands=$(find ./ -name '*_B*10m.jp2')
	R20bands=$(find ./ -name '*_B*20m.jp2' ! -name '*_B02*' ! -name '*_B03*' ! -name '*_B04*' ! -name '*_B08*')
	R60bands=$(find ./ -name '*_B01_60m.jp2' -o  -name '*_B09_60m.jp2')
	rawMask=$(find ./ -name '*_CLD_20m.jp2')	
#copy raw data 
	cp -r $R10bands $DATA/rawData/$tileName/$tileDate
	cp -r $R20bands $DATA/rawData/$tileName/$tileDate
	cp -r $R60bands $DATA/rawData/$tileName/$tileDate
	cp $rawMask $DATA/rawData/$tileName/$tileDate
#create sen2cor mask
	outMask=$DATA/rawData/$tileName/$tileDate/$tileName'_'$tileDate'_Sen2corMask.tif'
	B4=$(find ./ -name '*_B04_10m.jp2')
	python $mainPath/PREPARATION/createCLDMask.py $rawMask $B4 $outMask
#index computation
	INDEX_computation $DATA $tileName $tileDate	 
	cd ..
	rm -r $file
done
cd ..
}




#-------------------------------------
while getopts "b:e:t:" option
do
case $option in
b)
 echo "Starting date : $OPTARG"
 B_date=$OPTARG
 ;;
 e)
 echo "Stopping date : $OPTARG"
 E_date=$OPTARG
 ;;
 t)
 echo "Chosen tiles : $OPTARG"
 tiles=$OPTARG
 ;;
 esac
 done

cd $mainPath/onedate_onetile
     python ./peps_download.py -c S2ST --lonmin $lonmin --lonmax $lonmax --latmin $latmin --latmax $latmax -a peps.txt -d $B_date -f $E_date -w ./acquisition -t $tiles

treatment2017
#-------------------------------------



