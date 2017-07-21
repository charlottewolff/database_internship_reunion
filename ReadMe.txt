
********
This document presents how to prepare and run the script for the automatization of Sentinel-2 images acquisition, Sen2cor correction and index computation, as well as csv file writting.
********


I) Folders organization 

The main folder contains 2 folders :
	- CREATE_BDD --> to create the data base with images 
	- CREATE_CSV --> to create the csv file
You also can have the DATA folder -containing the database with raw images, index images and water masks images for each tile- in this folder

	I.1) CREATE_BDD folder
	The folder contains 3 main folders:
		- AUTOMATIZATION --> contains the script 'acquisition.sh' for the every-day acquisition automatization
		- PREPARATION --> contains the script 'preparation.sh'. It prepares the DATA folder and download the old images
		- NEW_INDEX --> create the folder in DATA for a new chosen index

	The 'parametres.txt' file contains the informations about the tiles to download (longitude, latitude and wanted tiles)
	The 'paquages_installation' contains informations about the libraries and software to download to make the script run

	I.2) CREATE_CSV folder
	The folder contains 2 main folders:
		- CSV_PREPARATION --> contains scripts to create a csv for one index with all the images
		- CSV_AUTOMATIZATION --> contains scripts to set up the csv every week

	The 'parametres.txt' file contains the informations about the csv and the different paths. 
	The point shapefile is the shapefile with the different epidemologic sites. 

II) How to use CREATE_BDD

- Create an account on the peps website to download Sentinel-2 images
- In the folders AUTOMATIZATION and PREPARATION, complete the 'peps.txt' file with the information about your peps account

- Prepare the parametres.txt file with the required informations. Water Mask gives the path to the shapefile where each polygon is land.
 
WARNING 
!!!!!!!!!!!!!!!!! The attribut table must have a column called 'land' with 99 for each polygon WARNING !!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!! The DATA folder you create must contain the following folders : rawData and one folder for each index !!!!!!!!!!!!
You must give the tiles you want. 
WARNING

- PREPARATION : open the terminal in the folder and write :

			bash ./PREPARATION/preparation.sh

- This will download the old images and correct them. Wait until it is done.

- AUTOMATIZATION : with a cron command, make the line run every day : 
			
			bash ./AUTOMATIZATION/acquisition.sh


III) Add new index 

It is possible to add new index. In 'acquisition.sh' and 'preparation.sh', index can be added in the INDEX DEFINITION paragraph, following the ndvi example.

In DATA, add a folder with the name of the new index before running the different scripts.

It is also possible to add a new index folder without downloading again all the images. The script is contained in the 'NEW_INDEX' folder. In the script, change the index name with the name of the new index to add. 
Then change the following line :   otbcli_BandMath -il $B04 $B08 -out $1'.tif' -exp "ndvi(im1b1,im2b1)"    with the needed band and the index expression. 
Save the script and open a command line to write :		bash new_index.sh
You must create in DATA a folder with the name of the new index before running the script


VI) How to use CREATE_CSV 
WARNING 
!!!!!!!!!!!!!!!!! The attribut table of shapefile with the epidemiologic sites must contain a column 'tile' containing the name of the tile we take to calculate the mean on this site !!!!!!!!!!!!
WARNING
